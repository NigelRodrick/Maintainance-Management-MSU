"""
Assignments API v1 Endpoints
Assignment management endpoints.
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1 import api_v1_bp
from app.services.assignment_service import AssignmentService
from app.domain.assignment import AssignmentTransition
from app.repositories.assignment_repository import AssignmentRepository
from app.repositories.worker_repository import WorkerRepository
from app.repositories.job_repository import JobRepository


@api_v1_bp.route('/assignments', methods=['GET'])
@jwt_required()
def get_assignments():
    """Get all assignments with optional filters."""
    try:
        # Parse query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 25))
        status = request.args.get('status')
        worker_id = request.args.get('worker_id')
        
        # Initialize services
        assignment_repo = AssignmentRepository()
        assignment_service = AssignmentService(assignment_repo, WorkerRepository(), JobRepository())
        
        # Get assignments
        result = assignment_service.get_assignments_with_pagination(
            page, per_page, status, int(worker_id) if worker_id else None
        )
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/assignments/<int:assignment_id>', methods=['GET'])
@jwt_required()
def get_assignment(assignment_id):
    """Get assignment by ID."""
    try:
        assignment_repo = AssignmentRepository()
        assignment_service = AssignmentService(assignment_repo, WorkerRepository(), JobRepository())
        
        assignment = assignment_service.get_assignment_by_id(assignment_id)
        if assignment:
            return jsonify({
                'success': True,
                'data': assignment.dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Assignment not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/assignments', methods=['POST'])
@jwt_required()
def create_assignment():
    """Create a new assignment."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        job_id = data.get('job_id')
        worker_id = data.get('worker_id')
        
        if not job_id or not worker_id:
            return jsonify({
                'success': False,
                'error': 'job_id and worker_id are required'
            }), 400
        
        # Initialize services
        assignment_repo = AssignmentRepository()
        assignment_service = AssignmentService(assignment_repo, WorkerRepository(), JobRepository())
        
        # Create assignment
        assignment = assignment_service.create_assignment(job_id, worker_id)
        
        return jsonify({
            'success': True,
            'data': assignment.dict()
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


@api_v1_bp.route('/assignments/<int:assignment_id>/start', methods=['POST'])
@jwt_required()
def start_assignment(assignment_id):
    """Start an assignment."""
    try:
        assignment_repo = AssignmentRepository()
        assignment_service = AssignmentService(assignment_repo, WorkerRepository(), JobRepository())
        
        assignment = assignment_service.start_assignment(assignment_id)
        if assignment:
            return jsonify({
                'success': True,
                'data': assignment.dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Assignment not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/assignments/<int:assignment_id>/complete', methods=['POST'])
@jwt_required()
def complete_assignment(assignment_id):
    """Complete an assignment."""
    try:
        assignment_repo = AssignmentRepository()
        assignment_service = AssignmentService(assignment_repo, WorkerRepository(), JobRepository())
        
        assignment = assignment_service.complete_assignment(assignment_id)
        if assignment:
            return jsonify({
                'success': True,
                'data': assignment.dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Assignment not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/assignments/<int:assignment_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_assignment(assignment_id):
    """Cancel an assignment."""
    try:
        assignment_repo = AssignmentRepository()
        assignment_service = AssignmentService(assignment_repo, WorkerRepository(), JobRepository())
        
        assignment = assignment_service.cancel_assignment(assignment_id)
        if assignment:
            return jsonify({
                'success': True,
                'data': assignment.dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Assignment not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/assignments/<int:assignment_id>/reassign', methods=['POST'])
@jwt_required()
def reassign_assignment(assignment_id):
    """Reassign assignment to a different worker."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        new_worker_id = data.get('worker_id')
        if not new_worker_id:
            return jsonify({
                'success': False,
                'error': 'worker_id is required'
            }), 400
        
        assignment_repo = AssignmentRepository()
        assignment_service = AssignmentService(assignment_repo, WorkerRepository(), JobRepository())
        
        assignment = assignment_service.reassign_worker(assignment_id, new_worker_id)
        if assignment:
            return jsonify({
                'success': True,
                'data': assignment.dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Assignment not found'
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


@api_v1_bp.route('/assignments/active', methods=['GET'])
@jwt_required()
def get_active_assignments():
    """Get all active assignments."""
    try:
        assignment_repo = AssignmentRepository()
        assignment_service = AssignmentService(assignment_repo, WorkerRepository(), JobRepository())
        
        assignments = assignment_service.get_active_assignments()
        
        return jsonify({
            'success': True,
            'data': [assignment.dict() for assignment in assignments]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/assignments/worker/<int:worker_id>/current', methods=['GET'])
@jwt_required()
def get_worker_current_assignment(worker_id):
    """Get current assignment for a worker."""
    try:
        assignment_repo = AssignmentRepository()
        assignment_service = AssignmentService(assignment_repo, WorkerRepository(), JobRepository())
        
        assignment = assignment_service.get_current_assignment(worker_id)
        if assignment:
            return jsonify({
                'success': True,
                'data': assignment.dict()
            }), 200
        else:
            return jsonify({
                'success': True,
                'data': None
            }), 200
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/assignments/job/<int:job_id>', methods=['GET'])
@jwt_required()
def get_job_assignments(job_id):
    """Get assignments for a specific job."""
    try:
        assignment_repo = AssignmentRepository()
        assignment_service = AssignmentService(assignment_repo, WorkerRepository(), JobRepository())
        
        assignments = assignment_service.get_assignments_by_job(job_id)
        
        return jsonify({
            'success': True,
            'data': [assignment.dict() for assignment in assignments]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/assignments/stats', methods=['GET'])
@jwt_required()
def get_assignment_stats():
    """Get assignment statistics."""
    try:
        assignment_repo = AssignmentRepository()
        assignment_service = AssignmentService(assignment_repo, WorkerRepository(), JobRepository())
        
        stats = assignment_service.get_assignment_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
