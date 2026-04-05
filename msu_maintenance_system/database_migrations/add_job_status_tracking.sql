-- Database Migration: Add Job Status Tracking
-- MSU Maintenance System
-- Created: 2024-03-29

-- =====================================================
-- 1. Update JobRequests table to support proper status tracking
-- =====================================================

-- Add updated_at column if it doesn't exist
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'JobRequests' AND COLUMN_NAME = 'updated_at')
BEGIN
    ALTER TABLE JobRequests 
    ADD updated_at DATETIME DEFAULT GETDATE();
    PRINT 'Added updated_at column to JobRequests table';
END
ELSE
BEGIN
    PRINT 'updated_at column already exists in JobRequests table';
END

-- Update existing records to have updated_at = date_created where updated_at is NULL
UPDATE JobRequests 
SET updated_at = date_created 
WHERE updated_at IS NULL;

-- Ensure the default value is set for future inserts
ALTER TABLE JobRequests 
ADD CONSTRAINT DF_JobRequests_updated_at DEFAULT GETDATE() FOR updated_at;

-- =====================================================
-- 2. Create JobStatusAudit table for tracking status changes
-- =====================================================

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES 
               WHERE TABLE_NAME = 'JobStatusAudit')
BEGIN
    CREATE TABLE JobStatusAudit (
        id INT PRIMARY KEY IDENTITY(1,1),
        job_id INT NOT NULL,
        old_status VARCHAR(20) NULL,
        new_status VARCHAR(20) NOT NULL,
        updated_by INT NOT NULL,
        timestamp DATETIME DEFAULT GETDATE(),
        notes VARCHAR(500) NULL,
        
        -- Foreign key constraint
        CONSTRAINT FK_JobStatusAudit_JobRequests 
            FOREIGN KEY (job_id) REFERENCES JobRequests(id) ON DELETE CASCADE,
        
        -- Foreign key to Users table
        CONSTRAINT FK_JobStatusAudit_Users 
            FOREIGN KEY (updated_by) REFERENCES Users(id)
    );
    
    -- Create indexes for better performance
    CREATE INDEX IX_JobStatusAudit_job_id ON JobStatusAudit(job_id);
    CREATE INDEX IX_JobStatusAudit_timestamp ON JobStatusAudit(timestamp);
    CREATE INDEX IX_JobStatusAudit_updated_by ON JobStatusAudit(updated_by);
    
    PRINT 'Created JobStatusAudit table with indexes';
END
ELSE
BEGIN
    PRINT 'JobStatusAudit table already exists';
END

-- =====================================================
-- 3. Add check constraint for valid status values
-- =====================================================

-- Drop existing check constraint if it exists
IF EXISTS (SELECT * FROM sys.check_constraints 
           WHERE name = 'CK_JobRequests_status')
BEGIN
    ALTER TABLE JobRequests DROP CONSTRAINT CK_JobRequests_status;
    PRINT 'Dropped existing CK_JobRequests_status constraint';
END

-- Add new check constraint for valid status values
ALTER TABLE JobRequests 
ADD CONSTRAINT CK_JobRequests_status 
CHECK (status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED'));

PRINT 'Added CK_JobRequests_status constraint';

-- =====================================================
-- 4. Update existing status values to match new format
-- =====================================================

-- Standardize existing status values to uppercase
UPDATE JobRequests 
SET status = 'PENDING' 
WHERE status IN ('Pending', 'pending', 'PENDING');

UPDATE JobRequests 
SET status = 'IN_PROGRESS' 
WHERE status IN ('In Progress', 'In Progress', 'IN_PROGRESS', 'in progress');

UPDATE JobRequests 
SET status = 'COMPLETED' 
WHERE status IN ('Completed', 'completed', 'COMPLETED');

PRINT 'Standardized existing status values';

-- =====================================================
-- 5. Create trigger to automatically update updated_at
-- =====================================================

-- Drop existing trigger if it exists
IF EXISTS (SELECT * FROM sys.triggers WHERE name = 'TR_JobRequests_update_timestamp')
BEGIN
    DROP TRIGGER TR_JobRequests_update_timestamp;
    PRINT 'Dropped existing TR_JobRequests_update_timestamp trigger';
END

-- Create new trigger
CREATE TRIGGER TR_JobRequests_update_timestamp
ON JobRequests
AFTER UPDATE
AS
BEGIN
    -- Prevent recursive updates
    IF NOT UPDATE(updated_at)
    BEGIN
        UPDATE JobRequests
        SET updated_at = GETDATE()
        FROM JobRequests jr
        INNER JOIN inserted i ON jr.id = i.id
        WHERE jr.id = i.id;
    END
END;

PRINT 'Created TR_JobRequests_update_timestamp trigger';

-- =====================================================
-- 6. Create view for job status summary
-- =====================================================

IF EXISTS (SELECT * FROM sys.views WHERE name = 'VW_JobStatusSummary')
BEGIN
    DROP VIEW VW_JobStatusSummary;
    PRINT 'Dropped existing VW_JobStatusSummary view';
END

CREATE VIEW VW_JobStatusSummary AS
SELECT 
    status,
    COUNT(*) as job_count,
    CAST(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM JobRequests) AS DECIMAL(5,2)) as percentage,
    MIN(date_created) as earliest_job,
    MAX(date_created) as latest_job
