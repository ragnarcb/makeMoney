# Database Integration for Video Generator and Voice Cloning

This document describes the PostgreSQL database setup for integrating the video generator and voice cloning services.

## Overview

The database serves as the central coordination point between:
- **Video Generator Service**: Creates videos and manages the overall workflow
- **WhatsApp Clone Service**: Generates chat images and returns paths
- **Voice Cloning Service**: Processes text-to-speech requests

## Database Schema

### Tables

#### 1. `videos` - Main video entries
- `id` (UUID): Primary key
- `title` (VARCHAR): Video title
- `description` (TEXT): Video description
- `background_video_path` (VARCHAR): Path to background video
- `output_video_path` (VARCHAR): Path to final generated video
- `whatsapp_images_paths` (TEXT[]): Array of WhatsApp chat image paths
- `status` (video_status): Current status (pending, processing, completed, failed)
- `metadata` (JSONB): Additional video metadata
- `created_at`, `updated_at`, `completed_at` (TIMESTAMP): Timestamps

#### 2. `voices` - Voice cloning requests
- `id` (UUID): Primary key
- `video_id` (UUID): Foreign key to videos table
- `voice_mapping_id` (UUID): Foreign key to voice_mappings table
- `character_name` (VARCHAR): Character name for the voice
- `text_content` (TEXT): Text to convert to speech
- `output_audio_path` (VARCHAR): Path to generated audio file
- `status` (voice_status): Current status (pending, processing, completed, failed)
- `processing_started_at`, `processing_completed_at` (TIMESTAMP): Processing timestamps
- `error_message` (TEXT): Error message if failed
- `created_at`, `updated_at` (TIMESTAMP): Timestamps

#### 3. `voice_mappings` - Voice configuration (replaces JSON config)
- `id` (UUID): Primary key
- `voice_id` (VARCHAR): Unique voice identifier (e.g., "aluno", "professora")
- `voice_name` (VARCHAR): Display name
- `voice_file` (VARCHAR): Path to voice file
- `description` (TEXT): Voice description
- `gender` (VARCHAR): Gender (male, female, other)
- `language` (VARCHAR): Language code (e.g., "pt-br")
- `quality` (VARCHAR): Quality level (low, medium, high)
- `is_default` (BOOLEAN): Whether this is the default voice
- `created_at`, `updated_at` (TIMESTAMP): Timestamps

#### 4. `settings` - Global configuration
- `id` (UUID): Primary key
- `setting_key` (VARCHAR): Setting name
- `setting_value` (TEXT): Setting value
- `description` (TEXT): Setting description
- `created_at`, `updated_at` (TIMESTAMP): Timestamps

### Views

#### `video_processing_status` - Processing status overview
Provides a summary of video processing status including voice completion counts.

## Workflow

### 1. Video Creation
```python
from database_utils import VideoManager

video_manager = VideoManager()
video_id = video_manager.create_video(
    title="My Video",
    description="A test video",
    background_video_path="/path/to/background.mp4"
)
```

### 2. Voice Request Creation
```python
from database_utils import VoiceManager, VoiceMappingManager

voice_manager = VoiceManager()
vm_manager = VoiceMappingManager()

# Get voice mapping for character
aluno_mapping = vm_manager.get_voice_mapping("aluno")

# Create voice request
voice_id = voice_manager.create_voice_request(
    video_id=video_id,
    character_name="Aluno",
    text_content="Olá professor!",
    voice_mapping_id=aluno_mapping['id'] if aluno_mapping else None
)
```

### 3. Voice Processing (Voice Cloning Service)
```python
# Start processing
voice_manager.start_voice_processing(voice_id)

# Complete processing
voice_manager.complete_voice_processing(voice_id, "/path/to/audio.wav")
```

### 4. Video Completion
```python
# Update with WhatsApp images
video_manager.update_video_status(
    video_id=video_id,
    status="processing",
    whatsapp_images_paths=["/path/to/image1.png", "/path/to/image2.png"]
)

# Complete video
video_manager.update_video_completed(video_id, "/path/to/final_video.mp4")
```

### 5. Status Monitoring
```python
from database_utils import get_video_processing_status, check_video_voices_completion

# Check overall status
status = get_video_processing_status(video_id)
print(f"Video status: {status}")

# Check if all voices are completed
all_completed = check_video_voices_completion(video_id)
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r database_requirements.txt
```

### 2. Initialize Database
```bash
# Run the initialization script
python init_database.py
```

### 3. Test Setup
```bash
# Run the test suite
python test_database.py
```

## Connection Parameters

```python
POSTGRES_HOST = "192.168.1.218"  # k3s node IP
POSTGRES_PORT = 30432            # NodePort
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres123"
DATABASE_NAME = "video_voice_integration"
```

## Integration Points

### Video Generator Service
- Creates video entries in the database
- Monitors voice completion status
- Updates video with WhatsApp image paths
- Finalizes video when all processing is complete

### Voice Cloning Service
- Polls for pending voice requests
- Updates voice status during processing
- Stores generated audio file paths
- Notifies completion

### WhatsApp Clone Service
- Receives video ID from video generator
- Returns image paths to video generator
- No direct database interaction

## Error Handling

The database includes error tracking:
- Voice requests can have error messages
- Failed status tracking for both videos and voices
- Timestamp tracking for debugging

## Performance Considerations

- Indexes on frequently queried columns
- UUID primary keys for distributed systems
- JSONB for flexible metadata storage
- Array type for WhatsApp image paths

## Security Notes

- Use environment variables for production credentials
- Implement proper connection pooling
- Consider read-only database users for monitoring
- Regular database backups recommended

## Troubleshooting

### Common Issues

1. **Connection refused**: Check PostgreSQL service and network connectivity
2. **Authentication failed**: Verify username/password
3. **Database not found**: Run initialization script
4. **Permission denied**: Check database user privileges

### Debug Queries

```sql
-- Check video status
SELECT * FROM video_processing_status WHERE video_id = 'your-video-id';

-- Check pending voices
SELECT * FROM voices WHERE status = 'pending';

-- Check voice mappings
SELECT * FROM voice_mappings ORDER BY voice_name;
``` 


### Clear db 

``` sql
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'video_voice_integration';

DROP DATABASE video_voice_integration;
```