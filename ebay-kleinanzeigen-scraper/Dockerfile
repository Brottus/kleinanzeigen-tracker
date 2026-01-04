FROM python:3.14-alpine

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY server.py .

# Expose port
EXPOSE 3000

# Health check using wget (already in alpine)
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:3000/health || exit 1

# Run as non-root user for security
RUN adduser -D appuser && chown -R appuser:appuser /app
USER appuser

# Start server with Gunicorn (production WSGI server)
# --bind 0.0.0.0:3000 - Listen on all interfaces, port 3000
# --workers 4 - Use 4 worker processes (adjust based on CPU cores)
# --timeout 120 - 120 second timeout for scraping operations
# --access-logfile - - Log requests to stdout
# --error-logfile - - Log errors to stdout
CMD ["gunicorn", "--bind", "0.0.0.0:3000", "--workers", "4", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-", "server:app"]
