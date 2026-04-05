-- Update Database Schema for MSU Maintenance System
-- Add is_deleted columns to all tables that need them

-- Add is_deleted to job_requests
ALTER TABLE job_requests ADD is_deleted BIT DEFAULT 0;
ALTER TABLE job_requests ADD CONSTRAINT DF_job_requests_is_deleted DEFAULT 0;

-- Add is_deleted to assignments  
ALTER TABLE assignments ADD is_deleted BIT DEFAULT 0;
ALTER TABLE assignments ADD CONSTRAINT DF_assignments_is_deleted DEFAULT 0;

-- Add is_deleted to materials
ALTER TABLE materials ADD is_deleted BIT DEFAULT 0;
ALTER TABLE materials ADD CONSTRAINT DF_materials_is_deleted DEFAULT 0;

-- Add is_deleted to workers
ALTER TABLE workers ADD is_deleted BIT DEFAULT 0;
ALTER TABLE workers ADD CONSTRAINT DF_workers_is_deleted DEFAULT 0;

-- Add is_deleted to job_status_history
ALTER TABLE job_status_history ADD is_deleted BIT DEFAULT 0;
ALTER TABLE job_status_history ADD CONSTRAINT DF_job_status_history_is_deleted DEFAULT 0;

PRINT 'Schema update completed';
