"""
Workers API v1 Endpoints
Worker management endpoints.
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1 import api_v1_bp
from app.services.worker_service import WorkerService
from app.domain.worker import WorkerCreate, WorkerUpdate, WorkerSearchRequest
from app.repositories.worker_repository import WorkerRepository
from app.repositories.user_repository import UserRepository


@api_v1_bp.route('/workers', methods=['GET'])
@jwt_required()
def get_workers():
    """Get all workers with optional filters."""
    try:
        # Parse query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 25))
        skill_category = request.args.get('skill_category')
        department = request.args.get('department')
        keyword = request.args.get('keyword')
        available_only = request.args.get('available_only', 'false').lower() == 'true'
        
        # Create search request
        search_data = {
            'page': page,
            'per_page': per_page,
            'skill_category': skill_category,
            'department': department,
            'keyword': keyword,
            'available_only': available_only
        }
        
        search_request = WorkerSearchRequest(**search_data)
        
        # Initialize services
        worker_repo = WorkerRepository()
        worker_service = WorkerService(worker_repo, UserRepository())
        
        # Get workers
        result = worker_service.search_workers(search_request)
        
        return jsonify({
            'success': True,
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/workers/<int:worker_id>', methods=['GET'])
@jwt_required()
def get_worker(worker_id):
    """Get worker by ID."""
    try:
        worker_repo = WorkerRepository()
        worker_service = WorkerService(worker_repo, UserRepository())
        
        worker = worker_service.get_worker_by_id(worker_id)
        if worker:
            return jsonify({
                'success': True,
                'data': worker.dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Worker not found'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/workers', methods=['POST'])
@jwt_required()
def create_worker():
    """Create a new worker."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Create worker request
        worker_data = WorkerCreate(**data)
        
        # Initialize services
        worker_repo = WorkerRepository()
        worker_service = WorkerService(worker_repo, UserRepository())
        
        # Create worker
        worker = worker_service.create_worker(worker_data)
        
        return jsonify({
            'success': True,
            'data': worker.dict()
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


@api_v1_bp.route('/workers/<int:worker_id>', methods=['PUT'])
@jwt_required()
def update_worker(worker_id):
    """Update worker details."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Create update request
        update_data = WorkerUpdate(**data)
        
        # Initialize services
        worker_repo = WorkerRepository()
        worker_service = WorkerService(worker_repo, UserRepository())
        
        # Update worker
        worker = worker_service.update_worker(worker_id, update_data)
        if worker:
            return jsonify({
                'success': True,
                'data': worker.dict()
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Worker not found'
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


@api_v1_bp.route('/workers/<int:worker_id>/workload', methods=['GET'])
@jwt_required()
def get_worker_workload(worker_id):
    """Get worker workload information."""
    try:
        worker_repo = WorkerRepository()
        worker_service = WorkerService(worker_repo, UserRepository())
        
        workload = worker_service.get_worker_workload(worker_id)
        
        return jsonify({
            'success': True,
            'data': workload.dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/workers/<int:worker_id>/performance', methods=['GET'])
@jwt_required()
def get_worker_performance(worker_id):
    """Get worker performance statistics."""
    try:
        days = int(request.args.get('days', 30))
        
        worker_repo = WorkerRepository()
        worker_service = WorkerService(worker_repo, UserRepository())
        
        performance = worker_service.get_worker_performance(worker_id, days)
        
        return jsonify({
            'success': True,
            'data': performance.dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/workers/available', methods=['GET'])
@jwt_required()
def get_available_workers():
    """Get available workers."""
    try:
        skill_category = request.args.get('skill_category')
        
        worker_repo = WorkerRepository()
        worker_service = WorkerService(worker_repo, UserRepository())
        
        if skill_category:
            from app.domain import SkillCategory
            workers = worker_service.get_available_workers(SkillCategory(skill_category))
        else:
            workers = worker_service.get_available_workers()
        
        return jsonify({
            'success': True,
            'data': [worker.dict() for worker in workers]
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/workers/recommendations', methods=['GET'])
@jwt_required()
def get_worker_recommendations():
    """Get worker recommendations for a job."""
    try:
        skill_category = request.args.get('skill_category')
        limit = int(request.args.get('limit', 5))
        
        if not skill_category:
            return jsonify({
                'success': False,
                'error': 'skill_category parameter is required'
            }), 400
        
        worker_repo = WorkerRepository()
        worker_service = WorkerService(worker_repo, UserRepository())
        
        recommendations = worker_service.get_recommended_workers(skill_category, limit)
        
        return jsonify({
            'success': True,
            'data': recommendations
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@api_v1_bp.route('/workers/stats', methods=['GET'])
@jwt_required()
def get_worker_stats():
    """Get worker statistics."""
    try:
        worker_repo = WorkerRepository()
        worker_service = WorkerService(worker_repo, UserRepository())
        
        stats = worker_service.get_worker_stats()
        
        return jsonify({
            'success': True,
            'data': stats
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
