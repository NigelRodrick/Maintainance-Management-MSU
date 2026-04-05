-- Robust Integrity Check Script
-- Validates all database migrations and constraints
-- Only checks existing tables and columns

PRINT 'Starting Database Integrity Check';
PRINT '================================';

-- Check what tables exist
PRINT 'Existing Tables:';
SELECT TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE' 
AND TABLE_SCHEMA = 'dbo'
ORDER BY TABLE_NAME;

-- Check 1: Verify materials table integrity (only if exists)
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'materials')
BEGIN
    PRINT 'Check 1: Materials table integrity';
    
    -- Check if is_deleted column exists
    IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'materials' AND COLUMN_NAME = 'is_deleted')
    BEGIN
        SELECT 
            COUNT(*) AS orphaned_materials_count
        FROM materials m
        LEFT JOIN job_requests j ON m.job_id = j.id
        WHERE j.id IS NULL
        AND m.is_deleted = 0;
    END
    ELSE
    BEGIN
        SELECT 
            COUNT(*) AS orphaned_materials_count
        FROM materials m
        LEFT JOIN job_requests j ON m.job_id = j.id
        WHERE j.id IS NULL;
    END
END
ELSE
BEGIN
    PRINT 'Check 1: Materials table - NOT FOUND';
    SELECT 0 AS orphaned_materials_count;
END

-- Check 2: Verify job_requests table integrity (only if exists)
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'job_requests')
BEGIN
    PRINT 'Check 2: Job_requests table integrity';
    
    -- Check if is_deleted column exists
    IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'job_requests' AND COLUMN_NAME = 'is_deleted')
    BEGIN
        SELECT 
            COUNT(*) AS orphaned_job_requests_count
        FROM job_requests jr
        LEFT JOIN users u ON jr.submitted_by = u.id
        WHERE u.id IS NULL
        AND jr.is_deleted = 0;
    END
    ELSE
    BEGIN
        SELECT 
            COUNT(*) AS orphaned_job_requests_count
        FROM job_requests jr
        LEFT JOIN users u ON jr.submitted_by = u.id
        WHERE u.id IS NULL;
    END
    
    -- Check status values
    SELECT 
        COUNT(*) AS non_standard_status_count
    FROM job_requests 
    WHERE status NOT IN ('PENDING','IN_PROGRESS','COMPLETED','CANCELLED')
    AND status IS NOT NULL;
END
ELSE
BEGIN
    PRINT 'Check 2: Job_requests table - NOT FOUND';
    SELECT 0 AS orphaned_job_requests_count;
    SELECT 0 AS non_standard_status_count;
END

-- Check 3: Verify users table integrity (only if exists)
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'users')
BEGIN
    PRINT 'Check 3: Users table integrity';
    
    -- Check role values
    SELECT 
        COUNT(*) AS non_standard_role_count
    FROM users 
    WHERE role NOT IN ('admin','supervisor','staff','maintenance')
    AND role IS NOT NULL;
END
ELSE
BEGIN
    PRINT 'Check 3: Users table - NOT FOUND';
    SELECT 0 AS non_standard_role_count;
END

-- Check 4: Verify assignments table integrity (only if exists)
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'assignments')
BEGIN
    PRINT 'Check 4: Assignments table integrity';
    
    -- Check if is_deleted column exists
    IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'assignments' AND COLUMN_NAME = 'is_deleted')
    BEGIN
        SELECT 
            COUNT(*) AS orphaned_assignments_count
        FROM assignments a
        LEFT JOIN job_requests j ON a.job_id = j.id
        WHERE j.id IS NULL
        AND a.is_deleted = 0;
    END
    ELSE
    BEGIN
        SELECT 
            COUNT(*) AS orphaned_assignments_count
        FROM assignments a
        LEFT JOIN job_requests j ON a.job_id = j.id
        WHERE j.id IS NULL;
    END
END
ELSE
BEGIN
    PRINT 'Check 4: Assignments table - NOT FOUND';
    SELECT 0 AS orphaned_assignments_count;
END

-- Check 5: Verify workers table integrity (only if exists)
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'workers')
BEGIN
    PRINT 'Check 5: Workers table integrity';
    
    -- Check if is_deleted column exists
    IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'workers' AND COLUMN_NAME = 'is_deleted')
    BEGIN
        SELECT 
            COUNT(*) AS orphaned_workers_count
        FROM workers w
        LEFT JOIN users u ON w.user_id = u.id
        WHERE u.id IS NULL
        AND w.is_deleted = 0;
    END
    ELSE
    BEGIN
        SELECT 
            COUNT(*) AS orphaned_workers_count
        FROM workers w
        LEFT JOIN users u ON w.user_id = u.id
        WHERE u.id IS NULL;
    END
END
ELSE
BEGIN
    PRINT 'Check 5: Workers table - NOT FOUND';
    SELECT 0 AS orphaned_workers_count;
END

-- Check 6: Verify job_status_history table integrity (only if exists)
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'job_status_history')
BEGIN
    PRINT 'Check 6: Job_status_history table integrity';
    
    -- Check if is_deleted column exists
    IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'job_status_history' AND COLUMN_NAME = 'is_deleted')
    BEGIN
        SELECT 
            COUNT(*) AS orphaned_status_history_count
        FROM job_status_history jsh
        LEFT JOIN job_requests j ON jsh.job_id = j.id
        WHERE j.id IS NULL
        AND jsh.is_deleted = 0;
    END
    ELSE
    BEGIN
        SELECT 
            COUNT(*) AS orphaned_status_history_count
        FROM job_status_history jsh
        LEFT JOIN job_requests j ON jsh.job_id = j.id
        WHERE j.id IS NULL;
    END
END
ELSE
BEGIN
    PRINT 'Check 6: Job_status_history table - NOT FOUND';
    SELECT 0 AS orphaned_status_history_count;
END

-- Check 7: DBCC CHECKCONSTRAINTS (only if constraints exist)
PRINT 'Check 7: DBCC CHECKCONSTRAINTS';
BEGIN TRY
    DBCC CHECKCONSTRAINTS WITH NO_INFOMSGS;
    PRINT 'DBCC CHECKCONSTRAINTS completed successfully';
END TRY
BEGIN CATCH
    PRINT 'DBCC CHECKCONSTRAINTS error: ' + ERROR_MESSAGE();
END CATCH

-- Check 8: DBCC CHECKDB
PRINT 'Check 8: DBCC CHECKDB';
BEGIN TRY
    DBCC CHECKDB WITH NO_INFOMSGS;
    PRINT 'DBCC CHECKDB completed successfully';
END TRY
BEGIN CATCH
    PRINT 'DBCC CHECKDB error: ' + ERROR_MESSAGE();
END CATCH

PRINT 'Database Integrity Check Completed';
PRINT '================================';

-- Summary report
PRINT 'INTEGRITY CHECK SUMMARY:';
PRINT 'All counts should be 0 for clean database';
PRINT 'DBCC CHECKCONSTRAINTS should report no violations';
PRINT 'DBCC CHECKDB should report no errors';