FROM JobRequests
GROUP BY status;

PRINT 'Created VW_JobStatusSummary view';

-- =====================================================
-- 7. Create stored procedures for common operations
-- =====================================================

-- Procedure to get job status history
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'SP_GetJobStatusHistory')
BEGIN
    DROP PROCEDURE SP_GetJobStatusHistory;
    PRINT 'Dropped existing SP_GetJobStatusHistory procedure';
END

CREATE PROCEDURE SP_GetJobStatusHistory
    @job_id INT
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        jsa.id,
        jsa.old_status,
        jsa.new_status,
        jsa.updated_by,
        u.email as updated_by_email,
        u.role as updated_by_role,
        jsa.timestamp,
        jsa.notes
    FROM JobStatusAudit jsa
    LEFT JOIN Users u ON jsa.updated_by = u.id
    WHERE jsa.job_id = @job_id
    ORDER BY jsa.timestamp DESC;
END;

PRINT 'Created SP_GetJobStatusHistory procedure';

-- Procedure to update job status with audit
IF EXISTS (SELECT * FROM sys.procedures WHERE name = 'SP_UpdateJobStatus')
BEGIN
    DROP PROCEDURE SP_UpdateJobStatus;
    PRINT 'Dropped existing SP_UpdateJobStatus procedure';
END

CREATE PROCEDURE SP_UpdateJobStatus
    @job_id INT,
    @new_status VARCHAR(20),
    @updated_by INT,
    @notes VARCHAR(500) = NULL
AS
BEGIN
    SET NOCOUNT ON;
    DECLARE @old_status VARCHAR(20);
    DECLARE @update_count INT;
    
    BEGIN TRY
        BEGIN TRANSACTION;
        
        -- Get current status
        SELECT @old_status = status FROM JobRequests WHERE id = @job_id;
        
        IF @old_status IS NULL
        BEGIN
            RAISERROR('Job not found', 16, 1);
            RETURN;
        END
        
        -- Update job status
        UPDATE JobRequests 
        SET status = @new_status, updated_at = GETDATE()
        WHERE id = @job_id;
        
        SET @update_count = @@ROWCOUNT;
        
        -- Log the change
        INSERT INTO JobStatusAudit (job_id, old_status, new_status, updated_by, timestamp, notes)
        VALUES (@job_id, @old_status, @new_status, @updated_by, GETDATE(), @notes);
        
        COMMIT TRANSACTION;
        
        SELECT @update_count as records_updated, @old_status as old_status, @new_status as new_status;
        
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
            
        DECLARE @error_message NVARCHAR(4000) = ERROR_MESSAGE();
        RAISERROR(@error_message, 16, 1);
    END CATCH;
END;

PRINT 'Created SP_UpdateJobStatus procedure';

-- =====================================================
-- 8. Verify migration completion
-- =====================================================

PRINT '=== Migration Summary ===';
PRINT '1. JobRequests table updated with updated_at column';
PRINT '2. JobStatusAudit table created for audit trail';
PRINT '3. Status validation constraints added';
PRINT '4. Existing status values standardized';
PRINT '5. Automatic timestamp trigger created';
PRINT '6. Status summary view created';
PRINT '7. Stored procedures created';
PRINT '=== Migration completed successfully ===';

-- Show current status distribution
SELECT 
    status,
    COUNT(*) as count,
    'Current status distribution' as note
FROM JobRequests
GROUP BY status
ORDER BY status;
