#!/bin/bash
# Database Backup Script
# Creates automated database backups with rotation

set -e

# Configuration
DB_SERVER="${DB_SERVER:-localhost}"
DB_NAME="${DB_NAME:-CentralServices_AM_DB}"
DB_USER="${DB_USER:-msu_app_user}"
DB_PASSWORD="${DB_PASSWORD:-ComplexPassword123!@#}"
BACKUP_DIR="${BACKUP_DIR:-/var/backups/msu_maintenance}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
BACKUP_TYPE="${BACKUP_TYPE:-FULL}"  # FULL, DIFFERENTIAL, or LOG
COMPRESSION="${COMPRESSION:-gzip}"  # gzip, bzip2, or none
S3_BUCKET="${S3_BUCKET:-}"  # Optional S3 bucket for offsite backup

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

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate backup filename
TIMESTAMP=$(date +'%Y%m%d_%H%M%S')
BACKUP_FILENAME="${DB_NAME}_${BACKUP_TYPE}_${TIMESTAMP}.sql"
BACKUP_PATH="$BACKUP_DIR/$BACKUP_FILENAME"

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

# Function to create full backup
create_full_backup() {
    log "Creating full database backup..."
    
    local backup_cmd="sqlcmd -S \"$DB_SERVER\" -U \"$DB_USER\" -P \"$DB_PASSWORD\" -Q \"
        BACKUP DATABASE [$DB_NAME] 
        TO DISK = '$BACKUP_PATH'
        WITH NOFORMAT, NOINIT, 
        NAME = 'MSU_Maintenance_Full_Backup_$TIMESTAMP',
        SKIP, NOREWIND, NOUNLOAD, STATS = 10,
        CHECKSUM;
    \""
    
    if eval "$backup_cmd"; then
        log "Full backup created successfully: $BACKUP_PATH"
        return 0
    else
        error "Failed to create full backup"
        return 1
    fi
}

# Function to create differential backup
create_differential_backup() {
    log "Creating differential database backup..."
    
    local backup_cmd="sqlcmd -S \"$DB_SERVER\" -U \"$DB_USER\" -P \"$DB_PASSWORD\" -Q \"
        BACKUP DATABASE [$DB_NAME] 
        TO DISK = '$BACKUP_PATH'
        WITH DIFFERENTIAL, NOFORMAT, NOINIT,
        NAME = 'MSU_Maintenance_Differential_Backup_$TIMESTAMP',
        SKIP, NOREWIND, NOUNLOAD, STATS = 10,
        CHECKSUM;
    \""
    
    if eval "$backup_cmd"; then
        log "Differential backup created successfully: $BACKUP_PATH"
        return 0
    else
        error "Failed to create differential backup"
        return 1
    fi
}

# Function to create transaction log backup
create_log_backup() {
    log "Creating transaction log backup..."
    
    local backup_cmd="sqlcmd -S \"$DB_SERVER\" -U \"$DB_USER\" -P \"$DB_PASSWORD\" -Q \"
        BACKUP LOG [$DB_NAME] 
        TO DISK = '$BACKUP_PATH'
        WITH NOFORMAT, NOINIT,
        NAME = 'MSU_Maintenance_Log_Backup_$TIMESTAMP',
        SKIP, NOREWIND, NOUNLOAD, STATS = 10;
    \""
    
    if eval "$backup_cmd"; then
        log "Log backup created successfully: $BACKUP_PATH"
        return 0
    else
        error "Failed to create log backup"
        return 1
    fi
}

# Function to compress backup
compress_backup() {
    local file="$1"
    
    if [ "$COMPRESSION" = "gzip" ]; then
        log "Compressing backup with gzip..."
        gzip "$file"
        BACKUP_PATH="${file}.gz"
        log "Backup compressed: ${BACKUP_PATH}"
    elif [ "$COMPRESSION" = "bzip2" ]; then
        log "Compressing backup with bzip2..."
        bzip2 "$file"
        BACKUP_PATH="${file}.bz2"
        log "Backup compressed: ${BACKUP_PATH}"
    else
        log "No compression specified"
    fi
}

# Function to upload to S3
upload_to_s3() {
    local file="$1"
    
    if [ -n "$S3_BUCKET" ]; then
        log "Uploading backup to S3: $S3_BUCKET"
        
        if command -v aws &> /dev/null; then
            aws s3 cp "$file" "s3://$S3_BUCKET/database-backups/" --storage-class GLACIER_IR || {
                error "Failed to upload backup to S3"
                return 1
            }
            log "Backup uploaded to S3 successfully"
        else
            warn "AWS CLI not found. Skipping S3 upload."
        fi
    fi
}

