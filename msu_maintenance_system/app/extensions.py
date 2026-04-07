"""
Flask Extensions Configuration

Centralized initialization of all Flask extensions.
"""

import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import redis
from celery import Celery

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
cache = None
celery = None

def init_extensions(app):
    """Initialize all extensions with the Flask app."""
    global cache, celery
    
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Redis client connects lazily on first command; no Redis server is required at startup.
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    cache = redis.from_url(redis_url, decode_responses=False)
    
    # Initialize Celery (Flask only — do not load celery.fixups.django; it is not
    # used here and PyInstaller builds fail with ModuleNotFoundError otherwise.)
    celery = Celery(app.name, fixups=())
    celery.conf.update(
        broker_url=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
        result_backend=os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0'),
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
    )
    
    # Configure LoginManager
    login_manager.login_view = 'auth.select_login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
