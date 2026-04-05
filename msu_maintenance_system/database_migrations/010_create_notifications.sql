-- Create Notifications Table
-- For in-app notifications system

USE CentralServices_AM_DB;
GO

-- Create notifications table
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'notifications')
BEGIN
    CREATE TABLE notifications (
        id INT IDENTITY(1,1) PRIMARY KEY,
        user_id INT NOT NULL,
        title NVARCHAR(200) NOT NULL,
        message NVARCHAR(MAX) NOT NULL,
        notification_type NVARCHAR(50) NOT NULL,
        related_entity_type NVARCHAR(50) NULL,
        related_entity_id INT NULL,
        is_read BIT NOT NULL DEFAULT 0,
        is_deleted BIT NOT NULL DEFAULT 0,
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        expires_at DATETIME2 NULL,
        priority NVARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
        action_url NVARCHAR(500) NULL,
        action_text NVARCHAR(100) NULL,
        metadata NVARCHAR(MAX) NULL,
        
        CONSTRAINT FK_notifications_users FOREIGN KEY (user_id) REFERENCES users(id),
        CONSTRAINT CHK_notifications_type CHECK (notification_type IN ('JOB_ASSIGNED', 'JOB_STATUS_CHANGED', 'MATERIAL_SHORTAGE', 'ASSIGNMENT_COMPLETED', 'SYSTEM_ALERT', 'REMINDER')),
        CONSTRAINT CHK_notifications_priority CHECK (priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')),
        CONSTRAINT CHK_notifications_read CHECK (is_read IN (0, 1)),
        CONSTRAINT CHK_notifications_deleted CHECK (is_deleted IN (0, 1))
    );
    
    PRINT '✓ Created notifications table';
END
ELSE
BEGIN
    PRINT 'ℹ Notifications table already exists';
END
GO

-- Create indexes
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_notifications_user_id')
BEGIN
    CREATE INDEX IX_notifications_user_id ON notifications(user_id);
    PRINT '✓ Created index on notifications(user_id)';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_notifications_created_at')
BEGIN
    CREATE INDEX IX_notifications_created_at ON notifications(created_at DESC);
    PRINT '✓ Created index on notifications(created_at)';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_notifications_user_unread')
BEGIN
    CREATE INDEX IX_notifications_user_unread ON notifications(user_id, is_read, created_at DESC);
    PRINT '✓ Created index on notifications(user_id, is_read, created_at)';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_notifications_type')
BEGIN
    CREATE INDEX IX_notifications_type ON notifications(notification_type);
    PRINT '✓ Created index on notifications(notification_type)';
END

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_notifications_entity')
BEGIN
    CREATE INDEX IX_notifications_entity ON notifications(related_entity_type, related_entity_id);
    PRINT '✓ Created index on notifications(related_entity_type, related_entity_id)';
END
GO

-- Create notification preferences table
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'notification_preferences')
BEGIN
    CREATE TABLE notification_preferences (
        id INT IDENTITY(1,1) PRIMARY KEY,
        user_id INT NOT NULL,
        notification_type NVARCHAR(50) NOT NULL,
        is_enabled BIT NOT NULL DEFAULT 1,
        email_enabled BIT NOT NULL DEFAULT 0,
        push_enabled BIT NOT NULL DEFAULT 1,
        created_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        updated_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        
        CONSTRAINT FK_notification_preferences_users FOREIGN KEY (user_id) REFERENCES users(id),
        CONSTRAINT UQ_notification_preferences_user_type UNIQUE (user_id, notification_type),
        CONSTRAINT CHK_notification_preferences_enabled CHECK (is_enabled IN (0, 1)),
        CONSTRAINT CHK_notification_preferences_email CHECK (email_enabled IN (0, 1)),
        CONSTRAINT CHK_notification_preferences_push CHECK (push_enabled IN (0, 1))
    );
    
    PRINT '✓ Created notification_preferences table';
END
ELSE
BEGIN
    PRINT 'ℹ Notification preferences table already exists';
END
GO

-- Create indexes for notification preferences
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_notification_preferences_user_id')
BEGIN
    CREATE INDEX IX_notification_preferences_user_id ON notification_preferences(user_id);
    PRINT '✓ Created index on notification_preferences(user_id)';
END
GO

-- Insert default notification preferences for all users
INSERT INTO notification_preferences (user_id, notification_type, is_enabled, email_enabled, push_enabled)
SELECT 
    u.id,
    n.notification_type,
    1, -- is_enabled
    CASE 
        WHEN n.notification_type IN ('JOB_ASSIGNED', 'JOB_STATUS_CHANGED', 'ASSIGNMENT_COMPLETED') THEN 1
        ELSE 0
    END, -- email_enabled
    1 -- push_enabled
FROM users u
CROSS JOIN (
    VALUES 
    ('JOB_ASSIGNED'),
    ('JOB_STATUS_CHANGED'),
    ('MATERIAL_SHORTAGE'),
    ('ASSIGNMENT_COMPLETED'),
    ('SYSTEM_ALERT'),
    ('REMINDER')
) n(notification_type)
WHERE NOT EXISTS (
    SELECT 1 FROM notification_preferences np 
    WHERE np.user_id = u.id AND np.notification_type = n.notification_type
);
GO

