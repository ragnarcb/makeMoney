# Build stage
FROM node:18-slim AS builder

# Install system dependencies required for Playwright (no Chromium or Puppeteer)
RUN apt-get update && apt-get install -y \
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

# Create app directory
WORKDIR /app

# Copy package files for dependency installation
COPY package*.json ./

# Install all dependencies (including dev dependencies for build)
RUN npm install && npm cache clean --force

# Copy source code
COPY . .

# Build React app
RUN npm run build

# Production stage
FROM node:18-slim AS production

# Install system dependencies required for Playwright (no Chromium or Puppeteer)
RUN apt-get update && apt-get install -y \
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

# Create app directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm install --omit=dev && npm cache clean --force

# Copy built React app from builder stage
COPY --from=builder /app/build ./build

# Copy server files
COPY server.js ./

# Create non-root user for security
RUN groupadd -g 1001 nodejs && \
    useradd -u 1001 -g nodejs -s /bin/bash nextjs

# Set Playwright to install browsers in project directory and install browsers for nextjs user
ENV PLAYWRIGHT_BROWSERS_PATH=0
# Install system dependencies and browser as root
RUN npx playwright install --with-deps chromium
# Ensure all files are owned by nextjs user
RUN chown -R nextjs:nodejs /app
# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3001

# Health check (optional)
# HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD curl -f http://localhost:3001/api/health || exit 1

# Start the server
CMD ["npm", "start"] 