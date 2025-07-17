import os
from loguru import logger
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import concatenate_audioclips
import moviepy

def build_video(frame_paths, audio_paths, output_path, background_video_path=None, fps=30):
    """
    Build video with WhatsApp chat frames overlaid at the top of a looping background video with TTS audio.
    """
    logger.info(f"Building video with {len(frame_paths)} frames and {len(audio_paths)} audio clips")
    logger.debug(f"Output path: {output_path}")
    logger.debug(f"Background video: {background_video_path}")

    # Calculate total duration
    total_duration = len(frame_paths) / fps
    logger.info(f"Total video duration: {total_duration:.2f}s")

    # Create the chat overlay video (from frames)
    chat_clip = ImageSequenceClip(frame_paths, fps=fps)

    # Concatenate all audio clips
    logger.info("Concatenating TTS audio clips...")
    audio_clips = [AudioFileClip(audio_path) for audio_path in audio_paths]
    combined_audio = concatenate_audioclips(audio_clips)

    if background_video_path and os.path.exists(background_video_path):
        logger.info(f"Loading and looping background video: {background_video_path}")
        bg_clip = VideoFileClip(background_video_path)
        # Loop the background video to match the total duration
        if bg_clip.duration < total_duration:
            n_loops = int(total_duration // bg_clip.duration) + 1
            logger.info(f"Background video duration: {bg_clip.duration:.2f}s, will loop {n_loops} times")
            looped_clips = [bg_clip] * n_loops
            bg_clip = moviepy.concatenate_videoclips(looped_clips)
            bg_clip = bg_clip.subclipped(0, total_duration)
        else:
            bg_clip = bg_clip.subclipped(0, total_duration)
        # Make chat overlay smaller (80% of background width)
        target_width = int(bg_clip.w * 0.8)
        target_height = int(chat_clip.h * target_width / chat_clip.w)
        chat_clip_resized = chat_clip.resized((target_width, target_height))
        # Use with_position to place at the top
        composite = CompositeVideoClip([
            bg_clip,
            chat_clip_resized.with_position((0, 0))
        ], size=bg_clip.size)
        final_clip = composite.with_duration(total_duration)
    else:
        logger.warning("No background video found, using chat frames only.")
        final_clip = chat_clip.with_duration(total_duration)

    # Add the audio to the final clip
    final_clip = final_clip.with_audio(combined_audio)

    logger.info(f"Writing final video to: {output_path}")
    logger.debug(f"Video settings: fps={fps}, codec=libx264, audio_codec=aac")
    final_clip.write_videofile(output_path, fps=fps, codec='libx264', audio_codec='aac')
    logger.success(f"Video successfully created: {output_path}") 