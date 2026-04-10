"""
Create ORM tables on an empty SQL Server database and seed demo users (if none).

Run after Docker SQL Server is up and the database exists. Set USE_SQLITE=0 and DB_* (or DATABASE_URL).

Usage (from msu_maintenance_system):
  set USE_SQLITE=0
  set DB_SERVER=localhost
  set DB_USER=sa
  set DB_PASSWORD=...
  python scripts/bootstrap_mssql_schema.py
"""
from __future__ import annotations

import os
import sys

# Ensure repo root (parent of this script's package) is importable
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

os.environ.setdefault("FLASK_ENV", "development")


def main() -> None:
    from env_bootstrap import load_msu_environment

    load_msu_environment()

    if os.environ.get("USE_SQLITE", "").lower() in ("1", "true", "yes"):
        print("USE_SQLITE is enabled; set USE_SQLITE=0 to bootstrap SQL Server.")
        sys.exit(1)

    # Minimal app: avoid create_app() (pulls analytics/pandas) during schema bootstrap.
    from flask import Flask
    from config import DevelopmentConfig
    from app.extensions import db
    import app.models  # noqa: F401

    app = Flask(__name__)
    app.config.from_object(DevelopmentConfig)
    uri = app.config.get("SQLALCHEMY_DATABASE_URI") or ""
    if str(uri).startswith("sqlite:"):
        print("Config still points to SQLite; set USE_SQLITE=0 and DB_SERVER / DB_USER / DB_PASSWORD.")
        sys.exit(1)

    db.init_app(app)

    demo_pw = os.environ.get("MSU_DEMO_PASSWORD", "ChangeMeAfterClone123!")

    with app.app_context():
        print("Creating tables from SQLAlchemy models...")
        db.create_all()
        from app.models import User

        if User.query.count() > 0:
            print(f"Users already present ({User.query.count()}); skipping demo seed.")
        else:
            staff = User(email="demo@staff.msu.ac.zw", role="staff")
            staff.set_password(demo_pw)
            admin = User(email="admin@staff.msu.ac.zw", role="admin")
            admin.set_password(demo_pw)
            db.session.add_all([staff, admin])
            db.session.commit()
            print("Seeded demo@staff.msu.ac.zw and admin@staff.msu.ac.zw")

        conn = db.engine.connect()
        one = conn.exec_driver_sql("SELECT 1").scalar()
        conn.close()
        if one != 1:
            raise RuntimeError("SELECT 1 check failed")
        print("SQL Server schema bootstrap OK.")


if __name__ == "__main__":
    main()
