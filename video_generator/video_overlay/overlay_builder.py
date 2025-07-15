import os
from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips, VideoFileClip, CompositeVideoClip

def build_video(image_paths, audio_paths, output_path, background_video_path=None, fps=30):
    """
    Build video with WhatsApp images overlaid on background video (if provided)
    """
    clips = []
    
    for img_path, audio_path in zip(image_paths, audio_paths):
        audio_clip = AudioFileClip(audio_path)
        duration = audio_clip.duration
        
        if background_video_path and os.path.exists(background_video_path):
            # Use background video
            bg_clip = VideoFileClip(background_video_path).subclip(0, duration)
            img_clip = ImageClip(img_path).set_duration(duration).set_fps(fps)
            
            # Composite image over background video
            composite = CompositeVideoClip([bg_clip, img_clip.set_position(('center', 'bottom'))])
            composite = composite.set_audio(audio_clip)
            clips.append(composite)
        else:
            # Use image only (no background video)
            img_clip = ImageClip(img_path).set_duration(duration).set_fps(fps)
            img_clip = img_clip.set_audio(audio_clip)
            clips.append(img_clip)
    
    final_clip = concatenate_videoclips(clips)
    final_clip.write_videofile(output_path, fps=fps, codec='libx264', audio_codec='aac') 