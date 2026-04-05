"""
Unified Authentication Service

Bridges Flask-Login and legacy session-based authentication
to provide a single, consistent authentication interface.
"""

import logging
from typing import Optional, Tuple, Any
from flask import session, request
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash

from .database import db_service
from ..models import User
from ..utils.auth_utils import get_redirect_dashboard, validate_role
from ..utils.logging_config import log_authentication_attempt, log_system_error, get_logger

# Setup logger
logger = get_logger('unified_auth_service')


class UnifiedAuthService:
    """
    Unified authentication service that provides a single interface
    for both Flask-Login and legacy session-based authentication.
    """
    
    def __init__(self):
        self.legacy_mode = False  # Flag to track legacy session usage
        self.email_pattern = r'^[a-zA-Z0-9]+@staff\.msu\.ac\.zw$'
    
    def authenticate_user(self, email: str, password: str) -> Tuple[Optional[dict], str]:
        """
        Authenticate user using unified approach.
        
        Args:
            email: User email
            password: User password
            
        Returns:
            tuple: (user_data, message) or (None, error_message)
        """
        if not self._validate_email(email):
            log_authentication_attempt(email, False)
            return None, "Invalid MSU staff email format"
        
        try:
            # Try SQLAlchemy approach first (preferred)
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                # Set up Flask-Login session
                if login_user(user):
                    # Also set legacy session for backward compatibility
                    session['user_id'] = user.id
                    session['email'] = user.email
                    session['role'] = user.role
                    
                    user_data = {
                        'id': user.id,
                        'email': user.email,
                        'role': user.role,
                        'auth_method': 'flask_login'
                    }
                    
                    log_authentication_attempt(email, True)
                    logger.info(f"User authenticated via Flask-Login: {email}")
                    return user_data, "Login successful"
                else:
                    log_authentication_attempt(email, False)
                    return None, "Login failed"
            else:
                log_authentication_attempt(email, False)
                return None, "Invalid email or password"
                
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            log_system_error(e, "user_authentication")
            return None, "Authentication system error"
    
    def create_user(self, email: str, password: str, role: str = 'USER') -> Tuple[bool, str]:
        """
        Create a new user with validated role.
        
        Args:
            email: User email
            password: User password
            role: User role
            
        Returns:
            tuple: (success, message)
        """
        if not self._validate_email(email):
            return False, "Invalid MSU staff email format"
        
        # Validate role
        validated_role = validate_role(role)
        if not validated_role:
            return False, "Invalid role specified"
        
        try:
            # Check if user already exists
            if User.query.filter_by(email=email).first():
                return False, "User with this email already exists"
            
            # Create user using SQLAlchemy
            user = User(email=email, role=validated_role)
            user.set_password(password)
            
            from ..extensions import db
            db.session.add(user)
            db.session.commit()
            
            logger.info(f"User created successfully: {email} with role {validated_role}")
            return True, "User created successfully"
            
        except Exception as e:
            logger.error(f"User creation error: {str(e)}")
            return False, f"Error creating user: {str(e)}"
    
    def logout_user(self) -> str:
        """
        Logout user using unified approach.
        
        Returns:
            str: Success message
        """
        try:
            # Clear Flask-Login session
            logout_user()
            
            # Clear legacy session
            session.clear()
            
            logger.info("User logged out successfully")
            return "You have been logged out"
            
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return "Error during logout"
    
    def get_current_user(self) -> Optional[dict]:
        """
        Get current user information in unified format.
        
        Returns:
            dict: User data or None if not authenticated
        """
        try:
            if current_user.is_authenticated:
                return {
                    'id': current_user.id,
                    'email': current_user.email,
                    'role': current_user.role,
                    'is_authenticated': True,
                    'auth_method': 'flask_login'
                }
            else:
                # Fallback to legacy session check
                if 'user_id' in session:
                    return {
                        'id': session.get('user_id'),
                        'email': session.get('email'),
                        'role': session.get('role'),
                        'is_authenticated': True,
                        'auth_method': 'legacy_session'
                    }
                else:
                    return None
        except Exception as e:
            logger.error(f"Error getting current user: {str(e)}")
            return None
    
    def is_authenticated(self) -> bool:
        """
        Check if current user is authenticated.
        
        Returns:
            bool: True if authenticated
        """
        try:
            # Check Flask-Login first
            if current_user.is_authenticated:
                return True
            
            # Fallback to legacy session
            return 'user_id' in session
            
        except Exception as e:
            logger.error(f"Authentication check error: {str(e)}")
            return False
    
    def get_user_role(self) -> str:
        """
        Get current user's role.
        
        Returns:
            str: User role or 'anonymous'
        """
        try:
            user_data = self.get_current_user()
            return user_data.get('role', 'anonymous') if user_data else 'anonymous'
        except Exception as e:
            logger.error(f"Error getting user role: {str(e)}")
            return 'anonymous'
    
    def require_login(self, redirect_url: str = None) -> Tuple[bool, str]:
        """
        Check if login is required and provide redirect.
        
        Args:
            redirect_url: Custom redirect URL
            
        Returns:
            tuple: (is_authenticated, redirect_url_or_message)
        """
        if self.is_authenticated():
            return True, None
        
        if not redirect_url:
            redirect_url = get_redirect_dashboard(self.get_user_role()) if self.get_user_role() != 'anonymous' else '/login'
        
        return False, redirect_url
    
    def _validate_email(self, email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email to validate
            
        Returns:
            bool: True if valid
        """
        import re
        return re.match(self.email_pattern, email) is not None
    
    def sync_legacy_session(self) -> bool:
        """
        Sync legacy session with Flask-Login for backward compatibility.
        
        Returns:
            bool: True if sync successful
        """
        try:
            if current_user.is_authenticated:
                session['user_id'] = current_user.id
                session['email'] = current_user.email
                session['role'] = current_user.role
                logger.debug("Legacy session synced with Flask-Login")
                return True
            return False
        except Exception as e:
            logger.error(f"Session sync error: {str(e)}")
            return False


# Create global instance
unified_auth_service = UnifiedAuthService()


# Backward compatibility functions
def login_required_legacy(f):
    """
    Legacy login_required decorator that uses unified auth service.
    """
    from functools import wraps
    from flask import redirect, url_for, flash
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_auth, redirect_url = unified_auth_service.require_login()
        if not is_auth:
            flash('Please login to access this page', 'warning')
            return redirect(redirect_url or url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required_legacy(f):
    """
    Legacy admin_required decorator that uses unified auth service.
    """
    from functools import wraps
    from flask import redirect, url_for, flash
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_auth, redirect_url = unified_auth_service.require_login()
        if not is_auth:
            flash('Please login to access this page', 'warning')
            return redirect(redirect_url or url_for('auth.login'))
        
        if unified_auth_service.get_user_role() != 'admin':
            flash('Admin access required', 'error')
            return redirect(url_for('main.dashboard'))
        
        return f(*args, **kwargs)
    return decorated_function
