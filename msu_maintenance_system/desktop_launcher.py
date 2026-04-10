"""
Windows desktop entry point for PyInstaller (.exe).
Sets writable data dirs and serves the app with Waitress (no Flask dev server).
"""
from __future__ import annotations

import os
import socket
import sqlite3
import sys
import threading
import webbrowser


def _prepare_environment() -> None:
    # Before any app import: services/__init__.py pulls in matplotlib via analytics_service.
    # Non-GUI backend avoids immediate exit when the frozen .exe has no display / wrong Tk.
    os.environ.setdefault("MPLBACKEND", "Agg")

    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
        os.chdir(base)
        if base not in sys.path:
            sys.path.insert(0, base)
    else:
        os.chdir(os.path.dirname(os.path.abspath(__file__)))

    from env_bootstrap import load_msu_environment

    load_msu_environment()

    local = os.environ.get("LOCALAPPDATA") or os.path.join(
        os.path.expanduser("~"), "AppData", "Local"
    )
    os.environ.setdefault("FLASK_ENV", "development")
    os.environ.setdefault("USE_SQLITE", "1")
    os.environ.setdefault(
        "MSU_INSTANCE_DIR",
        os.path.join(local, "MSUMaintenance", "instance"),
    )
    os.environ.setdefault(
        "MSU_REPORTS_DIR",
        os.path.join(local, "MSUMaintenance", "reports"),
    )
    os.makedirs(os.environ["MSU_INSTANCE_DIR"], exist_ok=True)
    os.makedirs(os.environ["MSU_REPORTS_DIR"], exist_ok=True)


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _can_connect_sql_server() -> tuple[bool, str]:
    try:
        import pyodbc
    except Exception as exc:
        return False, f"pyodbc unavailable ({exc})"

    drivers = set(pyodbc.drivers())
    if "ODBC Driver 18 for SQL Server" not in drivers:
        return False, "missing ODBC Driver 18 for SQL Server"

    db_server = os.environ.get("DB_SERVER", "localhost")
    db_name = os.environ.get("DB_NAME", "CentralServices_AM_DB")
    db_user = os.environ.get("DB_USER", "")
    db_password = os.environ.get("DB_PASSWORD", "")

    if db_user and db_password:
        conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={db_server};DATABASE={db_name};"
            f"UID={db_user};PWD={db_password};"
            "Encrypt=no;TrustServerCertificate=yes;"
        )
    else:
        conn_str = (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"SERVER={db_server};DATABASE={db_name};"
            "Trusted_Connection=yes;Encrypt=no;TrustServerCertificate=yes;"
        )

    try:
        conn = pyodbc.connect(conn_str, timeout=5)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        value = cur.fetchone()[0]
        conn.close()
        if value != 1:
            return False, "SQL Server probe returned unexpected value"
        return True, f"connected to SQL Server {db_server}/{db_name}"
    except Exception as exc:
        return False, f"SQL Server not reachable ({exc})"


def _configure_database_backend() -> None:
    """
    Auto-configure DB backend at startup:
    - Use SQL Server when explicitly requested and healthy.
    - Otherwise force local SQLite fallback for a reliable EXE experience.
    """
    want_sqlite = _env_bool("USE_SQLITE", default=True)
    if want_sqlite:
        print("Database preflight: using SQLite mode.", flush=True)
        return

    ok, detail = _can_connect_sql_server()
    if ok:
        print(f"Database preflight: SQL Server healthy ({detail}).", flush=True)
        return

    os.environ["USE_SQLITE"] = "1"
    print(
        f"Database preflight: SQL Server unavailable, switching to SQLite ({detail}).",
        flush=True,
    )


def _check_sqlite_writable() -> tuple[bool, str]:
    instance_dir = os.environ["MSU_INSTANCE_DIR"]
    db_path = os.path.join(instance_dir, "msu_maintenance.db")
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        _ = cur.fetchone()
        conn.close()
        return True, f"sqlite file ready at {db_path}"
    except Exception as exc:
        return False, f"sqlite file check failed ({exc})"


