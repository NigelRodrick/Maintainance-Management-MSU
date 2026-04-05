"""
Notification Repository
Database operations for notification management.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import text, and_, or_, func
from sqlalchemy.orm import Session

from app.repositories.base_repository import BaseRepository
from app.models import User
from app.domain.notification import (
    NotificationCreate, NotificationUpdate, NotificationResponse,
    NotificationPreference, NotificationPreferenceCreate, NotificationPreferenceUpdate,
    NotificationPreferenceResponse, NotificationSearch, NotificationBatch,
    NotificationType, NotificationPriority, NotificationEntityType
)


class NotificationRepository(BaseRepository):
    """Repository for notification operations."""
    
    def create_notification(self, notification_data: NotificationCreate) -> Optional[NotificationResponse]:
        """Create a new notification."""
        try:
            # Check user preferences
            if not self._is_notification_enabled(notification_data.user_id, notification_data.notification_type):
                return None
            
            # Calculate expiration time
            expires_at = None
            if notification_data.expires_hours:
                expires_at = datetime.utcnow() + timedelta(hours=notification_data.expires_hours)
            
            # Insert notification
            query = text("""
                EXEC sp_create_notification 
                    @user_id = :user_id,
                    @title = :title,
                    @message = :message,
                    @notification_type = :notification_type,
                    @related_entity_type = :related_entity_type,
                    @related_entity_id = :related_entity_id,
                    @priority = :priority,
                    @action_url = :action_url,
                    @action_text = :action_text,
                    @expires_hours = :expires_hours
            """)
            
            result = self.db_session.execute(query, {
                'user_id': notification_data.user_id,
                'title': notification_data.title,
                'message': notification_data.message,
                'notification_type': notification_data.notification_type.value,
                'related_entity_type': notification_data.related_entity_type.value if notification_data.related_entity_type else None,
                'related_entity_id': notification_data.related_entity_id,
                'priority': notification_data.priority.value,
                'action_url': notification_data.action_url,
                'action_text': notification_data.action_text,
                'expires_hours': notification_data.expires_hours
            })
            
            notification_id = result.scalar()
            
            if notification_id:
                return self.get_by_id(notification_id)
            
            return None
            
        except Exception as e:
            self.db_session.rollback()
            raise e
    
    def get_user_notifications(self, user_id: int, unread_only: bool = False, limit: int = 50, offset: int = 0) -> List[NotificationResponse]:
        """Get notifications for a user."""
        try:
            query = text("""
                EXEC sp_get_user_notifications 
                    @user_id = :user_id,
                    @unread_only = :unread_only,
                    @limit = :limit,
                    @offset = :offset
            """)
            
            result = self.db_session.execute(query, {
                'user_id': user_id,
                'unread_only': unread_only,
                'limit': limit,
                'offset': offset
            })
            
            notifications = []
            for row in result:
                notification = NotificationResponse(
                    id=row.id,
                    user_id=user_id,
                    title=row.title,
                    message=row.message,
                    notification_type=NotificationType(row.notification_type),
                    related_entity_type=NotificationEntityType(row.related_entity_type) if row.related_entity_type else None,
                    related_entity_id=row.related_entity_id,
                    is_read=bool(row.is_read),
                    is_deleted=False,
                    created_at=row.created_at,
                    expires_at=row.expires_at,
                    priority=NotificationPriority(row.priority),
                    action_url=row.action_url,
                    action_text=row.action_text,
                    metadata=None
                )
                notifications.append(notification)
            
            return notifications
            
        except Exception as e:
            raise e
    
    def get_unread_count(self, user_id: int) -> int:
        """Get unread notification count for a user."""
        try:
            query = text("EXEC sp_get_unread_count @user_id = :user_id")
            result = self.db_session.execute(query, {'user_id': user_id})
            return result.scalar() or 0
            
        except Exception as e:
            raise e
    
    def mark_as_read(self, user_id: int, notification_ids: Optional[List[int]] = None) -> bool:
        """Mark notifications as read."""
        try:
            notification_ids_str = ','.join(str(nid) for nid in notification_ids) if notification_ids else None
            
            query = text("""
                EXEC sp_mark_notifications_read 
                    @user_id = :user_id,
                    @notification_ids = :notification_ids
            """)
            
            self.db_session.execute(query, {
                'user_id': user_id,
                'notification_ids': notification_ids_str
            })
            
            self.db_session.commit()
            return True
            
        except Exception as e:
            self.db_session.rollback()
            raise e
    
    def mark_as_deleted(self, user_id: int, notification_ids: List[int]) -> bool:
        """Mark notifications as deleted."""
        try:
            if not notification_ids:
                return False
            
            query = text("""
                UPDATE notifications 
                SET is_deleted = 1 
                WHERE user_id = :user_id 
                AND id IN :notification_ids
                AND is_deleted = 0
            """)
            
            self.db_session.execute(query, {
                'user_id': user_id,
                'notification_ids': tuple(notification_ids)
            })
            
            self.db_session.commit()
            return True
            
        except Exception as e:
            self.db_session.rollback()
            raise e
    
    def get_by_id(self, notification_id: int) -> Optional[NotificationResponse]:
        """Get notification by ID."""
        try:
            query = text("""
                SELECT id, user_id, title, message, notification_type,
                       related_entity_type, related_entity_id, is_read, is_deleted,
                       created_at, expires_at, priority, action_url, action_text, metadata
                FROM notifications
                WHERE id = :notification_id
                AND is_deleted = 0
            """)
            
            result = self.db_session.execute(query, {'notification_id': notification_id})
            row = result.first()
            
            if row:
                return NotificationResponse(
                    id=row.id,
                    user_id=row.user_id,
                    title=row.title,
                    message=row.message,
                    notification_type=NotificationType(row.notification_type),
                    related_entity_type=NotificationEntityType(row.related_entity_type) if row.related_entity_type else None,
                    related_entity_id=row.related_entity_id,
                    is_read=bool(row.is_read),
                    is_deleted=bool(row.is_deleted),
                    created_at=row.created_at,
                    expires_at=row.expires_at,
                    priority=NotificationPriority(row.priority),
                    action_url=row.action_url,
                    action_text=row.action_text,
                    metadata=row.metadata
                )
            
            return None
            
        except Exception as e:
            raise e
    
    def search_notifications(self, search_params: NotificationSearch) -> List[NotificationResponse]:
        """Search notifications with filters."""
        try:
            conditions = ["n.is_deleted = 0"]
            params = {}
            
            if search_params.user_id:
                conditions.append("n.user_id = :user_id")
                params['user_id'] = search_params.user_id
            
            if search_params.notification_type:
                conditions.append("n.notification_type = :notification_type")
                params['notification_type'] = search_params.notification_type.value
            
            if search_params.priority:
                conditions.append("n.priority = :priority")
                params['priority'] = search_params.priority.value
            
            if search_params.is_read is not None:
                conditions.append("n.is_read = :is_read")
                params['is_read'] = search_params.is_read
            
            if search_params.created_after:
                conditions.append("n.created_at >= :created_after")
                params['created_after'] = search_params.created_after
            
            if search_params.created_before:
                conditions.append("n.created_at <= :created_before")
                params['created_before'] = search_params.created_before
            
            # Add expiration filter
            conditions.append("(n.expires_at IS NULL OR n.expires_at > GETUTCDATE())")
            
            where_clause = " AND ".join(conditions)
            
            # Safe parameterized query to prevent SQL injection
            query = text(f"""
                SELECT id, user_id, title, message, notification_type,
                       related_entity_type, related_entity_id, is_read, is_deleted,
                       created_at, expires_at, priority, action_url, action_text, metadata
                FROM notifications n
                WHERE {where_clause}
                ORDER BY n.created_at DESC
                OFFSET :offset ROWS FETCH NEXT :limit ROWS ONLY
            """)
            
            # Add where_clause to params for safe execution
            params['where_clause'] = where_clause
            
            params.update({
                'offset': search_params.offset,
                'limit': search_params.limit
            })
            
            result = self.db_session.execute(query, params)
            
            notifications = []
            for row in result:
                notification = NotificationResponse(
                    id=row.id,
                    user_id=row.user_id,
                    title=row.title,
                    message=row.message,
                    notification_type=NotificationType(row.notification_type),
                    related_entity_type=NotificationEntityType(row.related_entity_type) if row.related_entity_type else None,
                    related_entity_id=row.related_entity_id,
                    is_read=bool(row.is_read),
                    is_deleted=bool(row.is_deleted),
                    created_at=row.created_at,
                    expires_at=row.expires_at,
                    priority=NotificationPriority(row.priority),
                    action_url=row.action_url,
                    action_text=row.action_text,
                    metadata=row.metadata
                )
                notifications.append(notification)
            
            return notifications
            
        except Exception as e:
            raise e
    
    def get_notification_stats(self, user_id: int) -> Dict[str, Any]:
        """Get notification statistics for a user."""
        try:
            query = text("""
                SELECT 
                    COUNT(*) as total_notifications,
                    SUM(CASE WHEN is_read = 0 THEN 1 ELSE 0 END) as unread_notifications,
                    SUM(CASE WHEN is_read = 1 THEN 1 ELSE 0 END) as read_notifications,
                    SUM(CASE WHEN expires_at IS NOT NULL AND expires_at < GETUTCDATE() THEN 1 ELSE 0 END) as expired_notifications
                FROM notifications
                WHERE user_id = :user_id
                AND is_deleted = 0
            """)
            
            result = self.db_session.execute(query, {'user_id': user_id})
            stats_row = result.first()
            
            # Get breakdown by type
            type_query = text("""
                SELECT notification_type, COUNT(*) as count
                FROM notifications
                WHERE user_id = :user_id
                AND is_deleted = 0
                GROUP BY notification_type
            """)
            
            type_result = self.db_session.execute(type_query, {'user_id': user_id})
            by_type = {row.notification_type: row.count for row in type_result}
            
            # Get breakdown by priority
            priority_query = text("""
                SELECT priority, COUNT(*) as count
                FROM notifications
                WHERE user_id = :user_id
                AND is_deleted = 0
                GROUP BY priority
            """)
            
            priority_result = self.db_session.execute(priority_query, {'user_id': user_id})
            by_priority = {row.priority: row.count for row in priority_result}
            
            return {
                'total_notifications': stats_row.total_notifications,
                'unread_notifications': stats_row.unread_notifications,
                'read_notifications': stats_row.read_notifications,
                'expired_notifications': stats_row.expired_notifications,
                'notifications_by_type': by_type,
                'notifications_by_priority': by_priority
            }
            
        except Exception as e:
            raise e
    
    def cleanup_expired_notifications(self) -> int:
        """Clean up expired notifications."""
        try:
            query = text("""
                UPDATE notifications
                SET is_deleted = 1
                WHERE expires_at IS NOT NULL
                AND expires_at < GETUTCDATE()
                AND is_deleted = 0
            """)
            
            result = self.db_session.execute(query)
            deleted_count = result.rowcount
            self.db_session.commit()
            
            return deleted_count
            
        except Exception as e:
            self.db_session.rollback()
            raise e
    
    def _is_notification_enabled(self, user_id: int, notification_type: NotificationType) -> bool:
        """Check if notification type is enabled for user."""
        try:
            query = text("""
                SELECT is_enabled
                FROM notification_preferences
                WHERE user_id = :user_id
                AND notification_type = :notification_type
            """)
            
            result = self.db_session.execute(query, {
                'user_id': user_id,
                'notification_type': notification_type.value
            })
            
            enabled = result.scalar()
            return enabled if enabled is not None else True  # Default to enabled
            
        except Exception:
            return True  # Default to enabled on error


class NotificationPreferenceRepository(BaseRepository):
    """Repository for notification preference operations."""
    
    def get_user_preferences(self, user_id: int) -> List[NotificationPreferenceResponse]:
        """Get all notification preferences for a user."""
        try:
            query = text("""
                SELECT id, user_id, notification_type, is_enabled, email_enabled, push_enabled, created_at, updated_at
                FROM notification_preferences
                WHERE user_id = :user_id
                ORDER BY notification_type
            """)
            
            result = self.db_session.execute(query, {'user_id': user_id})
            
            preferences = []
            for row in result:
                preference = NotificationPreferenceResponse(
                    id=row.id,
                    user_id=row.user_id,
                    notification_type=NotificationType(row.notification_type),
                    is_enabled=bool(row.is_enabled),
                    email_enabled=bool(row.email_enabled),
                    push_enabled=bool(row.push_enabled),
                    created_at=row.created_at,
                    updated_at=row.updated_at
                )
                preferences.append(preference)
            
            return preferences
            
        except Exception as e:
            raise e
    
    def get_preference(self, user_id: int, notification_type: NotificationType) -> Optional[NotificationPreferenceResponse]:
        """Get specific notification preference for a user."""
        try:
            query = text("""
                SELECT id, user_id, notification_type, is_enabled, email_enabled, push_enabled, created_at, updated_at
                FROM notification_preferences
                WHERE user_id = :user_id
                AND notification_type = :notification_type
            """)
            
            result = self.db_session.execute(query, {
                'user_id': user_id,
                'notification_type': notification_type.value
            })
            
            row = result.first()
            if row:
                return NotificationPreferenceResponse(
                    id=row.id,
                    user_id=row.user_id,
                    notification_type=NotificationType(row.notification_type),
                    is_enabled=bool(row.is_enabled),
                    email_enabled=bool(row.email_enabled),
                    push_enabled=bool(row.push_enabled),
                    created_at=row.created_at,
                    updated_at=row.updated_at
                )
            
            return None
            
        except Exception as e:
            raise e
    
    def create_preference(self, preference_data: NotificationPreferenceCreate) -> NotificationPreferenceResponse:
        """Create a new notification preference."""
        try:
            query = text("""
                INSERT INTO notification_preferences (user_id, notification_type, is_enabled, email_enabled, push_enabled)
                VALUES (:user_id, :notification_type, :is_enabled, :email_enabled, :push_enabled)
                RETURNING id, user_id, notification_type, is_enabled, email_enabled, push_enabled, created_at, updated_at
            """)
            
            result = self.db_session.execute(query, {
                'user_id': preference_data.user_id,
                'notification_type': preference_data.notification_type.value,
                'is_enabled': preference_data.is_enabled,
                'email_enabled': preference_data.email_enabled,
                'push_enabled': preference_data.push_enabled
            })
            
            row = result.first()
            self.db_session.commit()
            
            return NotificationPreferenceResponse(
                id=row.id,
                user_id=row.user_id,
                notification_type=NotificationType(row.notification_type),
                is_enabled=bool(row.is_enabled),
                email_enabled=bool(row.email_enabled),
                push_enabled=bool(row.push_enabled),
                created_at=row.created_at,
                updated_at=row.updated_at
            )
            
        except Exception as e:
            self.db_session.rollback()
            raise e
    
    def update_preference(self, user_id: int, notification_type: NotificationType, update_data: NotificationPreferenceUpdate) -> Optional[NotificationPreferenceResponse]:
        """Update a notification preference."""
        try:
            # Build update fields
            update_fields = []
            params = {'user_id': user_id, 'notification_type': notification_type.value}
            
            if update_data.is_enabled is not None:
                update_fields.append("is_enabled = :is_enabled")
                params['is_enabled'] = update_data.is_enabled
            
            if update_data.email_enabled is not None:
                update_fields.append("email_enabled = :email_enabled")
                params['email_enabled'] = update_data.email_enabled
            
            if update_data.push_enabled is not None:
                update_fields.append("push_enabled = :push_enabled")
                params['push_enabled'] = update_data.push_enabled
            
            if not update_fields:
                return self.get_preference(user_id, notification_type)
            
            # Validate update_fields to prevent SQL injection
            allowed_fields = {
                'is_enabled', 'email_enabled', 'push_enabled', 'updated_at'
            }
            
            # Filter update_fields to only allowed ones
            safe_update_fields = []
            for field in update_fields:
                field_name = field.split('=')[0].strip()
                if field_name in allowed_fields:
                    safe_update_fields.append(field)
            
            if not safe_update_fields:
                return self.get_preference(user_id, notification_type)
            
            safe_update_fields.append("updated_at = GETUTCDATE()")
            
            query = text(f"""
                UPDATE notification_preferences
                SET {', '.join(safe_update_fields)}
                WHERE user_id = :user_id
                AND notification_type = :notification_type
                RETURNING id, user_id, notification_type, is_enabled, email_enabled, push_enabled, created_at, updated_at
            """)
            
            result = self.db_session.execute(query, params)
            row = result.first()
            
            if row:
                self.db_session.commit()
                return NotificationPreferenceResponse(
                    id=row.id,
                    user_id=row.user_id,
                    notification_type=NotificationType(row.notification_type),
                    is_enabled=bool(row.is_enabled),
                    email_enabled=bool(row.email_enabled),
                    push_enabled=bool(row.push_enabled),
                    created_at=row.created_at,
                    updated_at=row.updated_at
                )
            
            return None
            
        except Exception as e:
            self.db_session.rollback()
            raise e
    
    def delete_preference(self, user_id: int, notification_type: NotificationType) -> bool:
        """Delete a notification preference."""
        try:
            query = text("""
                DELETE FROM notification_preferences
                WHERE user_id = :user_id
                AND notification_type = :notification_type
            """)
            
            result = self.db_session.execute(query, {
                'user_id': user_id,
                'notification_type': notification_type.value
            })
            
            self.db_session.commit()
            return result.rowcount > 0
            
        except Exception as e:
            self.db_session.rollback()
            raise e
