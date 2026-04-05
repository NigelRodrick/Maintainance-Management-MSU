-- MSU Maintenance System Database Migration Script
-- Generated: 2026-03-29 18:53:50
-- Purpose: Synchronize database with SQLAlchemy models
-- Version: 1.0
-- Database: CentralServices_AM_DB
-- Server: DESKTOP-IO9GJQS\SQLEXPRESS

-- =====================================================
-- IMPORTANT: BACKUP DATABASE BEFORE RUNNING THIS SCRIPT
-- =====================================================

USE [CentralServices_AM_DB];
GO

-- =====================================================
-- PART 1: Add missing columns to users table
-- =====================================================

PRINT 'Adding missing columns to users table...';

-- Add password_hash column (NOT NULL constraint will be handled separately)
ALTER TABLE Users ADD password_hash VARCHAR(255) NULL;
GO

-- Add created_at column with default
ALTER TABLE Users ADD created_at DATETIME DEFAULT GETDATE();
GO

-- Add is_active column with default
ALTER TABLE Users ADD is_active BIT DEFAULT 1;
GO

-- =====================================================
-- PART 2: Add missing columns to job_requests table
-- =====================================================

PRINT 'Adding missing columns to job_requests table...';

-- Note: The existing table may have an ID column, check if it exists first
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'JobRequests' AND COLUMN_NAME = 'id')
BEGIN
    ALTER TABLE JobRequests ADD id INT IDENTITY(1,1) PRIMARY KEY;
END
GO

-- Add department column (NOT NULL constraint will be handled separately)
ALTER TABLE JobRequests ADD department VARCHAR(100) NULL;
GO

-- Add description column (NOT NULL constraint will be handled separately)
ALTER TABLE JobRequests ADD description TEXT NULL;
GO

-- Add category column (NOT NULL constraint will be handled separately)
ALTER TABLE JobRequests ADD category VARCHAR(50) NULL;
GO

-- Add priority column (NOT NULL constraint will be handled separately)
ALTER TABLE JobRequests ADD priority VARCHAR(50) NULL;
GO

-- Add status column (NOT NULL constraint will be handled separately)
ALTER TABLE JobRequests ADD status VARCHAR(50) NULL;
GO

-- Add date_created column with default
ALTER TABLE JobRequests ADD date_created DATETIME DEFAULT GETDATE();
GO

-- Add updated_at column with default
ALTER TABLE JobRequests ADD updated_at DATETIME DEFAULT GETDATE();
GO

-- Add submitted_by column
ALTER TABLE JobRequests ADD submitted_by INT NULL;
GO

-- =====================================================
-- PART 3: Add missing columns to assignments table
-- =====================================================

PRINT 'Adding missing columns to assignments table...';

-- Add status column with default
ALTER TABLE Assignments ADD status VARCHAR(50) DEFAULT 'Assigned';
GO

-- Add worker_id column (new foreign key to users)
ALTER TABLE Assignments ADD worker_id INT NULL;
GO

-- Update job_id to be NOT NULL (model change)
UPDATE Assignments SET job_id = ISNULL(job_id, 0) WHERE job_id IS NULL;
ALTER TABLE Assignments ALTER COLUMN job_id INT NOT NULL;
GO

-- =====================================================
-- PART 4: Create predictions table (new model)
-- =====================================================

PRINT 'Creating predictions table...';

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_NAME = 'predictions')
BEGIN
    CREATE TABLE predictions (
        id INT IDENTITY(1,1) PRIMARY KEY,
        job_id INT NOT NULL,
        predicted_priority VARCHAR(50) NOT NULL,
        predicted_category VARCHAR(50) NOT NULL,
        confidence FLOAT NOT NULL,
        created_at DATETIME DEFAULT GETDATE()
    );
    PRINT 'Created predictions table';
END
GO

-- =====================================================
-- PART 5: Add missing columns to materials table
-- =====================================================

PRINT 'Materials table - checking for missing columns...';

-- Materials table appears to have all required columns
-- No additions needed based on schema comparison