# Function to cleanup old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    
    # Find and remove old backup files
    local deleted_count=0
    while IFS= read -r -d '' file; do
        rm -f "$file"
        ((deleted_count++))
    done < <(find "$BACKUP_DIR" -name "*.sql*" -type f -mtime +$RETENTION_DAYS -print0 2>/dev/null)
    
    log "Deleted $deleted_count old backup files"
    
    # Cleanup S3 if configured
    if [ -n "$S3_BUCKET" ] && command -v aws &> /dev/null; then
        log "Cleaning up old S3 backups..."
        local s3_deleted=$(aws s3 ls "s3://$S3_BUCKET/database-backups/" | awk "\$1 < \"$(date -d '$RETENTION_DAYS days ago' '+%Y-%m-%d')\" {print \$4}" | wc -l)
        if [ "$s3_deleted" -gt 0 ]; then
            aws s3 ls "s3://$S3_BUCKET/database-backups/" | awk "\$1 < \"$(date -d '$RETENTION_DAYS days ago' '+%Y-%m-%d')\" {print \$4}" | xargs -I {} aws s3 rm "s3://$S3_BUCKET/database-backups/{}"
            log "Deleted $s3_deleted old S3 backups"
        fi
    fi
}

# Function to verify backup integrity
verify_backup() {
    local file="$1"
    
    log "Verifying backup integrity..."
    
    # Check if file exists and is not empty
    if [ ! -s "$file" ]; then
        error "Backup file is empty or does not exist: $file"
        return 1
    fi
    
    # For compressed files, check compression integrity
    if [[ "$file" == *.gz ]]; then
        if ! gzip -t "$file" 2>/dev/null; then
            error "Compressed backup file is corrupted: $file"
            return 1
        fi
    elif [[ "$file" == *.bz2 ]]; then
        if ! bzip2 -t "$file" 2>/dev/null; then
            error "Compressed backup file is corrupted: $file"
            return 1
        fi
    fi
    
    log "Backup integrity verified: $file"
    return 0
}

# Function to create backup manifest
create_manifest() {
    local backup_file="$1"
    local manifest_file="${backup_file}.manifest"
    
    log "Creating backup manifest..."
    
    cat > "$manifest_file" << EOF
Backup Manifest
===============
Backup Type: $BACKUP_TYPE
Database: $DB_NAME
Server: $DB_SERVER
Created: $(date)
Filename: $backup_file
Size: $(du -h "$backup_file" | cut -f1)
Checksum: $(sha256sum "$backup_file" | cut -d' ' -f1)
Compression: $COMPRESSION
Retention: $RETENTION_DAYS days
EOF
    
    log "Backup manifest created: $manifest_file"
}

# Main backup process
log "Starting database backup process..."
log "Backup Type: $BACKUP_TYPE"
log "Database: $DB_NAME"
log "Server: $DB_SERVER"

# Create backup based on type
case "$BACKUP_TYPE" in
    "FULL")
        create_full_backup || exit 1
        ;;
    "DIFFERENTIAL")
        create_differential_backup || exit 1
        ;;
    "LOG")
        create_log_backup || exit 1
        ;;
    *)
        error "Invalid backup type: $BACKUP_TYPE. Use FULL, DIFFERENTIAL, or LOG."
        exit 1
        ;;
esac

# Compress backup if specified
if [ "$COMPRESSION" != "none" ]; then
    compress_backup "$BACKUP_PATH" || exit 1
fi

# Verify backup integrity
verify_backup "$BACKUP_PATH" || exit 1

# Create backup manifest
create_manifest "$BACKUP_PATH"

# Upload to S3 if configured
upload_to_s3 "$BACKUP_PATH"

# Cleanup old backups
cleanup_old_backups

# Log backup summary
BACKUP_SIZE=$(du -h "$BACKUP_PATH" | cut -f1)
BACKUP_CHECKSUM=$(sha256sum "$BACKUP_PATH" | cut -d' ' -f1)

log "Backup completed successfully!"
log "Backup file: $BACKUP_PATH"
log "Backup size: $BACKUP_SIZE"
log "Checksum: $BACKUP_CHECKSUM"

# Send notification if configured (optional)
if [ -n "$NOTIFICATION_EMAIL" ]; then
    log "Sending backup notification to $NOTIFICATION_EMAIL"
    echo "Database backup completed successfully.

Details:
- Database: $DB_NAME
- Server: $DB_SERVER
- Backup Type: $BACKUP_TYPE
- File: $BACKUP_PATH
- Size: $BACKUP_SIZE
- Created: $(date)
- Checksum: $BACKUP_CHECKSUM" | mail -s "Database Backup Completed: $DB_NAME" "$NOTIFICATION_EMAIL"
fi

exit 0
