# Voice Cloning TTS 2.0 Kubernetes Microservice
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV CONSUMER_QUEUE_NAME=voice-cloning-queue
ENV RABBITMQ_HOST=192.168.1.218
ENV RABBITMQ_PORT=30672
ENV RABBITMQ_USER=admin
ENV RABBITMQ_PASSWORD=admin123
ENV RABBITMQ_VHOST=/
ENV USE_MOCK_MODE=false
ENV OUTPUT_DIR=/tmp/voice_cloning_output
ENV COQUI_TOS_AGREED=1

# Database configuration
ENV POSTGRES_HOST=192.168.1.218
ENV POSTGRES_PORT=30432
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=postgres123
ENV DATABASE_NAME=video_voice_integration

# Install system dependencies for audio processing (cached layer)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    libportaudio2 \
    gcc \
    g++ \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies (this layer will be cached unless requirements.txt changes)
# Upgrade pip first for better compatibility
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt  

# Copy source code (these layers will be cached unless source changes)
COPY src/ ./src/
COPY voices/ ./voices/

# Database mode configuration
ENV USE_DATABASE_MODE=true

# Storage configuration
ENV USE_LOCAL_STORAGE=true
ENV LOCAL_STORAGE_URL=http://192.168.1.218:30880
ENV VOICE_STORAGE_BUCKET=voice-cloning

# Create necessary directories
RUN mkdir -p /tmp/voice_cloning_output /var/log /app/models

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app /tmp/voice_cloning_output /var/log

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.append('/app/src'); from database_integration import test_database_connection; sys.exit(0 if test_database_connection() else 1)"

# Expose port (if needed for health checks)
EXPOSE 8080

# Run the queue consumer
CMD ["python", "src/queue_consumer.py"] 