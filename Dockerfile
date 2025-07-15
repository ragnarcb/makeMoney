# Use Node.js base image
FROM node:18-slim

# Install Python and pip with full support
RUN apt-get update && apt-get install -y \
    python3-full \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install system dependencies for OpenCV and Puppeteer
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libgomp1 \
    libfontconfig1 \
    libxss1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libnss3 \
    libnspr4 \
    libatspi2.0-0 \
    libdrm2 \
    libxshmfence1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY whatsapp-clone/package*.json ./whatsapp-clone/
COPY video_generator/requirements.txt ./video_generator/

# Install Node.js dependencies
WORKDIR /app/whatsapp-clone
RUN npm install

# Create Python virtual environment and install dependencies
WORKDIR /app/video_generator
RUN python3 -m venv venv
ENV PATH="/app/video_generator/venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy source code
WORKDIR /app
COPY whatsapp-clone/ ./whatsapp-clone/
COPY video_generator/ ./video_generator/
COPY background_videos/ ./background_videos/

# Create directories for output
RUN mkdir -p /app/video_generator/temp_chat_imgs \
    && mkdir -p /app/video_generator/temp_audio \
    && mkdir -p /app/video_generator/output

# Expose Node.js API port
EXPOSE 3001

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting Node.js WhatsApp Image Generator..."\n\
cd /app/whatsapp-clone\n\
npm run server &\n\
NODE_PID=$!\n\
\n\
echo "Waiting for Node.js server to start..."\n\
sleep 5\n\
\n\
echo "Starting Python video generator..."\n\
cd /app/video_generator\n\
source venv/bin/activate\n\
python main.py "$@"\n\
\n\
wait $NODE_PID\n\
' > /app/start.sh && chmod +x /app/start.sh

# Set entrypoint
ENTRYPOINT ["/app/start.sh"] 