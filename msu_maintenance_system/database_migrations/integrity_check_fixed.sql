-- Modified Integrity Check Script
-- Validates all database migrations and constraints
-- Handles missing is_deleted columns gracefully

PRINT 'Starting Database Integrity Check';
PRINT '================================';

-- Check if is_deleted column exists in materials table
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'materials' AND COLUMN_NAME = 'is_deleted')
BEGIN
    PRINT 'Check 1: Orphaned materials records (job_id NOT NULL)';
    SELECT 
        COUNT(*) AS orphaned_materials_count
    FROM materials m
    LEFT JOIN job_requests j ON m.job_id = j.id
    WHERE j.id IS NULL
    AND m.is_deleted = 0;
END
ELSE
BEGIN
    PRINT 'Check 1: Orphaned materials records (job_id NOT NULL) - is_deleted column not found';
    SELECT 
        COUNT(*) AS orphaned_materials_count
    FROM materials m
    LEFT JOIN job_requests j ON m.job_id = j.id
    WHERE j.id IS NULL;
END

-- Check if is_deleted column exists in job_requests table
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'job_requests' AND COLUMN_NAME = 'is_deleted')
BEGIN
    PRINT 'Check 2: Orphaned job_requests (submitted_by NOT NULL)';
    SELECT 
        COUNT(*) AS orphaned_job_requests_count
    FROM job_requests jr
    LEFT JOIN users u ON jr.submitted_by = u.id
    WHERE u.id IS NULL
    AND jr.is_deleted = 0;
END
ELSE
BEGIN
    PRINT 'Check 2: Orphaned job_requests (submitted_by NOT NULL) - is_deleted column not found';
    SELECT 
        COUNT(*) AS orphaned_job_requests_count
    FROM job_requests jr
    LEFT JOIN users u ON jr.submitted_by = u.id
    WHERE u.id IS NULL;
END

-- Check 3: Verify status values are standardised
PRINT 'Check 3: Non-standard status values in job_requests';
SELECT 
    COUNT(*) AS non_standard_status_count
FROM job_requests 
WHERE status NOT IN ('PENDING','IN_PROGRESS','COMPLETED','CANCELLED');

-- Check 4: Verify role values are standardised
PRINT 'Check 4: Non-standard role values in users';
SELECT 
    COUNT(*) AS non_standard_role_count
FROM users 
WHERE role NOT IN ('admin','supervisor','staff','maintenance');

-- Check 5: Verify no orphaned assignments
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'assignments' AND COLUMN_NAME = 'is_deleted')
BEGIN
    PRINT 'Check 5: Orphaned assignments (job_id NOT NULL)';
    SELECT 
        COUNT(*) AS orphaned_assignments_count
    FROM assignments a
    LEFT JOIN job_requests j ON a.job_id = j.id
    WHERE j.id IS NULL
    AND a.is_deleted = 0;
END
ELSE
BEGIN
    PRINT 'Check 5: Orphaned assignments (job_id NOT NULL) - is_deleted column not found';
    SELECT 
        COUNT(*) AS orphaned_assignments_count
    FROM assignments a
    LEFT JOIN job_requests j ON a.job_id = j.id
    WHERE j.id IS NULL;
END

-- Check 6: Verify no orphaned workers
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'workers' AND COLUMN_NAME = 'is_deleted')
BEGIN
    PRINT 'Check 6: Orphaned workers (user_id NOT NULL)';
    SELECT 
        COUNT(*) AS orphaned_workers_count
    FROM workers w
    LEFT JOIN users u ON w.user_id = u.id
    WHERE u.id IS NULL
    AND w.is_deleted = 0;
END
ELSE
BEGIN
    PRINT 'Check 6: Orphaned workers (user_id NOT NULL) - is_deleted column not found';
    SELECT 
        COUNT(*) AS orphaned_workers_count
    FROM workers w
    LEFT JOIN users u ON w.user_id = u.id
    WHERE u.id IS NULL;
END

-- Check 7: Verify no orphaned job_status_history
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'job_status_history' AND COLUMN_NAME = 'is_deleted')
BEGIN
    PRINT 'Check 7: Orphaned job_status_history (job_id NOT NULL)';
    SELECT 
        COUNT(*) AS orphaned_status_history_count
    FROM job_status_history jsh
    LEFT JOIN job_requests j ON jsh.job_id = j.id
    WHERE j.id IS NULL
    AND jsh.is_deleted = 0;
END
ELSE
BEGIN
    PRINT 'Check 7: Orphaned job_status_history (job_id NOT NULL) - is_deleted column not found';
    SELECT 
        COUNT(*) AS orphaned_status_history_count
    FROM job_status_history jsh
    LEFT JOIN job_requests j ON jsh.job_id = j.id
    WHERE j.id IS NULL;
END

-- Check 8: DBCC CHECKCONSTRAINTS
PRINT 'Check 8: DBCC CHECKCONSTRAINTS';
DBCC CHECKCONSTRAINTS WITH NO_INFOMSGS;

-- Check 9: DBCC CHECKDB
PRINT 'Check 9: DBCC CHECKDB';
DBCC CHECKDB WITH NO_INFOMSGS;

PRINT 'Database Integrity Check Completed';
PRINT '================================';

-- Summary report
PRINT 'INTEGRITY CHECK SUMMARY:';
PRINT 'All counts should be 0 for clean database';
PRINT 'DBCC CHECKCONSTRAINTS should report no violations';
PRINT 'DBCC CHECKDB should report no errors';
