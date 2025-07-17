import os
from loguru import logger
from moviepy import ImageClip, AudioFileClip, concatenate_videoclips, VideoFileClip, CompositeVideoClip

def build_video(image_paths, audio_paths, output_path, background_video_path=None, fps=30):
    """
    Build video with WhatsApp images overlaid on background video (if provided)
    """
    clips = []
    
    logger.info(f"Building video with {len(image_paths)} images and {len(audio_paths)} audio clips")
    logger.debug(f"Output path: {output_path}")
    logger.debug(f"Background video: {background_video_path}")
    
    for i, (img_path, audio_path) in enumerate(zip(image_paths, audio_paths)):
        logger.debug(f"Processing clip {i+1}/{len(image_paths)}: {img_path}")
        
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        logger.debug(f"Audio duration: {duration:.2f}s")
        
        if background_video_path and os.path.exists(background_video_path):
            # Use background video
            logger.debug(f"Loading background video: {background_video_path}")
            bg_clip = VideoFileClip(background_video_path)
            
            # Use the correct method for newer moviepy versions
            if hasattr(bg_clip, 'subclip'):
                bg_clip = bg_clip.subclip(0, duration)
            else:
                # For newer versions, use slice notation
                bg_clip = bg_clip[:duration]
            
            # Create ImageClip with duration parameter only
            img_clip = ImageClip(img_path, duration=duration)
            
            # Composite image over background video
            # Position the image at the center-bottom of the video
            composite = CompositeVideoClip([bg_clip, img_clip], size=bg_clip.size)
            # Set audio on the composite clip
            composite = composite.with_audio(audio_clip)
            clips.append(composite)
            
            logger.debug(f"Created composite clip {i+1} with background video")
        else:
            # Use image only (no background video)
            logger.debug(f"Creating image-only clip {i+1}")
            # Create ImageClip with duration parameter only
            img_clip = ImageClip(img_path, duration=duration)
            img_clip = img_clip.with_audio(audio_clip)
            clips.append(img_clip)
    
    logger.info(f"Concatenating {len(clips)} video clips")
    final_clip = concatenate_videoclips(clips)
    
    logger.info(f"Writing final video to: {output_path}")
    logger.debug(f"Video settings: fps={fps}, codec=libx264, audio_codec=aac")
    
    final_clip.write_videofile(output_path, fps=fps, codec='libx264', audio_codec='aac')
    logger.success(f"Video successfully created: {output_path}") 