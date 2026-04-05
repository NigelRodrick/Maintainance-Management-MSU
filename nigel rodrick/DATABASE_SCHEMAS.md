# MSU Maintenance System - Database Schemas

## Overview

The MSU Maintenance Management System uses a comprehensive relational database schema designed to support all maintenance operations, user management, analytics, and reporting requirements. The database is built on Microsoft SQL Server and follows normalization principles for data integrity and performance.

## Database Architecture

### Design Principles
- **Normalization**: Third Normal Form (3NF) for data integrity
- **Referential Integrity**: Foreign key constraints for data consistency
- **Performance Optimization**: Strategic indexing for query performance
- **Scalability**: Design supports growth and expansion
- **Audit Trail**: Complete audit logging for all operations
- **Security**: Role-based data access and protection

### Naming Conventions
- **Tables**: PascalCase (e.g., JobRequests, Users, Assignments)
- **Columns**: PascalCase (e.g., DateCreated, IsActive, SubmittedBy)
- **Primary Keys**: Id (identity column)
- **Foreign Keys**: RelatedTableNameId (e.g., JobId, UserId)
- **Indexes**: IX_TableName_ColumnName

## Core Database Schema

### 1. Users Table
```sql
CREATE TABLE Users (
    Id INT PRIMARY KEY IDENTITY(1,1),
    Email VARCHAR(100) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL,
    Role VARCHAR(50) NOT NULL DEFAULT 'staff',
    FirstName VARCHAR(50) NULL,
    LastName VARCHAR(50) NULL,
    PhoneNumber VARCHAR(20) NULL,
    Department VARCHAR(100) NULL,
    IsActive BIT DEFAULT 1,
    IsDeleted BIT DEFAULT 0,
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE(),
    LastLoginAt DATETIME NULL,
    PasswordResetToken VARCHAR(255) NULL,
    PasswordResetExpires DATETIME NULL,
    
    -- Constraints
    CONSTRAINT CK_Users_Role CHECK (Role IN ('admin', 'supervisor', 'staff', 'worker')),
    CONSTRAINT CK_Users_Email CHECK (Email LIKE '%@staff.msu.ac.zw')
);

-- Indexes
CREATE INDEX IX_Users_Email ON Users(Email);
CREATE INDEX IX_Users_Role ON Users(Role);
CREATE INDEX IX_Users_IsActive ON Users(IsActive);
CREATE INDEX IX_Users_Department ON Users(Department);
```

### 2. Departments Table
```sql
CREATE TABLE Departments (
    Id INT PRIMARY KEY IDENTITY(1,1),
    Name VARCHAR(100) UNIQUE NOT NULL,
    Description TEXT NULL,
    Building VARCHAR(100) NULL,
    Floor VARCHAR(50) NULL,
    ContactPerson VARCHAR(100) NULL,
    ContactEmail VARCHAR(100) NULL,
    ContactPhone VARCHAR(20) NULL,
    IsActive BIT DEFAULT 1,
    IsDeleted BIT DEFAULT 0,
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE()
);

-- Indexes
CREATE INDEX IX_Departments_Name ON Departments(Name);
CREATE INDEX IX_Departments_IsActive ON Departments(IsActive);
```

### 3. JobCategories Table
```sql
CREATE TABLE JobCategories (
    Id INT PRIMARY KEY IDENTITY(1,1),
    Name VARCHAR(50) UNIQUE NOT NULL,
    Description TEXT NULL,
    Color VARCHAR(7) NULL,  -- Hex color code for UI
    Icon VARCHAR(50) NULL,   -- Icon class for UI
    IsActive BIT DEFAULT 1,
    IsDeleted BIT DEFAULT 0,
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE(),
    
    CONSTRAINT CK_JobCategories_Name CHECK (Name IN ('Electrical', 'Plumbing', 'Mechanical', 'Civil', 'General'))
);

-- Indexes
CREATE INDEX IX_JobCategories_Name ON JobCategories(Name);
```

