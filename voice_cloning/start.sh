#!/bin/bash

# Set up environment variables
export NUMBA_DISABLE_JIT=1
export NUMBA_CACHE_DIR=/tmp
export LIBROSA_CACHE_DIR=/tmp
export LIBROSA_CACHE_LEVEL=0

# Create cache directories with proper permissions
mkdir -p /tmp/librosa_cache/joblib
mkdir -p /tmp/numba_cache
mkdir -p /tmp/voice_cloning_output

# Set proper permissions
chmod -R 755 /tmp/librosa_cache
chmod -R 755 /tmp/numba_cache
chmod -R 755 /tmp/voice_cloning_output

# Ensure the app user owns these directories
if [ -d "/tmp/librosa_cache" ]; then
    chown -R app:app /tmp/librosa_cache
fi
if [ -d "/tmp/numba_cache" ]; then
    chown -R app:app /tmp/numba_cache
fi
if [ -d "/tmp/voice_cloning_output" ]; then
    chown -R app:app /tmp/voice_cloning_output
fi

# Start the application
exec python src/queue_consumer.py 