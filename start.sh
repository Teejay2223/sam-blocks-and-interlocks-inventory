#!/bin/bash
# Railway startup script
# Ensures PORT variable is properly used

# Default PORT to 5000 if not set
PORT=${PORT:-5000}

echo "Starting gunicorn on port $PORT"
exec gunicorn --bind 0.0.0.0:$PORT app:app --workers 3 --log-level info
