"""
Security Configuration
Implements HTTP security headers, session security, and security policies.
"""

import os
from flask import Flask
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime, timedelta


def init_security_headers(app: Flask):
    """Initialize HTTP security headers with Flask-Talisman."""
    
    # Content Security Policy - Allow only necessary sources
    csp = {
        'default-src': "'self'",
        'script-src': [
            "'self'",
            "'unsafe-inline'",  # Required for Bootstrap and existing templates
            'https://cdn.jsdelivr.net',
            'https://cdn.plot.ly',
            'https://code.jquery.com'
        ],
        'style-src': [
            "'self'",
            "'unsafe-inline'",  # Required for existing templates
            'https://cdn.jsdelivr.net',
            'https://fonts.googleapis.com'
        ],
        'img-src': [
            "'self'",
            'data:',
            'https:'
        ],
        'font-src': [
            "'self'",
            'https://fonts.gstatic.com'
        ],
        'connect-src': [
            "'self'"
        ],
        'frame-ancestors': "'none'",
        'base-uri': "'self'",
        'form-action': "'self'"
    }
    
    # Talisman configuration
    Talisman(app, 
        force_https=app.config.get('FORCE_HTTPS', False),
        strict_transport_security=True,
        strict_transport_security_preload=True,
        strict_transport_security_max_age=31536000,
        content_security_policy=csp,
        referrer_policy='strict-origin-when-cross-origin',
        permissions_policy={
            'geolocation': [],
            'camera': [],
            'microphone': [],
            'payment': [],
            'usb': [],
            'magnetometer': [],
            'gyroscope': [],
            'accelerometer': []
        })


def init_session_security(app: Flask):
    """Configure secure session settings."""
    
    # Session security settings
    app.config.update(
        SESSION_COOKIE_SECURE=app.config.get('SESSION_COOKIE_SECURE', True),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=30),  # 30 minutes
        SESSION_PROTECTION='strong'
    )


def init_rate_limiting(app: Flask) -> Limiter:
    """Initialize rate limiting with Flask-Limiter."""
    
    limiter = Limiter(
        key_func=get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    
    # Add specific rate limits for sensitive endpoints
    limiter.limit("5 per minute")(lambda: None)  # Will be applied to auth endpoints
    
    return limiter


def validate_password_complexity(password: str) -> tuple[bool, str]:
    """
    Validate password complexity according to security policy.
    
    Requirements:
    - Minimum 10 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
    
    if len(password) < 10:
        return False, "Password must be at least 10 characters long"
    
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter"
    
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter"
    
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit"
    
    special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    if not any(c in special_chars for c in password):
        return False, f"Password must contain at least one special character ({special_chars})"
    
    # Check for common weak patterns
    if password.lower() in ['password', '1234567890', 'qwertyuiop', 'admin123']:
        return False, "Password is too common and weak"
    
    # Check for sequential characters
    if any(ord(password[i]) + 1 == ord(password[i + 1]) for i in range(len(password) - 1)):
        return False, "Password cannot contain sequential characters"
    
    return True, "Password meets complexity requirements"


class BruteForceProtection:
    """Brute force protection for login attempts."""
    
    def __init__(self, max_attempts=5, lockout_duration=900):
        self.max_attempts = max_attempts
        self.lockout_duration = lockout_duration  # 15 minutes
        self.attempts = {}  # In production, use Redis or database
    
    def record_failed_attempt(self, identifier: str) -> tuple[bool, int]:
        """Record a failed login attempt and return if locked out."""
        if identifier not in self.attempts:
            self.attempts[identifier] = {'count': 0, 'locked_until': None}
        
        # Check if currently locked
        if self.attempts[identifier]['locked_until']:
            if datetime.utcnow().timestamp() < self.attempts[identifier]['locked_until']:
                remaining = int(self.attempts[identifier]['locked_until'] - datetime.utcnow().timestamp())
                return True, remaining
            else:
                # Lockout expired, reset counter
                self.attempts[identifier]['count'] = 0
                self.attempts[identifier]['locked_until'] = None
        
        # Increment attempt counter
        self.attempts[identifier]['count'] += 1
        
        # Check if should be locked
        if self.attempts[identifier]['count'] >= self.max_attempts:
            self.attempts[identifier]['locked_until'] = datetime.utcnow().timestamp() + self.lockout_duration
            return True, self.lockout_duration
        
        return False, 0
    
    def record_successful_attempt(self, identifier: str):
        """Record a successful login attempt and reset counter."""
        if identifier in self.attempts:
            self.attempts[identifier]['count'] = 0
            self.attempts[identifier]['locked_until'] = None
    
    def is_locked(self, identifier: str) -> tuple[bool, int]:
        """Check if identifier is currently locked out."""
        if identifier not in self.attempts:
            return False, 0
        
        if self.attempts[identifier]['locked_until']:
            if datetime.utcnow().timestamp() < self.attempts[identifier]['locked_until']:
                remaining = int(self.attempts[identifier]['locked_until'] - datetime.utcnow().timestamp())
                return True, remaining
            else:
                # Lockout expired
                self.attempts[identifier]['count'] = 0
                self.attempts[identifier]['locked_until'] = None
                return False, 0
        
        return False, 0


# Global brute force protection instance
brute_force_protection = BruteForceProtection()


def init_security(app: Flask):
    """Initialize all security features."""
    
    # Initialize security headers
    init_security_headers(app)
    
    # Initialize session security
    init_session_security(app)
    
    # Initialize rate limiting
    limiter = init_rate_limiting(app)
    
    # Store limiter in app context for use in routes
    app.limiter = limiter
    
    # Store brute force protection
    app.brute_force_protection = brute_force_protection
    
    return limiter
