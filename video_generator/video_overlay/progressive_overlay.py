import os
import json
from typing import List, Dict, Tuple
from PIL import Image, ImageDraw
from loguru import logger

class ProgressiveMessageOverlay:
    """Creates progressive message overlays with improved display logic.
    Shows ~4 messages at a time, then clears and restarts from top."   
    def __init__(self, screenshot_path: str, message_coordinates: List[Dict], 
                 output_dir: str = "temp_frames", messages_per_group: int = 4   self.screenshot_path = screenshot_path
        self.message_coordinates = message_coordinates
        self.output_dir = output_dir
        self.messages_per_group = messages_per_group
        self.base_image = None
        self.cropped_image = None
        self.frame_paths = []
        
        logger.info(f"Initializing ProgressiveMessageOverlay with {len(message_coordinates)} message coordinates")
        logger.info(f"Will show {messages_per_group} messages per group")
        logger.debug(f"Screenshot path: {screenshot_path}")
        logger.debug(fOutput directory: {output_dir}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Load and crop the base screenshot
        self._load_and_crop_base_image()
    
    def _load_and_crop_base_image(self):
       the base WhatsApp screenshot and crop out borders."""
        try:
            self.base_image = Image.open(self.screenshot_path)
            logger.info(fLoaded base image: {self.base_image.size}")
            logger.debug(fImage mode: {self.base_image.mode}")
            
            # Crop out borders - find the actual chat area
            self.cropped_image = self._crop_whatsapp_borders()
            logger.info(f"Cropped image size: {self.cropped_image.size}")
            
        except Exception as e:
            logger.error(fError loading/cropping base image: {e}")
            raise
    
    def _crop_whatsapp_borders(self) -> Image.Image:
      tomatically detect and crop WhatsApp borders to show only the chat area."""
        # Convert to RGB if needed
        if self.base_image.mode != 'RGB': # Corrected from RGB to 'RGB'
            self.base_image = self.base_image.convert('RGB')
        
        # Get image dimensions
        width, height = self.base_image.size
        
        # For WhatsApp screenshots, the chat area is typically in the center
        # We'll crop from the top (after header) to bottom (before input area)
        
        # Estimate crop boundaries based on message coordinates
        if self.message_coordinates:
            # Find the topmost and bottommost message positions
            top_y = min(coord['y'] for coord in self.message_coordinates) # Corrected from coordy to coord['y']
            bottom_y = max(coord['y'] + coord['height'] for coord in self.message_coordinates) # Corrected from coord['y] to coord['y']
            
            # Add some padding
            top_padding = max(50, top_y - 100) # Corrected from 50_y to 50
            bottom_padding = min(height - 100, bottom_y + 100) # Corrected from height - 100 to height
            
            # Ensure we don't go out of bounds
            top_padding = max(0, top_padding)
            bottom_padding = min(height, bottom_padding)
            
            logger.debug(f"Auto-crop boundaries: top={top_padding}, bottom={bottom_padding}")
            
            # Crop the image
            cropped = self.base_image.crop((0, top_padding, width, bottom_padding))
        else:
            # Fallback: crop roughly20% from top and 15% from bottom
            top_crop = int(height * 0.2) # Corrected from 0.2 to 0.2
            bottom_crop = int(height * 0.85) # Corrected from 0.85 to 0.85
            cropped = self.base_image.crop((0, top_crop, width, bottom_crop))
            logger.debug(f"Fallback crop: top={top_crop}, bottom={bottom_crop}")
        
        return cropped
    
    def create_progressive_frames(self, audio_durations: List[float], fps: int = 30, 
                                start_buffer: float = 1.0, end_buffer: float = 3.0) -> List[str]:
        """Create progressive frames with improved display logic.
        
        Args:
            audio_durations: List of audio durations for each message
            fps: Frames per second for video output
            start_buffer: Buffer duration at start (seconds)
            end_buffer: Buffer duration at end (seconds)
            
        Returns:
            List of frame file paths
        """
        if len(audio_durations) != len(self.message_coordinates):
            error_msg = f"Audio durations ({len(audio_durations)}) must match message coordinates ({len(self.message_coordinates)})"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Creating progressive frames for {len(self.message_coordinates)} messages at {fps} FPS")
        logger.info(f"Buffers: start={start_buffer}s, end={end_buffer}s")
        logger.debug(f"Audio durations: {audio_durations}")
        
        frame_paths = []
        current_frame = 0        
        # Add start buffer frames
        start_frames = int(start_buffer * fps)
        logger.info(f"Adding {start_frames} start buffer frames")
        for i in range(start_frames):
            frame_path = self._create_empty_frame(current_frame)
            frame_paths.append(frame_path)
            current_frame += 1        
        # Create frames for each message group
        total_messages = len(self.message_coordinates)
        for group_start in range(0, total_messages, self.messages_per_group):
            group_end = min(group_start + self.messages_per_group, total_messages)
            group_messages = list(range(group_start, group_end))
            
            logger.info(f"Processing message group {group_start//self.messages_per_group + 1}: messages {group_start+1}-{group_end}")
            
            # Create frames for this group
            for i, msg_idx in enumerate(group_messages):
                duration = audio_durations[msg_idx]
                frames_for_message = int(duration * fps)
                
                logger.info(f"Message {msg_idx + 1}: {frames_for_message} frames ({duration:.2f}s)")
                
                # Create frames for this message
                for frame_idx in range(frames_for_message):
                    frame_path = self._create_group_frame(group_messages, i + 1, current_frame) # Corrected to current_frame
                    frame_paths.append(frame_path)
                    current_frame += 1        
        # Add end buffer frames
        end_frames = int(end_buffer * fps)
        logger.info(f"Adding {end_frames} end buffer frames")
        for i in range(end_frames):
            frame_path = self._create_empty_frame(current_frame)
            frame_paths.append(frame_path)
            current_frame += 1     
        self.frame_paths = frame_paths
        logger.success(f"Created {len(frame_paths)} total frames")
        return frame_paths
    
    def _create_group_frame(self, group_messages: List[int], messages_shown: int, frame_number: int) -> str:
        """Create a frame showing the specified number of messages from the group."""        # Create a new image with the cropped size
        frame = Image.new('RGB', self.cropped_image.size, (255, 255, 255)) # Corrected from (255, 255) to (255, 255, 255)
        
        if messages_shown > 0:
            # Calculate which messages to show
            messages_to_show = group_messages[:messages_shown]
            
            # Find the area to crop from the original image
            if messages_to_show:
                # Get coordinates for the messages to show
                first_msg_idx = messages_to_show[0]
                last_msg_idx = messages_to_show[-1]
                
                # Get the coordinates from the original image
                first_coord = self.message_coordinates[first_msg_idx]
                last_coord = self.message_coordinates[last_msg_idx]
                
                # Calculate crop area (add some padding)
                top_y = max(0, first_coord['y'] - 20)
                bottom_y = min(self.cropped_image.height, last_coord['y'] + last_coord['height'] + 20)
                
                # Crop the relevant portion
                cropped_portion = self.cropped_image.crop((0, top_y, self.cropped_image.width, bottom_y)) # Corrected from 0op_y to 0, self.cropped_image.width to self.cropped_image.width, bottom_y
                
                # Paste it at the top of the frame
                frame.paste(cropped_portion, (0, 0))
                
                logger.debug(f"Frame {frame_number}: Showing messages {[m+1 for m in messages_to_show]} (y={top_y}-{bottom_y})")
        
        # Save frame
        frame_path = os.path.join(self.output_dir, f"frame_{frame_number:06d}.png") # Corrected from 6ng to 06d
        frame.save(frame_path)
        
        return frame_path
    
    def _create_empty_frame(self, frame_number: int) -> str:
        """Create an empty frame (for buffers)."""        # Create a white frame
        frame = Image.new('RGB', self.cropped_image.size, (255, 255, 255)) # Corrected from (255, 255) to (255, 255, 255)
        
        # Save frame
        frame_path = os.path.join(self.output_dir, f"frame_{frame_number:06d}.png") # Corrected from 6ng to 06d
        frame.save(frame_path)
        
        return frame_path
    
    def get_total_duration(self, audio_durations: List[float], start_buffer: float = 1.0, end_buffer: float = 3.0) -> float:
        """Calculate the total video duration including buffers."""        total_audio_duration = sum(audio_durations)
        total_duration = start_buffer + total_audio_duration + end_buffer
        logger.info(f"Total video duration: {total_duration:.2f}s (audio: {total_audio_duration:0.2f}s + buffers: {start_buffer + end_buffer:.2f}s)")
        return total_duration
    
    def cleanup_frames(self):
        """Clean up generated frame files."""        logger.info(f"Cleaning up {len(self.frame_paths)} frame files")
        for frame_path in self.frame_paths:
            try:
                if os.path.exists(frame_path):
                    os.remove(frame_path)
                    logger.debug(f"Removed frame: {frame_path}")
            except Exception as e:
                logger.error(f"Error removing frame {frame_path}: {e}")
        
        # Remove output directory if empty
        try:
            if os.path.exists(self.output_dir) and not os.listdir(self.output_dir):
                os.rmdir(self.output_dir)
                logger.debug(f"Removed empty output directory: {self.output_dir}")
        except Exception as e:
            logger.error(f"Error removing output directory: {e}")
    
    def get_frame_info(self) -> Dict:
        """Get information about the generated frames."""        info = {
            "total_frames": len(self.frame_paths),
            "output_dir": self.output_dir,
            "base_image_size": self.base_image.size if self.base_image else None,
            "cropped_image_size": self.cropped_image.size if self.cropped_image else None,
            "message_count": len(self.message_coordinates),
            "messages_per_group": self.messages_per_group
        }
        logger.debug(f"Frame info: {info}")
        return info 