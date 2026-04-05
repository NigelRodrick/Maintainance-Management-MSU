-- Migration 007: Add Composite Indexes
-- Adds performance-optimized composite indexes

BEGIN TRANSACTION;

PRINT 'Starting migration 007: Add Composite Indexes';

-- Composite index for job_requests: status + date_created (dashboard filters)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('job_requests') AND name = 'IX_job_requests_status_date')
BEGIN
    CREATE INDEX IX_job_requests_status_date 
    ON job_requests(status, date_created) 
    WHERE is_deleted = 0;
    PRINT '✓ Created IX_job_requests_status_date';
END

-- Composite index for job_requests: department + status (hotspot analysis)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('job_requests') AND name = 'IX_job_requests_dept_status')
BEGIN
    CREATE INDEX IX_job_requests_dept_status 
    ON job_requests(department, status) 
    WHERE is_deleted = 0;
    PRINT '✓ Created IX_job_requests_dept_status';
END

-- Composite index for assignments: worker_id + status (workload queries)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('assignments') AND name = 'IX_assignments_worker_status')
BEGIN
    CREATE INDEX IX_assignments_worker_status 
    ON assignments(worker_id, status) 
    WHERE is_deleted = 0;
    PRINT '✓ Created IX_assignments_worker_status';
END

-- Composite index for job_status_history: job_id + changed_at (audit trail)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('job_status_history') AND name = 'IX_job_status_history_job')
BEGIN
    CREATE INDEX IX_job_status_history_job 
    ON job_status_history(job_id, changed_at) 
    WHERE is_deleted = 0;
    PRINT '✓ Created IX_job_status_history_job';
END

-- Composite index for materials: job_id (foreign key optimization)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('materials') AND name = 'IX_materials_job_id')
BEGIN
    CREATE INDEX IX_materials_job_id 
    ON materials(job_id) 
    WHERE is_deleted = 0;
    PRINT '✓ Created IX_materials_job_id';
END

-- Composite index for workers: skill_category + is_active (worker availability)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE object_id = OBJECT_ID('workers') AND name = 'IX_workers_skill_active')
BEGIN
    CREATE INDEX IX_workers_skill_active 
    ON workers(skill_category, is_active) 
    WHERE is_deleted = 0;
    PRINT '✓ Created IX_workers_skill_active';
END

-- Full-text index for job_requests.description (search functionality)
IF NOT EXISTS (SELECT * FROM sys.fulltext_catalogs WHERE name = 'FT_MaintenanceSystem')
BEGIN
    CREATE FULLTEXT CATALOG FT_MaintenanceSystem AS DEFAULT;
    PRINT '✓ Created full-text catalog';
END

IF NOT EXISTS (SELECT * FROM sys.fulltext_indexes WHERE object_id = OBJECT_ID('job_requests'))
BEGIN
    CREATE FULLTEXT INDEX ON job_requests(description) 
    KEY INDEX PK__job_requests__3213E83F1A14E395
    ON FT_MaintenanceSystem
    WITH CHANGE_TRACKING AUTO;
    PRINT '✓ Created full-text index on job_requests.description';
END

-- Verify all indexes
PRINT 'All indexes on job_requests:';
SELECT 
    i.name AS index_name,
    i.type_desc,
    i.is_unique,
    i.is_primary_key,
    STRING_AGG(c.name, ', ') WITHIN GROUP (ORDER BY ic.key_ordinal) AS columns
FROM sys.indexes i
INNER JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE i.object_id = OBJECT_ID('job_requests')
GROUP BY i.name, i.type_desc, i.is_unique, i.is_primary_key
ORDER BY i.name;

COMMIT TRANSACTION;

PRINT 'Migration 007 completed successfully!';
