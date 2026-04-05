"""
Job Status API Routes for MSU Maintenance System

RESTful endpoints for job status management.
"""

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from typing import Dict, Any

from ..services.job_status_service import job_status_service
from ..constants.job_status import JobStatusTransition, STATUS_DISPLAY_NAMES
from ..decorators.auth_decorators import supervisor_required

job_status_bp = Blueprint('job_status', __name__)


@job_status_bp.route('/jobs/<int:job_id>/status', methods=['PUT'])
@login_required
@supervisor_required  # Only supervisors and admins can update status
def update_job_status(job_id: int):
    """
    Update job status endpoint.
    
    Request Body:
        {
            "status": "IN_PROGRESS"
        }
    
    Response:
        {
            "success": true,
            "message": "Job status updated successfully",
            "job_id": 1,
            "old_status": "PENDING",
            "new_status": "IN_PROGRESS",
            "updated_at": "2024-03-29T13:30:00"
        }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Request body is required'
            }), 400
        
        new_status = data.get('status')
        if not new_status:
            return jsonify({
                'success': False,
                'message': 'Status field is required'
            }), 400
        
        # Get user ID from current_user
        user_id = int(current_user.id)
        if not user_id:
            return jsonify({
                'success': False,
                'message': 'User not authenticated'
            }), 401
        
        # Check if user has override permissions
        user_role = getattr(current_user, 'role', '').lower()
        is_override = user_role in ['admin', 'supervisor']
        
        # Validate the update
        can_update, reason = job_status_service.can_user_update_job_status(
            user_id, job_id, new_status
        )
        
        if not can_update:
            return jsonify({
                'success': False,
                'message': reason
            }), 403
        
        # Perform the update
        result = job_status_service.update_job_status(
            job_id, new_status, user_id, is_override
        )
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': result['message'],
                'job_id': result['job_id'],
                'old_status': result['old_status'],
                'new_status': result['new_status'],
                'updated_at': result['updated_at'].isoformat() if hasattr(result['updated_at'], 'isoformat') else str(result['updated_at'])
            }), 200
        else:
            return jsonify({
                'success': False,
                'message': result['message']
            }), 400
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@job_status_bp.route('/jobs/<int:job_id>/status', methods=['GET'])
@login_required
def get_job_status(job_id: int):
    """
    Get current job status and history.
    
    Response:
        {
            "success": true,
            "job_id": 1,
            "current_status": "IN_PROGRESS",
            "status_history": [
                {
                    "old_status": null,
                    "new_status": "PENDING",
                    "updated_by": null,
                    "timestamp": "2024-03-29T10:00:00"
                },
                {
                    "old_status": "PENDING",
                    "new_status": "IN_PROGRESS",
                    "updated_by": 123,
                    "timestamp": "2024-03-29T13:30:00"
                }
            ]
        }
    """
    try:
        # Get job details
        job = job_status_service._get_job_by_id(job_id)
        if not job:
            return jsonify({
                'success': False,
                'message': 'Job not found'
            }), 404
        
        # Get status history
        history = job_status_service.get_job_status_history(job_id)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'current_status': job['status'],
            'status_history': history,
            'job_details': {
                'department': job['department'],
                'description': job['description'],
                'category': job['category'],
                'priority': job['priority'],
                'date_created': job['date_created'].isoformat() if hasattr(job['date_created'], 'isoformat') else str(job['date_created'])
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@job_status_bp.route('/jobs/status/summary', methods=['GET'])
@login_required
def get_status_summary():
    """
    Get summary of jobs by status.
    
    Response:
        {
            "success": true,
            "summary": {
                "PENDING": 15,
                "IN_PROGRESS": 8,
                "COMPLETED": 42
            },
            "total_jobs": 65
        }
    """
    try:
        summary = job_status_service.get_status_summary()
        total_jobs = sum(summary.values())
        
        return jsonify({
            'success': True,
            'summary': summary,
            'total_jobs': total_jobs
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@job_status_bp.route('/jobs/status/<string:status>', methods=['GET'])
@login_required
def get_jobs_by_status(status: str):
    """
    Get all jobs with a specific status.
    
    Response:
        {
            "success": true,
            "status": "IN_PROGRESS",
            "jobs": [...]
        }
    """
    try:
        # Validate status
        if status.upper() not in JobStatusTransition.get_all_statuses():
            return jsonify({
                'success': False,
                'message': f'Invalid status: {status}. Valid statuses: {JobStatusTransition.get_all_statuses()}'
            }), 400
        
        jobs = job_status_service.get_jobs_by_status(status)
        
        # Format dates for JSON response
        for job in jobs:
            if 'date_created' in job and hasattr(job['date_created'], 'isoformat'):
                job['date_created'] = job['date_created'].isoformat()
            if 'updated_at' in job and hasattr(job['updated_at'], 'isoformat'):
                job['updated_at'] = job['updated_at'].isoformat()
        
        return jsonify({
            'success': True,
            'status': status.upper(),
            'jobs': jobs,
            'count': len(jobs)
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500


@job_status_bp.route('/jobs/<int:job_id>/valid-transitions', methods=['GET'])
@login_required
def get_valid_transitions(job_id: int):
    """
    Get valid status transitions for a job.
    
    Response:
        {
            "success": true,
            "job_id": 1,
            "current_status": "PENDING",
            "valid_transitions": ["IN_PROGRESS"],
            "override_transitions": ["IN_PROGRESS", "COMPLETED"]
        }
    """
    try:
        # Get job details
        job = job_status_service._get_job_by_id(job_id)
        if not job:
            return jsonify({
                'success': False,
                'message': 'Job not found'
            }), 404
        
        current_status = job['status']
        
        # Get user role for override permissions
        user_role = getattr(current_user, 'role', '').lower()
        is_override = user_role in ['admin', 'supervisor']
        
        # Get valid transitions
        valid_transitions = JobStatusTransition.get_valid_next_statuses(current_status, False)
        override_transitions = JobStatusTransition.get_valid_next_statuses(current_status, True)
        
        return jsonify({
            'success': True,
            'job_id': job_id,
            'current_status': current_status,
            'valid_transitions': valid_transitions,
            'override_transitions': override_transitions if is_override else [],
            'can_override': is_override
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
