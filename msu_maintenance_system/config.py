import os
from datetime import timedelta

_BASE_DIR = os.path.abspath(os.path.dirname(__file__))
_INSTANCE_DIR = os.path.join(_BASE_DIR, 'instance')


def _writable_instance_dir():
    """SQLite + instance files; use MSU_INSTANCE_DIR when installed under Program Files."""
    override = os.environ.get('MSU_INSTANCE_DIR')
    if override:
        return os.path.abspath(override)
    return _INSTANCE_DIR


def _reports_dir():
    """Generated Excel reports — writable path when MSU_REPORTS_DIR is set (MSI / Program Files)."""
    override = os.environ.get('MSU_REPORTS_DIR')
    if override:
        return os.path.abspath(override)
    return os.path.join(_BASE_DIR, 'reports')


def _mssql_uri():
    """SQL Server URL (requires pyodbc + ODBC driver on the machine)."""
    db_server = os.environ.get('DB_SERVER', 'localhost')
    db_name = os.environ.get('DB_NAME', 'CentralServices_AM_DB')
    db_user = os.environ.get('DB_USER', '')
    db_password = os.environ.get('DB_PASSWORD', '')
    if db_user and db_password:
        return (
            f"mssql+pyodbc://{db_user}:{db_password}@{db_server}/{db_name}"
            f"?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes&Encrypt=no"
        )
    return (
        f"mssql+pyodbc://@{db_server}/{db_name}"
        f"?driver=ODBC+Driver+18+for+SQL+Server&Trusted_Connection=yes&TrustServerCertificate=yes&Encrypt=no"
    )


def _sqlite_uri():
    inst = _writable_instance_dir()
    os.makedirs(inst, exist_ok=True)
    db_path = os.path.join(inst, 'msu_maintenance.db').replace('\\', '/')
    return f'sqlite:///{db_path}'


def build_sqlalchemy_uri(use_sqlite_default):
    """
    DATABASE_URL overrides everything.
    Otherwise USE_SQLITE (when set) or use_sqlite_default picks SQLite vs SQL Server.
    """
    direct = os.environ.get('DATABASE_URL')
    if direct:
        return direct
    raw = os.environ.get('USE_SQLITE')
    if raw is not None:
        use_sqlite = raw.lower() in ('1', 'true', 'yes')
    else:
        use_sqlite = use_sqlite_default
    if use_sqlite:
        return _sqlite_uri()
    return _mssql_uri()


class Config:
    # Security - MUST be set via environment variables
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    # Session configuration
    PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.environ.get('SESSION_TIMEOUT_HOURS', '8')))

    # File paths
    BASE_DIR = _BASE_DIR
    MODELS_DIR = os.path.join(BASE_DIR, 'models')
    STATIC_DIR = os.path.join(BASE_DIR, 'static')
    REPORTS_DIR = _reports_dir()

    # Email validation pattern
    EMAIL_PATTERN = os.environ.get('EMAIL_PATTERN', r'^[a-zA-Z0-9]+@staff\.msu\.ac\.zw$')


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = build_sqlalchemy_uri(use_sqlite_default=True)
    # Allow login over http://localhost (Secure cookies break sessions without HTTPS)
    SESSION_COOKIE_SECURE = False
    FORCE_HTTPS = False


class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = build_sqlalchemy_uri(use_sqlite_default=False)

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
