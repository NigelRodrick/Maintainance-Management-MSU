-- Migration 006: Add CHECK Constraints
-- Adds data integrity constraints to all tables

BEGIN TRANSACTION;

PRINT 'Starting migration 006: Add CHECK Constraints';

-- Add CHECK constraints for job_requests
IF NOT EXISTS (SELECT * FROM sys.check_constraints WHERE parent_object_id = OBJECT_ID('job_requests') AND name = 'CK_job_requests_status')
BEGIN
    ALTER TABLE job_requests 
    ADD CONSTRAINT CK_job_requests_status 
    CHECK (status IN ('PENDING','IN_PROGRESS','COMPLETED','CANCELLED'));
    PRINT '✓ Added CK_job_requests_status';
END

IF NOT EXISTS (SELECT * FROM sys.check_constraints WHERE parent_object_id = OBJECT_ID('job_requests') AND name = 'CK_job_requests_priority')
BEGIN
    ALTER TABLE job_requests 
    ADD CONSTRAINT CK_job_requests_priority 
    CHECK (priority IN ('LOW','MEDIUM','HIGH','CRITICAL'));
    PRINT '✓ Added CK_job_requests_priority';
END

-- Add CHECK constraints for assignments
IF NOT EXISTS (SELECT * FROM sys.check_constraints WHERE parent_object_id = OBJECT_ID('assignments') AND name = 'CK_assignments_dates')
BEGIN
    ALTER TABLE assignments 
    ADD CONSTRAINT CK_assignments_dates 
    CHECK (end_time IS NULL OR end_time >= start_time);
    PRINT '✓ Added CK_assignments_dates';
END

IF NOT EXISTS (SELECT * FROM sys.check_constraints WHERE parent_object_id = OBJECT_ID('assignments') AND name = 'CK_assignments_status')
BEGIN
    ALTER TABLE assignments 
    ADD CONSTRAINT CK_assignments_status 
    CHECK (status IN ('ASSIGNED','IN_PROGRESS','COMPLETED','CANCELLED'));
    PRINT '✓ Added CK_assignments_status';
END

-- Add CHECK constraints for materials
IF NOT EXISTS (SELECT * FROM sys.check_constraints WHERE parent_object_id = OBJECT_ID('materials') AND name = 'CK_materials_quantity')
BEGIN
    ALTER TABLE materials 
    ADD CONSTRAINT CK_materials_quantity 
    CHECK (quantity_used <= quantity_required AND quantity_required > 0);
    PRINT '✓ Added CK_materials_quantity';
END

-- Make job_id NOT NULL in materials (first ensure no NULL values exist)
UPDATE materials SET job_id = 0 WHERE job_id IS NULL;
ALTER TABLE materials ALTER COLUMN job_id INT NOT NULL;
PRINT '✓ Made materials.job_id NOT NULL';

-- Make submitted_by NOT NULL in job_requests (first create a system user if needed)
IF EXISTS (SELECT 1 FROM job_requests WHERE submitted_by IS NULL)
BEGIN
    -- Create a system user if it doesn't exist
    IF NOT EXISTS (SELECT 1 FROM users WHERE email = 'system@msu.ac.zw')
    BEGIN
        INSERT INTO users (email, password_hash, role, created_at, is_active)
        VALUES ('system@msu.ac.zw', 'system-user-hash', 'admin', GETDATE(), 1);
        PRINT '✓ Created system user for orphaned records';
    END
    
    -- Update orphaned job_requests
    UPDATE job_requests 
    SET submitted_by = (SELECT id FROM users WHERE email = 'system@msu.ac.zw')
    WHERE submitted_by IS NULL;
    PRINT '✓ Updated orphaned job_requests.submitted_by';
END

ALTER TABLE job_requests ALTER COLUMN submitted_by INT NOT NULL;
PRINT '✓ Made job_requests.submitted_by NOT NULL';

-- Add CHECK constraints for workers
IF NOT EXISTS (SELECT * FROM sys.check_constraints WHERE parent_object_id = OBJECT_ID('workers') AND name = 'CK_workers_skill_category')
BEGIN
    ALTER TABLE workers 
    ADD CONSTRAINT CK_workers_skill_category 
    CHECK (skill_category IN ('electrical','plumbing','carpentry','mechanical','civil','general'));
    PRINT '✓ Added CK_workers_skill_category';
END

-- Verify all constraints
PRINT 'All CHECK constraints:';
SELECT 
    t.name AS table_name,
    c.name AS constraint_name,
    c.definition
FROM sys.check_constraints c
INNER JOIN sys.tables t ON c.parent_object_id = t.object_id
WHERE t.name IN ('job_requests', 'assignments', 'materials', 'workers')
ORDER BY t.name, c.name;

COMMIT TRANSACTION;

PRINT 'Migration 006 completed successfully!';
