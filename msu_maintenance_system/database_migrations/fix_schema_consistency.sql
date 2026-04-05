-- Database Migration: Fix Schema Consistency
-- MSU Maintenance System
-- Created: 2024-03-29

-- =====================================================
-- 1. Add missing columns to JobRequests table
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
IF NOT EXISTS (SELECT * FROM sys.default_constraints 
               WHERE name = 'DF_JobRequests_updated_at')
BEGIN
    ALTER TABLE JobRequests 
    ADD CONSTRAINT DF_JobRequests_updated_at DEFAULT GETDATE() FOR updated_at;
    PRINT 'Added DF_JobRequests_updated_at constraint';
END

-- Add submitted_by column if it doesn't exist
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS 
               WHERE TABLE_NAME = 'JobRequests' AND COLUMN_NAME = 'submitted_by')
BEGIN
    ALTER TABLE JobRequests 
    ADD submitted_by INT NULL;
    PRINT 'Added submitted_by column to JobRequests table';
END
ELSE
BEGIN
    PRINT 'submitted_by column already exists in JobRequests table';
END

-- =====================================================
-- 2. Add Foreign Key Constraints
-- =====================================================

-- Add foreign key for Assignments.job_id
IF NOT EXISTS (SELECT * FROM sys.foreign_keys 
               WHERE name = 'FK_Assignments_JobRequests')
BEGIN
    ALTER TABLE Assignments
    ADD CONSTRAINT FK_Assignments_JobRequests
    FOREIGN KEY (job_id) REFERENCES JobRequests(id)
    ON DELETE SET NULL;
    PRINT 'Added FK_Assignments_JobRequests constraint';
END
ELSE
BEGIN
    PRINT 'FK_Assignments_JobRequests constraint already exists';
END

-- Add foreign key for Materials.job_id
IF NOT EXISTS (SELECT * FROM sys.foreign_keys 
               WHERE name = 'FK_Materials_JobRequests')
BEGIN
    ALTER TABLE Materials
    ADD CONSTRAINT FK_Materials_JobRequests
    FOREIGN KEY (job_id) REFERENCES JobRequests(id)
    ON DELETE SET NULL;
    PRINT 'Added FK_Materials_JobRequests constraint';
END
ELSE
BEGIN
    PRINT 'FK_Materials_JobRequests constraint already exists';
END

-- Add foreign key for JobRequests.submitted_by
IF NOT EXISTS (SELECT * FROM sys.foreign_keys 
               WHERE name = 'FK_JobRequests_Users')
BEGIN
    ALTER TABLE JobRequests
    ADD CONSTRAINT FK_JobRequests_Users
    FOREIGN KEY (submitted_by) REFERENCES Users(id)
    ON DELETE SET NULL;
    PRINT 'Added FK_JobRequests_Users constraint';
END
ELSE
BEGIN
    PRINT 'FK_JobRequests_Users constraint already exists';
END

-- =====================================================
-- 3. Add Indexes for Performance
-- =====================================================

-- Index for JobRequests.status
IF NOT EXISTS (SELECT * FROM sys.indexes 
               WHERE name = 'IX_JobRequests_status' AND object_id = OBJECT_ID('JobRequests'))
BEGIN
    CREATE INDEX IX_JobRequests_status ON JobRequests(status);
    PRINT 'Created IX_JobRequests_status index';
END

-- Index for JobRequests.submitted_by
IF NOT EXISTS (SELECT * FROM sys.indexes 
               WHERE name = 'IX_JobRequests_submitted_by' AND object_id = OBJECT_ID('JobRequests'))
BEGIN
    CREATE INDEX IX_JobRequests_submitted_by ON JobRequests(submitted_by);
    PRINT 'Created IX_JobRequests_submitted_by index';
END

-- Index for Assignments.job_id
IF NOT EXISTS (SELECT * FROM sys.indexes 
               WHERE name = 'IX_Assignments_job_id' AND object_id = OBJECT_ID('Assignments'))
BEGIN
    CREATE INDEX IX_Assignments_job_id ON Assignments(job_id);
    PRINT 'Created IX_Assignments_job_id index';
END

-- Index for Materials.job_id
IF NOT EXISTS (SELECT * FROM sys.indexes 
               WHERE name = 'IX_Materials_job_id' AND object_id = OBJECT_ID('Materials'))
BEGIN
    CREATE INDEX IX_Materials_job_id ON Materials(job_id);
    PRINT 'Created IX_Materials_job_id index';
END

-- =====================================================
-- 4. Add Check Constraints for Data Integrity
-- =====================================================

-- Ensure status values are valid
IF NOT EXISTS (SELECT * FROM sys.check_constraints 
               WHERE name = 'CK_JobRequests_status')
BEGIN
    ALTER TABLE JobRequests
    ADD CONSTRAINT CK_JobRequests_status
    CHECK (status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED'));
    PRINT 'Added CK_JobRequests_status constraint';
END

-- Ensure priority values are valid
IF NOT EXISTS (SELECT * FROM sys.check_constraints 
               WHERE name = 'CK_JobRequests_priority')
BEGIN
    ALTER TABLE JobRequests
    ADD CONSTRAINT CK_JobRequests_priority
    CHECK (priority IN ('Low', 'Medium', 'High'));
    PRINT 'Added CK_JobRequests_priority constraint';
END

-- =====================================================
-- 5. Verify Schema
-- =====================================================

PRINT '=== Schema Verification ==='
PRINT 'Tables in database:'
SELECT name FROM sys.tables WHERE name IN ('Users', 'JobRequests', 'Assignments', 'Materials') ORDER BY name

PRINT 'Foreign Key Constraints:'
SELECT name, parent_object_id, referenced_object_id 
FROM sys.foreign_keys 
WHERE parent_object_id IN (OBJECT_ID('JobRequests'), OBJECT_ID('Assignments'), OBJECT_ID('Materials'))

PRINT 'Check Constraints:'
SELECT name, parent_object_id 
FROM sys.check_constraints 
WHERE parent_object_id IN (OBJECT_ID('JobRequests'), OBJECT_ID('Users'))

PRINT 'Schema consistency migration completed successfully!'
