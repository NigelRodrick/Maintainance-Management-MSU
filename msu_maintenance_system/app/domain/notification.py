"""
Notification Domain Models
Pydantic models for notification data validation and business logic.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    """Notification types."""
    JOB_ASSIGNED = "JOB_ASSIGNED"
    JOB_STATUS_CHANGED = "JOB_STATUS_CHANGED"
    MATERIAL_SHORTAGE = "MATERIAL_SHORTAGE"
    ASSIGNMENT_COMPLETED = "ASSIGNMENT_COMPLETED"
    SYSTEM_ALERT = "SYSTEM_ALERT"
    REMINDER = "REMINDER"
    WORKER_PERFORMANCE = "WORKER_PERFORMANCE"
    MAINTENANCE_REQUIRED = "MAINTENANCE_REQUIRED"


class NotificationPriority(str, Enum):
    """Notification priority levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


class NotificationEntityType(str, Enum):
    """Related entity types."""
    JOB = "job"
    ASSIGNMENT = "assignment"
    WORKER = "worker"
    MATERIAL = "material"
    USER = "user"
    SYSTEM = "system"


class NotificationBase(BaseModel):
    """Base notification model."""
    title: str = Field(..., min_length=1, max_length=200, description="Notification title")
    message: str = Field(..., min_length=1, max_length=2000, description="Notification message")
    notification_type: NotificationType = Field(..., description="Type of notification")
    related_entity_type: Optional[NotificationEntityType] = Field(None, description="Related entity type")
    related_entity_id: Optional[int] = Field(None, description="Related entity ID")
    priority: NotificationPriority = Field(NotificationPriority.MEDIUM, description="Notification priority")
    action_url: Optional[str] = Field(None, max_length=500, description="Action URL for notification")
    action_text: Optional[str] = Field(None, max_length=100, description="Action button text")
    expires_hours: Optional[int] = Field(None, ge=1, le=8760, description="Hours until notification expires")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    @validator('title')
    def validate_title(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v.strip()
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError('Message cannot be empty')
        return v.strip()


class NotificationCreate(NotificationBase):
    """Notification creation model."""
    user_id: int = Field(..., gt=0, description="User ID to send notification to")


class NotificationUpdate(BaseModel):
    """Notification update model."""
    is_read: Optional[bool] = Field(None, description="Mark notification as read")
    is_deleted: Optional[bool] = Field(None, description="Mark notification as deleted")


class NotificationResponse(NotificationBase):
    """Notification response model."""
    id: int
    user_id: int
    is_read: bool
    is_deleted: bool
    created_at: datetime
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class NotificationList(BaseModel):
    """Notification list response model."""
    notifications: List[NotificationResponse]
    total_count: int
    unread_count: int
    has_more: bool


class NotificationPreference(BaseModel):
    """Notification preference model."""
    notification_type: NotificationType
    is_enabled: bool = True
    email_enabled: bool = False
    push_enabled: bool = True


class NotificationPreferenceCreate(BaseModel):
    """Notification preference creation model."""
    user_id: int = Field(..., gt=0, description="User ID")
    notification_type: NotificationType
    is_enabled: bool = True
    email_enabled: bool = False
    push_enabled: bool = True


class NotificationPreferenceUpdate(BaseModel):
    """Notification preference update model."""
    is_enabled: Optional[bool] = None
    email_enabled: Optional[bool] = None
    push_enabled: Optional[bool] = None


class NotificationPreferenceResponse(NotificationPreference):
    """Notification preference response model."""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NotificationStats(BaseModel):
    """Notification statistics model."""
    total_notifications: int
    unread_notifications: int
    read_notifications: int
    expired_notifications: int
    notifications_by_type: Dict[str, int]
    notifications_by_priority: Dict[str, int]


class NotificationSearch(BaseModel):
    """Notification search model."""
    user_id: Optional[int] = None
    notification_type: Optional[NotificationType] = None
    priority: Optional[NotificationPriority] = None
    is_read: Optional[bool] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    limit: int = Field(50, ge=1, le=100, description="Maximum number of results")
    offset: int = Field(0, ge=0, description="Offset for pagination")


class NotificationBatch(BaseModel):
    """Batch notification operations model."""
    notification_ids: List[int] = Field(..., min_items=1, description="List of notification IDs")
    action: str = Field(..., regex=r'^(mark_read|mark_unread|delete)$', description="Batch action")
    
    @validator('notification_ids')
    def validate_notification_ids(cls, v):
        if len(v) > 100:
            raise ValueError('Cannot process more than 100 notifications at once')
        return v


class NotificationTemplate(BaseModel):
    """Notification template model."""
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    notification_type: NotificationType
    title_template: str = Field(..., min_length=1, max_length=200, description="Title template")
    message_template: str = Field(..., min_length=1, max_length=2000, description="Message template")
    default_priority: NotificationPriority = NotificationPriority.MEDIUM
    action_url_template: Optional[str] = Field(None, max_length=500, description="Action URL template")
    action_text_template: Optional[str] = Field(None, max_length=100, description="Action text template")
    expires_hours: Optional[int] = Field(None, ge=1, le=8760, description="Default expiration hours")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('Template name cannot be empty')
        return v.strip().upper()


class NotificationTemplateResponse(NotificationTemplate):
    """Notification template response model."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class NotificationTrigger(BaseModel):
    """Notification trigger model."""
    event_type: str = Field(..., min_length=1, max_length=100, description="Event type")
    entity_type: NotificationEntityType
    entity_id: int
    user_id: Optional[int] = None  # If None, will be determined from entity
    additional_data: Optional[Dict[str, Any]] = None
    
    @validator('event_type')
    def validate_event_type(cls, v):
        if not v.strip():
            raise ValueError('Event type cannot be empty')
        return v.strip().lower()


class NotificationChannel(str, Enum):
    """Notification channels."""
    IN_APP = "in_app"
    EMAIL = "email"
    PUSH = "push"
    SMS = "sms"


class NotificationDelivery(BaseModel):
    """Notification delivery model."""
    notification_id: int
    channel: NotificationChannel
    status: str = Field(..., regex=r'^(pending|sent|failed|retry)$')
    delivered_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = Field(0, ge=0, description="Number of retry attempts")
    
    class Config:
        from_attributes = True


class NotificationAnalytics(BaseModel):
    """Notification analytics model."""
    period_days: int = Field(30, ge=1, le=365, description="Analysis period in days")
    total_sent: int
    total_delivered: int
    total_read: int
    delivery_rate: float
    read_rate: float
    average_read_time_hours: Optional[float]
    notifications_by_type: Dict[str, int]
    notifications_by_channel: Dict[str, int]
    most_active_users: List[Dict[str, Any]]
    most_common_types: List[Dict[str, Any]]


# Helper functions for notification creation
def create_job_assigned_notification(user_id: int, job_id: int, job_title: str) -> NotificationCreate:
    """Create a job assigned notification."""
    return NotificationCreate(
        user_id=user_id,
        title="New Job Assigned",
        message=f"You have been assigned a new job: {job_title}",
        notification_type=NotificationType.JOB_ASSIGNED,
        related_entity_type=NotificationEntityType.JOB,
        related_entity_id=job_id,
        priority=NotificationPriority.MEDIUM,
        action_url=f"/jobs/{job_id}",
        action_text="View Job",
        expires_hours=168  # 7 days
    )


def create_job_status_notification(user_id: int, job_id: int, job_title: str, old_status: str, new_status: str) -> NotificationCreate:
    """Create a job status change notification."""
    return NotificationCreate(
        user_id=user_id,
        title=f"Job Status Changed",
        message=f"Job '{job_title}' status changed from {old_status} to {new_status}",
        notification_type=NotificationType.JOB_STATUS_CHANGED,
        related_entity_type=NotificationEntityType.JOB,
        related_entity_id=job_id,
        priority=NotificationPriority.MEDIUM,
        action_url=f"/jobs/{job_id}",
        action_text="View Job",
        expires_hours=168  # 7 days
    )


def create_material_shortage_notification(user_id: int, material_id: int, item_name: str, shortage_amount: float) -> NotificationCreate:
    """Create a material shortage notification."""
    return NotificationCreate(
        user_id=user_id,
        title="Material Shortage Alert",
        message=f"Material '{item_name}' is running low. Shortage: {shortage_amount} units",
        notification_type=NotificationType.MATERIAL_SHORTAGE,
        related_entity_type=NotificationEntityType.MATERIAL,
        related_entity_id=material_id,
        priority=NotificationPriority.HIGH,
        action_url=f"/materials/{material_id}",
        action_text="Manage Materials",
        expires_hours=48  # 2 days
    )


def create_assignment_completed_notification(user_id: int, assignment_id: int, job_title: str) -> NotificationCreate:
    """Create an assignment completed notification."""
    return NotificationCreate(
        user_id=user_id,
        title="Assignment Completed",
        message=f"Assignment for job '{job_title}' has been completed",
        notification_type=NotificationType.ASSIGNMENT_COMPLETED,
        related_entity_type=NotificationEntityType.ASSIGNMENT,
        related_entity_id=assignment_id,
        priority=NotificationPriority.MEDIUM,
        action_url=f"/assignments/{assignment_id}",
        action_text="View Assignment",
        expires_hours=168  # 7 days
    )


def create_system_alert_notification(user_id: int, title: str, message: str, priority: NotificationPriority = NotificationPriority.MEDIUM) -> NotificationCreate:
    """Create a system alert notification."""
    return NotificationCreate(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=NotificationType.SYSTEM_ALERT,
        related_entity_type=NotificationEntityType.SYSTEM,
        priority=priority,
        expires_hours=24  # 1 day
    )


def create_reminder_notification(user_id: int, title: str, message: str, related_entity_type: Optional[NotificationEntityType] = None, related_entity_id: Optional[int] = None) -> NotificationCreate:
    """Create a reminder notification."""
    return NotificationCreate(
        user_id=user_id,
        title=title,
        message=message,
        notification_type=NotificationType.REMINDER,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        priority=NotificationPriority.LOW,
        expires_hours=72  # 3 days
    )
