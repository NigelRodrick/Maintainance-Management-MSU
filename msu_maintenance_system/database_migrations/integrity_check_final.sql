-- Final Integrity Check Script
-- Only checks tables that actually exist

PRINT 'Starting Final Database Integrity Check';
PRINT '================================';

-- Check 1: Verify materials table integrity (only if exists)
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'materials')
BEGIN
    PRINT 'Check 1: Materials table orphaned records';
    SELECT 
        COUNT(*) AS orphaned_materials_count
    FROM materials m
    LEFT JOIN job_requests j ON m.job_id = j.id
    WHERE j.id IS NULL;
END
ELSE
BEGIN
    PRINT 'Check 1: Materials table - NOT FOUND';
    SELECT 0 AS orphaned_materials_count;
END

-- Check 2: Verify job_requests table integrity
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'job_requests')
BEGIN
    PRINT 'Check 2: Job_requests table orphaned records';
    SELECT 
        COUNT(*) AS orphaned_job_requests_count
    FROM job_requests jr
    LEFT JOIN users u ON jr.submitted_by = u.id
    WHERE u.id IS NULL;
    
    PRINT 'Check 3: Non-standard status values in job_requests';
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

-- Check 3: Verify users table integrity
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'users')
BEGIN
    PRINT 'Check 4: Non-standard role values in users';
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

-- Check 4: Verify assignments table integrity
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'assignments')
BEGIN
    PRINT 'Check 5: Assignments table orphaned records';
    SELECT 
        COUNT(*) AS orphaned_assignments_count
    FROM assignments a
    LEFT JOIN job_requests j ON a.job_id = j.id
    WHERE j.id IS NULL;
END
ELSE
BEGIN
    PRINT 'Check 4: Assignments table - NOT FOUND';
    SELECT 0 AS orphaned_assignments_count;
END

-- Check 5: Verify workers table integrity
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'workers')
BEGIN
    PRINT 'Check 6: Workers table orphaned records';
    SELECT 
        COUNT(*) AS orphaned_workers_count
    FROM workers w
    LEFT JOIN users u ON w.user_id = u.id
    WHERE u.id IS NULL;
END
ELSE
BEGIN
    PRINT 'Check 5: Workers table - NOT FOUND';
    SELECT 0 AS orphaned_workers_count;
END

-- Check 6: Verify job_status_history table integrity
IF EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'job_status_history')
BEGIN
    PRINT 'Check 7: Job_status_history table orphaned records';
    SELECT 
        COUNT(*) AS orphaned_status_history_count
    FROM job_status_history jsh
    LEFT JOIN job_requests j ON jsh.job_id = j.id
    WHERE j.id IS NULL;
END
ELSE
BEGIN
    PRINT 'Check 6: Job_status_history table - NOT FOUND';
    SELECT 0 AS orphaned_status_history_count;
END

-- Check 7: DBCC CHECKCONSTRAINTS
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

PRINT 'Final Database Integrity Check Completed';
PRINT '================================';

-- Summary report
PRINT 'FINAL INTEGRITY CHECK SUMMARY:';
PRINT 'All counts should be 0 for clean database';
PRINT 'DBCC CHECKCONSTRAINTS should report no violations';
PRINT 'DBCC CHECKDB should report no errors';
