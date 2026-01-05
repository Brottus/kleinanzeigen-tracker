#!/bin/sh
# Docker entrypoint script for Job Scheduler
# Prints startup banner and ensures /app/data has correct permissions

set -e

# Print startup banner
echo "================================================================================"
echo " ____  __.__         .__                                   .__                        "
echo "│    │╱ _│  │   ____ │__│ ____ _____    ____ ________ ____ │__│ ____   ____   ____    "
echo "│      < │  │ _╱ __ ╲│  │╱    ╲╲__  ╲  ╱    ╲╲___   ╱╱ __ ╲│  │╱ ___╲_╱ __ ╲ ╱    ╲   "
echo "│    │  ╲│  │_╲  ___╱│  │   │  ╲╱ __ ╲│   │  ╲╱    ╱╲  ___╱│  ╱ ╱_╱  >  ___╱│   │  ╲  "
echo "│____│__ ╲____╱╲___  >__│___│  (____  ╱___│  ╱_____ ╲╲___  >__╲___  ╱ ╲___  >___│  ╱  "
echo "        ╲╱         ╲╱        ╲╱     ╲╱     ╲╱      ╲╱    ╲╱  ╱_____╱      ╲╱     ╲╱   "
echo "     ____.     ___.       _________      .__               .___    .__                "
echo "    │    │ ____╲_ │__    ╱   _____╱ ____ │  │__   ____   __│ _╱_ __│  │   ___________ "
echo "    │    │╱  _ ╲│ __ ╲   ╲_____  ╲_╱ ___╲│  │  ╲_╱ __ ╲ ╱ __ │  │  ╲  │ _╱ __ ╲_  __ ╲"
echo "╱╲__│    (  <_> ) ╲_╲ ╲  ╱        ╲  ╲___│   Y  ╲  ___╱╱ ╱_╱ │  │  ╱  │_╲  ___╱│  │ ╲╱"
echo "╲________│╲____╱│___  ╱ ╱_______  ╱╲___  >___│  ╱╲___  >____ │____╱│____╱╲___  >__│   "
echo "                    ╲╱          ╲╱     ╲╱     ╲╱     ╲╱     ╲╱               ╲╱       "
echo "================================================================================"
echo "  Version: 1.0.0"
echo "  Log Level: ${LOG_LEVEL:-INFO}"
echo "================================================================================"
echo ""

# Get database directory from DB_PATH environment variable (default: /app/data/jobs.db)
DB_PATH="${DB_PATH:-/app/data/jobs.db}"
DB_DIR=$(dirname "$DB_PATH")

echo "🔧 Checking database directory permissions..."
echo "   DB_PATH: $DB_PATH"
echo "   DB_DIR: $DB_DIR"

# Check if database directory exists
if [ ! -d "$DB_DIR" ]; then
    echo "❌ Database directory does not exist: $DB_DIR"
    exit 1
fi

# Check current ownership
CURRENT_OWNER=$(stat -c '%U:%G' "$DB_DIR" 2>/dev/null || stat -f '%Su:%Sg' "$DB_DIR" 2>/dev/null)
echo "   Current owner: $CURRENT_OWNER"

# If owned by root, we need to fix it
if [ "$CURRENT_OWNER" = "root:root" ]; then
    echo "⚠️  $DB_DIR is owned by root, attempting to fix permissions..."
    
    # Try to change ownership (this will only work if we're root or have permissions)
    if [ "$(id -u)" = "0" ]; then
        chown -R appuser:appuser "$DB_DIR"
        echo "✅ Permissions fixed: appuser:appuser"
    else
        echo "⚠️  Running as non-root user, cannot fix permissions"
        echo "   Volume should be pre-created with correct ownership"
        echo "   Run: docker run --rm -v scheduler-data:/data alpine chown -R 1000:1000 /data"
    fi
else
    echo "✅ Permissions OK: $CURRENT_OWNER"
fi

# Check if we can write to database directory
if [ -w "$DB_DIR" ]; then
    echo "✅ $DB_DIR is writable"
else
    echo "❌ $DB_DIR is NOT writable!"
    echo "   Current user: $(whoami) (UID: $(id -u))"
    echo "   Directory permissions: $(ls -ld "$DB_DIR")"
    exit 1
fi

echo "🚀 Starting application..."
echo ""

# Execute the main command (gunicorn)
exec "$@"