def _find_listen_port(preferred: int, attempts: int = 40) -> int:
    """Pick a free loopback port (Windows often blocks 5000 for other services)."""
    for p in range(preferred, preferred + attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", p))
                return p
            except OSError:
                continue
    raise RuntimeError(
        f"No free TCP port in range {preferred}–{preferred + attempts - 1}."
    )


def _seed_sqlite_demo(flask_app) -> None:
    uri = flask_app.config.get("SQLALCHEMY_DATABASE_URI") or ""
    if not str(uri).startswith("sqlite:"):
        return
    import importlib

    from app.extensions import db
    importlib.import_module("app.models")

    with flask_app.app_context():
        db.create_all()
        from app.models import User

        if User.query.count() > 0:
            return
        demo_pw = os.environ.get("MSU_DEMO_PASSWORD", "ChangeMeAfterClone123!")
        staff = User(email="demo@staff.msu.ac.zw", role="staff")
        staff.set_password(demo_pw)
        admin = User(email="admin@staff.msu.ac.zw", role="admin")
        admin.set_password(demo_pw)
        db.session.add_all([staff, admin])
        db.session.commit()


def _verify_runtime_database_health(flask_app) -> None:
    uri = str(flask_app.config.get("SQLALCHEMY_DATABASE_URI") or "")
    from app.extensions import db

    with flask_app.app_context():
        conn = db.engine.connect()
        value = conn.exec_driver_sql("SELECT 1").scalar()
        conn.close()
        if value != 1:
            raise RuntimeError("database health check failed (SELECT 1 != 1)")

    if uri.startswith("sqlite:"):
        ok, detail = _check_sqlite_writable()
        if not ok:
            raise RuntimeError(detail)
        print(f"Database health: OK ({detail}).", flush=True)
    else:
        print("Database health: OK (SQL Server query successful).", flush=True)


def main() -> None:
    _prepare_environment()
    _configure_database_backend()

    from app import create_app

    config_name = os.environ.get("FLASK_ENV", "development")
    try:
        app = create_app(config_name)
    except Exception as exc:
        # Last-resort recovery for packaged desktop mode.
        if not _env_bool("USE_SQLITE", default=True):
            os.environ["USE_SQLITE"] = "1"
            print(
                f"Database startup: app init failed with SQL Server ({exc}); retrying with SQLite.",
                flush=True,
            )
            app = create_app(config_name)
        else:
            raise
    # Packaged .exe: turn off Flask debug so routes don’t expose the interactive debugger
    # or confusing “unhandled” tracebacks to the browser.
    if getattr(sys, "frozen", False):
        app.config["DEBUG"] = False
        app.config["PROPAGATE_EXCEPTIONS"] = False
    _seed_sqlite_demo(app)
    _verify_runtime_database_health(app)

    preferred = int(os.environ.get("PORT", "5000"))
    port = _find_listen_port(preferred)
    url = f"http://127.0.0.1:{port}"

    def _open_browser() -> None:
        import time

        time.sleep(1.0)
        webbrowser.open(url)

    threading.Thread(target=_open_browser, daemon=True).start()

    from waitress import serve

    if port != preferred:
        print(f"Port {preferred} was in use; listening on {port}.", flush=True)
    print(f"MSU Maintenance — {url}  (close this window to stop)", flush=True)
    if getattr(sys, "frozen", False):
        tpl = os.path.join(sys._MEIPASS, "packaging", "sql_connection.env.example")
        if os.path.isfile(tpl):
            dest = os.path.join(
                os.environ.get("LOCALAPPDATA", ""),
                "MSUMaintenance",
                ".env",
            )
            print(
                f"SQL Server (pyodbc bundled): copy/edit template → {dest}  (source: {tpl}). "
                "Install ODBC Driver 18 on this PC if needed.",
                flush=True,
            )
    serve(app, host="127.0.0.1", port=port, threads=4)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        import traceback

        traceback.print_exc()
        print("\nThe app stopped because of an error above.", flush=True)
        try:
            input("Press Enter to close…")
        except EOFError:
            pass
        raise