### 4. JobRequests Table
```sql
CREATE TABLE JobRequests (
    Id INT PRIMARY KEY IDENTITY(1,1),
    DepartmentId INT NOT NULL,
    CategoryId INT NOT NULL,
    Description TEXT NOT NULL,
    Priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
    Status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    SubmittedBy INT NOT NULL,
    AssignedTo INT NULL,  -- Worker ID
    Location VARCHAR(200) NULL,
    Building VARCHAR(100) NULL,
    Room VARCHAR(50) NULL,
    UrgencyLevel INT DEFAULT 3,  -- 1=Low, 2=Medium, 3=High, 4=Urgent
    EstimatedDuration INT NULL,  -- In hours
    ActualDuration INT NULL,    -- In hours
    DateCreated DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE(),
    AssignedAt DATETIME NULL,
    StartedAt DATETIME NULL,
    CompletedAt DATETIME NULL,
    ClosedAt DATETIME NULL,
    IsActive BIT DEFAULT 1,
    IsDeleted BIT DEFAULT 0,
    
    -- Foreign Key Constraints
    CONSTRAINT FK_JobRequests_Department FOREIGN KEY (DepartmentId) REFERENCES Departments(Id),
    CONSTRAINT FK_JobRequests_Category FOREIGN KEY (CategoryId) REFERENCES JobCategories(Id),
    CONSTRAINT FK_JobRequests_SubmittedBy FOREIGN KEY (SubmittedBy) REFERENCES Users(Id),
    CONSTRAINT FK_JobRequests_AssignedTo FOREIGN KEY (AssignedTo) REFERENCES Users(Id),
    
    -- Check Constraints
    CONSTRAINT CK_JobRequests_Priority CHECK (Priority IN ('LOW', 'MEDIUM', 'HIGH', 'URGENT')),
    CONSTRAINT CK_JobRequests_Status CHECK (Status IN ('PENDING', 'ASSIGNED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED', 'CLOSED')),
    CONSTRAINT CK_JobRequests_UrgencyLevel CHECK (UrgencyLevel BETWEEN 1 AND 4)
);

-- Indexes
CREATE INDEX IX_JobRequests_DepartmentId ON JobRequests(DepartmentId);
CREATE INDEX IX_JobRequests_CategoryId ON JobRequests(CategoryId);
CREATE INDEX IX_JobRequests_Status ON JobRequests(Status);
CREATE INDEX IX_JobRequests_Priority ON JobRequests(Priority);
CREATE INDEX IX_JobRequests_SubmittedBy ON JobRequests(SubmittedBy);
CREATE INDEX IX_JobRequests_AssignedTo ON JobRequests(AssignedTo);
CREATE INDEX IX_JobRequests_DateCreated ON JobRequests(DateCreated);
CREATE INDEX IX_JobRequests_Status_Priority ON JobRequests(Status, Priority);
```

### 5. Workers Table
```sql
CREATE TABLE Workers (
    Id INT PRIMARY KEY IDENTITY(1,1),
    UserId INT UNIQUE NOT NULL,
    EmployeeNumber VARCHAR(20) UNIQUE NOT NULL,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PhoneNumber VARCHAR(20) NULL,
    Skills TEXT NULL,  -- Comma-separated list of skills
    Specialization VARCHAR(100) NULL,
    ExperienceLevel VARCHAR(20) DEFAULT 'JUNIOR',  -- JUNIOR, INTERMEDIATE, SENIOR, EXPERT
    IsActive BIT DEFAULT 1,
    IsDeleted BIT DEFAULT 0,
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE(),
    
    -- Foreign Key Constraint
    CONSTRAINT FK_Workers_UserId FOREIGN KEY (UserId) REFERENCES Users(Id),
    
    -- Check Constraints
    CONSTRAINT CK_Workers_ExperienceLevel CHECK (ExperienceLevel IN ('JUNIOR', 'INTERMEDIATE', 'SENIOR', 'EXPERT'))
);

-- Indexes
CREATE INDEX IX_Workers_UserId ON Workers(UserId);
CREATE INDEX IX_Workers_Email ON Workers(Email);
CREATE INDEX IX_Workers_Specialization ON Workers(Specialization);
CREATE INDEX IX_Workers_ExperienceLevel ON Workers(ExperienceLevel);
CREATE INDEX IX_Workers_IsActive ON Workers(IsActive);
```

