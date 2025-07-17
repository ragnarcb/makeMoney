#!/bin/bash

echo "🚀 Starting WhatsApp Clone Server..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "📦 Installing dependencies..."
npm install

echo "🔨 Building React app..."
cd src && npm install && npm run build && cd ..

echo "🌐 Starting Node.js server on port 3001..."
echo "📱 React app will be available at: http://localhost:3001"
echo "🔌 API endpoints:"
echo "   POST /api/generate-screenshots - Generate screenshots"
echo "   GET  /api/messages - Get current messages"
echo "   GET  /api/health - Health check"
echo ""
echo "Press Ctrl+C to stop the server"

npm start 