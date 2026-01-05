FROM python:3.14-alpine

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY server.py .
COPY openapi.yaml .
COPY --chown=appuser:appuser --chmod=750 docker-entrypoint.sh .

# Expose port
EXPOSE 3000

# Health check using wget (already in alpine)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Run as non-root user for security
RUN adduser -D appuser && chown -R appuser:appuser /app
USER appuser

# Use entrypoint script that prints banner before starting Gunicorn
ENTRYPOINT ["./docker-entrypoint.sh"]

# Start server with Gunicorn (production WSGI server)
# --bind 0.0.0.0:3000 - Listen on all interfaces, port 3000
# --workers 1 - Use 1 worker process
# --threads 2 - Use 2 threads per worker
# --timeout 120 - 120 second timeout for scraping operations
# --access-logfile - - Log requests to stdout
# --error-logfile - - Log errors to stdout
# --capture-output - Capture stdout/stderr from application
# --enable-stdio-inheritance - Allow workers to inherit stdio
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "1", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "--capture-output", "--enable-stdio-inheritance", "server:app"]
