"""
Supervisor Dashboard Routes for MSU Maintenance System

Supervisor interface with job management and ML predictions.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required

from ..decorators.auth_decorators import role_required, log_access
from ..services.dashboard_service import dashboard_service
from ..services.job_status_service import job_status_service
from ..services.assignment_service import assignment_service
from ..constants.roles import ROLE_DISPLAY_NAMES, ROLE_COLORS, ROLE_ICONS

supervisor_bp = Blueprint('supervisor', __name__, url_prefix='/supervisor')


@supervisor_bp.route('/dashboard')
@login_required
@role_required('SUPERVISOR')
def supervisor_dashboard():
    """
    Supervisor dashboard with job queue management.
    
    Features:
    - View all job cards
    - Assign technicians
    - Update job status
    - View ML predictions
    - Generate reports
    """
    try:
        # Get jobs grouped by status
        jobs_by_status = dashboard_service.get_supervisor_jobs()
        queue_metrics = dashboard_service.get_job_queue_metrics()
        
        return render_template('supervisor/dashboard.html', 
                         jobs_by_status=jobs_by_status,
                         queue_metrics=queue_metrics,
                         user_role='SUPERVISOR',
                         ROLE_DISPLAY_NAMES=ROLE_DISPLAY_NAMES,
                         ROLE_COLORS=ROLE_COLORS,
                         ROLE_ICONS=ROLE_ICONS)
        
    except Exception as e:
        flash(f'Error loading supervisor dashboard: {str(e)}', 'error')
        return render_template('supervisor/dashboard.html', 
                         jobs_by_status={},
                         queue_metrics={},
                         user_role='SUPERVISOR')


@supervisor_bp.route('/jobs/<int:job_id>/assign', methods=['GET', 'POST'])
@login_required
@role_required('SUPERVISOR')
def assign_technician(job_id):
    """
    Assign technician to job interface.
    
    Features:
    - Select technician from list
    - View job details
    - ML recommendations
    """
    try:
        from ..services.job_service import job_service
        
        job = job_service.get_job_by_id(job_id)
        if not job:
            flash('Job not found', 'error')
            return redirect(url_for('supervisor.supervisor_dashboard'))
        
        if request.method == 'POST':
            worker_name = request.form.get('worker_name', '').strip()
            
            if not worker_name:
                flash('Worker name is required', 'error')
                return render_template('supervisor/assign_technician.html', 
                                 job=job, user_role='SUPERVISOR')
            
            # Assign worker
            assignment_service.assign_worker(job_id, worker_name)
            flash(f'Job assigned to {worker_name}', 'success')
            return redirect(url_for('supervisor.supervisor_dashboard'))
        
        # Get worker recommendation
        recommendation = assignment_service.get_worker_recommendation(job['category'])
        
        return render_template('supervisor/assign_technician.html', 
                         job=job, 
                         recommendation=recommendation,
                         user_role='SUPERVISOR')
        
    except Exception as e:
        flash(f'Error assigning technician: {str(e)}', 'error')
        return redirect(url_for('supervisor.supervisor_dashboard'))


@supervisor_bp.route('/jobs/<int:job_id>/status', methods=['POST'])
@login_required
@role_required('SUPERVISOR')
def update_job_status(job_id):
    """
    Update job status interface.
    
    Features:
    - Status dropdown with validation
    - ML predictions display
    - Status history
    """
    try:
        new_status = request.form.get('status', '').strip().upper()
        user_id = current_user.id
        
        if not new_status:
            flash('Status is required', 'error')
            return redirect(url_for('supervisor.supervisor_dashboard'))
        
        # Update status
        result = job_status_service.update_job_status(
            job_id, new_status, user_id, is_override=True
        )
        
        if result['success']:
            flash(f'Job status updated to {new_status}', 'success')
        else:
            flash(f'Error updating status: {result["message"]}', 'error')
            
    except Exception as e:
        flash(f'Error updating job status: {str(e)}', 'error')
    
    return redirect(url_for('supervisor.supervisor_dashboard'))


@supervisor_bp.route('/jobs/<int:job_id>/analysis')
@login_required
@role_required('SUPERVISOR')
def job_analysis(job_id):
    """
    View job analysis for a job.
    
    Features:
    - Category classification
    - Priority assessment
    - Estimated completion time
    - Resource requirements
    """
    try:
        # Get job analysis
        analysis = dashboard_service.get_job_analysis(job_id)
        
        if not analysis:
            flash('Unable to get job analysis', 'error')
            return redirect(url_for('supervisor.supervisor_dashboard'))
        
        # Get job details
        from ..services.job_service import job_service
        job = job_service.get_job_by_id(job_id)
        
        return render_template('supervisor/analysis.html', 
                         job=job,
                         analysis=analysis,
                         user_role='SUPERVISOR')
        
    except Exception as e:
        flash(f'Error loading analysis: {str(e)}', 'error')
        return redirect(url_for('supervisor.supervisor_dashboard'))


@supervisor_bp.route('/reports')
@login_required
@role_required('SUPERVISOR')
def generate_reports():
    """
    Generate and export reports interface.
    
    Features:
    - Excel report generation
    - Date range filtering
    - Status filtering
    - Department filtering
    """
    try:
        from ..services.reports_service import reports_service
        
        if request.method == 'POST':
            # Get report parameters
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            status_filter = request.form.get('status', '')
            department_filter = request.form.get('department', '')
            
            # Generate report
            report_file = reports_service.generate_supervisor_report(
                start_date, end_date, status_filter, department_filter
            )
            
            if report_file:
                flash('Report generated successfully', 'success')
                return redirect(url_for('supervisor.download_report', 
                                     filename=report_file))
            else:
                flash('Error generating report', 'error')
        
        return render_template('supervisor/reports.html', 
                         user_role='SUPERVISOR')
        
    except Exception as e:
        flash(f'Error generating reports: {str(e)}', 'error')
        return render_template('supervisor/reports.html', 
                         user_role='SUPERVISOR')


@supervisor_bp.route('/download/<filename>')
@login_required
@role_required('SUPERVISOR')
def download_report(filename):
    """
    Download generated report file.
    """
    try:
        from flask import send_from_directory
        import os
        
        reports_dir = os.path.join(os.getcwd(), 'reports')
        return send_from_directory(reports_dir, filename, as_attachment=True)
        
    except Exception as e:
        flash(f'Error downloading report: {str(e)}', 'error')
        return redirect(url_for('supervisor.generate_reports'))


@supervisor_bp.route('/api/queue-metrics')
@login_required
@role_required('SUPERVISOR')
def api_queue_metrics():
    """
    API endpoint for real-time queue metrics.
    
    Returns:
        JSON with current job queue metrics
    """
    try:
        metrics = dashboard_service.get_job_queue_metrics()
        return jsonify({
            'success': True,
            'metrics': metrics
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@supervisor_bp.route('/api/jobs/<int:job_id>/analysis')
@login_required
@role_required('SUPERVISOR')
def api_job_analysis(job_id):
    """
    API endpoint for job analysis.
    
    Returns:
        JSON with job analysis
    """
    try:
        analysis = dashboard_service.get_job_analysis(job_id)
        return jsonify({
            'success': True,
            'analysis': analysis
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
