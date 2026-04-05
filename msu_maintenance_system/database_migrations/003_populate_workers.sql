-- Migration 003: Populate Workers from Assignments
-- Extracts unique workers from assignments and populates workers table

BEGIN TRANSACTION;

PRINT 'Starting migration 003: Populate Workers from Assignments';

-- Insert unique workers from assignments
-- Map worker_name to appropriate skill_category based on common patterns
INSERT INTO workers (full_name, department, skill_category)
SELECT DISTINCT 
    worker_name,
    CASE 
        WHEN worker_name LIKE '%electrical%' OR worker_name LIKE '%electric%' THEN 'Electrical'
        WHEN worker_name LIKE '%plumb%' OR worker_name LIKE '%pipe%' THEN 'Plumbing'
        WHEN worker_name LIKE '%carpent%' OR worker_name LIKE '%wood%' THEN 'Carpentry'
        WHEN worker_name LIKE '%mechanic%' OR worker_name LIKE '%engine%' THEN 'Mechanical'
        WHEN worker_name LIKE '%civil%' OR worker_name LIKE '%build%' THEN 'Civil'
        ELSE 'General'
    END AS skill_category,
    CASE 
        WHEN worker_name LIKE '%electrical%' OR worker_name LIKE '%electric%' THEN 'Electrical Services'
        WHEN worker_name LIKE '%plumb%' OR worker_name LIKE '%pipe%' THEN 'Plumbing Services'
        WHEN worker_name LIKE '%carpent%' OR worker_name LIKE '%wood%' THEN 'Carpentry Workshop'
        WHEN worker_name LIKE '%mechanic%' OR worker_name LIKE '%engine%' THEN 'Mechanical Workshop'
        WHEN worker_name LIKE '%civil%' OR worker_name LIKE '%build%' THEN 'Civil Works'
        ELSE 'General Maintenance'
    END AS department
FROM assignments 
WHERE worker_name IS NOT NULL 
AND TRIM(worker_name) <> ''
AND NOT EXISTS (
    SELECT 1 FROM workers w WHERE w.full_name = assignments.worker_name
);

PRINT '✓ Populated workers table from assignments';

-- Update assignments to reference workers table
-- Create a mapping between worker_name and worker_id
UPDATE a
SET worker_id = w.id
FROM assignments a
INNER JOIN workers w ON a.worker_name = w.full_name
WHERE a.worker_id IS NULL;

PRINT '✓ Updated assignments.worker_id references';

-- Verify the migration
PRINT 'Workers created:';
SELECT COUNT(*) AS total_workers FROM workers;

PRINT 'Assignments updated:';
SELECT COUNT(*) AS updated_assignments 
FROM assignments 
WHERE worker_id IS NOT NULL;

COMMIT TRANSACTION;

PRINT 'Migration 003 completed successfully!';