### 6. Assignments Table
```sql
CREATE TABLE Assignments (
    Id INT PRIMARY KEY IDENTITY(1,1),
    JobId INT NOT NULL,
    WorkerId INT NOT NULL,
    AssignedBy INT NOT NULL,  -- Supervisor who assigned
    Status VARCHAR(20) NOT NULL DEFAULT 'ASSIGNED',
    AssignedAt DATETIME DEFAULT GETDATE(),
    StartedAt DATETIME NULL,
    CompletedAt DATETIME NULL,
    EstimatedHours INT NULL,
    ActualHours INT NULL,
    Notes TEXT NULL,
    SupervisorNotes TEXT NULL,
    WorkerNotes TEXT NULL,
    QualityRating INT NULL,  -- 1-5 rating
    CustomerFeedback TEXT NULL,
    IsActive BIT DEFAULT 1,
    IsDeleted BIT DEFAULT 0,
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE(),
    
    -- Foreign Key Constraints
    CONSTRAINT FK_Assignments_Job FOREIGN KEY (JobId) REFERENCES JobRequests(Id),
    CONSTRAINT FK_Assignments_Worker FOREIGN KEY (WorkerId) REFERENCES Workers(Id),
    CONSTRAINT FK_Assignments_AssignedBy FOREIGN KEY (AssignedBy) REFERENCES Users(Id),
    
    -- Check Constraints
    CONSTRAINT CK_Assignments_Status CHECK (Status IN ('ASSIGNED', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED')),
    CONSTRAINT CK_Assignments_QualityRating CHECK (QualityRating BETWEEN 1 AND 5)
);

-- Indexes
CREATE INDEX IX_Assignments_JobId ON Assignments(JobId);
CREATE INDEX IX_Assignments_WorkerId ON Assignments(WorkerId);
CREATE INDEX IX_Assignments_Status ON Assignments(Status);
CREATE INDEX IX_Assignments_AssignedAt ON Assignments(AssignedAt);
CREATE INDEX IX_Assignments_Worker_Status ON Assignments(WorkerId, Status);
```

### 7. Materials Table
```sql
CREATE TABLE Materials (
    Id INT PRIMARY KEY IDENTITY(1,1),
    JobId INT NOT NULL,
    ItemName VARCHAR(100) NOT NULL,
    Description TEXT NULL,
    QuantityRequired DECIMAL(10,2) NOT NULL,
    QuantityUsed DECIMAL(10,2) DEFAULT 0,
    Unit VARCHAR(20) NOT NULL DEFAULT 'units',
    UnitCost DECIMAL(10,2) NULL,
    TotalCost DECIMAL(10,2) NULL,
    Supplier VARCHAR(100) NULL,
    MaterialCode VARCHAR(50) NULL,
    RecordedBy INT NOT NULL,  -- Worker who recorded
    RecordedAt DATETIME DEFAULT GETDATE(),
    IsActive BIT DEFAULT 1,
    IsDeleted BIT DEFAULT 0,
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE(),
    
    -- Foreign Key Constraints
    CONSTRAINT FK_Materials_Job FOREIGN KEY (JobId) REFERENCES JobRequests(Id),
    CONSTRAINT FK_Materials_RecordedBy FOREIGN KEY (RecordedBy) REFERENCES Users(Id),
    
    -- Check Constraints
    CONSTRAINT CK_Materials_Quantity CHECK (QuantityRequired >= 0 AND QuantityUsed >= 0)
);

-- Indexes
CREATE INDEX IX_Materials_JobId ON Materials(JobId);
CREATE INDEX IX_Materials_ItemName ON Materials(ItemName);
CREATE INDEX IX_Materials_RecordedAt ON Materials(RecordedAt);
CREATE INDEX IX_Materials_Supplier ON Materials(Supplier);
```

### 8. MaterialInventory Table
```sql
CREATE TABLE MaterialInventory (
    Id INT PRIMARY KEY IDENTITY(1,1),
    ItemName VARCHAR(100) NOT NULL,
    Description TEXT NULL,
    CurrentStock DECIMAL(10,2) NOT NULL DEFAULT 0,
    MinimumStock DECIMAL(10,2) NOT NULL DEFAULT 0,
    MaximumStock DECIMAL(10,2) NULL,
    Unit VARCHAR(20) NOT NULL DEFAULT 'units',
    UnitCost DECIMAL(10,2) NULL,
    Supplier VARCHAR(100) NULL,
    MaterialCode VARCHAR(50) UNIQUE NULL,
    Category VARCHAR(50) NULL,
    StorageLocation VARCHAR(100) NULL,
    ReorderPoint DECIMAL(10,2) NULL,
    IsActive BIT DEFAULT 1,
    IsDeleted BIT DEFAULT 0,
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE(),
    LastRestockedAt DATETIME NULL,
    
    -- Check Constraints
    CONSTRAINT CK_MaterialInventory_CurrentStock CHECK (CurrentStock >= 0),
    CONSTRAINT CK_MaterialInventory_MinimumStock CHECK (MinimumStock >= 0)
);

-- Indexes
CREATE INDEX IX_MaterialInventory_ItemName ON MaterialInventory(ItemName);
CREATE INDEX IX_MaterialInventory_Category ON MaterialInventory(Category);
CREATE INDEX IX_MaterialInventory_Supplier ON MaterialInventory(Supplier);
CREATE INDEX IX_MaterialInventory_CurrentStock ON MaterialInventory(CurrentStock);
```

