import os
import json
import uuid
from loguru import logger
from whatsapp_gen.chat_generator import generate_chat
from whatsapp_gen.node_service_client import NodeServiceClient
from voice_cloning_client import VoiceCloningServiceClient
from video_overlay.progressive_overlay import ProgressiveMessageOverlay
from video_overlay.overlay_builder import build_video
from utils.file_utils import cleanup_temp_dirs
from utils.video_utils import get_random_background_video, validate_video_file
import sys
import argparse

# Configure logging based on environment variable
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logger.remove()  # Remove default handler
logger.add(sys.stderr, level=log_level, format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
logger.info(f"Logging configured with level: {log_level}")

# --- CONFIG ---
PARTICIPANTS = ["Ana", "Bruno"]
TEMP_IMG_DIR = "temp_chat_imgs"
TEMP_AUDIO_DIR = "temp_audio"
TEMP_FRAMES_DIR = "temp_frames"
OUTPUT_VIDEO_PATH = "output_with_overlay.mp4"
BACKGROUND_VIDEO_FOLDER = "../background_videos"  # Folder containing background videos
LANG = 'pt-br'
FPS = 30
IMG_SIZE = (1920, 1080)  # height, width (portrait)


def main():
    logger.info("Starting WhatsApp video generation pipeline")
    
    # Generate unique video ID
    video_id = str(uuid.uuid4())
    logger.info(f"Generated video ID: {video_id}")
    
    parser = argparse.ArgumentParser(description="Generate WhatsApp video with custom prompt")
    parser.add_argument("--prompt", type=str, help="Custom prompt for the conversation", default=None)
    parser.add_argument("--participants", nargs=2, default=PARTICIPANTS, help="Participant names")
    parser.add_argument("--use-s3", action="store_true", help="Use S3 storage for files")
    parser.add_argument("--node-url", type=str, default="http://localhost:3010", help="Node.js service URL")
    parser.add_argument("--voice-cloning-dir", type=str, default="../voice_cloning", help="Voice Cloning directory path")
    parser.add_argument("--messages-per-group", type=int, default=4, help="Number of messages to show at once")
    parser.add_argument("--start-buffer", type=float, default=1.0, help="Buffer (seconds) at start of video")
    parser.add_argument("--end-buffer", type=float, default=3.0, help="Buffer (seconds) at end of video")
    parser.add_argument("--voice-mapping", nargs='*', help="Map participants to voice files: participant:voice.wav")
    parser.add_argument("--no-voice-cloning", action="store_true", help="Disable voice cloning")
    parser.add_argument("--video-id", type=str, default=video_id, help="Video ID for tracking")
    args = parser.parse_args()

    logger.info(f"Configuration: participants={args.participants}, lang={LANG}, fps={FPS}, img_size={IMG_SIZE}")
    logger.info(f"Progressive overlay: messages_per_group={args.messages_per_group}, start_buffer={args.start_buffer}, end_buffer={args.end_buffer}")
    logger.debug(f"Arguments: {vars(args)}")

    logger.info("Generating WhatsApp chat JSON...")
    if args.prompt:
        logger.info(f"Using custom prompt: {args.prompt}")
        messages = generate_chat(args.participants, custom_prompt=args.prompt)
    else:
        logger.info("Using default funny conversation prompt")
        messages = generate_chat(args.participants)
    logger.success(f"Generated {len(messages)} messages.")
    logger.debug(f"First few messages: {messages[:3] if len(messages) >= 3 else messages}")

    # Initialize Voice Cloning TTS microservice client
    logger.info(f"Initializing Voice Cloning TTS microservice client for video {args.video_id}")
    tts_client = VoiceCloningServiceClient(video_id=args.video_id)

    # Check Voice Cloning TTS system health
    logger.info("Checking Voice Cloning TTS system health...")
    if not tts_client.health_check():
        error_msg = "Voice Cloning TTS system is not healthy. Check voice files and configuration."
        logger.error(error_msg)
        sys.exit(1)

    # Process voice mapping
    voice_mapping = {}
    if args.voice_mapping:
        for mapping in args.voice_mapping:
            if ':' in mapping:
                participant, voice_file = mapping.split(':', 1)
                voice_mapping[participant.strip()] = voice_file.strip()
            else:
                logger.warning(f"Invalid voice mapping format: {mapping}")
                logger.info("Use format: participant:voice.wav")

    logger.info("Generating TTS audio for each message using Voice Cloning TTS...")
    try:
        audio_paths = tts_client.generate_tts(
            messages=messages,
            participants=args.participants,
            output_dir=TEMP_AUDIO_DIR,
            voice_mapping=voice_mapping,
            use_voice_cloning=not args.no_voice_cloning,
            lang=LANG
        )
        logger.success(f"Generated TTS for {len(audio_paths)} messages using Voice Cloning TTS.")
        logger.debug(f"Audio paths: {audio_paths}")
    except Exception as e:
        error_msg = f"Failed to generate TTS audio: {e}"
        logger.error(error_msg)
        sys.exit(1)

    # Initialize Node.js service client
    s3_config = {} # Add your S3 config here if needed
    logger.info(f"Initializing Node.js service client with URL: {args.node_url}")
    node_client = NodeServiceClient(
        api_url=args.node_url,
        use_s3=args.use_s3,
        s3_config=s3_config
    )

    # Check Node.js service health
    logger.info("Checking Node.js service health...")
    if not node_client.health_check():
        error_msg = "Node.js service is not responding. Make sure it's running on the specified URL."
        logger.error(error_msg)
        sys.exit(1)

    logger.info("Getting WhatsApp screenshot with message coordinates from Node.js service...")
    try:
        screenshot_path, message_coordinates = node_client.get_screenshot_with_coordinates(
            messages, args.participants, TEMP_IMG_DIR, img_size=IMG_SIZE
        )
        logger.success(f"Generated WhatsApp screenshot: {screenshot_path}")
        logger.info(f"Extracted {len(message_coordinates)} message coordinates")
        logger.debug(f"Message coordinates summary: {[{'index': c['index'], 'y': c['y'], 'from': c['from']} for c in message_coordinates]}")
    except Exception as e:
        error_msg = f"Failed to generate WhatsApp screenshot: {e}"
        logger.error(error_msg)
        logger.error("Make sure the Node.js server is running on the specified URL")
        sys.exit(1)

    if not message_coordinates:
        error_msg = "No message coordinates were extracted. Cannot create progressive overlay."
        logger.error(error_msg)
        sys.exit(1)

    # Create progressive message overlay
    logger.info("Creating progressive message overlay...")
    try:
        overlay = ProgressiveMessageOverlay(
            screenshot_path=screenshot_path,
            message_coordinates=message_coordinates,
            output_dir=TEMP_FRAMES_DIR,
            messages_per_group=args.messages_per_group
        )

        # Get audio durations for frame generation
        logger.info("Calculating audio durations for frame generation...")
        from moviepy import AudioFileClip
        audio_durations = []
        for i, audio_path in enumerate(audio_paths):
            audio_clip = AudioFileClip(audio_path)
            duration = audio_clip.duration
            audio_durations.append(duration)
            audio_clip.close()
            logger.debug(f"Audio {i}: {duration:.2f}s")
        logger.info(f"Audio durations calculated: {audio_durations}")

        # Generate progressive frames
        frame_paths = overlay.create_progressive_frames(
            audio_durations, 
            fps=FPS, 
            start_buffer=args.start_buffer, 
            end_buffer=args.end_buffer
        )
        logger.success(f"Generated {len(frame_paths)} progressive frames")

    except Exception as e:
        error_msg = f"Failed to create progressive overlay: {e}"
        logger.error(error_msg)
        sys.exit(1)

    # Select background video
    logger.info(f"Looking for background videos in: {BACKGROUND_VIDEO_FOLDER}")
    background_video = get_random_background_video(BACKGROUND_VIDEO_FOLDER)
    if background_video:
        logger.info(f"Using background video: {background_video}")
    else:
        logger.warning(f"No background videos found in {BACKGROUND_VIDEO_FOLDER}. Using frames only.")

    logger.info("Building the final video...")
    try:
        logger.debug(f"Building video with {len(frame_paths)} frames and background: {background_video}")
        build_video(
            frame_paths,
            audio_paths,
            OUTPUT_VIDEO_PATH,
            background_video_path=background_video,
            fps=FPS
        )
        logger.success(f"Video saved to {OUTPUT_VIDEO_PATH}")
    except Exception as e:
        error_msg = f"Failed to build video: {e}"
        logger.error(error_msg)
        sys.exit(1)

    logger.info("Video generation pipeline completed successfully!")
    
    # Optional cleanup
    # logger.info("Cleaning up temporary files...")
    # cleanup_temp_dirs(TEMP_IMG_DIR, TEMP_AUDIO_DIR, TEMP_FRAMES_DIR)

if __name__ == "__main__":
    # Check if we should run in queue mode
    if os.getenv('CONSUMER_QUEUE_NAME'):
        # Import and run queue consumer
        from queue_consumer import main as queue_main
        queue_main()
    else:
        # Run in direct mode (original behavior)
    main() 