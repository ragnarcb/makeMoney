# WhatsApp Video Generator

A microservice system that generates WhatsApp-style videos with custom conversations, using Python and Node.js components running in the same Docker container.

## 🏗️ Architecture

The system consists of two main components:

1. **Python Service** (Orchestrator):
   - Generates chat conversations using OpenAI API
   - Creates TTS audio for each message
   - Calls Node.js service to generate WhatsApp images
   - Assembles final video with background overlay

2. **Node.js Service** (Image Generator):
   - Receives message JSON from Python service
   - Uses Puppeteer to render React WhatsApp clone
   - Takes progressive screenshots (1 message, 2 messages, etc.)
   - Returns image paths to Python service

## 🔄 Complete System Workflow

This system integrates with a jobber-based microservices architecture for scalable video generation with voice cloning.

### **High-Level System Architecture**

```mermaid
graph TB
    subgraph "Video Generation Pipeline"
        VG[Video Generator]
        WG[WhatsApp Clone Service]
        DB[(PostgreSQL DB)]
    end
    
    subgraph "Jobber Orchestration"
        JQ[Jobber Queue]
        JB[Jobber Service]
        TQ[Temp Queue]
    end
    
    subgraph "Voice Processing"
        VC[Voice Cloning Pod]
        TTS[Coqui TTS Engine]
    end
    
    subgraph "Storage Services"
        LS[Local Storage]
        RS[Remote Storage Service]
    end
    
    VG --> DB
    VG --> WG
    VG --> JQ
    JQ --> JB
    JB --> TQ
    TQ --> VC
    VC --> TTS
    VC --> DB
    VC --> LS
    VC --> RS
    
    VG -.->|Poll Status| DB
```

### **Detailed Workflow Sequence**

```mermaid
sequenceDiagram
    participant VG as Video Generator
    participant DB as PostgreSQL DB
    participant WG as WhatsApp Clone
    participant JQ as Jobber Queue
    participant JB as Jobber Service
    participant VC as Voice Cloning Pod
    participant ST as Storage Service

    Note over VG,ST: Phase 1: Video Initialization
    VG->>DB: Create video entry (status: 'processing')
    VG->>VG: Generate chat conversation with OpenAI
    
    Note over VG,ST: Phase 2: WhatsApp Image Generation
    VG->>WG: Send messages for image generation
    WG->>WG: Generate progressive screenshots
    WG->>VG: Return image paths
    
    Note over VG,ST: Phase 3: Voice Cloning Request
    VG->>JQ: Send voice cloning request
    Note over VG,JQ: {app: "text-processor", data: {video_id, messages, voice_mapping}}
    
    Note over VG,ST: Phase 4: Jobber Orchestration
    JQ->>JB: Consume request
    JB->>JB: Create temporary queue
    JB->>VC: Instantiate voice cloning pod
    Note over JB,VC: CONSUMER_QUEUE_NAME=<temp_queue>
    
    Note over VG,ST: Phase 5: Voice Processing
    JB->>VC: Send simplified message
    Note over JB,VC: {video_id, messages, voice_mapping}
    VC->>DB: Create voice requests for each message
    VC->>VC: Process voice cloning with Coqui TTS
    VC->>ST: Store audio files (local/remote)
    VC->>DB: Update voice processing status
    VC->>VC: Exit pod when complete
    
    Note over VG,ST: Phase 6: Video Assembly
    VG->>DB: Poll for voice completion status
    DB->>VG: Return voice file paths
    VG->>VG: Assemble final video with audio
    VG->>DB: Update video status to 'completed'
```

### **Database Schema**

```mermaid
erDiagram
    VIDEOS {
        uuid id PK
        string title
        string status
        jsonb metadata
        timestamp created_at
        timestamp updated_at
    }
    
    VOICES {
        uuid id PK
        uuid video_id FK
        string character_name
        text text_content
        string status
        string local_file_path
        string remote_storage_path
        boolean is_local_storage
        timestamp created_at
        timestamp updated_at
    }
    
    VOICE_MAPPINGS {
        uuid id PK
        string character_name
        string voice_file_path
        jsonb metadata
        timestamp created_at
    }
    
    SETTINGS {
        string key PK
        text value
        timestamp updated_at
    }
    
    VIDEOS ||--o{ VOICES : "has many"
    VOICES }o--|| VOICE_MAPPINGS : "maps to"
```

### **Message Flow States**

