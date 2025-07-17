import os
import json
from loguru import logger
from whatsapp_gen.chat_generator import generate_chat
from whatsapp_gen.node_service_client import NodeServiceClient
from tts.tts_generator import generate_tts
from video_overlay.progressive_overlay import ProgressiveMessageOverlay
from video_overlay.overlay_builder import build_video
from utils.file_utils import cleanup_temp_dirs
from utils.video_utils import get_random_background_video, validate_video_file
import sys
import argparse

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
    parser = argparse.ArgumentParser(description="Generate WhatsApp video with custom prompt")
    parser.add_argument("--prompt", type=str, help="Custom prompt for the conversation", default=None)
    parser.add_argument("--participants", nargs=2, default=PARTICIPANTS, help="Participant names")
    parser.add_argument("--use-s3", action="store_true", help="Use S3 storage for files")
    parser.add_argument("--node-url", type=str, default="http://localhost:3010", help="Node.js service URL")
    args = parser.parse_args()

    logger.info("Generating WhatsApp chat JSON...")
    if args.prompt:
        logger.info(f"Using custom prompt: {args.prompt}")
        messages = generate_chat(args.participants, custom_prompt=args.prompt)
    else:
        logger.info("Using default funny conversation prompt")
        messages = generate_chat(args.participants)
    logger.success(f"Generated {len(messages)} messages.")

    logger.info("Generating TTS audio for each message...")
    audio_paths = generate_tts(messages, TEMP_AUDIO_DIR, lang=LANG)
    logger.success(f"Generated TTS for {len(audio_paths)} messages.")

    # Initialize Node.js service client
    s3_config = {} # Add your S3 config here if needed
    node_client = NodeServiceClient(
        api_url=args.node_url,
        use_s3=args.use_s3,
        s3_config=s3_config
    )

    # Check Node.js service health
    if not node_client.health_check():
        logger.error("Node.js service is not responding. Make sure it's running on the specified URL.")
        sys.exit(1)

    logger.info("Getting WhatsApp screenshot with message coordinates from Node.js service...")
    try:
        screenshot_path, message_coordinates = node_client.get_screenshot_with_coordinates(
            messages, args.participants, TEMP_IMG_DIR, img_size=IMG_SIZE
        )
        logger.success(f"Generated WhatsApp screenshot: {screenshot_path}")
        logger.info(f"Extracted {len(message_coordinates)} message coordinates")
    except Exception as e:
        logger.error(f"Failed to generate WhatsApp screenshot: {e}")
        logger.error("Make sure the Node.js server is running on the specified URL")
        sys.exit(1)

    if not message_coordinates:
        logger.error("No message coordinates were extracted. Cannot create progressive overlay.")
        sys.exit(1)

    # Create progressive message overlay
    logger.info("Creating progressive message overlay...")
    try:
        overlay = ProgressiveMessageOverlay(
            screenshot_path=screenshot_path,
            message_coordinates=message_coordinates,
            output_dir=TEMP_FRAMES_DIR
        )

        # Get audio durations for frame generation
        from moviepy.editor import AudioFileClip
        audio_durations = []
        for audio_path in audio_paths:
            audio_clip = AudioFileClip(audio_path)
            audio_durations.append(audio_clip.duration)
            audio_clip.close()

        # Generate progressive frames
        frame_paths = overlay.create_progressive_frames(audio_durations, fps=FPS)
        logger.success(f"Generated {len(frame_paths)} progressive frames")

    except Exception as e:
        logger.error(f"Failed to create progressive overlay: {e}")
        sys.exit(1)

    # Select background video
    background_video = get_random_background_video(BACKGROUND_VIDEO_FOLDER)
    if background_video:
        logger.info(f"Using background video: {background_video}")
    else:
        logger.warning(f"No background videos found in {BACKGROUND_VIDEO_FOLDER}. Using frames only.")

    logger.info("Building the final video...")
    try:
        # Use the first frame as the base image for video generation
        # The overlay builder will handle the progressive frames
        build_video([screenshot_path], audio_paths, OUTPUT_VIDEO_PATH, 
                   background_video_path=background_video, fps=FPS)
        logger.success(f"Video saved to {OUTPUT_VIDEO_PATH}")
    except Exception as e:
        logger.error(f"Failed to build video: {e}")
        sys.exit(1)

    # Optional cleanup
    # cleanup_temp_dirs(TEMP_IMG_DIR, TEMP_AUDIO_DIR, TEMP_FRAMES_DIR)

if __name__ == "__main__":
    main() 