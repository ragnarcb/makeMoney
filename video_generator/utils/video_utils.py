import os
import random
from pathlib import Path

def get_random_background_video(video_folder_path):
    """
    Select a random video file from the specified folder
    """
    if not os.path.exists(video_folder_path):
        return None
    
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    video_files = []
    
    for file in os.listdir(video_folder_path):
        if any(file.lower().endswith(ext) for ext in video_extensions):
            video_files.append(os.path.join(video_folder_path, file))
    
    if not video_files:
        return None
    
    return random.choice(video_files)

def validate_video_file(video_path):
    """
    Check if a video file exists and is valid
    """
    if not video_path or not os.path.exists(video_path):
        return False
    
    # Basic check - file exists and has video extension
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
    return any(video_path.lower().endswith(ext) for ext in video_extensions)

def get_video_duration(video_path):
    """
    Get the duration of a video file in seconds
    """
    try:
        from moviepy.editor import VideoFileClip
        clip = VideoFileClip(video_path)
        duration = clip.duration
        clip.close()
        return duration
    except Exception:
        return None 