```mermaid
stateDiagram-v2
    [*] --> VideoCreated: Create video entry
    VideoCreated --> ImagesGenerated: Generate WhatsApp images
    ImagesGenerated --> VoiceRequestSent: Send to jobber queue
    VoiceRequestSent --> VoiceProcessing: Jobber instantiates pod
    VoiceProcessing --> VoiceCompleted: Voice cloning finished
    VoiceCompleted --> VideoCompleted: Assemble final video
    VideoCompleted --> [*]
    
    VoiceProcessing --> VoiceFailed: Processing error
    VoiceFailed --> VoiceRequestSent: Retry
```

### **Service Communication**

```mermaid
flowchart LR
    subgraph "Video Generator Service"
        A[Main Orchestrator]
        B[Database Manager]
        C[WhatsApp Client]
    end
    
    subgraph "External Services"
        D[PostgreSQL DB]
        E[RabbitMQ Jobber]
        F[Voice Cloning Pods]
        G[Storage Service]
    end
    
    A --> B
    B --> D
    A --> C
    C --> E
    E --> F
    F --> D
    F --> G
    
    A -.->|Poll Status| D
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key

### Setup
1. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

2. Build and run the system:
   ```bash
   docker-compose up --build
   ```

3. The system will:
   - Build the React WhatsApp clone
   - Start the Node.js server on port 3001
   - Generate a WhatsApp video with the default prompt
   - Save the output to `./output/output_with_overlay.mp4`

## 🔧 How It Works

### 1. Message Flow
```
Python Service → OpenAI API → Chat JSON → Node.js Service → WhatsApp Images
```

### 2. Node.js Integration
The Node.js service:
- Runs an Express server on port 3001
- Serves the React WhatsApp clone
- Uses Puppeteer to take screenshots
- Provides API endpoints:
  - `POST /api/generate-screenshots` - Generate progressive screenshots
  - `GET /api/messages` - Get current messages
  - `GET /api/health` - Health check

### 3. Image Generation Process
1. Python sends message JSON to Node.js service
2. Node.js updates the React app with messages
3. Puppeteer takes screenshots progressively:
   - Screenshot 1: 1 message
   - Screenshot 2: 2 messages
   - Screenshot 3: 3 messages
   - etc.
4. Node.js returns image paths to Python
5. Python uses images to create final video

## 📁 Project Structure

```
makeMoney/
├── video_generator/          # Python orchestrator
│   ├── main.py              # Main entry point
│   ├── whatsapp_gen/        # Chat generation
│   ├── tts/                 # Text-to-speech
│   ├── video_overlay/       # Video assembly
│   └── utils/               # Utilities
├── whatsapp-clone/          # Node.js image generator
│   ├── server.js            # Express server
│   ├── src/                 # React app
│   └── package.json         # Node.js dependencies
├── background_videos/        # Background video files
├── output/                  # Generated videos
├── Dockerfile               # Container setup
└── docker-compose.yml       # Service orchestration
```

## 🎯 Customization

### Custom Prompts
```bash
docker-compose run --rm whatsapp-video-generator --prompt "Uma conversa engraçada sobre programação"
```

### Custom Participants
```bash
docker-compose run --rm whatsapp-video-generator --participants "João" "Maria"
```

### Testing Node.js Service
```bash
python test_node_service.py
```

## 🔍 Troubleshooting

### Node.js Service Issues
- Check if port 3001 is available
- Verify React app builds successfully
- Check Docker logs: `docker-compose logs whatsapp-video-generator`

### Image Generation Issues
- Ensure Puppeteer dependencies are installed
- Check if React app loads correctly
- Verify message JSON format

### Video Generation Issues
- Check OpenAI API key is set
- Verify background videos exist
- Check output directory permissions

## 🛠️ Development

### Local Development
1. Start Node.js service:
   ```bash
   cd whatsapp-clone
   npm install
   cd src && npm install && npm run build && cd ..
   node server.js
   ```

2. Run Python service:
   ```bash
   cd video_generator
   pip install -r requirements.txt
   python main.py
   ```

### API Endpoints

#### Generate Screenshots
```bash
curl -X POST http://localhost:3001/api/generate-screenshots \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [...],
    "participants": ["Ana", "Bruno"],
    "outputDir": "./output",
    "img_size": [1920, 1080]
  }'
```

#### Health Check
```bash
curl http://localhost:3001/api/health
```

## 📝 Notes

- The system uses a phone aspect ratio (portrait) for videos
- Images are generated progressively to sync with TTS audio
- Background videos are randomly selected from the `background_videos/` folder
- The React WhatsApp clone provides a realistic WhatsApp interface
- All services run in a single Docker container for simplicity 