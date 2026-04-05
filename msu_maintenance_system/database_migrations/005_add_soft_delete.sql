-- Migration 005: Add Soft-Delete Columns
-- Adds is_deleted columns to all transaction tables

BEGIN TRANSACTION;

PRINT 'Starting migration 005: Add Soft-Delete Columns';

-- Add is_deleted column to job_requests
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('job_requests') AND name = 'is_deleted')
BEGIN
    ALTER TABLE job_requests ADD is_deleted BIT NOT NULL DEFAULT 0;
    PRINT '✓ Added is_deleted to job_requests';
END

-- Add is_deleted column to assignments
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('assignments') AND name = 'is_deleted')
BEGIN
    ALTER TABLE assignments ADD is_deleted BIT NOT NULL DEFAULT 0;
    PRINT '✓ Added is_deleted to assignments';
END

-- Add is_deleted column to materials
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('materials') AND name = 'is_deleted')
BEGIN
    ALTER TABLE materials ADD is_deleted BIT NOT NULL DEFAULT 0;
    PRINT '✓ Added is_deleted to materials';
END

-- Add is_deleted column to workers (should already exist from creation, but check)
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('workers') AND name = 'is_deleted')
BEGIN
    ALTER TABLE workers ADD is_deleted BIT NOT NULL DEFAULT 0;
    PRINT '✓ Added is_deleted to workers';
END

-- Add is_deleted column to job_status_history
IF NOT EXISTS (SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('job_status_history') AND name = 'is_deleted')
BEGIN
    ALTER TABLE job_status_history ADD is_deleted BIT NOT NULL DEFAULT 0;
    PRINT '✓ Added is_deleted to job_status_history';
END

-- Create indexes for soft-delete queries
CREATE INDEX IX_job_requests_is_deleted ON job_requests(is_deleted) WHERE is_deleted = 0;
CREATE INDEX IX_assignments_is_deleted ON assignments(is_deleted) WHERE is_deleted = 0;
CREATE INDEX IX_materials_is_deleted ON materials(is_deleted) WHERE is_deleted = 0;
CREATE INDEX IX_workers_is_deleted ON workers(is_deleted) WHERE is_deleted = 0;
CREATE INDEX IX_job_status_history_is_deleted ON job_status_history(is_deleted) WHERE is_deleted = 0;

PRINT '✓ Created soft-delete indexes';

-- Verify the changes
PRINT 'Tables with is_deleted column:';
SELECT 
    t.name AS table_name,
    c.name AS column_name,
    c.is_nullable,
    c.default_object_id
FROM sys.tables t
INNER JOIN sys.columns c ON t.object_id = c.object_id
WHERE c.name = 'is_deleted'
AND t.name IN ('job_requests', 'assignments', 'materials', 'workers', 'job_status_history')
ORDER BY t.name;

COMMIT TRANSACTION;

PRINT 'Migration 005 completed successfully!';