### 9. Notifications Table
```sql
CREATE TABLE Notifications (
    Id INT PRIMARY KEY IDENTITY(1,1),
    UserId INT NOT NULL,
    Title VARCHAR(200) NOT NULL,
    Message TEXT NOT NULL,
    Type VARCHAR(50) NOT NULL DEFAULT 'INFO',  -- INFO, SUCCESS, WARNING, ERROR
    Category VARCHAR(50) NOT NULL DEFAULT 'SYSTEM',  -- SYSTEM, JOB, ASSIGNMENT, MATERIAL
    RelatedId INT NULL,  -- Related entity ID (job, assignment, etc.)
    RelatedType VARCHAR(50) NULL,  -- Related entity type
    IsRead BIT DEFAULT 0,
    IsDeleted BIT DEFAULT 0,
    CreatedAt DATETIME DEFAULT GETDATE(),
    ReadAt DATETIME NULL,
    
    -- Foreign Key Constraint
    CONSTRAINT FK_Notifications_UserId FOREIGN KEY (UserId) REFERENCES Users(Id),
    
    -- Check Constraints
    CONSTRAINT CK_Notifications_Type CHECK (Type IN ('INFO', 'SUCCESS', 'WARNING', 'ERROR')),
    CONSTRAINT CK_Notifications_Category CHECK (Category IN ('SYSTEM', 'JOB', 'ASSIGNMENT', 'MATERIAL', 'USER'))
);

-- Indexes
CREATE INDEX IX_Notifications_UserId ON Notifications(UserId);
CREATE INDEX IX_Notifications_IsRead ON Notifications(IsRead);
CREATE INDEX IX_Notifications_Type ON Notifications(Type);
CREATE INDEX IX_Notifications_CreatedAt ON Notifications(CreatedAt);
CREATE INDEX IX_Notifications_User_Read ON Notifications(UserId, IsRead);
```

### 10. AuditLog Table
```sql
CREATE TABLE AuditLog (
    Id INT PRIMARY KEY IDENTITY(1,1),
    UserId INT NULL,
    Action VARCHAR(50) NOT NULL,
    EntityType VARCHAR(50) NOT NULL,
    EntityId INT NULL,
    OldValue TEXT NULL,
    NewValue TEXT NULL,
    Description TEXT NULL,
    IPAddress VARCHAR(45) NULL,
    UserAgent VARCHAR(500) NULL,
    SessionId VARCHAR(100) NULL,
    CreatedAt DATETIME DEFAULT GETDATE(),
    
    -- Foreign Key Constraint
    CONSTRAINT FK_AuditLog_UserId FOREIGN KEY (UserId) REFERENCES Users(Id)
);

-- Indexes
CREATE INDEX IX_AuditLog_UserId ON AuditLog(UserId);
CREATE INDEX IX_AuditLog_Action ON AuditLog(Action);
CREATE INDEX IX_AuditLog_EntityType ON AuditLog(EntityType);
CREATE INDEX IX_AuditLog_CreatedAt ON AuditLog(CreatedAt);
CREATE INDEX IX_AuditLog_Entity ON AuditLog(EntityType, EntityId);
```

### 11. SystemSettings Table
```sql
CREATE TABLE SystemSettings (
    Id INT PRIMARY KEY IDENTITY(1,1),
    SettingKey VARCHAR(100) UNIQUE NOT NULL,
    SettingValue TEXT NULL,
    Description TEXT NULL,
    DataType VARCHAR(20) NOT NULL DEFAULT 'STRING',  -- STRING, INTEGER, BOOLEAN, DECIMAL
    Category VARCHAR(50) NOT NULL DEFAULT 'GENERAL',
    IsEditable BIT DEFAULT 1,
    CreatedAt DATETIME DEFAULT GETDATE(),
    UpdatedAt DATETIME DEFAULT GETDATE(),
    UpdatedBy INT NULL,
    
    -- Foreign Key Constraint
    CONSTRAINT FK_SystemSettings_UpdatedBy FOREIGN KEY (UpdatedBy) REFERENCES Users(Id),
    
    -- Check Constraints
    CONSTRAINT CK_SystemSettings_DataType CHECK (DataType IN ('STRING', 'INTEGER', 'BOOLEAN', 'DECIMAL'))
);

-- Indexes
CREATE INDEX IX_SystemSettings_SettingKey ON SystemSettings(SettingKey);
CREATE INDEX IX_SystemSettings_Category ON SystemSettings(Category);
```

