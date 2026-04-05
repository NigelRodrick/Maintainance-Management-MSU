"""
Authentication Blueprint

Handles login route selection and authentication logic.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from ..models import User
from ..extensions import db

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/select')
def select_login():
    """Main login selection page."""
    if current_user.is_authenticated:
        # Redirect to appropriate dashboard if already logged in
        return redirect(url_for('main.dashboard'))
    return render_template('auth/select_login.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login_default():
    """Default login route - redirects to role selection."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.select_login'))

@auth_bp.route('/login/<role>', methods=['GET', 'POST'])
def login(role):
    """Handle role-specific login."""
    
    # Redirect if already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Validate role
    valid_roles = ['staff', 'admin', 'maintenance_admin']
    if role not in valid_roles:
        flash('Invalid role specified', 'error')
        return redirect(url_for('auth.select_login'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Email and password are required', 'error')
            return render_template(f'auth/{role}_login.html', role=role)
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Invalid email or password', 'error')
            return render_template(f'auth/{role}_login.html', role=role)
        
        # Verify role matches
        if user.role != role:
            flash(f'Access denied. This login is for {role} users only.', 'error')
            return render_template(f'auth/{role}_login.html', role=role)
        
        # Check if user is active
        if not user.is_active:
            flash('Your account has been deactivated', 'error')
            return render_template(f'auth/{role}_login.html', role=role)
        
        # Login user
        login_user(user)
        flash(f'Welcome back, {user.email}!', 'success')
        
        # Redirect to appropriate dashboard
        return redirect(url_for('main.dashboard'))
    
    return render_template(f'auth/{role}_login.html', role=role)

@auth_bp.route('/logout')
def logout():
    """Handle user logout."""
    from flask import session
    logout_user()
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.select_login'))
