-- Migration 004: Rename JobStatusAudit to job_status_history
-- Standardises table naming and updates schema

BEGIN TRANSACTION;

PRINT 'Starting migration 004: Rename JobStatusAudit to job_status_history';

-- Check if JobStatusAudit table exists
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'JobStatusAudit')
BEGIN
    -- Create the new job_status_history table with proper schema
    CREATE TABLE job_status_history (
        id              INT           PRIMARY KEY IDENTITY(1,1),
        job_id          INT           NOT NULL,
        from_status     VARCHAR(20)   NULL,
        to_status       VARCHAR(20)   NOT NULL,
        changed_by      INT           NOT NULL,
        changed_at      DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
        notes           NVARCHAR(500) NULL,
        CONSTRAINT FK_jsh_job_requests FOREIGN KEY (job_id) REFERENCES job_requests(id),
        CONSTRAINT FK_jsh_users        FOREIGN KEY (changed_by) REFERENCES users(id)
    );
    
    PRINT '✓ Created job_status_history table';
    
    -- Migrate data from JobStatusAudit if it exists
    IF EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('JobStatusAudit'))
    BEGIN
        INSERT INTO job_status_history (job_id, from_status, to_status, changed_by, changed_at, notes)
        SELECT 
            job_id,
            from_status,
            to_status,
            changed_by,
            changed_at,
            notes
        FROM JobStatusAudit;
        
        PRINT '✓ Migrated data from JobStatusAudit to job_status_history';
    END
    
    -- Drop the old table
    DROP TABLE JobStatusAudit;
    
    PRINT '✓ Dropped JobStatusAudit table';
END
ELSE
BEGIN
    -- Create job_status_history table if JobStatusAudit doesn't exist
    CREATE TABLE job_status_history (
        id              INT           PRIMARY KEY IDENTITY(1,1),
        job_id          INT           NOT NULL,
        from_status     VARCHAR(20)   NULL,
        to_status       VARCHAR(20)   NOT NULL,
        changed_by      INT           NOT NULL,
        changed_at      DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
        notes           NVARCHAR(500) NULL,
        CONSTRAINT FK_jsh_job_requests FOREIGN KEY (job_id) REFERENCES job_requests(id),
        CONSTRAINT FK_jsh_users        FOREIGN KEY (changed_by) REFERENCES users(id)
    );
    
    PRINT '✓ Created job_status_history table (JobStatusAudit did not exist)';
END

-- Create indexes
CREATE INDEX IX_job_status_history_job ON job_status_history(job_id, changed_at);

PRINT '✓ Created job_status_history indexes';

COMMIT TRANSACTION;

PRINT 'Migration 004 completed successfully!';
