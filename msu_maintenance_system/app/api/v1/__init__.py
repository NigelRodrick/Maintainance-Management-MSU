"""
API v1 Package
Versioned REST API endpoints for the MSU Maintenance System.
"""

from flask import Blueprint

# Create the API v1 blueprint
api_v1_bp = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# Import all endpoint modules to register routes
from . import auth
from . import jobs
from . import workers
from . import assignments
from . import notifications
