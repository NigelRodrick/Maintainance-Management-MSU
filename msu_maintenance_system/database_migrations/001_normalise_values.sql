-- Migration 001: Normalise Status and Role Values
-- Standardises all mixed-case values to consistent format

BEGIN TRANSACTION;

PRINT 'Starting migration 001: Normalise Status and Role Values';

-- Normalise job_requests status to UPPER_SNAKE_CASE
UPDATE job_requests 
SET status = UPPER(TRIM(status))
WHERE status NOT IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED');

PRINT '✓ Normalised job_requests status values';

-- Normalise users role to lowercase
UPDATE users 
SET role = LOWER(TRIM(role))
WHERE role NOT IN ('admin', 'supervisor', 'staff', 'maintenance_admin');

PRINT '✓ Normalised users role values';

-- Verify the changes
PRINT 'Current status values in job_requests:';
SELECT DISTINCT status AS job_status_values FROM job_requests;

PRINT 'Current role values in users:';
SELECT DISTINCT role AS user_role_values FROM users;

COMMIT TRANSACTION;

PRINT 'Migration 001 completed successfully!';
