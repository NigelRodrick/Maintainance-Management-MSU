"""
User Dashboard Routes for MSU Maintenance System

User interface for job submission and tracking.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from ..decorators.auth_decorators import role_required, log_access
from ..services.dashboard_service import dashboard_service
from ..services.job_service import job_service
from ..constants.roles import ROLE_DISPLAY_NAMES, ROLE_COLORS, ROLE_ICONS

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/dashboard')
@login_required
@role_required('USER')
def user_dashboard():
    """
    User dashboard with job submission and tracking.
    
    Features:
    - Submit job card
    - View own job requests
    - Track job status
    - Job history
    """
    try:
        user_id = current_user.id
        
        # Get user's jobs
        user_jobs = dashboard_service.get_user_jobs(user_id)
        activity_summary = dashboard_service.get_user_activity_summary(user_id)
        
        return render_template('user/dashboard.html', 
                         jobs=user_jobs,
                         activity_summary=activity_summary,
                         user_role='USER',
                         ROLE_DISPLAY_NAMES=ROLE_DISPLAY_NAMES,
                         ROLE_COLORS=ROLE_COLORS,
                         ROLE_ICONS=ROLE_ICONS)
        
    except Exception as e:
        flash(f'Error loading user dashboard: {str(e)}', 'error')
        return render_template('user/dashboard.html', 
                         jobs=[],
                         activity_summary={},
                         user_role='USER')


@user_bp.route('/submit', methods=['GET', 'POST'])
@login_required
@role_required('USER')
def submit_job():
    """
    Submit new maintenance request interface.
    
    Features:
    - Job submission form
    - Department selection
    - Description field
    - Category prediction
    - Priority prediction
    """
    if request.method == 'POST':
        try:
            department = request.form.get('department', '').strip()
            description = request.form.get('description', '').strip()
            
            if not all([department, description]):
                flash('Department and description are required', 'error')
                return render_template('user/submit_job.html', user_role='USER')
            
            # Submit job (will use ML predictions internally)
            job_id, category, priority = job_service.create_job(department, description)
            
            flash(f'Job submitted successfully! Category: {category}, Priority: {priority}', 'success')
            return redirect(url_for('user.user_dashboard'))
            
        except Exception as e:
            flash(f'Error submitting job: {str(e)}', 'error')
    
    return render_template('user/submit_job.html', user_role='USER')


@user_bp.route('/jobs/<int:job_id>')
@login_required
@role_required('USER')
def view_job(job_id):
    """
    View job details interface.
    
    Features:
    - Job details
    - Current status
    - Status history
    - Progress tracking
    """
    try:
        # Get job details
        job = job_service.get_job_by_id(job_id)
        if not job:
            flash('Job not found', 'error')
            return redirect(url_for('user.user_dashboard'))
        
        # Get status history
        from ..services.job_status_service import job_status_service
        status_history = job_status_service.get_job_status_history(job_id)
        
        return render_template('user/view_job.html', 
                         job=job,
                         status_history=status_history,
                         user_role='USER')
        
    except Exception as e:
        flash(f'Error loading job details: {str(e)}', 'error')
        return redirect(url_for('user.user_dashboard'))


@user_bp.route('/jobs/<int:job_id>/status')
@login_required
@role_required('USER')
def job_status(job_id):
    """
    View job status and progress.
    
    Features:
    - Current status display
    - Status timeline
    - Progress indicators
    - Estimated completion
    """
    try:
        # Get job details
        job = job_service.get_job_by_id(job_id)
        if not job:
            flash('Job not found', 'error')
            return redirect(url_for('user.user_dashboard'))
        
        # Get status history
        from ..services.job_status_service import job_status_service
        status_history = job_status_service.get_job_status_history(job_id)
        
        return render_template('user/job_status.html', 
                         job=job,
                         status_history=status_history,
                         user_role='USER')
        
    except Exception as e:
        flash(f'Error loading job status: {str(e)}', 'error')
        return redirect(url_for('user.user_dashboard'))


@user_bp.route('/history')
@login_required
@role_required('USER')
def job_history():
    """
    Job history interface.
    
    Features:
    - Complete job history
    - Filtering options
    - Status filtering
    - Date range filtering
    """
    try:
        user_id = current_user.id
        
        # Get user's jobs
        user_jobs = dashboard_service.get_user_jobs(user_id)
        
        # Apply filters if provided
        status_filter = request.args.get('status', '').upper()
        if status_filter:
            user_jobs = [job for job in user_jobs if job.get('status') == status_filter]
        
        return render_template('user/job_history.html', 
                         jobs=user_jobs,
                         status_filter=status_filter,
                         user_role='USER')
        
    except Exception as e:
        flash(f'Error loading job history: {str(e)}', 'error')
        return render_template('user/job_history.html', 
                         jobs=[],
                         user_role='USER')


@user_bp.route('/profile')
@login_required
@role_required('USER')
def user_profile():
    """
    User profile interface.
    
    Features:
    - User information
    - Activity summary
    - Statistics
    - Preferences
    """
    try:
        user_id = current_user.id
        
        # Get user activity summary
        activity_summary = dashboard_service.get_user_activity_summary(user_id)
        
        return render_template('user/profile.html', 
                         activity_summary=activity_summary,
                         user_role='USER')
        
    except Exception as e:
        flash(f'Error loading profile: {str(e)}', 'error')
        return render_template('user/profile.html', 
                         activity_summary={},
                         user_role='USER')


@user_bp.route('/api/my-jobs')
@login_required
@role_required('USER')
def api_my_jobs():
    """
    API endpoint for user's jobs.
    
    Returns:
        JSON with user's job submissions
    """
    try:
        user_id = current_user.id
        
        user_jobs = dashboard_service.get_user_jobs(user_id)
        
        return jsonify({
            'success': True,
            'jobs': user_jobs,
            'count': len(user_jobs)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@user_bp.route('/api/activity-summary')
@login_required
@role_required('USER')
def api_activity_summary():
    """
    API endpoint for user activity summary.
    
    Returns:
        JSON with user activity metrics
    """
    try:
        user_id = current_user.id
        
        activity_summary = dashboard_service.get_user_activity_summary(user_id)
        
        return jsonify({
            'success': True,
            'activity_summary': activity_summary
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
