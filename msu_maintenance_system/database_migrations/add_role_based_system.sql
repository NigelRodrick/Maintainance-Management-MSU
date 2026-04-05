-- Database Migration: Add Role-Based System
-- MSU Maintenance System
-- Created: 2024-03-29

-- =====================================================
-- 1. Update Users table to include role
-- =====================================================

-- Add role column if it doesn't exist
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'Users' AND COLUMN_NAME = 'role')
BEGIN
    ALTER TABLE Users 
    ADD role VARCHAR(20) NOT NULL DEFAULT 'USER';
    PRINT 'Added role column to Users table';
END
ELSE
BEGIN
    PRINT 'role column already exists in Users table';
END

-- Add check constraint for valid roles
IF NOT EXISTS (SELECT * FROM sys.check_constraints 
           WHERE name = 'CK_Users_role')
BEGIN
    ALTER TABLE Users 
    ADD CONSTRAINT CK_Users_role 
    CHECK (role IN ('ADMIN', 'SUPERVISOR', 'USER'));
    PRINT 'Added CK_Users_role constraint';
END
ELSE
BEGIN
    PRINT 'CK_Users_role constraint already exists';
END

-- Update existing users to have USER role by default
UPDATE Users 
SET role = 'USER' 
WHERE role IS NULL OR role NOT IN ('ADMIN', 'SUPERVISOR', 'USER');

-- =====================================================
-- 2. Add submitted_by column to JobRequests for user tracking
-- =====================================================

-- Add submitted_by column if it doesn't exist
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'JobRequests' AND COLUMN_NAME = 'submitted_by')
BEGIN
    ALTER TABLE JobRequests 
    ADD submitted_by INT NULL;
    PRINT 'Added submitted_by column to JobRequests table';
END
ELSE
BEGIN
    PRINT 'submitted_by column already exists in JobRequests table';
END

-- Add foreign key constraint for submitted_by
IF NOT EXISTS (SELECT * FROM sys.foreign_keys 
           WHERE name = 'FK_JobRequests_Users_submitted_by')
BEGIN
    ALTER TABLE JobRequests 
    ADD CONSTRAINT FK_JobRequests_Users_submitted_by 
        FOREIGN KEY (submitted_by) REFERENCES Users(id);
    PRINT 'Added FK_JobRequests_Users_submitted_by constraint';
END
ELSE
BEGIN
    PRINT 'FK_JobRequests_Users_submitted_by constraint already exists';
END

-- =====================================================
-- 3. Create UserActivityLog table for audit trail
-- =====================================================

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES 
               WHERE TABLE_NAME = 'UserActivityLog')
BEGIN
    CREATE TABLE UserActivityLog (
        id INT PRIMARY KEY IDENTITY(1,1),
        user_id INT NOT NULL,
        action VARCHAR(100) NOT NULL,
        resource_type VARCHAR(50) NULL,  -- 'job', 'user', 'report', etc.
        resource_id INT NULL,
        ip_address VARCHAR(45) NULL,
        user_agent VARCHAR(500) NULL,
        timestamp DATETIME DEFAULT GETDATE(),
        details VARCHAR(1000) NULL,
        
        -- Foreign key constraints
        CONSTRAINT FK_UserActivityLog_Users 
            FOREIGN KEY (user_id) REFERENCES Users(id)
    );
    
    -- Create indexes for better performance
    CREATE INDEX IX_UserActivityLog_user_id ON UserActivityLog(user_id);
    CREATE INDEX IX_UserActivityLog_timestamp ON UserActivityLog(timestamp);
    CREATE INDEX IX_UserActivityLog_action ON UserActivityLog(action);
    
    PRINT 'Created UserActivityLog table with indexes';
END
ELSE
BEGIN
    PRINT 'UserActivityLog table already exists';
END

-- =====================================================
-- 4. Create views for role-based access
-- =====================================================

-- Admin view - all data
IF EXISTS (SELECT * FROM sys.views WHERE name = 'VW_AdminDashboard')
BEGIN
    DROP VIEW VW_AdminDashboard;
    PRINT 'Dropped existing VW_AdminDashboard view';
END

