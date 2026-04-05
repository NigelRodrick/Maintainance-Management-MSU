"""
Jobs API v1 Endpoints
RESTful endpoints for job management.
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1 import api_v1_bp
from app.services.job_service import JobService
from app.services.auth_service import AuthService
from app.domain.job import JobRequestCreate, JobRequestUpdate, JobStatusTransition, JobSearchRequest
from app.repositories.job_repository import JobRepository
from app.repositories.user_repository import UserRepository


@api_v1_bp.route('/jobs', methods=['GET'])
@jwt_required()
def get_jobs():
    """Get all jobs with optional filters."""
    try:
        # Parse query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 25))
        status = request.args.get('status')
        department = request.args.get('department')
        priority = request.args.get('priority')
        keyword = request.args.get('keyword')
        
        # Create search request
        search_data = {
            'page': page,
            'per_page': per_page,
            'status': status,
            'department': department,
            'priority': priority,
            'keyword': keyword
        }
        
        search_request = JobSearchRequest(**search_data)
        
        # Initialize services
        job_repo = JobRepository()
        job_service = JobService(job_repo, UserRepository())
        
        # Get jobs
        result = job_service.search_jobs(search_request)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/jobs/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job(job_id):
    """Get job by ID."""
    try:
        job_repo = JobRepository()
        job_service = JobService(job_repo, UserRepository())
        
        job = job_service.get_job_by_id(job_id)
        if job:
            return jsonify({
                'success': True,
                'data': job.dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/jobs', methods=['POST'])
@jwt_required()
def create_job():
    """Create a new job."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Get current user ID
        current_user_id = get_jwt_identity()
        
        # Create job request
        job_data = JobRequestCreate(**data)
        
        # Initialize services
        job_repo = JobRepository()
        job_service = JobService(job_repo, UserRepository())
        
        # Create job
        job = job_service.create_job(job_data, current_user_id)
        
        return jsonify({
            'success': True,
            'data': job.dict()
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/jobs/<int:job_id>', methods=['PUT'])
@jwt_required()
def update_job(job_id):
    """Update job details."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Create update request
        update_data = JobRequestUpdate(**data)
        
        # Initialize services
        job_repo = JobRepository()
        job_service = JobService(job_repo, UserRepository())
        
        # Update job
        job = job_service.update_job(job_id, update_data)
        if job:
            return jsonify({
                'success': True,
                'data': job.dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/jobs/<int:job_id>/status', methods=['PUT'])
@jwt_required()
def update_job_status(job_id):
    """Update job status."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Get current user ID
        current_user_id = get_jwt_identity()
        
        # Create status transition
        status_data = {
            'to_status': data.get('status'),
            'changed_by': current_user_id,
            'notes': data.get('notes')
        }
        status_transition = JobStatusTransition(**status_data)
        
        # Initialize services
        job_repo = JobRepository()
        job_service = JobService(job_repo, UserRepository())
        
        # Update status
        job = job_service.update_job_status(job_id, status_transition)
        if job:
            return jsonify({
                'success': True,
                'data': job.dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
            
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/jobs/<int:job_id>', methods=['DELETE'])
@jwt_required()
def delete_job(job_id):
    """Soft delete a job."""
    try:
        # Initialize services
        job_repo = JobRepository()
        job_service = JobService(job_repo, UserRepository())
        
        # Delete job
        success = job_service.delete_job(job_id)
        if success:
            return jsonify({
                'success': True,
                'message': 'Job deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Job not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/jobs/stats', methods=['GET'])
@jwt_required()
def get_job_stats():
    """Get job statistics."""
    try:
        # Initialize services
        job_repo = JobRepository()
        job_service = JobService(job_repo, UserRepository())
        
        # Get statistics
        stats = job_service.get_job_statistics()
        
        return jsonify({
            'success': True,
            'data': stats.dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
