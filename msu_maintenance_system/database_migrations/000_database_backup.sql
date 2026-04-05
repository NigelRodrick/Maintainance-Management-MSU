-- Database Backup Script for MSU Maintenance System
-- Creates a full backup before migration operations

DECLARE @BackupPath NVARCHAR(500)
DECLARE @DatabaseName NVARCHAR(100)
DECLARE @Timestamp NVARCHAR(20)

SET @DatabaseName = 'CentralServices_AM_DB'
SET @Timestamp = REPLACE(REPLACE(REPLACE(CONVERT(NVARCHAR, GETDATE(), 120), '-', ''), ' ', '_'), ':', '')
SET @BackupPath = 'C:\Backup\' + @DatabaseName + '_PreMigration_' + @Timestamp + '.bak'

-- Create backup directory if it doesn't exist
DECLARE @Result INT
EXEC master.dbo.xp_create_subdir 'C:\Backup'

-- Perform the backup
BACKUP DATABASE @DatabaseName 
TO DISK = @BackupPath
WITH FORMAT, 
COMPRESSION,
INIT,
NAME = @DatabaseName + ' Full Backup before Migration',
STATS = 10

PRINT 'Database backup completed successfully!'
PRINT 'Backup file location: ' + @BackupPath
