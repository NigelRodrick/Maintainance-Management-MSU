import os

from flask import Flask, Response
from werkzeug.exceptions import HTTPException

from config import config

def create_app(config_name='default'):
    """Application factory pattern."""
    
    # Get parent directory of app/ (project root)
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
    
    app = Flask(__name__, 
                template_folder=template_dir, 
                static_folder=static_dir)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    from .extensions import init_extensions
    init_extensions(app)
    
    # Initialize security features
    from .security import init_security
    limiter = init_security(app)
    
    # Setup user loader for Flask-Login
    from .models import User
    
    @app.login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints with safe imports and logging
    import logging
    logger = logging.getLogger(__name__)
    
    # Core blueprints (always required)
    try:
        from .auth import auth_bp
        from .routes.main import main_bp
        from .routes.analytics import analytics_bp
        from .routes.reports import reports_bp
        from .routes.user_routes import user_bp
        from .routes.supervisor_routes import supervisor_bp
        from .routes.admin_routes import admin_bp
        from .routes.admin_full_access import admin_full_access_bp
        
        app.register_blueprint(auth_bp)
        app.register_blueprint(main_bp)
        app.register_blueprint(analytics_bp)
        app.register_blueprint(reports_bp)
        app.register_blueprint(user_bp)
        app.register_blueprint(supervisor_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(admin_full_access_bp)
        logger.info("Core blueprints registered successfully")
    except Exception as e:
        logger.error(f"Failed to register core blueprints: {e}")
        raise
    
    # Optional blueprints (with graceful fallback)
    optional_blueprints = [
        ('staff', 'staff_bp', 'from .staff import staff_bp'),
        # Skip admin_legacy due to conflicts with admin blueprint
        ('maintenance_admin', 'maintenance_admin_bp', 'from .maintenance_admin import maintenance_admin_bp')
    ]
    
    for name, var_name, import_stmt in optional_blueprints:
        try:
            # Safe blueprint import without exec()
            if name == 'staff':
                from .staff import staff_bp
                blueprint = staff_bp
            elif name == 'maintenance_admin':
                from .maintenance_admin import maintenance_admin_bp
                blueprint = maintenance_admin_bp
            else:
                logger.warning(f"Unknown optional blueprint: {name}")
                continue
                
            app.register_blueprint(blueprint)
            logger.info(f"Optional blueprint '{name}' registered successfully")
        except ImportError as e:
            logger.warning(f"Optional blueprint '{name}' not available: {e}")
            logger.info(f"Continuing without '{name}' blueprint")
        except Exception as e:
            logger.error(f"Failed to register optional blueprint '{name}': {e}")
            logger.info(f"Continuing without '{name}' blueprint")

    @app.errorhandler(Exception)
    def handle_unhandled_exception(e):
        """Avoid raw tracebacks in the browser / Waitress; log server-side."""
        if isinstance(e, HTTPException):
            return e
        app.logger.exception("Unhandled exception")
        html = (
            "<!DOCTYPE html><html><head><meta charset='utf-8'><title>Error</title></head>"
            "<body><h1>Something went wrong</h1>"
            "<p>An unexpected error occurred. Please try again later.</p></body></html>"
        )
        return Response(html, status=500, mimetype="text/html")

    return app
