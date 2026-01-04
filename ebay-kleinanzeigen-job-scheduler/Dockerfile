# Service 2: Job Scheduler - Dockerfile
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install system dependencies (Alpine uses apk instead of apt)
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for database (will be mounted as volume)
RUN mkdir -p /app/data

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

# Run as non-root user for security
RUN adduser -D appuser && chown -R appuser:appuser /app
USER appuser

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:3001", "--workers", "1", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "server:app"]
