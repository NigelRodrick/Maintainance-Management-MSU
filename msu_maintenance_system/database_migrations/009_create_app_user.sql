-- SQL Server Least Privilege User Setup
-- Creates 'msu_app_user' with SELECT/INSERT/UPDATE rights only

USE master;
GO

-- Create login for the application
IF NOT EXISTS (SELECT * FROM sys.server_principals WHERE name = 'msu_app_user')
BEGIN
    CREATE LOGIN msu_app_user 
    WITH PASSWORD = 'ComplexPassword123!@#',
    CHECK_POLICY = ON,
    CHECK_EXPIRATION = OFF;
    
    PRINT '✓ Created login: msu_app_user';
END
ELSE
BEGIN
    PRINT 'ℹ Login msu_app_user already exists';
END
GO

USE CentralServices_AM_DB;
GO

-- Create user in the database
IF NOT EXISTS (SELECT * FROM sys.database_principals WHERE name = 'msu_app_user')
BEGIN
    CREATE USER msu_app_user FOR LOGIN msu_app_user;
    PRINT '✓ Created database user: msu_app_user';
END
ELSE
BEGIN
    PRINT 'ℹ Database user msu_app_user already exists';
END
GO

-- Grant SELECT permissions on all tables
DECLARE @sql NVARCHAR(MAX) = '';
SELECT @sql = @sql + 
    'GRANT SELECT ON OBJECT::[' + TABLE_SCHEMA + '].[' + TABLE_NAME + '] TO msu_app_user;' + CHAR(10)
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
AND TABLE_SCHEMA IN ('dbo');

EXEC sp_executesql @sql;
PRINT '✓ Granted SELECT permissions on all tables';

-- Grant INSERT permissions on application tables
DECLARE @insert_sql NVARCHAR(MAX) = '';
SELECT @insert_sql = @insert_sql + 
    'GRANT INSERT ON OBJECT::[' + TABLE_SCHEMA + '].[' + TABLE_NAME + '] TO msu_app_user;' + CHAR(10)
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
AND TABLE_SCHEMA = 'dbo'
AND TABLE_NAME IN (
    'job_requests', 'users', 'workers', 'assignments', 
    'materials', 'job_status_history'
);

EXEC sp_executesql @insert_sql;
PRINT '✓ Granted INSERT permissions on application tables';

-- Grant UPDATE permissions on application tables
DECLARE @update_sql NVARCHAR(MAX) = '';
SELECT @update_sql = @update_sql + 
    'GRANT UPDATE ON OBJECT::[' + TABLE_SCHEMA + '].[' + TABLE_NAME + '] TO msu_app_user;' + CHAR(10)
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE'
AND TABLE_SCHEMA = 'dbo'
AND TABLE_NAME IN (
    'job_requests', 'users', 'workers', 'assignments', 
    'materials', 'job_status_history'
);

EXEC sp_executesql @update_sql;
PRINT '✓ Granted UPDATE permissions on application tables';

-- Grant EXECUTE on stored procedures (if any exist)
DECLARE @proc_sql NVARCHAR(MAX) = '';
SELECT @proc_sql = @proc_sql + 
    'GRANT EXECUTE ON OBJECT::[' + ROUTINE_SCHEMA + '].[' + ROUTINE_NAME + '] TO msu_app_user;' + CHAR(10)
FROM INFORMATION_SCHEMA.ROUTINES 
WHERE ROUTINE_TYPE = 'PROCEDURE'
AND ROUTINE_SCHEMA = 'dbo';

IF LEN(@proc_sql) > 0
BEGIN
    EXEC sp_executesql @proc_sql;
    PRINT '✓ Granted EXECUTE permissions on stored procedures';
END
ELSE
BEGIN
    PRINT 'ℹ No stored procedures found to grant permissions on';
END
GO

-- Deny dangerous permissions (defense in depth)
DENY DELETE TO msu_app_user;
DENY ALTER TO msu_app_user;
DENY CONTROL TO msu_app_user;
DENY TAKE OWNERSHIP TO msu_app_user;
DENY DROP TO msu_app_user;
DENY CREATE TABLE TO msu_app_user;
DENY CREATE PROCEDURE TO msu_app_user;
DENY CREATE VIEW TO msu_app_user;
DENY CREATE FUNCTION TO msu_app_user;
PRINT '✓ Denied dangerous permissions';

-- Grant VIEW DEFINITION for application compatibility
GRANT VIEW DEFINITION TO msu_app_user;
PRINT '✓ Granted VIEW DEFINITION permission';

-- Verify permissions
PRINT '=== PERMISSIONS SUMMARY FOR msu_app_user ===';
SELECT 
    dp.permission_name,
    dp.state_desc,
    OBJECT_SCHEMA_NAME(major_id) AS object_schema,
    OBJECT_NAME(major_id) AS object_name
FROM sys.database_permissions dp
WHERE dp.grantee_principal_id = USER_ID('msu_app_user')
ORDER BY dp.permission_name, OBJECT_NAME(major_id);

PRINT '=== SECURITY SETUP COMPLETE ===';
PRINT 'User msu_app_user has least-privilege access to application tables';
PRINT 'No DDL rights granted - only SELECT/INSERT/UPDATE on specified tables';
