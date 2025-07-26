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

# Fix numba/librosa caching issues in Kubernetes
ENV NUMBA_DISABLE_JIT=1
ENV NUMBA_CACHE_DIR=/tmp/numba_cache
ENV LIBROSA_CACHE_DIR=/tmp/librosa_cache
ENV LIBROSA_CACHE_LEVEL=0

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
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies in stages to handle large packages better
RUN pip install --upgrade pip setuptools wheel

# Configure pip for better network handling
RUN pip config set global.timeout 600 && \
    pip config set global.retries 10

# Install core dependencies first (smaller packages)
RUN pip install --no-cache-dir \
    "numpy>=1.26.0,<2.0.0" \
    "requests>=2.31.0,<3.0.0" \
    "tqdm>=4.64.0,<5.0.0" \
    "regex>=2021.8.0,<2024.0.0" \
    "psutil>=5.8.0,<6.0.0" \
    "psycopg2-binary>=2.9.9,<3.0.0"

# Install audio processing packages
RUN pip install --no-cache-dir \
    "soundfile>=0.12.0,<1.0.0" \
    "pydub>=0.25.1,<1.0.0"

# Install queue consumer
RUN pip install --no-cache-dir "pika>=1.3.0,<2.0.0"

# Install large ML packages separately with retry logic
RUN pip install --no-cache-dir "torch>=2.1.0,<3.0.0" "torchaudio>=2.1.0,<3.0.0" || \
    (echo "PyTorch install failed, retrying..." && \
     pip install --no-cache-dir --timeout 900 --retries 15 "torch>=2.1.0,<3.0.0" "torchaudio>=2.1.0,<3.0.0")

# Install librosa (large package) with cache fixes
RUN pip install --no-cache-dir "librosa>=0.11.0,<1.0.0" || \
    (echo "Librosa install failed, retrying..." && \
     pip install --no-cache-dir --timeout 900 --retries 15 "librosa>=0.11.0,<1.0.0")

# Install coqui-tts last (largest package)
RUN pip install --no-cache-dir "coqui-tts>=0.27.0,<1.0.0" || \
    (echo "Coqui-TTS install failed, retrying with different approach..." && \
     pip install --no-cache-dir --timeout 1200 --retries 20 --trusted-host pypi.org --trusted-host files.pythonhosted.org "coqui-tts>=0.27.0,<1.0.0")

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
RUN mkdir -p /tmp/voice_cloning_output /var/log /app/models /tmp/librosa_cache /tmp/numba_cache

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app /tmp/voice_cloning_output /var/log /tmp/librosa_cache /tmp/numba_cache

# Switch to non-root user
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.append('/app/src'); from database_integration import test_database_connection; sys.exit(0 if test_database_connection() else 1)"

# Expose port (if needed for health checks)
EXPOSE 8080

# Run the queue consumer
CMD ["python", "src/queue_consumer.py"] 