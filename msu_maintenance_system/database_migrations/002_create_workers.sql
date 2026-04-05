-- Migration 002: Create Workers Table
-- Creates a dedicated workers table for proper worker management

BEGIN TRANSACTION;

PRINT 'Starting migration 002: Create Workers Table';

-- Create workers table
CREATE TABLE workers (
    id              INT           PRIMARY KEY IDENTITY(1,1),
    user_id         INT           NULL,   -- FK to users.id (NULL if worker has no system account)
    full_name       VARCHAR(150)  NOT NULL,
    department      VARCHAR(100)  NOT NULL,
    skill_category  VARCHAR(50)   NOT NULL,  -- electrical|plumbing|carpentry|mechanical|civil
    is_active       BIT           NOT NULL DEFAULT 1,
    created_at      DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    updated_at      DATETIME2     NOT NULL DEFAULT SYSUTCDATETIME(),
    is_deleted      BIT           NOT NULL DEFAULT 0,
    CONSTRAINT FK_workers_users FOREIGN KEY (user_id) REFERENCES users(id)
);

PRINT '✓ Created workers table';

-- Create indexes for workers table
CREATE INDEX IX_workers_department ON workers(department);
CREATE INDEX IX_workers_skill_category ON workers(skill_category);
CREATE INDEX IX_workers_is_active ON workers(is_active);

PRINT '✓ Created workers table indexes';

COMMIT TRANSACTION;

PRINT 'Migration 002 completed successfully!';
