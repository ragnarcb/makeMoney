import os
import json
from typing import List, Dict, Tuple
from PIL import Image, ImageDraw

class ProgressiveMessageOverlay:
    """Creates progressive message overlays using a single screenshot and message coordinates.
    Progressively reveals more of the image as messages are spoken."""   
    def __init__(self, screenshot_path: str, message_coordinates: List[Dict], 
                 output_dir: str = "temp_frames"):
        self.screenshot_path = screenshot_path
        self.message_coordinates = message_coordinates
        self.output_dir = output_dir
        self.base_image = None
        self.frame_paths = []
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Load the base screenshot
        self._load_base_image()
    
    def _load_base_image(self):
        """Load the base WhatsApp screenshot."""
        try:
            self.base_image = Image.open(self.screenshot_path)
            print(f"Loaded base image: {self.base_image.size}")
        except Exception as e:
            print(f"Error loading base image: {e}")
            raise
    
    def create_progressive_frames(self, audio_durations: List[float], fps: int = 30) -> List[str]:
        """Create progressive frames that reveal messages as TTS speaks.
        
        Args:
            audio_durations: List of audio durations for each message
            fps: Frames per second for video output
            
        Returns:
            List of frame file paths
        """
        if len(audio_durations) != len(self.message_coordinates):
            raise ValueError(f"Audio durations ({len(audio_durations)}) must match message coordinates ({len(self.message_coordinates)})")
        
        print(f"Creating progressive frames for {len(self.message_coordinates)} messages...")
        
        frame_paths = []
        current_frame = 0        
        # Create frames for each message
        for i, (coord, duration) in enumerate(zip(self.message_coordinates, audio_durations)):
            frames_for_message = int(duration * fps)
            
            print(f"Message {i}: {frames_for_message} frames ({duration:.2f}s)")
            
            # Create frames for this message
            for frame_idx in range(frames_for_message):
                frame_path = self._create_frame_at_step(i + 1, current_frame, frame_idx, frames_for_message)
                frame_paths.append(frame_path)
                current_frame += 1     
        self.frame_paths = frame_paths
        print(f"Created {len(frame_paths)} total frames")
        return frame_paths
    
    def _create_frame_at_step(self, message_count: int, frame_number: int, 
                            frame_in_message: int, total_frames_in_message: int) -> str:
        """Create a single frame showing up to message_count messages.
        
        Instead of overlays, we crop the image to show only the revealed portion.
        """
        # Calculate the reveal height based on how many messages should be shown
        if message_count == 0:
            # Show nothing - just the top portion
            reveal_height = 0
        else:
            # Calculate the bottom Y position of the last message to show
            last_message_idx = message_count - 1
            if last_message_idx < len(self.message_coordinates):
                last_coord = self.message_coordinates[last_message_idx]
                reveal_height = last_coord['y'] + last_coord['height']
            else:
                reveal_height = self.base_image.height
        
        # Ensure base_image is loaded
        if self.base_image is None:
            raise ValueError("Base image not loaded.")
        # Add some padding to the reveal height for smooth transition
        padding = 20
        reveal_height = min(reveal_height + padding, self.base_image.height)

        # Crop the image to show only the revealed portion
        cropped_frame = self.base_image.crop((0, 0, self.base_image.width, reveal_height))

        # If the cropped frame is smaller than the original, pad it with white
        if cropped_frame.height < self.base_image.height:
            # Create a new image with the original size
            final_frame = Image.new('RGB', self.base_image.size, (255, 255, 255))  # Paste the cropped portion at the top
            final_frame.paste(cropped_frame, (0, 0))
        else:
            final_frame = cropped_frame
        
        # Save frame
        frame_path = os.path.join(self.output_dir, f"frame_{frame_number:06d}.png")
        final_frame.save(frame_path)
        
        return frame_path
    
    def cleanup_frames(self):
        """Clean up generated frame files."""
        for frame_path in self.frame_paths:
            try:
                if os.path.exists(frame_path):
                    os.remove(frame_path)
            except Exception as e:
                print(f"Error removing frame {frame_path}: {e}")
        
        # Remove output directory if empty
        try:
            if os.path.exists(self.output_dir) and not os.listdir(self.output_dir):
                os.rmdir(self.output_dir)
        except Exception as e:
            print(f"Error removing output directory: {e}")
    
    def get_frame_info(self) -> Dict:
        """Get information about the generated frames."""
        return {
            "total_frames": len(self.frame_paths),
            "output_dir": self.output_dir,
            "base_image_size": self.base_image.size if self.base_image else None,
            "message_count": len(self.message_coordinates)
        } 