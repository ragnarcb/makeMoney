#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 WhatsApp Video Generator - Build & Run Script${NC}"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Load environment variables from .env file
if [ -f .env ]; then
    echo -e "${BLUE}📄 Loading environment variables from .env file...${NC}"
    # Read .env file and export variables properly
    while IFS= read -r line; do
        # Skip comments and empty lines
        [[ $line =~ ^[[:space:]]*# ]] && continue
        [[ -z $line ]] && continue
        
        # Export the variable
        export "$line"
    done < .env
else
    echo -e "${YELLOW}⚠️  .env file not found. Creating one...${NC}"
    cat > .env << EOF
# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Node.js Server Configuration
NODE_PORT=3001

# Video Generation Configuration
DEFAULT_PROMPT=Uma conversa engraçada sobre tecnologia
DEFAULT_PARTICIPANT1=Ana
DEFAULT_PARTICIPANT2=Bruno

# Output Configuration
OUTPUT_DIR=./output
BACKGROUND_VIDEOS_DIR=./background_videos
EOF
    echo -e "${RED}❌ Please edit .env file and set your OPENAI_API_KEY${NC}"
    exit 1
fi

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key-here" ]; then
    echo -e "${RED}❌ OPENAI_API_KEY not set in .env file${NC}"
    echo "Please edit .env file and set your OpenAI API key"
    exit 1
fi

# Build the Docker image
echo -e "${BLUE}🔨 Building Docker image...${NC}"
docker build -t whatsapp-video-generator .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Build successful!${NC}"

# Create output directory if it doesn't exist
mkdir -p output

# Run the container
echo -e "${BLUE}🚀 Running container...${NC}"
echo -e "${YELLOW}📝 Usage:${NC}"
echo "  Default: ./build-and-run.sh"
echo "  Custom prompt: ./build-and-run.sh 'Uma conversa engraçada sobre programação'"
echo "  Custom participants: ./build-and-run.sh 'prompt' 'João' 'Maria'"
echo ""

# Get arguments with defaults from .env
PROMPT=${1:-"$DEFAULT_PROMPT"}
PARTICIPANT1=${2:-"$DEFAULT_PARTICIPANT1"}
PARTICIPANT2=${3:-"$DEFAULT_PARTICIPANT2"}

echo -e "${BLUE}🎬 Generating video with:${NC}"
echo "  Prompt: $PROMPT"
echo "  Participants: $PARTICIPANT1, $PARTICIPANT2"
echo ""

# Run the container
docker run --rm \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    -v "$(pwd)/$OUTPUT_DIR:/app/video_generator/output" \
    -v "$(pwd)/$BACKGROUND_VIDEOS_DIR:/app/background_videos" \
    -p $NODE_PORT:3001 \
    whatsapp-video-generator \
    --prompt "$PROMPT" \
    --participants "$PARTICIPANT1" "$PARTICIPANT2"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}🎉 Video generation completed!${NC}"
    echo -e "${BLUE}📁 Output saved to: ./output/output_with_overlay.mp4${NC}"
else
    echo -e "${RED}❌ Video generation failed!${NC}"
    exit 1
fi 