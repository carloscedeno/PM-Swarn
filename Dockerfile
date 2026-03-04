# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH /app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies using pip
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy project
COPY . .

# Run the application (placeholder for main entry point)
# CMD ["python", "-m", "src.main"]
CMD ["pytest"]
