"""
Admin Dashboard Routes for MSU Maintenance System

Administrative interface with full system access and user management.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required

from ..decorators.auth_decorators import role_required, log_access
from ..services.dashboard_service import dashboard_service
from ..services.auth_service import auth_service
from ..constants.roles import ROLE_DISPLAY_NAMES, ROLE_COLORS, ROLE_ICONS

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@login_required
@role_required('ADMIN')
@log_access('view_dashboard')
def admin_dashboard():
    """
    Admin dashboard with system overview and metrics.
    
    Features:
    - User management
    - System metrics
    - Activity logs
    - Total users/jobs/completed jobs
    """
    try:
        # Get admin metrics
        metrics = dashboard_service.get_admin_metrics()
        
        return render_template('admin/dashboard.html', 
                         metrics=metrics,
                         user_role='ADMIN',
                         ROLE_DISPLAY_NAMES=ROLE_DISPLAY_NAMES,
                         ROLE_COLORS=ROLE_COLORS,
                         ROLE_ICONS=ROLE_ICONS)
        
    except Exception as e:
        flash(f'Error loading admin dashboard: {str(e)}', 'error')
        return render_template('admin/dashboard.html', 
                         metrics={},
                         user_role='ADMIN')


@admin_bp.route('/users')
@login_required
@role_required('ADMIN')
@log_access('manage_users')
def manage_users():
    """
    User management interface.
    
    Features:
    - View all users
    - Create new users
    - Edit user roles
    - Delete users
    """
    try:
        users = auth_service.get_all_users()
        return render_template('admin/users.html', 
                         users=users,
                         user_role='ADMIN')
        
    except Exception as e:
        flash(f'Error loading users: {str(e)}', 'error')
        return render_template('admin/users.html', 
                         users=[],
                         user_role='ADMIN')


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@role_required('ADMIN')
@log_access('create_user')
def create_user():
    """
    Create new user interface.
    
    Features:
    - User creation form
    - Role assignment
    - Password generation
    """
    if request.method == 'POST':
        try:
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip()
            role = request.form.get('role', '').strip().upper()
            
            if not all([email, password, role]):
                flash('All fields are required', 'error')
                return render_template('admin/create_user.html', user_role='ADMIN')
            
            # Validate role
            from ..constants.roles import UserRole
            if role not in [r.value for r in UserRole]:
                flash('Invalid role selected', 'error')
                return render_template('admin/create_user.html', user_role='ADMIN')
            
            # Create user
            user_id = auth_service.create_user(email, password, role)
            
            if user_id:
                flash(f'User {email} created successfully', 'success')
                return redirect(url_for('admin.manage_users'))
            else:
                flash('Error creating user', 'error')
                
        except Exception as e:
            flash(f'Error creating user: {str(e)}', 'error')
    
    return render_template('admin/create_user.html', 
                     user_role='ADMIN',
                     available_roles=[r.value for r in UserRole])


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@role_required('ADMIN')
@log_access('delete_user')
def delete_user(user_id):
    """
    Delete user interface.
    
    Features:
    - User deletion with confirmation
    - Activity logging
    """
    try:
        # Prevent self-deletion
        current_user_id = current_user.id
        if user_id == current_user_id:
            flash('You cannot delete your own account', 'error')
            return redirect(url_for('admin.manage_users'))
        
        success = auth_service.delete_user(user_id)
        
        if success:
            flash('User deleted successfully', 'success')
        else:
            flash('Error deleting user', 'error')
            
    except Exception as e:
        flash(f'Error deleting user: {str(e)}', 'error')
    
    return redirect(url_for('admin.manage_users'))


@admin_bp.route('/activity')
@login_required
@role_required('ADMIN')
@log_access('view_activity')
def activity_logs():
    """
    System activity logs interface.
    
    Features:
    - View all system activities
    - Filter by user/action
    - Export logs
    """
    try:
        # Get recent activity
        metrics = dashboard_service.get_admin_metrics()
        recent_activity = metrics.get('recent_activity', [])
        
        return render_template('admin/activity.html', 
                         activities=recent_activity,
                         user_role='ADMIN')
        
    except Exception as e:
        flash(f'Error loading activity logs: {str(e)}', 'error')
        return render_template('admin/activity.html', 
                         activities=[],
                         user_role='ADMIN')


@admin_bp.route('/system')
@login_required
@role_required('ADMIN')
@log_access('view_system')
def system_overview():
    """
    System overview and health monitoring.
    
    Features:
    - System health metrics
    - Database status
    - ML model status
    - Performance metrics
    """
    try:
        metrics = dashboard_service.get_admin_metrics()
        system_health = metrics.get('system_health', {})
        
        return render_template('admin/system.html', 
                         system_health=system_health,
                         metrics=metrics,
                         user_role='ADMIN')
        
    except Exception as e:
        flash(f'Error loading system overview: {str(e)}', 'error')
        return render_template('admin/system.html', 
                         system_health={},
                         metrics={},
                         user_role='ADMIN')


@admin_bp.route('/api/metrics')
@login_required
@role_required('ADMIN')
def api_metrics():
    """
    API endpoint for real-time metrics.
    
    Returns:
        JSON with current system metrics
    """
    try:
        metrics = dashboard_service.get_admin_metrics()
        return jsonify({
            'success': True,
            'metrics': metrics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