-- Create trigger to update updated_at timestamp
IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_notification_preferences_update')
BEGIN
    DROP TRIGGER TR_notification_preferences_update;
    PRINT '✓ Dropped existing trigger TR_notification_preferences_update';
END
GO

CREATE TRIGGER TR_notification_preferences_update
ON notification_preferences
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    UPDATE notification_preferences
    SET updated_at = GETUTCDATE()
    WHERE id IN (SELECT id FROM inserted);
END
GO

PRINT '✓ Created trigger for notification_preferences.updated_at';
GO

-- Grant permissions to application user
GRANT SELECT, INSERT, UPDATE ON notifications TO msu_app_user;
GRANT SELECT, INSERT, UPDATE ON notification_preferences TO msu_app_user;
PRINT '✓ Granted permissions to msu_app_user';
GO

-- Create stored procedure for creating notifications
IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'sp_create_notification')
BEGIN
    DROP PROCEDURE sp_create_notification;
    PRINT '✓ Dropped existing procedure sp_create_notification';
END
GO

CREATE PROCEDURE sp_create_notification
    @user_id INT,
    @title NVARCHAR(200),
    @message NVARCHAR(MAX),
    @notification_type NVARCHAR(50),
    @related_entity_type NVARCHAR(50) = NULL,
    @related_entity_id INT = NULL,
    @priority NVARCHAR(20) = 'MEDIUM',
    @action_url NVARCHAR(500) = NULL,
    @action_text NVARCHAR(100) = NULL,
    @expires_hours INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @expires_at DATETIME2 = NULL;
    
    IF @expires_hours IS NOT NULL
    BEGIN
        SET @expires_at = DATEADD(HOUR, @expires_hours, GETUTCDATE());
    END
    
    INSERT INTO notifications (
        user_id, title, message, notification_type,
        related_entity_type, related_entity_id, priority,
        action_url, action_text, expires_at
    )
    VALUES (
        @user_id, @title, @message, @notification_type,
        @related_entity_type, @related_entity_id, @priority,
        @action_url, @action_text, @expires_at
    );
    
    SELECT SCOPE_IDENTITY() AS notification_id;
END
GO

PRINT '✓ Created procedure sp_create_notification';
GO

-- Create stored procedure for getting user notifications
IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'sp_get_user_notifications')
BEGIN
    DROP PROCEDURE sp_get_user_notifications;
    PRINT '✓ Dropped existing procedure sp_get_user_notifications';
END
GO

CREATE PROCEDURE sp_get_user_notifications
    @user_id INT,
    @unread_only BIT = 0,
    @limit INT = 50,
    @offset INT = 0
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        id,
        title,
        message,
        notification_type,
        related_entity_type,
        related_entity_id,
        is_read,
        created_at,
        expires_at,
        priority,
        action_url,
        action_text,
        metadata
    FROM notifications
    WHERE user_id = @user_id
    AND is_deleted = 0
    AND (@unread_only = 0 OR is_read = 0)
    AND (expires_at IS NULL OR expires_at > GETUTCDATE())
    ORDER BY created_at DESC
    OFFSET @offset ROWS FETCH NEXT @limit ROWS ONLY;
END
GO

PRINT '✓ Created procedure sp_get_user_notifications';
GO

-- Create stored procedure for marking notifications as read
IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'sp_mark_notifications_read')
BEGIN
    DROP PROCEDURE sp_mark_notifications_read;
    PRINT '✓ Dropped existing procedure sp_mark_notifications_read';
END
GO

CREATE PROCEDURE sp_mark_notifications_read
    @user_id INT,
    @notification_ids NVARCHAR(MAX) = NULL -- Comma-separated list of notification IDs
AS
BEGIN
    SET NOCOUNT ON;
    
    IF @notification_ids IS NOT NULL
    BEGIN
        -- Mark specific notifications as read
        UPDATE notifications
        SET is_read = 1
        WHERE user_id = @user_id
        AND id IN (SELECT value FROM STRING_SPLIT(@notification_ids, ','))
        AND is_deleted = 0;
    END
    ELSE
    BEGIN
        -- Mark all notifications as read
        UPDATE notifications
        SET is_read = 1
        WHERE user_id = @user_id
        AND is_read = 0
        AND is_deleted = 0;
    END
END
GO

PRINT '✓ Created procedure sp_mark_notifications_read';
GO

-- Create stored procedure for getting unread notification count
IF EXISTS (SELECT * FROM sys.objects WHERE type = 'P' AND name = 'sp_get_unread_count')
BEGIN
    DROP PROCEDURE sp_get_unread_count;
    PRINT '✓ Dropped existing procedure sp_get_unread_count';
END
GO

CREATE PROCEDURE sp_get_unread_count
    @user_id INT
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT COUNT(*) AS unread_count
    FROM notifications
    WHERE user_id = @user_id
    AND is_read = 0
    AND is_deleted = 0
    AND (expires_at IS NULL OR expires_at > GETUTCDATE());
END
GO

PRINT '✓ Created procedure sp_get_unread_count';
GO

PRINT '=== NOTIFICATIONS SETUP COMPLETE ===';
PRINT '✓ Created notifications table with proper indexes';
PRINT '✓ Created notification_preferences table';
PRINT '✓ Created stored procedures for notification management';
PRINT '✓ Set up proper permissions for msu_app_user';
