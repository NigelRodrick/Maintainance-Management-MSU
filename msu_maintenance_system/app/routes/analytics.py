"""
Analytics Routes - MSU Maintenance System
API endpoints for analytics and ML predictions
"""

from flask import Blueprint, jsonify, request, render_template
from app.analytics import AnalyticsModule
from app.services.ml_model_service import MLModelService
from functools import wraps
import logging

logger = logging.getLogger(__name__)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

# Initialize services
analytics = AnalyticsModule()
ml_service = MLModelService()

def require_analytics_access(f):
    """Decorator to require analytics access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Add role-based access control here
        return f(*args, **kwargs)
    return decorated_function

@analytics_bp.route('/')
@require_analytics_access
def analytics_dashboard():
    """Analytics dashboard HTML page"""
    return render_template('analytics_dashboard.html')

@analytics_bp.route('/dashboard')
@require_analytics_access
def get_dashboard():
    """Get comprehensive dashboard data"""
    try:
        data = analytics.get_dashboard_data()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        logger.error(f"Dashboard error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/department-summary')
@require_analytics_access
def get_department_summary():
    """Get department performance summary"""
    try:
        data = analytics.get_department_summary()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        logger.error(f"Department summary error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/worker-performance')
@require_analytics_access
def get_worker_performance():
    """Get worker performance analytics"""
    try:
        data = analytics.get_worker_performance()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        logger.error(f"Worker performance error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/job-trends')
@require_analytics_access
def get_job_trends():
    """Get job trends over time"""
    try:
        days = request.args.get('days', 30, type=int)
        data = analytics.get_job_trends(days)
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        logger.error(f"Job trends error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/ml/predict-priority', methods=['POST'])
@require_analytics_access
def predict_priority():
    """Predict job priority using ML"""
    try:
        features = request.get_json()
        if not features:
            return jsonify({
                'success': False,
                'error': 'No features provided'
            }), 400
        
        prediction = ml_service.predict_priority(features)
        return jsonify({
            'success': True,
            'data': prediction
        })
    except Exception as e:
        logger.error(f"Priority prediction error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/ml/estimate-time', methods=['POST'])
@require_analytics_access
def estimate_resolution_time():
    """Estimate job resolution time using ML"""
    try:
        features = request.get_json()
        if not features:
            return jsonify({
                'success': False,
                'error': 'No features provided'
            }), 400
        
        estimation = ml_service.estimate_resolution_time(features)
        return jsonify({
            'success': True,
            'data': estimation
        })
    except Exception as e:
        logger.error(f"Time estimation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/ml/recommend-technician', methods=['POST'])
@require_analytics_access
def recommend_technician():
    """Recommend technician using ML"""
    try:
        features = request.get_json()
        if not features:
            return jsonify({
                'success': False,
                'error': 'No features provided'
            }), 400
        
        recommendations = ml_service.recommend_technician(features)
        return jsonify({
            'success': True,
            'data': recommendations
        })
    except Exception as e:
        logger.error(f"Technician recommendation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/ml/models')
@require_analytics_access
def get_model_info():
    """Get information about loaded ML models"""
    try:
        info = ml_service.get_model_info()
        return jsonify({
            'success': True,
            'data': info
        })
    except Exception as e:
        logger.error(f"Model info error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@analytics_bp.route('/cache/clear', methods=['POST'])
@require_analytics_access
def clear_cache():
    """Clear analytics cache"""
    try:
        analytics.clear_cache()
        return jsonify({
            'success': True,
            'message': 'Analytics cache cleared'
        })
    except Exception as e:
        logger.error(f"Cache clear error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
