"""
Maintenance Admin Blueprint

Handles maintenance admin-specific routes and functionality.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models import JobRequest, Assignment, Material, User
from ..extensions import db

maintenance_admin_bp = Blueprint('maintenance_admin', __name__, url_prefix='/maintenance_admin')

@maintenance_admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Maintenance admin dashboard - job management and assignments."""
    
    # Verify role
    if not current_user.is_maintenance_admin():
        flash('Access denied. Maintenance admin access required.', 'error')
        return redirect(url_for('auth.select_login'))
    
    # Get job statistics
    total_jobs = JobRequest.query.count()
    pending_jobs = JobRequest.query.filter_by(status='Pending').count()
    in_progress_jobs = JobRequest.query.filter_by(status='In Progress').count()
    completed_jobs = JobRequest.query.filter_by(status='Completed').count()
    
    # Get recent jobs
    recent_jobs = JobRequest.query.order_by(JobRequest.date_created.desc()).limit(10).all()
    
    # Get assignments
    active_assignments = Assignment.query.filter_by(status='Assigned').count()
    
    # Get jobs by priority
    high_priority_jobs = JobRequest.query.filter_by(priority='High', status='Pending').count()
    medium_priority_jobs = JobRequest.query.filter_by(priority='Medium', status='Pending').count()
    low_priority_jobs = JobRequest.query.filter_by(priority='Low', status='Pending').count()
    
    return render_template('maintenance_admin/dashboard.html',
                         total_jobs=total_jobs,
                         pending_jobs=pending_jobs,
                         in_progress_jobs=in_progress_jobs,
                         completed_jobs=completed_jobs,
                         recent_jobs=recent_jobs,
                         active_assignments=active_assignments,
                         high_priority_jobs=high_priority_jobs,
                         medium_priority_jobs=medium_priority_jobs,
                         low_priority_jobs=low_priority_jobs)

@maintenance_admin_bp.route('/jobs')
@login_required
def jobs():
    """View and manage all jobs."""
    
    # Verify role
    if not current_user.is_maintenance_admin():
        flash('Access denied. Maintenance admin access required.', 'error')
        return redirect(url_for('auth.select_login'))
    
    # Get filter parameters
    status_filter = request.args.get('status', '')
    priority_filter = request.args.get('priority', '')
    page = request.args.get('page', 1, type=int)
    
    query = JobRequest.query
    
    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if priority_filter:
        query = query.filter_by(priority=priority_filter)
    
    # Paginate results
    jobs = query.order_by(JobRequest.date_created.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('maintenance_admin/jobs.html', 
                         jobs=jobs, 
                         status_filter=status_filter,
                         priority_filter=priority_filter)

@maintenance_admin_bp.route('/job/<int:job_id>/assign', methods=['GET', 'POST'])
@login_required
def assign_job(job_id):
    """Assign job to technician."""
    
    # Verify role
    if not current_user.is_maintenance_admin():
        flash('Access denied. Maintenance admin access required.', 'error')
        return redirect(url_for('auth.select_login'))
    
    job = JobRequest.query.get_or_404(job_id)
    
    if request.method == 'POST':
        worker_name = request.form.get('worker_name', '').strip()
        
        if not worker_name:
            flash('Worker name is required', 'error')
            return render_template('maintenance_admin/assign_job.html', job=job)
        
        # Create assignment
        assignment = Assignment(
            job_id=job_id,
            worker_name=worker_name,
            status='Assigned'
        )
        
        # Update job status
        job.status = 'In Progress'
        
        db.session.add(assignment)
        db.session.commit()
        
        flash(f'Job assigned to {worker_name}', 'success')
        return redirect(url_for('maintenance_admin.jobs'))
    
    return render_template('maintenance_admin/assign_job.html', job=job)

@maintenance_admin_bp.route('/job/<int:job_id>/status', methods=['POST'])
@login_required
def update_job_status(job_id):
    """Update job status."""
    
    # Verify role
    if not current_user.is_maintenance_admin():
        flash('Access denied. Maintenance admin access required.', 'error')
        return redirect(url_for('auth.select_login'))
    
    job = JobRequest.query.get_or_404(job_id)
    new_status = request.form.get('status', '')
    
    if new_status not in ['Pending', 'In Progress', 'Completed']:
        flash('Invalid status', 'error')
        return redirect(url_for('maintenance_admin.jobs'))
    
    job.status = new_status
    db.session.commit()
    
    flash(f'Job status updated to {new_status}', 'success')
    return redirect(url_for('maintenance_admin.jobs'))

@maintenance_admin_bp.route('/assignments')
@login_required
def assignments():
    """View all assignments."""
    
    # Verify role
    if not current_user.is_maintenance_admin():
        flash('Access denied. Maintenance admin access required.', 'error')
        return redirect(url_for('auth.select_login'))
    
    assignments = Assignment.query.order_by(Assignment.start_time.desc()).all()
    return render_template('maintenance_admin/assignments.html', assignments=assignments)
