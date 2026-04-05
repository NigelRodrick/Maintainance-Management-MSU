#!/bin/bash
# Database Migration Script
# Runs all database migrations in order

set -e

# Configuration
DB_SERVER="${DB_SERVER:-localhost}"
DB_NAME="${DB_NAME:-CentralServices_AM_DB}"
DB_USER="${DB_USER:-msu_app_user}"
DB_PASSWORD="${DB_PASSWORD:-ComplexPassword123!@#}"
MIGRATIONS_DIR="database_migrations"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Check if sqlcmd is available
if ! command -v sqlcmd &> /dev/null; then
    error "sqlcmd is not installed or not in PATH"
    exit 1
fi

# Test database connection
log "Testing database connection..."
if ! sqlcmd -S "$DB_SERVER" -U "$DB_USER" -P "$DB_PASSWORD" -Q "SELECT 1" -d "$DB_NAME" &> /dev/null; then
    error "Cannot connect to database. Please check connection parameters."
    exit 1
fi

log "Database connection successful"

# Get list of migration files
MIGRATION_FILES=($(ls -v "$MIGRATIONS_DIR"/*.sql 2>/dev/null || true))

if [ ${#MIGRATION_FILES[@]} -eq 0 ]; then
    warn "No migration files found in $MIGRATIONS_DIR"
    exit 0
fi

log "Found ${#MIGRATION_FILES[@]} migration files"

# Create migrations table to track applied migrations
log "Creating migrations tracking table..."
sqlcmd -S "$DB_SERVER" -U "$DB_USER" -P "$DB_PASSWORD" -d "$DB_NAME" -Q "
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'schema_migrations')
BEGIN
    CREATE TABLE schema_migrations (
        id INT IDENTITY(1,1) PRIMARY KEY,
        filename NVARCHAR(255) NOT NULL UNIQUE,
        applied_at DATETIME2 NOT NULL DEFAULT GETUTCDATE(),
        checksum NVARCHAR(64) NOT NULL
    );
    PRINT 'Created schema_migrations table';
END
ELSE
BEGIN
    PRINT 'schema_migrations table already exists';
END
" || {
    error "Failed to create migrations tracking table"
    exit 1
}

# Function to calculate file checksum
calculate_checksum() {
    local file="$1"
    sha256sum "$file" | cut -d' ' -f1
}

# Function to check if migration has been applied
is_migration_applied() {
    local filename="$1"
    local checksum="$2"
    
    local result=$(sqlcmd -S "$DB_SERVER" -U "$DB_USER" -P "$DB_PASSWORD" -d "$DB_NAME" -Q "
        SELECT COUNT(*) FROM schema_migrations 
        WHERE filename = '$filename' AND checksum = '$checksum'
    " -h -1 | tr -d '[:space:]')
    
    [ "$result" = "1" ]
}

# Function to mark migration as applied
mark_migration_applied() {
    local filename="$1"
    local checksum="$2"
    
    sqlcmd -S "$DB_SERVER" -U "$DB_USER" -P "$DB_PASSWORD" -d "$DB_NAME" -Q "
        INSERT INTO schema_migrations (filename, checksum)
        VALUES ('$filename', '$checksum')
    " || {
        error "Failed to mark migration $filename as applied"
        return 1
    }
}

# Run migrations
APPLIED_COUNT=0
SKIPPED_COUNT=0
FAILED_COUNT=0

for migration_file in "${MIGRATION_FILES[@]}"; do
    filename=$(basename "$migration_file")
    checksum=$(calculate_checksum "$migration_file")
    
    log "Processing migration: $filename"
    
    # Check if migration has already been applied
    if is_migration_applied "$filename" "$checksum"; then
        warn "Migration $filename already applied with same checksum. Skipping."
        ((SKIPPED_COUNT++))
        continue
    fi
    
    # Check if migration exists with different checksum
    if sqlcmd -S "$DB_SERVER" -U "$DB_USER" -P "$DB_PASSWORD" -d "$DB_NAME" -Q "
        SELECT COUNT(*) FROM schema_migrations WHERE filename = '$filename'
    " -h -1 | tr -d '[:space:]' | grep -q "1"; then
        warn "Migration $filename exists with different checksum. This may indicate file modification."
        read -p "Do you want to reapply this migration? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            warn "Skipping migration $filename"
            ((SKIPPED_COUNT++))
            continue
        fi
    fi
    
    # Apply migration
    log "Applying migration: $filename"
    
    if sqlcmd -S "$DB_SERVER" -U "$DB_USER" -P "$DB_PASSWORD" -d "$DB_NAME" -i "$migration_file"; then
        log "Successfully applied migration: $filename"
        mark_migration_applied "$filename" "$checksum"
        ((APPLIED_COUNT++))
    else
        error "Failed to apply migration: $filename"
        ((FAILED_COUNT++))
        
        # Ask whether to continue
        read -p "Continue with remaining migrations? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            error "Migration process aborted by user"
            exit 1
        fi
    fi
done

# Summary
log "Migration process completed"
log "Applied: $APPLIED_COUNT migrations"
log "Skipped: $SKIPPED_COUNT migrations"
log "Failed: $FAILED_COUNT migrations"

if [ $FAILED_COUNT -gt 0 ]; then
    error "Some migrations failed. Please review the errors above."
    exit 1
else
    log "All migrations completed successfully!"
fi

# Show migration status
log "Current migration status:"
sqlcmd -S "$DB_SERVER" -U "$DB_USER" -P "$DB_PASSWORD" -d "$DB_NAME" -Q "
    SELECT filename, applied_at 
    FROM schema_migrations 
    ORDER BY applied_at;
"
