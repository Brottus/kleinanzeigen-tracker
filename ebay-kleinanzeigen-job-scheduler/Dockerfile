# Service 2: Job Scheduler - Dockerfile
FROM python:3.14-alpine

# Set working directory
WORKDIR /app

# Install system dependencies (Alpine uses apk instead of apt)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    su-exec

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code (only what's needed)
COPY server.py .
COPY database.py .
COPY openapi.yaml .
COPY templates/ templates/
COPY static/ static/

# Expose port
EXPOSE 3001

# Environment variables with defaults (only non-sensitive ones)
ENV PORT=3001 \
    DB_PATH=/app/data/jobs.db \
    ADMIN_USERNAME=admin \
    LOG_LEVEL=INFO

# NOTE: Security-sensitive variables MUST be set at runtime:
# - ADMIN_PASSWORD (required)
# - SESSION_SECRET (required)
# - JWT_SECRET (required)
# - SCRAPER_API_KEY (required)
# - SCRAPER_API_URL (optional, defaults to http://scraper:3000)

# Health check (using wget which is built into Alpine)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3001/health || exit 1

# Create non-root user and set up data directory with proper permissions
RUN adduser -D appuser && \
    mkdir -p /app/data && \
    chown -R appuser:appuser /app

# Copy and set up entrypoint script (set permissions in same layer)
COPY --chmod=755 docker-entrypoint.sh /usr/local/bin/docker-entrypoint.sh

# Don't switch to appuser yet - entrypoint needs to run as root to fix permissions
# The entrypoint script will switch to appuser after fixing permissions

# Use entrypoint to fix permissions, then switch to appuser and run gunicorn
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["su-exec", "appuser", "gunicorn", \
     "--bind", "0.0.0.0:3001", \
     "--workers", "1", \
     "--threads", "2", \
     "--timeout", "120", \
     "--log-level", "info", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--capture-output", \
     "--enable-stdio-inheritance", \
     "server:app"]
