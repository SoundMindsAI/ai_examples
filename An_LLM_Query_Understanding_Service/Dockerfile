# For Mac testing, use Python base image instead of NVIDIA CUDA
FROM python:3.10-slim

# Install minimal dependencies and clean up to reduce image size
RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set workdir
WORKDIR /app

# Install Python dependencies without caching to save space
COPY requirements.txt .
RUN pip3 --no-cache-dir install -r requirements.txt

# Copy application code
COPY . .

# Create directory for model cache
RUN mkdir -p /root/.cache/huggingface

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV LOG_LEVEL=INFO
ENV JSON_LOGS=true
ENV REDIS_ENABLED=true

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["python", "main.py"]
