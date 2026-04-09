"""
Windows desktop entry point for PyInstaller (.exe).
Sets writable data dirs and serves the app with Waitress (no Flask dev server).
"""
from __future__ import annotations

import os
import socket
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


def main() -> None:
    _prepare_environment()

    from app import create_app

    config_name = os.environ.get("FLASK_ENV", "development")
    app = create_app(config_name)
    # Packaged .exe: turn off Flask debug so routes don’t expose the interactive debugger
    # or confusing “unhandled” tracebacks to the browser.
    if getattr(sys, "frozen", False):
        app.config["DEBUG"] = False
        app.config["PROPAGATE_EXCEPTIONS"] = False
    _seed_sqlite_demo(app)

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
