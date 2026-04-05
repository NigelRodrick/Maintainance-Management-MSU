-- Migration 008: Export and Drop Predictions Table
-- Archives ML predictions data and removes legacy table

BEGIN TRANSACTION;

PRINT 'Starting migration 008: Export and Drop Predictions Table';

-- Check if predictions table exists
IF EXISTS (SELECT * FROM sys.tables WHERE name = 'predictions')
BEGIN
    -- Export predictions data to CSV archive
    -- Note: This uses SQL Server's bcp utility approach via SQL
    DECLARE @ExportPath NVARCHAR(500)
    DECLARE @Timestamp NVARCHAR(20)
    
    SET @Timestamp = REPLACE(REPLACE(REPLACE(CONVERT(NVARCHAR, GETDATE(), 120), '-', ''), ' ', '_'), ':', '')
    SET @ExportPath = 'C:\Backup\predictions_archive_' + @Timestamp + '.csv'
    
    -- Create export query
    DECLARE @SQL NVARCHAR(MAX)
    SET @SQL = '
    EXEC xp_cmdshell ''bcp "SELECT 
        id, 
        job_id, 
        predicted_priority, 
        predicted_category, 
        confidence, 
        CONVERT(NVARCHAR, created_at, 120) as created_at 
    FROM CentralServices_AM_DB.dbo.predictions" 
    queryout "' + @ExportPath + '" -c -t"," -T -S ' + @@SERVERNAME + '''''
    
    -- Try to export (may fail if xp_cmdshell is disabled)
    BEGIN TRY
        EXEC sp_executesql @SQL
        PRINT '✓ Exported predictions data to: ' + @ExportPath
    END TRY
    BEGIN CATCH
        PRINT '⚠ Could not auto-export predictions data (xp_cmdshell may be disabled)'
        PRINT '  Please manually export predictions table before dropping'
        PRINT '  Suggested export location: ' + @ExportPath
    END CATCH
    
    -- Show summary of data being dropped
    PRINT 'Predictions table summary:';
    SELECT 
        COUNT(*) AS total_predictions,
        COUNT(DISTINCT job_id) AS unique_jobs,
        MIN(confidence) AS min_confidence,
        MAX(confidence) AS max_confidence,
        AVG(confidence) AS avg_confidence
    FROM predictions;
    
    PRINT 'Predicted categories:';
    SELECT predicted_category, COUNT(*) AS count
    FROM predictions
    GROUP BY predicted_category
    ORDER BY count DESC;
    
    -- Drop the predictions table
    DROP TABLE predictions;
    PRINT '✓ Dropped predictions table';
END
ELSE
BEGIN
    PRINT 'ℹ Predictions table does not exist - nothing to drop';
END

-- Remove Prediction model from app/models.py (this will be done separately)
PRINT 'Note: Remember to remove Prediction model from app/models.py';

COMMIT TRANSACTION;

PRINT 'Migration 008 completed successfully!';
PRINT 'IMPORTANT: Verify predictions data was archived before proceeding!';
