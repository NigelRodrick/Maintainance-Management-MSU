from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from ..services.job_service import job_service
from ..services.job_status_service import job_status_service
from ..services.assignment_service import assignment_service
from ..services.material_service import material_service
from ..constants.job_status import JobStatusTransition, STATUS_DISPLAY_NAMES, STATUS_COLORS, STATUS_ICONS

main_bp = Blueprint('main', __name__)

@main_bp.route("/", methods=['GET', 'POST'])
@login_required
def index():
    if request.method == "POST":
        department = request.form.get("department", "").strip()
        description = request.form.get("description", "").strip()
        
        if not department or not description:
            flash('Department and description are required', 'error')
            return render_template("index.html")
        
        try:
            # Get current user ID
            user_id = current_user.id
            
            # Create job using the database directly for now
            from app.extensions import db
            from app.models import JobRequest
            from ..classification_service import classify_request
            
            # Classify the request
            category, priority = classify_request(description)
            
            # Create new job
            new_job = JobRequest(
                department=department,
                description=description,
                category=category,
                priority=priority,
                status='PENDING',
                submitted_by=user_id
            )
            
            db.session.add(new_job)
            db.session.commit()
            
            flash(f'Request submitted successfully: {category} - {priority} priority', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            flash(f'Error submitting request: {str(e)}', 'error')
    
    return render_template("index.html")

@main_bp.route("/dashboard")
@login_required
def dashboard():
    try:
        # Get user role from current_user
        user_role = getattr(current_user, 'role', 'USER')
        user_email = getattr(current_user, 'email', '')
        user_id = getattr(current_user, 'id', None)
        
        # Use database directly
        from app.extensions import db
        from app.models import JobRequest, User
        
        if user_role in ['admin', 'ADMIN', 'SUPERVISOR']:
            # Admin/Supervisor: See all jobs and full statistics
            jobs = JobRequest.query.filter_by(is_deleted=False).order_by(JobRequest.date_created.desc()).all()
            
            # Calculate basic stats
            total_jobs = len(jobs)
            completed_jobs = len([j for j in jobs if j.status == 'Completed'])
            pending_jobs = len([j for j in jobs if j.status == 'Pending'])
            
            stats = {
                'total_jobs': total_jobs,
                'completed_jobs': completed_jobs,
                'pending_jobs': pending_jobs,
                'completion_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
            }
            template_name = "dashboard.html"
        else:
            # Regular staff: See only their submitted jobs and personal statistics
            jobs = JobRequest.query.filter_by(submitted_by=user_id, is_deleted=False).order_by(JobRequest.date_created.desc()).all()
            
            # Calculate basic stats
            total_jobs = len(jobs)
            completed_jobs = len([j for j in jobs if j.status == 'Completed'])
            pending_jobs = len([j for j in jobs if j.status == 'Pending'])
            
            stats = {
                'total_jobs': total_jobs,
                'completed_jobs': completed_jobs,
                'pending_jobs': pending_jobs,
                'completion_rate': (completed_jobs / total_jobs * 100) if total_jobs > 0 else 0
            }
            template_name = "dashboard.html"
        
        return render_template(template_name, jobs=jobs, stats=stats, user_role=user_role, 
                        STATUS_COLORS=STATUS_COLORS, STATUS_ICONS=STATUS_ICONS)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template("dashboard.html", jobs=[], stats=None, user_role='staff')

@main_bp.route("/assign/<int:job_id>", methods=["GET", "POST"])
@login_required
def assign(job_id):
    job = job_service.get_job_by_id(job_id)
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == "POST":
        worker_name = request.form.get("worker", "").strip()
        
        if not worker_name:
            flash('Worker name is required', 'error')
            return render_template("assign.html", job=job)
        
        try:
            assignment_service.assign_worker(job_id, worker_name)
            flash(f'Job assigned to {worker_name}', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            flash(f'Error assigning job: {str(e)}', 'error')
    
    # Get worker recommendation
    recommendation = assignment_service.get_worker_recommendation(job.category)
    return render_template("assign.html", job=job, recommendation=recommendation)

@main_bp.route("/complete/<int:job_id>")
@login_required
def complete(job_id):
    try:
        assignment_service.complete_job(job_id)
        flash('Job marked as completed', 'success')
    except Exception as e:
        flash(f'Error completing job: {str(e)}', 'error')
    
    return redirect(url_for('main.dashboard'))

@main_bp.route("/update-status/<int:job_id>", methods=["POST"])
@login_required
def update_job_status(job_id):
    """Update job status with validation and logging."""
    try:
        new_status = request.form.get("status", "").strip().upper()
        user_id = int(current_user.id)
        user_role = getattr(current_user, 'role', '').lower()
        
        if not new_status:
            flash('Status is required', 'error')
            return redirect(url_for('main.dashboard'))
        
        if not user_id:
            flash('User not authenticated', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Check if user has permission
        if user_role not in ['admin', 'supervisor']:
            flash('Only supervisors and administrators can update job status', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Validate the update
        can_update, reason = job_status_service.can_user_update_job_status(
            user_id, job_id, new_status
        )
        
        if not can_update:
            flash(f'Cannot update status: {reason}', 'error')
            return redirect(url_for('main.dashboard'))
        
        # Perform the update
        is_override = user_role in ['admin', 'supervisor']
        result = job_status_service.update_job_status(
            job_id, new_status, user_id, is_override
        )
        
        if result['success']:
            flash(f'Job status updated to {STATUS_DISPLAY_NAMES.get(new_status, new_status)}', 'success')
        else:
            flash(f'Error updating status: {result["message"]}', 'error')
            
    except Exception as e:
        flash(f'Error updating job status: {str(e)}', 'error')
    
    return redirect(url_for('main.dashboard'))

@main_bp.route("/materials/<int:job_id>", methods=["GET", "POST"])
@login_required
def materials(job_id):
    job = job_service.get_job_by_id(job_id)
    if not job:
        flash('Job not found', 'error')
        return redirect(url_for('main.dashboard'))
    
    if request.method == "POST":
        item = request.form.get("item", "").strip()
        qty_required = request.form.get("qty_required", "").strip()
        qty_used = request.form.get("qty_used", "").strip()
        
        if not item or not qty_required or not qty_used:
            flash('All material fields are required', 'error')
            return render_template("materials.html", job=job)
        
        try:
            qty_req_int = int(qty_required)
            qty_used_int = int(qty_used)
            material_service.add_material(job_id, item, qty_req_int, qty_used_int)
            flash('Material added successfully', 'success')
            return redirect(url_for('main.dashboard'))
        except ValueError:
            flash('Quantities must be numbers', 'error')
        except Exception as e:
            flash(f'Error adding material: {str(e)}', 'error')
    
    return render_template("materials.html", job=job)