### 12. Reports Table
```sql
CREATE TABLE Reports (
    Id INT PRIMARY KEY IDENTITY(1,1),
    Name VARCHAR(200) NOT NULL,
    Description TEXT NULL,
    ReportType VARCHAR(50) NOT NULL,  -- JOB, ASSIGNMENT, MATERIAL, PERFORMANCE
    Parameters TEXT NULL,  -- JSON string of parameters
    GeneratedBy INT NOT NULL,
    FilePath VARCHAR(500) NULL,
    FileSize INT NULL,
    Status VARCHAR(20) NOT NULL DEFAULT 'GENERATING',  -- GENERATING, COMPLETED, FAILED
    GeneratedAt DATETIME DEFAULT GETDATE(),
    ExpiresAt DATETIME NULL,
    IsActive BIT DEFAULT 1,
    IsDeleted BIT DEFAULT 0,
    
    -- Foreign Key Constraint
    CONSTRAINT FK_Reports_GeneratedBy FOREIGN KEY (GeneratedBy) REFERENCES Users(Id),
    
    -- Check Constraints
    CONSTRAINT CK_Reports_ReportType CHECK (ReportType IN ('JOB', 'ASSIGNMENT', 'MATERIAL', 'PERFORMANCE', 'SYSTEM')),
    CONSTRAINT CK_Reports_Status CHECK (Status IN ('GENERATING', 'COMPLETED', 'FAILED', 'EXPIRED'))
);

-- Indexes
CREATE INDEX IX_Reports_ReportType ON Reports(ReportType);
CREATE INDEX IX_Reports_GeneratedBy ON Reports(GeneratedBy);
CREATE INDEX IX_Reports_Status ON Reports(Status);
CREATE INDEX IX_Reports_GeneratedAt ON Reports(GeneratedAt);
```

## Database Relationships

### Entity Relationship Diagram
```
Users (1) ──────── (∞) JobRequests (SubmittedBy)
Users (1) ──────── (∞) JobRequests (AssignedTo)
Users (1) ──────── (∞) Workers
Users (1) ──────── (∞) Assignments (AssignedBy)
Users (1) ──────── (∞) Materials (RecordedBy)
Users (1) ──────── (∞) Notifications
Users (1) ──────── (∞) AuditLog
Users (1) ──────── (∞) Reports (GeneratedBy)

Departments (1) ──── (∞) JobRequests
JobCategories (1) ──── (∞) JobRequests

JobRequests (1) ────── (∞) Assignments
JobRequests (1) ────── (∞) Materials

Workers (1) ────────── (∞) Assignments

MaterialInventory (1) ── (∞) Materials (ItemName)
```

### Relationship Types
- **One-to-Many**: Users to JobRequests, Departments to JobRequests
- **One-to-One**: Users to Workers
- **Many-to-Many**: Workers and JobRequests through Assignments

## Database Indexes Strategy

### Clustered Indexes
- **Primary Keys**: All tables have clustered primary key on Id column
- **Performance**: Optimized for most common query patterns

### Non-Clustered Indexes
- **Foreign Keys**: All foreign key columns indexed
- **Search Columns**: Frequently searched columns indexed
- **Date Columns**: Date columns indexed for time-based queries
- **Composite Indexes**: Multi-column indexes for common query patterns

### Index Maintenance
- **Statistics**: Regular statistics updates for query optimization
- **Rebuilding**: Periodic index rebuilding for performance
- **Monitoring**: Monitor index usage and fragmentation

## Database Views

### 1. JobSummaryView
```sql
CREATE VIEW JobSummaryView AS
SELECT 
    j.Id,
    j.Description,
    d.Name AS DepartmentName,
    c.Name AS CategoryName,
    j.Priority,
    j.Status,
    u.FirstName + ' ' + u.LastName AS SubmittedByName,
    w.FirstName + ' ' + w.LastName AS AssignedToName,
    j.DateCreated,
    j.AssignedAt,
    j.StartedAt,
    j.CompletedAt,
    DATEDIFF(HOUR, j.DateCreated, ISNULL(j.CompletedAt, GETDATE())) AS DurationHours
FROM JobRequests j
LEFT JOIN Departments d ON j.DepartmentId = d.Id
LEFT JOIN JobCategories c ON j.CategoryId = c.Id
LEFT JOIN Users u ON j.SubmittedBy = u.Id
LEFT JOIN Workers w ON j.AssignedTo = w.UserId;
```

