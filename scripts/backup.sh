#!/bin/bash

# Database backup script for FastAPI User Management System

set -e

# Configuration
DB_HOST=${DB_HOST:-db}
DB_PORT=${DB_PORT:-5432}
DB_NAME=${DB_NAME:-fastapi_users}
DB_USER=${DB_USER:-fastapi_user}
BACKUP_DIR=${BACKUP_DIR:-/backups}
RETENTION_DAYS=${RETENTION_DAYS:-30}

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Generate backup filename with timestamp
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_${DB_NAME}_${TIMESTAMP}.sql"
BACKUP_FILE_COMPRESSED="$BACKUP_FILE.gz"

echo "Starting database backup..."
echo "Database: $DB_NAME"
echo "Host: $DB_HOST:$DB_PORT"
echo "User: $DB_USER"
echo "Backup file: $BACKUP_FILE_COMPRESSED"

# Create backup
pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
    --verbose \
    --no-password \
    --format=plain \
    --no-privileges \
    --no-tablespaces \
    --quote-all-identifiers \
    > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

# Verify backup was created
if [ -f "$BACKUP_FILE_COMPRESSED" ]; then
    BACKUP_SIZE=$(du -h "$BACKUP_FILE_COMPRESSED" | cut -f1)
    echo "✅ Backup completed successfully!"
    echo "📁 File: $BACKUP_FILE_COMPRESSED"
    echo "📏 Size: $BACKUP_SIZE"
else
    echo "❌ Backup failed!"
    exit 1
fi

# Clean up old backups
echo "🧹 Cleaning up backups older than $RETENTION_DAYS days..."
find "$BACKUP_DIR" -name "backup_${DB_NAME}_*.sql.gz" -mtime +$RETENTION_DAYS -delete

# List remaining backups
echo "📋 Remaining backups:"
ls -lh "$BACKUP_DIR"/backup_${DB_NAME}_*.sql.gz || echo "No backups found"

echo "✨ Backup process completed!"