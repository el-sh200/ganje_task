# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables to prevent python from writing pyc files to disc and to set the default encoding to UTF-8
ENV PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8

# Set the working directory in the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install system dependencies and required Python packages in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev && \
    pip install --upgrade pip && \
    pip install -r requirements.txt && \
    apt-get purge -y --auto-remove build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copy the rest of the application code
COPY . .

# Expose port 8000 (default for Django)
EXPOSE 8000

# Run Django application
CMD ["gunicorn", "--bind", "localhost:8000", "booking.wsgi:application"]