import os
import json
from loguru import logger
from whatsapp_gen.chat_generator import generate_chat
from whatsapp_gen.chat_image_renderer import get_chat_images
from tts.tts_generator import generate_tts
from video_overlay.overlay_builder import build_video
from utils.file_utils import cleanup_temp_dirs
from utils.video_utils import get_random_background_video, validate_video_file
import sys
import argparse

# --- CONFIG ---
PARTICIPANTS = ["Ana", "Bruno"]
TEMP_IMG_DIR = "temp_chat_imgs"
TEMP_AUDIO_DIR = "temp_audio"
OUTPUT_VIDEO_PATH = "output_with_overlay.mp4"
BACKGROUND_VIDEO_FOLDER = "../background_videos"  # Folder containing background videos
LANG = 'pt-br'
FPS = 30
IMG_SIZE = (1920, 1080)  # height, width (portrait)

def main():
    parser = argparse.ArgumentParser(description="Generate WhatsApp video with custom prompt")
    parser.add_argument("--prompt", type=str, help="Custom prompt for the conversation", default=None)
    parser.add_argument("--participants", nargs=2, default=PARTICIPANTS, help="Participant names")
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

    logger.info("Calling Node.js API to generate WhatsApp images...")
    try:
        img_paths = get_chat_images(messages, args.participants, TEMP_IMG_DIR, img_size=IMG_SIZE)
        logger.success(f"Generated {len(img_paths)} WhatsApp images via Node.js API.")
    except Exception as e:
        logger.error(f"Failed to generate WhatsApp images: {e}")
        logger.error("Make sure the Node.js server is running: cd ../whatsapp-clone && npm run server")
        sys.exit(1)

    if not img_paths:
        logger.error("No images were generated. Check the Node.js API.")
        sys.exit(1)

    # Select background video
    background_video = get_random_background_video(BACKGROUND_VIDEO_FOLDER)
    if background_video:
        logger.info(f"Using background video: {background_video}")
    else:
        logger.warning(f"No background videos found in {BACKGROUND_VIDEO_FOLDER}. Using images only.")

    logger.info("Building the final video...")
    build_video(img_paths, audio_paths, OUTPUT_VIDEO_PATH, background_video_path=background_video, fps=FPS)
    logger.success(f"Overlay video saved to {OUTPUT_VIDEO_PATH}")

    # Optional cleanup
    # cleanup_temp_dirs(TEMP_IMG_DIR, TEMP_AUDIO_DIR)

if __name__ == "__main__":
    main() 