### 2. WorkerPerformanceView
```sql
CREATE VIEW WorkerPerformanceView AS
SELECT 
    w.Id,
    w.FirstName,
    w.LastName,
    w.Specialization,
    COUNT(a.Id) AS TotalAssignments,
    SUM(CASE WHEN a.Status = 'COMPLETED' THEN 1 ELSE 0 END) AS CompletedAssignments,
    AVG(a.QualityRating) AS AverageQualityRating,
    AVG(a.ActualHours) AS AverageActualHours,
    AVG(a.EstimatedHours) AS AverageEstimatedHours
FROM Workers w
LEFT JOIN Assignments a ON w.Id = a.WorkerId
WHERE w.IsActive = 1
GROUP BY w.Id, w.FirstName, w.LastName, w.Specialization;
```

### 3. MaterialUsageView
```sql
CREATE VIEW MaterialUsageView AS
SELECT 
    m.ItemName,
    m.Unit,
    SUM(m.QuantityUsed) AS TotalUsed,
    SUM(m.QuantityUsed * m.UnitCost) AS TotalCost,
    COUNT(DISTINCT m.JobId) AS JobCount,
    AVG(m.UnitCost) AS AverageUnitCost
FROM Materials m
WHERE m.IsActive = 1
GROUP BY m.ItemName, m.Unit;
```

## Stored Procedures

### 1. sp_CreateJobRequest
```sql
CREATE PROCEDURE sp_CreateJobRequest
    @DepartmentId INT,
    @CategoryId INT,
    @Description TEXT,
    @Priority VARCHAR(20),
    @SubmittedBy INT,
    @Location VARCHAR(200),
    @Building VARCHAR(100),
    @Room VARCHAR(50)
AS
BEGIN
    SET NOCOUNT ON;
    
    DECLARE @JobId INT;
    
    INSERT INTO JobRequests (
        DepartmentId, CategoryId, Description, Priority, 
        SubmittedBy, Location, Building, Room
    )
    VALUES (
        @DepartmentId, @CategoryId, @Description, @Priority,
        @SubmittedBy, @Location, @Building, @Room
    );
    
    SET @JobId = SCOPE_IDENTITY();
    
    -- Create notification for supervisors
    INSERT INTO Notifications (UserId, Title, Message, Type, Category, RelatedId, RelatedType)
    SELECT 
        u.Id, 
        'New Job Request', 
        'A new maintenance request has been submitted: ' + @Description,
        'INFO', 
        'JOB',
        @JobId,
        'JOBREQUEST'
    FROM Users u
    WHERE u.Role = 'supervisor' AND u.IsActive = 1;
    
    SELECT @JobId AS JobId;
END;
```

### 2. sp_AssignJob
```sql
CREATE PROCEDURE sp_AssignJob
    @JobId INT,
    @WorkerId INT,
    @AssignedBy INT,
    @EstimatedHours INT,
    @Notes TEXT
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Create assignment
    INSERT INTO Assignments (
        JobId, WorkerId, AssignedBy, EstimatedHours, Notes
    )
    VALUES (
        @JobId, @WorkerId, @AssignedBy, @EstimatedHours, @Notes
    );
    
    -- Update job request
    UPDATE JobRequests
    SET 
        AssignedTo = @WorkerId,
        Status = 'ASSIGNED',
        AssignedAt = GETDATE(),
        UpdatedAt = GETDATE()
    WHERE Id = @JobId;
    
    -- Create notification for worker
    INSERT INTO Notifications (UserId, Title, Message, Type, Category, RelatedId, RelatedType)
    SELECT 
        w.UserId,
        'New Assignment',
        'You have been assigned a new job: ' + j.Description,
        'INFO',
        'ASSIGNMENT',
        @JobId,
        'JOBREQUEST'
    FROM Workers w
    WHERE w.Id = @WorkerId;
    
    -- Log assignment
    INSERT INTO AuditLog (UserId, Action, EntityType, EntityId, Description)
    VALUES (@AssignedBy, 'ASSIGN', 'JOBREQUEST', @JobId, 'Job assigned to worker ' + CAST(@WorkerId AS VARCHAR));
END;
```