CREATE VIEW VW_AdminDashboard AS
SELECT 
    u.id as user_id,
    u.email,
    u.role,
    COUNT(jr.id) as total_jobs,
    SUM(CASE WHEN jr.status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_jobs,
    SUM(CASE WHEN jr.status = 'PENDING' THEN 1 ELSE 0 END) as pending_jobs,
    SUM(CASE WHEN jr.status = 'IN_PROGRESS' THEN 1 ELSE 0 END) as in_progress_jobs,
    MAX(jr.date_created) as last_activity
FROM Users u
LEFT JOIN JobRequests jr ON u.id = jr.submitted_by
GROUP BY u.id, u.email, u.role;

PRINT 'Created VW_AdminDashboard view';

-- Supervisor view - jobs and metrics
IF EXISTS (SELECT * FROM sys.views WHERE name = 'VW_SupervisorDashboard')
BEGIN
    DROP VIEW VW_SupervisorDashboard;
    PRINT 'Dropped existing VW_SupervisorDashboard view';
END

CREATE VIEW VW_SupervisorDashboard AS
SELECT 
    jr.id,
    jr.department,
    jr.description,
    jr.category,
    jr.priority,
    jr.status,
    jr.date_created,
    jr.updated_at,
    jr.submitted_by,
    u.email as submitted_by_email,
    a.worker_name,
    a.start_time as assigned_time,
    a.end_time as completion_time
FROM JobRequests jr
LEFT JOIN Users u ON jr.submitted_by = u.id
LEFT JOIN Assignments a ON jr.id = a.job_id
ORDER BY jr.date_created DESC;

PRINT 'Created VW_SupervisorDashboard view';

-- User view - own jobs only
IF EXISTS (SELECT * FROM sys.views WHERE name = 'VW_UserDashboard')
BEGIN
    DROP VIEW VW_UserDashboard;
    PRINT 'Dropped existing VW_UserDashboard view';
END

CREATE VIEW VW_UserDashboard AS
SELECT 
    jr.id,
    jr.department,
    jr.description,
    jr.category,
    jr.priority,
    jr.status,
    jr.date_created,
    jr.updated_at,
    a.worker_name,
    a.start_time as assigned_time,
    a.end_time as completion_time
FROM JobRequests jr
LEFT JOIN Assignments a ON jr.id = a.job_id
WHERE jr.submitted_by = @user_id  -- Parameter will be set in application
ORDER BY jr.date_created DESC;

PRINT 'Created VW_UserDashboard view';

-- =====================================================
-- 5. Create stored procedures for role operations
-- =====================================================

-- Procedure to get user dashboard data
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'SP_GetUserDashboard')
BEGIN
    DROP PROCEDURE SP_GetUserDashboard;
    PRINT 'Dropped existing SP_GetUserDashboard procedure';
END

CREATE PROCEDURE SP_GetUserDashboard
    @user_id INT
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        jr.id,
        jr.department,
        jr.description,
        jr.category,
        jr.priority,
        jr.status,
        jr.date_created,
        jr.updated_at,
        a.worker_name,
        a.start_time as assigned_time,
        a.end_time as completion_time
    FROM JobRequests jr
    LEFT JOIN Assignments a ON jr.id = a.job_id
    WHERE jr.submitted_by = @user_id
    ORDER BY jr.date_created DESC;
END;

PRINT 'Created SP_GetUserDashboard procedure';

-- Procedure to log user activity
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'SP_LogUserActivity')
BEGIN
    DROP PROCEDURE SP_LogUserActivity;
    PRINT 'Dropped existing SP_LogUserActivity procedure';
END

CREATE PROCEDURE SP_LogUserActivity
    @user_id INT,
    @action VARCHAR(100),
    @resource_type VARCHAR(50) = NULL,
    @resource_id INT = NULL,
    @ip_address VARCHAR(45) = NULL,
    @user_agent VARCHAR(500) = NULL,
    @details VARCHAR(1000) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    INSERT INTO UserActivityLog (user_id, action, resource_type, resource_id, 
                              ip_address, user_agent, timestamp, details)
    VALUES (@user_id, @action, @resource_type, @resource_id, 
            @ip_address, @user_agent, GETDATE(), @details);
END;

PRINT 'Created SP_LogUserActivity procedure';

-- Procedure to get role-based metrics
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'SP_GetRoleMetrics')
BEGIN
    DROP PROCEDURE SP_GetRoleMetrics;
    PRINT 'Dropped existing SP_GetRoleMetrics procedure';
