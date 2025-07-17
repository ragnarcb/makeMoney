import os
from loguru import logger
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip

def build_video(frame_paths, output_path, background_video_path=None, fps=30):
    """
    Build video with WhatsApp chat frames overlaid at the top of a looping background video.
    """
    logger.info(f"Building video with {len(frame_paths)} frames")
    logger.debug(f"Output path: {output_path}")
    logger.debug(f"Background video: {background_video_path}")

    # Calculate total duration
    total_duration = len(frame_paths) / fps
    logger.info(f"Total video duration: {total_duration:.2f}s")

    # Create the chat overlay video (from frames)
    chat_clip = ImageSequenceClip(frame_paths, fps=fps)

    if background_video_path and os.path.exists(background_video_path):
        logger.info(f"Loading background video: {background_video_path}")
        bg_clip = VideoFileClip(background_video_path)
        # Use the background video (will repeat if shorter than total duration)
        if bg_clip.duration < total_duration:
            logger.info(f"Background video duration: {bg_clip.duration:.2f}s, will repeat")
        # Use subclipped instead of subclip for moviepy 20.10.2
        bg_clip = bg_clip.subclipped(0, min(bg_clip.duration, total_duration))
        # Create composite with proper positioning and duration
        composite = CompositeVideoClip([
            bg_clip,
            chat_clip.with_position((0, 0))
        ], size=bg_clip.size)
        final_clip = composite.with_duration(total_duration)
    else:
        logger.warning("No background video found, using chat frames only.")
        final_clip = chat_clip

    logger.info(f"Writing final video to: {output_path}")
    logger.debug(f"Video settings: fps={fps}, codec=libx264, audio_codec=aac")
    final_clip.write_videofile(output_path, fps=fps, codec='libx264', audio_codec='aac')
    logger.success(f"Video successfully created: {output_path}") 