-- =====================================================
-- PART 6: Update NULL constraints and default values
-- =====================================================

PRINT 'Updating NULL constraints and default values...';

-- Update users table constraints
UPDATE Users SET email = ISNULL(email, '') WHERE email IS NULL;
UPDATE Users SET role = ISNULL(role, 'staff') WHERE role IS NULL;
UPDATE Users SET password_hash = ISNULL(password_hash, '') WHERE password_hash IS NULL;

-- Update job_requests table constraints
UPDATE JobRequests SET department = ISNULL(department, 'Unknown') WHERE department IS NULL;
UPDATE JobRequests SET description = ISNULL(description, 'No description') WHERE description IS NULL;
UPDATE JobRequests SET category = ISNULL(category, 'General') WHERE category IS NULL;
UPDATE JobRequests SET priority = ISNULL(priority, 'Medium') WHERE priority IS NULL;
UPDATE JobRequests SET status = ISNULL(status, 'Pending') WHERE status IS NULL;

-- Update assignments table constraints
UPDATE Assignments SET worker_name = ISNULL(worker_name, 'Unassigned') WHERE worker_name IS NULL;

-- Update materials table constraints
UPDATE Materials SET item = ISNULL(item, 'Unknown') WHERE item IS NULL;
UPDATE Materials SET quantity_required = ISNULL(quantity_required, 0) WHERE quantity_required IS NULL;
UPDATE Materials SET quantity_used = ISNULL(quantity_used, 0) WHERE quantity_used IS NULL;

-- =====================================================
-- PART 7: Apply NOT NULL constraints
-- =====================================================

PRINT 'Applying NOT NULL constraints...';

-- Users table constraints
ALTER TABLE Users ALTER COLUMN email VARCHAR(100) NOT NULL;
ALTER TABLE Users ALTER COLUMN role VARCHAR(50) NOT NULL;
ALTER TABLE Users ALTER COLUMN password_hash VARCHAR(255) NOT NULL;
GO

-- JobRequests table constraints
ALTER TABLE JobRequests ALTER COLUMN department VARCHAR(100) NOT NULL;
ALTER TABLE JobRequests ALTER COLUMN description TEXT NOT NULL;
ALTER TABLE JobRequests ALTER COLUMN category VARCHAR(50) NOT NULL;
ALTER TABLE JobRequests ALTER COLUMN priority VARCHAR(50) NOT NULL;
ALTER TABLE JobRequests ALTER COLUMN status VARCHAR(50) NOT NULL;
GO

-- Assignments table constraints
ALTER TABLE Assignments ALTER COLUMN worker_name VARCHAR(100) NOT NULL;
GO

-- Materials table constraints
ALTER TABLE Materials ALTER COLUMN item VARCHAR(100) NOT NULL;
ALTER TABLE Materials ALTER COLUMN quantity_required INT NOT NULL;
GO

-- =====================================================
-- PART 8: Add constraints and indexes
-- =====================================================

PRINT 'Adding constraints and indexes...';

-- Drop existing password column if it exists (to avoid confusion)
IF EXISTS (SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Users' AND COLUMN_NAME = 'password')
BEGIN
    ALTER TABLE Users DROP COLUMN password;
    PRINT 'Dropped old password column';
END
GO

-- Add unique constraint on email
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.CONSTRAINTS WHERE CONSTRAINT_NAME = 'UQ_users_email')
BEGIN
    ALTER TABLE Users ADD CONSTRAINT UQ_users_email UNIQUE (email);
    PRINT 'Added unique constraint on users.email';
END
GO

-- Add foreign key constraints
IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.CONSTRAINTS WHERE CONSTRAINT_NAME = 'FK_job_requests_submitted_by')
BEGIN
    ALTER TABLE JobRequests ADD CONSTRAINT FK_job_requests_submitted_by FOREIGN KEY (submitted_by) REFERENCES Users(id);
    PRINT 'Added foreign key: job_requests.submitted_by -> users.id';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.CONSTRAINTS WHERE CONSTRAINT_NAME = 'FK_assignments_job_id')