END

CREATE PROCEDURE SP_GetRoleMetrics
    @role VARCHAR(20) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    IF @role = 'ADMIN'
    BEGIN
        SELECT 
            (SELECT COUNT(*) FROM Users) as total_users,
            (SELECT COUNT(*) FROM Users WHERE role = 'ADMIN') as admin_users,
            (SELECT COUNT(*) FROM Users WHERE role = 'SUPERVISOR') as supervisor_users,
            (SELECT COUNT(*) FROM Users WHERE role = 'USER') as regular_users,
            (SELECT COUNT(*) FROM JobRequests) as total_jobs,
            (SELECT COUNT(*) FROM JobRequests WHERE status = 'COMPLETED') as completed_jobs,
            (SELECT COUNT(*) FROM UserActivityLog WHERE timestamp >= DATEADD(day, -7, GETDATE())) as recent_activities
    END
    ELSE IF @role = 'SUPERVISOR'
    BEGIN
        SELECT 
            COUNT(*) as total_jobs,
            SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending_jobs,
            SUM(CASE WHEN status = 'IN_PROGRESS' THEN 1 ELSE 0 END) as in_progress_jobs,
            SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_jobs,
            AVG(DATEDIFF(hour, date_created, 
                COALESCE(updated_at, GETDATE()))) as avg_processing_hours
        FROM JobRequests
    END
    ELSE IF @role = 'USER'
    BEGIN
        SELECT 
            COUNT(*) as total_submissions,
            SUM(CASE WHEN status = 'PENDING' THEN 1 ELSE 0 END) as pending_submissions,
            SUM(CASE WHEN status = 'IN_PROGRESS' THEN 1 ELSE 0 END) as in_progress_submissions,
            SUM(CASE WHEN status = 'COMPLETED' THEN 1 ELSE 0 END) as completed_submissions
        FROM JobRequests
        WHERE submitted_by = @user_id
    END
END;

PRINT 'Created SP_GetRoleMetrics procedure';

-- =====================================================
-- 6. Create indexes for performance
-- =====================================================

-- Index for submitted_by lookups
IF NOT EXISTS (SELECT * FROM sys.indexes 
           WHERE name = 'IX_JobRequests_submitted_by' AND object_id = OBJECT_ID('JobRequests'))
BEGIN
    CREATE INDEX IX_JobRequests_submitted_by ON JobRequests(submitted_by);
    PRINT 'Created IX_JobRequests_submitted_by index';
END

-- Composite index for user activity queries
IF NOT EXISTS (SELECT * FROM sys.indexes 
           WHERE name = 'IX_UserActivityLog_user_timestamp' AND object_id = OBJECT_ID('UserActivityLog'))
BEGIN
    CREATE INDEX IX_UserActivityLog_user_timestamp ON UserActivityLog(user_id, timestamp);
    PRINT 'Created IX_UserActivityLog_user_timestamp index';
END

-- =====================================================
-- 7. Insert default admin user if none exists
-- =====================================================

IF NOT EXISTS (SELECT * FROM Users WHERE role = 'ADMIN')
BEGIN
    -- Insert default admin user (password should be changed immediately)
    INSERT INTO Users (email, role, password) 
    VALUES ('admin@msu.ac.zw', 'ADMIN', '$2b$12$placeholder_hash_change_me')
    
    PRINT 'Created default admin user - CHANGE PASSWORD IMMEDIATELY';
END
ELSE
BEGIN
    PRINT 'Admin user already exists';
END

-- =====================================================
-- 8. Verify migration completion
-- =====================================================

PRINT '=== Migration Summary ===';
PRINT '1. Added role column to Users table';
PRINT '2. Added submitted_by column to JobRequests table';
PRINT '3. Created UserActivityLog audit table';
PRINT '4. Created role-based dashboard views';
PRINT '5. Created stored procedures for role operations';
PRINT '6. Added performance indexes';
PRINT '7. Created default admin user if needed';
PRINT '=== Migration completed successfully ===';

-- Show current role distribution
SELECT 
    role,
    COUNT(*) as user_count,
    'Current role distribution' as note
FROM Users
GROUP BY role
ORDER BY user_count DESC;