### 3. sp_GenerateJobReport
```sql
CREATE PROCEDURE sp_GenerateJobReport
    @StartDate DATETIME,
    @EndDate DATETIME,
    @DepartmentId INT = NULL,
    @CategoryId INT = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        j.Id,
        d.Name AS DepartmentName,
        c.Name AS CategoryName,
        j.Description,
        j.Priority,
        j.Status,
        u.FirstName + ' ' + u.LastName AS SubmittedByName,
        w.FirstName + ' ' + w.LastName AS AssignedToName,
        j.DateCreated,
        j.AssignedAt,
        j.StartedAt,
        j.CompletedAt,
        DATEDIFF(HOUR, j.DateCreated, ISNULL(j.CompletedAt, GETDATE())) AS DurationHours,
        a.ActualHours,
        a.QualityRating,
        (SELECT SUM(m.QuantityUsed * m.UnitCost) 
         FROM Materials m 
         WHERE m.JobId = j.Id AND m.IsActive = 1) AS MaterialCost
    FROM JobRequests j
    LEFT JOIN Departments d ON j.DepartmentId = d.Id
    LEFT JOIN JobCategories c ON j.CategoryId = c.Id
    LEFT JOIN Users u ON j.SubmittedBy = u.Id
    LEFT JOIN Workers w ON j.AssignedTo = w.UserId
    LEFT JOIN Assignments a ON j.Id = a.JobId
    WHERE j.DateCreated BETWEEN @StartDate AND @EndDate
      AND j.IsActive = 1
      AND (@DepartmentId IS NULL OR j.DepartmentId = @DepartmentId)
      AND (@CategoryId IS NULL OR j.CategoryId = @CategoryId)
    ORDER BY j.DateCreated DESC;
END;
```

## Database Triggers

### 1. tr_JobRequest_Audit
```sql
CREATE TRIGGER tr_JobRequest_Audit
ON JobRequests
AFTER INSERT, UPDATE, DELETE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Insert
    IF EXISTS (SELECT * FROM inserted) AND NOT EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO AuditLog (Action, EntityType, EntityId, NewValue, Description)
        SELECT 
            'INSERT', 
            'JOBREQUEST', 
            Id, 
            'DepartmentId: ' + CAST(DepartmentId AS VARCHAR) + 
            ', CategoryId: ' + CAST(CategoryId AS VARCHAR) + 
            ', Description: ' + Description,
            'New job request created'
        FROM inserted;
    END
    
    -- Update
    IF EXISTS (SELECT * FROM inserted) AND EXISTS (SELECT * FROM deleted)
    BEGIN
        INSERT INTO AuditLog (Action, EntityType, EntityId, OldValue, NewValue, Description)
        SELECT 
            'UPDATE', 
            'JOBREQUEST', 
            i.Id, 
            'Status: ' + d.Status + ', AssignedTo: ' + CAST(d.AssignedTo AS VARCHAR),
            'Status: ' + i.Status + ', AssignedTo: ' + CAST(i.AssignedTo AS VARCHAR),
            'Job request updated'
        FROM inserted i
        JOIN deleted d ON i.Id = d.Id
        WHERE i.Status != d.Status OR i.AssignedTo != d.AssignedTo;
    END
    
    -- Delete
    IF EXISTS (SELECT * FROM deleted) AND NOT EXISTS (SELECT * FROM inserted)
    BEGIN
        INSERT INTO AuditLog (Action, EntityType, EntityId, Description)
        SELECT 
            'DELETE', 
            'JOBREQUEST', 
            Id, 
            'Job request deleted'
        FROM deleted;
    END
END;
```

### 2. tr_MaterialInventory_CheckLowStock
```sql
CREATE TRIGGER tr_MaterialInventory_CheckLowStock
ON MaterialInventory
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Check for low stock and create notifications
    INSERT INTO Notifications (UserId, Title, Message, Type, Category, RelatedId, RelatedType)
    SELECT DISTINCT
        u.Id,
        'Low Stock Alert',
        'Material ' + i.ItemName + ' is below minimum stock level. Current: ' + CAST(i.CurrentStock AS VARCHAR) + ', Minimum: ' + CAST(i.MinimumStock AS VARCHAR),
        'WARNING',
        'MATERIAL',
        i.Id,
        'MATERIALINVENTORY'
    FROM inserted i
    JOIN Users u ON u.Role = 'supervisor' AND u.IsActive = 1
    WHERE i.CurrentStock <= i.MinimumStock
      AND NOT EXISTS (
          SELECT 1 FROM Notifications n 
          WHERE n.UserId = u.Id 
            AND n.RelatedId = i.Id 
            AND n.RelatedType = 'MATERIALINVENTORY'
            AND n.Type = 'WARNING'
            AND n.IsRead = 0
      );
END;
```

