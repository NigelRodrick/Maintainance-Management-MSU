import os
from app import create_app

# Determine configuration based on environment
config_name = os.environ.get('FLASK_ENV', 'development')

app = create_app(config_name)


def _ensure_sqlite_schema_and_demo_users():
    """Create tables and demo logins when using SQLite (default for local development)."""
    uri = app.config.get('SQLALCHEMY_DATABASE_URI') or ''
    if not str(uri).startswith('sqlite:'):
        return
    from app.extensions import db
    import app.models  # noqa: F401 — register ORM models

    with app.app_context():
        db.create_all()
        from app.models import User

        if User.query.count() > 0:
            return
        # Set MSU_DEMO_PASSWORD in .env for local dev; never commit real passwords.
        demo_pw = os.environ.get('MSU_DEMO_PASSWORD', 'ChangeMeAfterClone123!')
        staff = User(email='demo@staff.msu.ac.zw', role='staff')
        staff.set_password(demo_pw)
        admin = User(email='admin@staff.msu.ac.zw', role='admin')
        admin.set_password(demo_pw)
        db.session.add_all([staff, admin])
        db.session.commit()


_ensure_sqlite_schema_and_demo_users()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', '5000'))
    app.run(debug=True, host='0.0.0.0', port=port)