BEGIN
    ALTER TABLE Assignments ADD CONSTRAINT FK_assignments_job_id FOREIGN KEY (job_id) REFERENCES JobRequests(id);
    PRINT 'Added foreign key: assignments.job_id -> job_requests.id';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.CONSTRAINTS WHERE CONSTRAINT_NAME = 'FK_assignments_worker_id')
BEGIN
    ALTER TABLE Assignments ADD CONSTRAINT FK_assignments_worker_id FOREIGN KEY (worker_id) REFERENCES Users(id);
    PRINT 'Added foreign key: assignments.worker_id -> users.id';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.CONSTRAINTS WHERE CONSTRAINT_NAME = 'FK_materials_job_id')
BEGIN
    ALTER TABLE Materials ADD CONSTRAINT FK_materials_job_id FOREIGN KEY (job_id) REFERENCES JobRequests(id);
    PRINT 'Added foreign key: materials.job_id -> job_requests.id';
END
GO

IF NOT EXISTS (SELECT * FROM INFORMATION_SCHEMA.CONSTRAINTS WHERE CONSTRAINT_NAME = 'FK_predictions_job_id')
BEGIN
    ALTER TABLE predictions ADD CONSTRAINT FK_predictions_job_id FOREIGN KEY (job_id) REFERENCES JobRequests(id);
    PRINT 'Added foreign key: predictions.job_id -> job_requests.id';
END
GO

-- =====================================================
-- PART 8: Create indexes for performance
-- =====================================================

PRINT 'Creating indexes for performance...';

-- Create indexes on frequently queried columns
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_job_requests_status')
BEGIN
    CREATE INDEX IX_job_requests_status ON JobRequests(status);
    PRINT 'Created index on job_requests.status';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_job_requests_priority')
BEGIN
    CREATE INDEX IX_job_requests_priority ON JobRequests(priority);
    PRINT 'Created index on job_requests.priority';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_job_requests_date_created')
BEGIN
    CREATE INDEX IX_job_requests_date_created ON JobRequests(date_created);
    PRINT 'Created index on job_requests.date_created';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_assignments_status')
BEGIN
    CREATE INDEX IX_assignments_status ON Assignments(status);
    PRINT 'Created index on assignments.status';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_predictions_job_id')
BEGIN
    CREATE INDEX IX_predictions_job_id ON predictions(job_id);
    PRINT 'Created index on predictions.job_id';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'IX_predictions_created_at')
BEGIN
    CREATE INDEX IX_predictions_created_at ON predictions(created_at);
    PRINT 'Created index on predictions.created_at';
END
GO

-- =====================================================
-- PART 9: Data validation and cleanup
-- =====================================================

PRINT 'Performing data validation...';

-- Check for duplicate emails
IF EXISTS (SELECT email, COUNT(*) as cnt FROM Users GROUP BY email HAVING COUNT(*) > 1)
BEGIN
    PRINT 'WARNING: Duplicate emails found in Users table. Please review manually.';
END
ELSE
BEGIN
    PRINT 'No duplicate emails found in Users table.';
END
GO

-- Check for orphaned records
IF EXISTS (SELECT * FROM JobRequests WHERE submitted_by IS NOT NULL AND submitted_by NOT IN (SELECT id FROM Users))
BEGIN
    PRINT 'WARNING: Orphaned job_requests found (submitted_by references non-existent user).';
END
ELSE
BEGIN
    PRINT 'No orphaned job_requests found.';
END
GO

-- =====================================================
-- MIGRATION COMPLETE
-- =====================================================

PRINT '=====================================================';
PRINT 'MIGRATION COMPLETED SUCCESSFULLY';
PRINT '=====================================================';
PRINT 'Summary of changes:';
PRINT '- Added missing columns to all tables';
PRINT '- Applied NOT NULL constraints';
PRINT '- Added unique and foreign key constraints';
PRINT '- Created performance indexes';
PRINT '- Performed data validation';
PRINT '';
PRINT 'Please verify the application functionality after migration.';
PRINT '=====================================================';

GO
