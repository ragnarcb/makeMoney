import os
from loguru import logger
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from moviepy.video.compositing.CompositeVideoClip import CompositeVideoClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.audio.AudioClip import concatenate_audioclips, AudioArrayClip
import moviepy
import numpy as np

def make_silence(duration, fps=44100):
    # Returns a silent AudioArrayClip of the given duration (in seconds)
    arr = np.zeros((int(duration * fps), 1), dtype=np.float32)
    return AudioArrayClip(arr, fps)

def build_video(frame_paths, audio_paths, output_path, background_video_path=None, fps=30, 
                start_buffer=1.0, end_buffer=3.0, pause_between_messages=0.5, audio_fps=44100):
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

    # Concatenate all audio clips with silence buffers and pauses
    logger.info("Concatenating TTS audio clips with silence buffers and pauses...")
    audio_clips = [AudioFileClip(audio_path) for audio_path in audio_paths]

    # Calculate durations for each TTS audio
    tts_durations = [clip.duration for clip in audio_clips]
    logger.info(f"TTS durations: {tts_durations}")

    # Build the audio track: start_silence + [tts, pause, tts, pause, ...] + end_silence
    clips = []
    # Start buffer
    if start_buffer > 0:
        clips.append(make_silence(start_buffer, fps=audio_fps))
    # Interleave TTS and pauses
    for i, tts_clip in enumerate(audio_clips):
        clips.append(tts_clip)
        if i < len(audio_clips) - 1 and pause_between_messages > 0:
            clips.append(make_silence(pause_between_messages, fps=audio_fps))
    # End buffer
    if end_buffer > 0:
        clips.append(make_silence(end_buffer, fps=audio_fps))
    combined_audio = concatenate_audioclips(clips)

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
        # Center horizontally and add vertical offset
        x_center = (bg_clip.w - target_width) // 2
        y_offset = 40  # pixels from the top
        composite = CompositeVideoClip([
            bg_clip,
            chat_clip_resized.with_position((x_center, y_offset))
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