# Use Python 3.11 slim as base image
FROM python:3.11-slim

# Install Node.js and system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    ca-certificates \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get install -y \
    chromium \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxss1 \
    libxtst6 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files first for better caching
COPY package*.json ./
COPY whatsapp-clone/package*.json ./whatsapp-clone/

# Install Node.js dependencies
RUN npm install
RUN cd whatsapp-clone && npm install

# Add missing TypeScript types
RUN cd whatsapp-clone && npm install --save-dev @types/react @types/react-dom

# Copy React app source files
COPY whatsapp-clone/public ./whatsapp-clone/public
COPY whatsapp-clone/src ./whatsapp-clone/src
COPY whatsapp-clone/tsconfig.json ./whatsapp-clone/
COPY whatsapp-clone/.gitignore ./whatsapp-clone/

# Build React app
RUN cd whatsapp-clone && npm run build

# Copy Node.js server
COPY whatsapp-clone/server.js ./whatsapp-clone/

# Copy Python requirements and install Python dependencies
COPY video_generator/requirements.txt ./video_generator/
RUN pip install --no-cache-dir -r video_generator/requirements.txt

# Copy Python source code
COPY video_generator ./video_generator
COPY background_videos ./background_videos

# Create necessary directories
RUN mkdir -p output temp_chat_imgs temp_audio

# Set Puppeteer to use installed Chromium
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Expose ports
EXPOSE 3000 8089

# Set environment variables
ENV NODE_ENV=production
ENV PYTHONPATH=/app

# Start both services
CMD ["sh", "-c", "cd whatsapp-clone && npm start & cd /app && python3 video_generator/main.py"] 