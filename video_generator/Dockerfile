# Multi-stage build for optimized Video Generator
FROM python:3.11-slim AS builder

# Install system dependencies for video processing and image manipulation
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    ffmpeg \
    imagemagick \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libfreetype6-dev \
    libharfbuzz-dev \
    libcairo2-dev \
    libpango1.0-dev \
    libgif-dev \
    libwebp-dev \
    librsvg2-dev \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim AS production

# Install runtime dependencies for video processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    imagemagick \
    libjpeg62-turbo \
    zlib1g \
    libpng16-16 \
    libfreetype6 \
    libharfbuzz0b \
    libcairo2 \
    libpango-1.0-0 \
    libgif7 \
    libwebp7 \
    librsvg2-2 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Create app directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create non-root user for security
RUN groupadd -g 1001 appgroup && \
    useradd -u 1001 -g appgroup -s /bin/bash appuser

# Create necessary directories and set permissions
RUN mkdir -p temp_chat_imgs temp_audio temp_frames output && \
    chown -R appuser:appgroup /app

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command - run in queue mode
CMD ["python", "main.py"] 