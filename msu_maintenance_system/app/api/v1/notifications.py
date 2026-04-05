"""
Notification API Endpoints
RESTful API for notification management.
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import List, Dict, Any

from app.services.notification_service import create_notification_service
from app.domain.notification import (
    NotificationCreate, NotificationUpdate, NotificationResponse,
    NotificationPreference, NotificationPreferenceCreate, NotificationPreferenceUpdate,
    NotificationPreferenceResponse, NotificationSearch, NotificationBatch,
    NotificationType, NotificationPriority, NotificationEntityType
)
from app.extensions import db
import logging

logger = logging.getLogger(__name__)

# Create blueprint
notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/v1/notifications')


def get_notification_service():
    """Get notification service instance."""
    return create_notification_service(db.session)


@notifications_bp.route('/', methods=['GET'])
@jwt_required()
def get_notifications():
    """Get notifications for current user."""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        limit = min(int(request.args.get('limit', 50)), 100)  # Max 100
        offset = int(request.args.get('offset', 0))
        
        # Get notifications
        notification_service = get_notification_service()
        notifications = notification_service.get_user_notifications(
            user_id=user_id,
            unread_only=unread_only,
            limit=limit,
            offset=offset
        )
        
        # Get unread count
        unread_count = notification_service.get_unread_count(user_id)
        
        return jsonify({
            'success': True,
            'data': {
                'notifications': [n.dict() for n in notifications],
                'unread_count': unread_count,
                'has_more': len(notifications) == limit
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve notifications'
        }), 500


@notifications_bp.route('/<int:notification_id>', methods=['GET'])
@jwt_required()
def get_notification(notification_id: int):
    """Get specific notification."""
    try:
        user_id = get_jwt_identity()
        
        notification_service = get_notification_service()
        notification = notification_service.notification_repo.get_by_id(notification_id)
        
        if not notification or notification.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Notification not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': notification.dict()
        })
        
    except Exception as e:
        logger.error(f"Error getting notification {notification_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve notification'
        }), 500


@notifications_bp.route('/', methods=['POST'])
@jwt_required()
def create_notification():
    """Create a new notification (admin only)."""
    try:
        user_id = get_jwt_identity()
        
        # Check if user is admin (implement proper role checking)
        # For now, allow all authenticated users
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate and create notification
        try:
            notification_data = NotificationCreate(**data)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Invalid data: {str(e)}'
            }), 400
        
        notification_service = get_notification_service()
        notification = notification_service.create_notification(notification_data)
        
        if not notification:
            return jsonify({
                'success': False,
                'error': 'Failed to create notification'
            }), 400
        
        return jsonify({
            'success': True,
            'data': notification.dict(),
            'message': 'Notification created successfully'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating notification: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to create notification'
        }), 500


@notifications_bp.route('/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_read(notification_id: int):
    """Mark notification as read."""
    try:
        user_id = get_jwt_identity()
        
        notification_service = get_notification_service()
        
        # Verify notification belongs to user
        notification = notification_service.notification_repo.get_by_id(notification_id)
        if not notification or notification.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Notification not found'
            }), 404
        
        # Mark as read
        success = notification_service.mark_as_read(user_id, [notification_id])
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to mark notification as read'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Notification marked as read'
        })
        
    except Exception as e:
        logger.error(f"Error marking notification {notification_id} as read: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to mark notification as read'
        }), 500


@notifications_bp.route('/mark-all-read', methods=['PUT'])
@jwt_required()
def mark_all_notifications_read():
    """Mark all notifications as read."""
    try:
        user_id = get_jwt_identity()
        
        notification_service = get_notification_service()
        success = notification_service.mark_as_read(user_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to mark notifications as read'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'All notifications marked as read'
        })
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to mark notifications as read'
        }), 500


@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
@jwt_required()
def delete_notification(notification_id: int):
    """Delete notification."""
    try:
        user_id = get_jwt_identity()
        
        notification_service = get_notification_service()
        
        # Verify notification belongs to user
        notification = notification_service.notification_repo.get_by_id(notification_id)
        if not notification or notification.user_id != user_id:
            return jsonify({
                'success': False,
                'error': 'Notification not found'
            }), 404
        
        # Mark as deleted
        success = notification_service.mark_as_deleted(user_id, [notification_id])
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to delete notification'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Notification deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting notification {notification_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete notification'
        }), 500


@notifications_bp.route('/batch', methods=['POST'])
@jwt_required()
def batch_operations():
    """Perform batch operations on notifications."""
    try:
        user_id = get_jwt_identity()
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate batch data
        try:
            batch_data = NotificationBatch(**data)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Invalid data: {str(e)}'
            }), 400
        
        notification_service = get_notification_service()
        success = notification_service.batch_operation(user_id, batch_data)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to perform batch operation'
            }), 400
        
        return jsonify({
            'success': True,
            'message': f'Batch operation "{batch_data.action}" completed successfully'
        })
        
    except Exception as e:
        logger.error(f"Error performing batch operation: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to perform batch operation'
        }), 500


@notifications_bp.route('/unread-count', methods=['GET'])
@jwt_required()
def get_unread_count():
    """Get unread notification count."""
    try:
        user_id = get_jwt_identity()
        
        notification_service = get_notification_service()
        count = notification_service.get_unread_count(user_id)
        
        return jsonify({
            'success': True,
            'data': {
                'unread_count': count
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting unread count: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get unread count'
        }), 500


@notifications_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_notification_stats():
    """Get notification statistics."""
    try:
        user_id = get_jwt_identity()
        
        notification_service = get_notification_service()
        stats = notification_service.get_notification_stats(user_id)
        
        return jsonify({
            'success': True,
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting notification stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get notification statistics'
        }), 500


@notifications_bp.route('/search', methods=['POST'])
@jwt_required()
def search_notifications():
    """Search notifications."""
    try:
        user_id = get_jwt_identity()
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Add user_id to search params
        data['user_id'] = user_id
        
        # Validate search data
        try:
            search_params = NotificationSearch(**data)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Invalid data: {str(e)}'
            }), 400
        
        notification_service = get_notification_service()
        notifications = notification_service.search_notifications(search_params)
        
        return jsonify({
            'success': True,
            'data': {
                'notifications': [n.dict() for n in notifications]
            }
        })
        
    except Exception as e:
        logger.error(f"Error searching notifications: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to search notifications'
        }), 500


# Notification Preferences Endpoints

@notifications_bp.route('/preferences', methods=['GET'])
@jwt_required()
def get_notification_preferences():
    """Get notification preferences for current user."""
    try:
        user_id = get_jwt_identity()
        
        notification_service = get_notification_service()
        preferences = notification_service.get_user_preferences(user_id)
        
        return jsonify({
            'success': True,
            'data': {
                'preferences': [p.dict() for p in preferences]
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting notification preferences: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get notification preferences'
        }), 500


@notifications_bp.route('/preferences/<notification_type>', methods=['GET'])
@jwt_required()
def get_notification_preference(notification_type: str):
    """Get specific notification preference."""
    try:
        user_id = get_jwt_identity()
        
        # Validate notification type
        try:
            notification_type_enum = NotificationType(notification_type.upper())
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid notification type'
            }), 400
        
        notification_service = get_notification_service()
        preference = notification_service.get_preference(user_id, notification_type_enum)
        
        if not preference:
            return jsonify({
                'success': False,
                'error': 'Preference not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': preference.dict()
        })
        
    except Exception as e:
        logger.error(f"Error getting notification preference: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get notification preference'
        }), 500


@notifications_bp.route('/preferences/<notification_type>', methods=['PUT'])
@jwt_required()
def update_notification_preference(notification_type: str):
    """Update notification preference."""
    try:
        user_id = get_jwt_identity()
        
        # Validate notification type
        try:
            notification_type_enum = NotificationType(notification_type.upper())
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid notification type'
            }), 400
        
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Validate update data
        try:
            update_data = NotificationPreferenceUpdate(**data)
        except Exception as e:
            return jsonify({
                'success': False,
                'error': f'Invalid data: {str(e)}'
            }), 400
        
        notification_service = get_notification_service()
        preference = notification_service.update_preference(user_id, notification_type_enum, update_data)
        
        if not preference:
            return jsonify({
                'success': False,
                'error': 'Failed to update preference'
            }), 400
        
        return jsonify({
            'success': True,
            'data': preference.dict(),
            'message': 'Preference updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Error updating notification preference: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update notification preference'
        }), 500


@notifications_bp.route('/preferences/reset', methods=['POST'])
@jwt_required()
def reset_notification_preferences():
    """Reset notification preferences to defaults."""
    try:
        user_id = get_jwt_identity()
        
        notification_service = get_notification_service()
        success = notification_service.set_default_preferences(user_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Failed to reset preferences'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Preferences reset to defaults successfully'
        })
        
    except Exception as e:
        logger.error(f"Error resetting notification preferences: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to reset notification preferences'
        }), 500


# Utility Endpoints

@notifications_bp.route('/cleanup', methods=['POST'])
@jwt_required()
def cleanup_expired_notifications():
    """Clean up expired notifications (admin only)."""
    try:
        user_id = get_jwt_identity()
        
        # Check if user is admin (implement proper role checking)
        # For now, allow all authenticated users
        
        notification_service = get_notification_service()
        count = notification_service.cleanup_expired_notifications()
        
        return jsonify({
            'success': True,
            'data': {
                'cleaned_count': count
            },
            'message': f'Cleaned up {count} expired notifications'
        })
        
    except Exception as e:
        logger.error(f"Error cleaning up expired notifications: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to clean up expired notifications'
        }), 500


@notifications_bp.route('/summary', methods=['GET'])
@jwt_required()
def get_notification_summary():
    """Get notification summary for dashboard."""
    try:
        user_id = get_jwt_identity()
        
        notification_service = get_notification_service()
        summary = notification_service.get_notification_summary(user_id)
        
        return jsonify({
            'success': True,
            'data': summary
        })
        
    except Exception as e:
        logger.error(f"Error getting notification summary: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get notification summary'
        }), 500


# Error handlers
@notifications_bp.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404


@notifications_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500
