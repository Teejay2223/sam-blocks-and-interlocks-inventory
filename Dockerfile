# Dockerfile for sam_blocks_inventory
# Builds a small image to run the Flask app with gunicorn

FROM python:3.11-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r /app/requirements.txt

# Copy source
COPY . /app

# Expose port
EXPOSE 5000

# Default env (can be overridden at runtime)
ENV FLASK_ENV=production
ENV PORT=5000

# Recommended command: use gunicorn for production
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT} app:app --workers 3 --log-level info"]