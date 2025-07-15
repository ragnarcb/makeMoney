import cv2
import numpy as np
from moviepy.editor import VideoFileClip
import os

def overlay_image_on_frame(frame, overlay_img, reveal_ratio):
    """
    Overlays a portion of overlay_img onto frame, revealing up to reveal_ratio (0.0 to 1.0) of the image.
    """
    h, w, _ = frame.shape
    oh, ow, _ = overlay_img.shape
    # Calculate how much of the overlay to show
    reveal_height = int(oh * reveal_ratio)
    if reveal_height <= 0:
        return frame
    # Resize overlay to fit frame width
    scale = w / ow
    overlay_resized = cv2.resize(overlay_img, (w, int(oh * scale)))
    # Only take the revealed part
    overlay_cropped = overlay_resized[:reveal_height, :, :]
    # Overlay on the bottom of the frame
    frame[-reveal_height:, :, :] = overlay_cropped
    return frame

def process_video_with_overlay(video_path, image_path, output_path):
    # Load overlay image
    overlay_img = cv2.imread(image_path)
    if overlay_img is None:
        raise FileNotFoundError(f"Overlay image not found: {image_path}")

    def make_frame(t, total_duration, video_clip):
        frame = video_clip.get_frame(t)
        reveal_ratio = min(1.0, t / total_duration)
        frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        frame_overlayed = overlay_image_on_frame(frame_bgr, overlay_img, reveal_ratio)
        return cv2.cvtColor(frame_overlayed, cv2.COLOR_BGR2RGB)

    # Load video
    video_clip = VideoFileClip(video_path)
    total_duration = video_clip.duration
    new_clip = video_clip.fl(lambda gf, t: make_frame(t, total_duration, video_clip))
    new_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')

def main():
    video_path = "../../videoplayback.mp4"  # Adjust as needed
    image_path = "whatsapp_chat.png"         # Placeholder, replace with actual image path
    output_path = "output_with_overlay.mp4"
    if not os.path.exists(video_path):
        print(f"Video not found: {video_path}")
        return
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return
    process_video_with_overlay(video_path, image_path, output_path)
    print(f"Overlay video saved to {output_path}")

if __name__ == "__main__":
    main() 