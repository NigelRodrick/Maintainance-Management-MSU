-- Simple Integrity Check Script
-- Validates database integrity without is_deleted dependencies

PRINT 'Starting Database Integrity Check';
PRINT '================================';

-- Check 1: Verify materials table integrity
PRINT 'Check 1: Materials table orphaned records';
SELECT 
    COUNT(*) AS orphaned_materials_count
FROM materials m
LEFT JOIN job_requests j ON m.job_id = j.id
WHERE j.id IS NULL;

-- Check 2: Verify job_requests table integrity
PRINT 'Check 2: Job_requests table orphaned records';
SELECT 
    COUNT(*) AS orphaned_job_requests_count
FROM job_requests jr
LEFT JOIN users u ON jr.submitted_by = u.id
WHERE u.id IS NULL;

-- Check 3: Verify status values are standardised
PRINT 'Check 3: Non-standard status values in job_requests';
SELECT 
    COUNT(*) AS non_standard_status_count
FROM job_requests 
WHERE status NOT IN ('PENDING','IN_PROGRESS','COMPLETED','CANCELLED')
AND status IS NOT NULL;

-- Check 4: Verify role values are standardised
PRINT 'Check 4: Non-standard role values in users';
SELECT 
    COUNT(*) AS non_standard_role_count
FROM users 
WHERE role NOT IN ('admin','supervisor','staff','maintenance')
AND role IS NOT NULL;

-- Check 5: Verify assignments table integrity
PRINT 'Check 5: Assignments table orphaned records';
SELECT 
    COUNT(*) AS orphaned_assignments_count
FROM assignments a
LEFT JOIN job_requests j ON a.job_id = j.id
WHERE j.id IS NULL;

-- Check 6: Verify workers table integrity
PRINT 'Check 6: Workers table orphaned records';
SELECT 
    COUNT(*) AS orphaned_workers_count
FROM workers w
LEFT JOIN users u ON w.user_id = u.id
WHERE u.id IS NULL;

-- Check 7: Verify job_status_history table integrity
PRINT 'Check 7: Job_status_history table orphaned records';
SELECT 
    COUNT(*) AS orphaned_status_history_count
FROM job_status_history jsh
LEFT JOIN job_requests j ON jsh.job_id = j.id
WHERE j.id IS NULL;

-- Check 8: DBCC CHECKCONSTRAINTS
PRINT 'Check 8: DBCC CHECKCONSTRAINTS';
BEGIN TRY
    DBCC CHECKCONSTRAINTS WITH NO_INFOMSGS;
    PRINT 'DBCC CHECKCONSTRAINTS completed successfully';
END TRY
BEGIN CATCH
    PRINT 'DBCC CHECKCONSTRAINTS error: ' + ERROR_MESSAGE();
END CATCH

-- Check 9: DBCC CHECKDB
PRINT 'Check 9: DBCC CHECKDB';
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
