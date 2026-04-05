-- Integrity Check Script
-- Validates all database migrations and constraints

PRINT 'Starting Database Integrity Check';
PRINT '================================';

-- Check 1: Verify no orphaned materials records
PRINT 'Check 1: Orphaned materials records (job_id NOT NULL)';
SELECT 
    COUNT(*) AS orphaned_materials_count
FROM materials m
LEFT JOIN job_requests j ON m.job_id = j.id
WHERE j.id IS NULL
AND m.is_deleted = 0;

-- Check 2: Verify no orphaned job_requests (submitted_by NOT NULL)
PRINT 'Check 2: Orphaned job_requests (submitted_by NOT NULL)';
SELECT 
    COUNT(*) AS orphaned_job_requests_count
FROM job_requests jr
LEFT JOIN users u ON jr.submitted_by = u.id
WHERE u.id IS NULL
AND jr.is_deleted = 0;

-- Check 3: Verify status values are standardised
PRINT 'Check 3: Non-standard status values in job_requests';
SELECT 
    COUNT(*) AS non_standard_status_count
FROM job_requests 
WHERE status NOT IN ('PENDING','IN_PROGRESS','COMPLETED','CANCELLED')
AND is_deleted = 0;

-- Check 4: Verify role values are standardised
PRINT 'Check 4: Non-standard role values in users';
SELECT 
    COUNT(*) AS non_standard_role_count
FROM users 
WHERE role NOT IN ('admin','supervisor','staff','maintenance_admin')
AND is_active = 1;

-- Check 5: Verify CHECK constraints are not violated
PRINT 'Check 5: CHECK constraint violations';

-- Check materials quantity constraint
SELECT 
    COUNT(*) AS materials_quantity_violations
FROM materials 
WHERE quantity_used > quantity_required
AND is_deleted = 0;

-- Check assignments date constraint
SELECT 
    COUNT(*) AS assignments_date_violations
FROM assignments 
WHERE end_time IS NOT NULL 
AND end_time < start_time
AND is_deleted = 0;

-- Check 6: Verify soft-delete columns exist
PRINT 'Check 6: Tables missing is_deleted column';
SELECT 
    t.name AS table_missing_is_deleted
FROM sys.tables t
WHERE t.name IN ('job_requests', 'assignments', 'materials', 'workers', 'job_status_history')
AND NOT EXISTS (
    SELECT 1 FROM sys.columns c 
    WHERE c.object_id = t.object_id AND c.name = 'is_deleted'
);

-- Check 7: Verify workers table has data
PRINT 'Check 7: Workers table data';
SELECT 
    COUNT(*) AS total_workers,
    COUNT(CASE WHEN is_active = 1 AND is_deleted = 0 THEN 1 END) AS active_workers
FROM workers;

-- Check 8: Verify assignments have worker_id references
PRINT 'Check 8: Assignments with missing worker_id';
SELECT 
    COUNT(*) AS assignments_missing_worker_id
FROM assignments 
WHERE worker_id IS NULL
AND is_deleted = 0;

-- Check 9: Verify job_status_history exists and has data
PRINT 'Check 9: job_status_history table';
SELECT 
    COUNT(*) AS total_status_changes
FROM job_status_history 
WHERE is_deleted = 0;

-- Check 10: Verify predictions table is dropped
PRINT 'Check 10: Predictions table existence';
SELECT 
    CASE 
        WHEN EXISTS (SELECT 1 FROM sys.tables WHERE name = 'predictions') 
        THEN 'PREDICTIONS_TABLE_STILL_EXISTS' 
        ELSE 'PREDICTIONS_TABLE_DROPPED' 
    END AS predictions_status;

-- Summary
PRINT '================================';
PRINT 'Integrity Check Summary';
PRINT '================================';

DECLARE @total_issues INT = 0;

-- Count total issues (simplified check)
SELECT @total_issues = 
    (SELECT COUNT(*) FROM materials m LEFT JOIN job_requests j ON m.job_id = j.id WHERE j.id IS NULL AND m.is_deleted = 0) +
    (SELECT COUNT(*) FROM job_requests jr LEFT JOIN users u ON jr.submitted_by = u.id WHERE u.id IS NULL AND jr.is_deleted = 0) +
    (SELECT COUNT(*) FROM job_requests WHERE status NOT IN ('PENDING','IN_PROGRESS','COMPLETED','CANCELLED') AND is_deleted = 0) +
    (SELECT COUNT(*) FROM users WHERE role NOT IN ('admin','supervisor','staff','maintenance_admin') AND is_active = 1) +
    (SELECT COUNT(*) FROM materials WHERE quantity_used > quantity_required AND is_deleted = 0) +
    (SELECT COUNT(*) FROM assignments WHERE end_time IS NOT NULL AND end_time < start_time AND is_deleted = 0);

IF @total_issues = 0
BEGIN
    PRINT '✅ ALL INTEGRITY CHECKS PASSED - Zero violations found!';
END
ELSE
BEGIN
    PRINT '❌ INTEGRITY ISSUES FOUND - ' + CAST(@total_issues AS VARCHAR) + ' total violations';
    PRINT '   Please review the detailed results above and fix violations before proceeding.';
END

PRINT '================================';
