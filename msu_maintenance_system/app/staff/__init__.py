"""
Staff Blueprint

Handles staff-specific routes and functionality.
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models import JobRequest, User
from ..extensions import db
from ..classification_service import classify_request
import logging

logger = logging.getLogger(__name__)

staff_bp = Blueprint('staff', __name__, url_prefix='/staff')

@staff_bp.route('/dashboard')
@login_required
def dashboard():
    """Staff dashboard - view and submit maintenance requests."""
    
    # Verify role
    if not current_user.is_staff():
        flash('Access denied. Staff access required.', 'error')
        return redirect(url_for('auth.select_login'))
    
    # Get staff's job requests
    staff_jobs = JobRequest.query.filter_by(submitted_by=current_user.id).order_by(JobRequest.date_created.desc()).all()
    
    # Get statistics
    total_jobs = len(staff_jobs)
    pending_jobs = len([job for job in staff_jobs if job.status == 'Pending'])
    in_progress_jobs = len([job for job in staff_jobs if job.status == 'In Progress'])
    completed_jobs = len([job for job in staff_jobs if job.status == 'Completed'])
    
    return render_template('staff/dashboard.html',
                         jobs=staff_jobs,
                         total_jobs=total_jobs,
                         pending_jobs=pending_jobs,
                         in_progress_jobs=in_progress_jobs,
                         completed_jobs=completed_jobs)

@staff_bp.route('/submit', methods=['GET', 'POST'])
@login_required
def submit_request():
    """Submit new maintenance request."""
    
    # Verify role
    if not current_user.is_staff():
        flash('Access denied. Staff access required.', 'error')
        return redirect(url_for('auth.select_login'))
    
    if request.method == 'POST':
        department = request.form.get('department', '').strip()
        description = request.form.get('description', '').strip()
        
        if not department or not description:
            flash('Department and description are required', 'error')
            return render_template('staff/submit_request.html')
        
        # Get classification using rule-based logic
        try:
            category, priority = classify_request(description)
            logger.info(f"Classification complete for request: {description[:50]}...")
        except Exception as e:
            logger.error(f"Classification service error: {str(e)}")
            category = 'General'
            priority = 'Medium'
            flash('Using default category and priority values', 'info')
        
        # Create job request
        job = JobRequest(
            department=department,
            description=description,
            category=category,
            priority=priority,
            submitted_by=current_user.id
        )
        
        db.session.add(job)
        db.session.commit()
        
        flash(f'Maintenance request submitted successfully! Category: {category}, Priority: {priority}', 'success')
        return redirect(url_for('staff.dashboard'))
    
    return render_template('staff/submit_request.html')

@staff_bp.route('/job/<int:job_id>')
@login_required
def view_job(job_id):
    """View job details."""
    
    # Verify role
    if not current_user.is_staff():
        flash('Access denied. Staff access required.', 'error')
        return redirect(url_for('auth.select_login'))
    
    job = JobRequest.query.get_or_404(job_id)
    
    # Ensure user can only view their own jobs
    if job.submitted_by != current_user.id:
        flash('Access denied. You can only view your own job requests.', 'error')
        return redirect(url_for('staff.dashboard'))
    
    return render_template('staff/view_job.html', job=job)
