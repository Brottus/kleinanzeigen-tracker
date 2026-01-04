# Service 2: Job Scheduler - Dockerfile
FROM python:3.14-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

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

# Environment variables with defaults
ENV PORT=3001 \
    DB_PATH=/app/data/jobs.db \
    ADMIN_USERNAME=admin \
    ADMIN_PASSWORD=admin \
    SESSION_SECRET=change-this-to-a-random-secret-key \
    LOG_LEVEL=INFO

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:3001/health', timeout=5)"

# Run with gunicorn for production
CMD ["gunicorn", "--bind", "0.0.0.0:3001", "--workers", "1", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "server:app"]