## Database Security

### User Roles and Permissions
```sql
-- Create database roles
CREATE ROLE MaintenanceAdmin;
CREATE ROLE MaintenanceSupervisor;
CREATE ROLE MaintenanceStaff;
CREATE ROLE MaintenanceWorker;

-- Grant permissions to roles
GRANT SELECT, INSERT, UPDATE, DELETE ON JobRequests TO MaintenanceAdmin;
GRANT SELECT, INSERT, UPDATE ON JobRequests TO MaintenanceSupervisor;
GRANT SELECT, INSERT ON JobRequests TO MaintenanceStaff;
GRANT SELECT, UPDATE ON JobRequests TO MaintenanceWorker;

GRANT SELECT, INSERT, UPDATE, DELETE ON Assignments TO MaintenanceAdmin;
GRANT SELECT, INSERT, UPDATE ON Assignments TO MaintenanceSupervisor;
GRANT SELECT ON Assignments TO MaintenanceStaff;
GRANT SELECT, UPDATE ON Assignments TO MaintenanceWorker;
```

### Data Encryption
```sql
-- Enable Transparent Data Encryption (TDE)
CREATE MASTER KEY ENCRYPTION BY PASSWORD = 'YourStrongPassword';
CREATE CERTIFICATE MaintenanceCert WITH SUBJECT = 'Maintenance Database Certificate';
CREATE DATABASE ENCRYPTION KEY WITH ALGORITHM = AES_256 ENCRYPTION BY SERVER CERTIFICATE MaintenanceCert;
ALTER DATABASE CentralServices_AM_DB SET ENCRYPTION ON;
```

## Database Performance Optimization

### Query Optimization
- **Execution Plans**: Regular review of query execution plans
- **Statistics**: Automatic statistics updates enabled
- **Parameterization**: Parameterized queries for plan reuse
- **Index Usage**: Monitor and optimize index usage

### Memory Optimization
- **Buffer Pool**: Configure appropriate buffer pool size
- **TempDB**: Optimize tempdb configuration
- **Memory Grants**: Monitor memory grant usage
- **Page Life Expectancy**: Monitor page life expectancy

### I/O Optimization
- **File Placement**: Separate data and log files
- **RAID Configuration**: Use appropriate RAID levels
- **Disk Partitioning**: Partition large tables
- **Backup Strategy**: Optimize backup performance

## Database Backup and Recovery

### Backup Strategy
```sql
-- Full backup (daily)
BACKUP DATABASE CentralServices_AM_DB 
TO DISK = 'C:\Backup\Maintenance_Full.bak'
WITH COMPRESSION, CHECKSUM;

-- Differential backup (every 4 hours)
BACKUP DATABASE CentralServices_AM_DB 
TO DISK = 'C:\Backup\Maintenance_Diff.bak'
WITH DIFFERENTIAL, COMPRESSION, CHECKSUM;

-- Transaction log backup (every 15 minutes)
BACKUP LOG CentralServices_AM_DB 
TO DISK = 'C:\Backup\Maintenance_Log.trn'
WITH COMPRESSION, CHECKSUM;
```

### Recovery Model
- **Recovery Model**: Full recovery model for point-in-time recovery
- **RetentionPolicy**: 30 days for backups
- **TestRestores**: Monthly test restore procedures
- **Documentation**: Complete recovery procedures documented

## Database Monitoring

### Performance Monitoring
- **SQL Server Agent**: Automated job scheduling
- **Performance Monitor**: System performance counters
- **Dynamic Management Views**: Query performance analysis
- **Extended Events**: Detailed event tracking

### Health Checks
- **Database Consistency**: Regular DBCC CHECKDB
- **Index Maintenance**: Automatic index rebuilding
- **Statistics Updates**: Automatic statistics updates
- **Space Monitoring**: Disk space usage tracking

---

**Database Schema Version**: 1.0  
**Last Updated**: 2026-04-05  
**Database Version**: SQL Server 2019+  
**Review Cycle**: Quarterly
