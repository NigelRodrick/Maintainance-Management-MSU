"""
Admin Blueprint

Handles admin-specific routes and functionality.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from ..models import User, JobRequest, Assignment, Material
from ..extensions import db

admin_bp = Blueprint('admin_legacy', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Admin dashboard - system overview and user management."""
    
    # Verify role
    if not current_user.is_admin():
        flash('Access denied. Admin access required.', 'error')
        return redirect(url_for('auth.select_login'))
    
    # Get system statistics
    total_users = User.query.count()
    total_jobs = JobRequest.query.count()
    pending_jobs = JobRequest.query.filter_by(status='Pending').count()
    in_progress_jobs = JobRequest.query.filter_by(status='In Progress').count()
    completed_jobs = JobRequest.query.filter_by(status='Completed').count()
    
    # Get recent jobs
    recent_jobs = JobRequest.query.order_by(JobRequest.date_created.desc()).limit(10).all()
    
    # Get users by role
    staff_users = User.query.filter_by(role='staff').count()
    admin_users = User.query.filter_by(role='admin').count()
    maintenance_admin_users = User.query.filter_by(role='maintenance_admin').count()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_jobs=total_jobs,
                         pending_jobs=pending_jobs,
                         in_progress_jobs=in_progress_jobs,
                         completed_jobs=completed_jobs,
                         recent_jobs=recent_jobs,
                         staff_users=staff_users,
                         admin_users=admin_users,
                         maintenance_admin_users=maintenance_admin_users)

@admin_bp.route('/users')
@login_required
def users():
    """Manage users."""
    
    # Verify role
    if not current_user.is_admin():
        flash('Access denied. Admin access required.', 'error')
        return redirect(url_for('auth.select_login'))
    
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
def create_user():
    """Create new user."""
    
    # Verify role
    if not current_user.is_admin():
        flash('Access denied. Admin access required.', 'error')
        return redirect(url_for('auth.select_login'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', '')
        
        if not email or not password or not role:
            flash('All fields are required', 'error')
            return render_template('admin/create_user.html')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            flash('User with this email already exists', 'error')
            return render_template('admin/create_user.html')
        
        # Create user
        user = User(email=email, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'User {email} created successfully with role: {role}', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/create_user.html')

@admin_bp.route('/users/<int:user_id>/toggle', methods=['POST'])
@login_required
def toggle_user(user_id):
    """Toggle user active status."""
    
    # Verify role
    if not current_user.is_admin():
        flash('Access denied. Admin access required.', 'error')
        return redirect(url_for('auth.select_login'))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deactivating self
    if user.id == current_user.id:
        flash('You cannot deactivate your own account', 'error')
        return redirect(url_for('admin.users'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User {user.email} has been {status}', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/jobs')
@login_required
def jobs():
    """View all jobs."""
    
    # Verify role
    if not current_user.is_admin():
        flash('Access denied. Admin access required.', 'error')
        return redirect(url_for('auth.select_login'))
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    
    query = JobRequest.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    # Paginate results
    jobs = query.order_by(JobRequest.date_created.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/jobs.html', jobs=jobs, status_filter=status_filter)
