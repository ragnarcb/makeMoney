import os
import json
from typing import List, Dict
from PIL import Image, ImageDraw
from loguru import logger

class ProgressiveMessageOverlay:
    """Creates progressive message overlays with improved display logic.
    Shows ~4 messages at a time, then clears and restarts from top."""
    def __init__(self, screenshot_path: str, message_coordinates: List[Dict], 
                 output_dir: str = "temp_frames", messages_per_group: int = 4):
        self.screenshot_path = screenshot_path
        self.message_coordinates = message_coordinates
        self.output_dir = output_dir
        self.messages_per_group = messages_per_group
        self.base_image = None
        self.cropped_image = None
        self.frame_paths = []
        
        logger.info(f"Initializing ProgressiveMessageOverlay with {len(message_coordinates)} message coordinates")
        logger.info(f"Will show {messages_per_group} messages per group")
        logger.debug(f"Screenshot path: {screenshot_path}")
        logger.debug(f"Output directory: {output_dir}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Load and crop the base screenshot
        self._load_and_crop_base_image()

    def _load_and_crop_base_image(self):
        """Load the base WhatsApp screenshot and crop out borders."""
        try:
            self.base_image = Image.open(self.screenshot_path)
            logger.info(f"Loaded base image: {self.base_image.size}")
            logger.debug(f"Image mode: {self.base_image.mode}")
            # Crop out borders - find the actual chat area
            self.cropped_image = self._crop_whatsapp_borders()
            logger.info(f"Cropped image size: {self.cropped_image.size}")
        except Exception as e:
            logger.error(f"Error loading/cropping base image: {e}")
            raise

    def _crop_whatsapp_borders(self) -> Image.Image:
        """Automatically detect and crop WhatsApp borders to show only the chat area."""
        # Convert to RGBA if needed
        if self.base_image.mode != 'RGBA':
            self.base_image = self.base_image.convert('RGBA')
        width, height = self.base_image.size
        if self.message_coordinates:
            top_y = min(coord['y'] for coord in self.message_coordinates)
            bottom_y = max(coord['y'] + coord['height'] for coord in self.message_coordinates)
            top_padding = max(0, top_y - 100)
            bottom_padding = min(height, bottom_y + 100)
            logger.debug(f"Auto-crop boundaries: top={top_padding}, bottom={bottom_padding}")
            cropped = self.base_image.crop((0, top_padding, width, bottom_padding))
        else:
            top_crop = int(height * 0.2)
            bottom_crop = int(height * 0.85)
            cropped = self.base_image.crop((0, top_crop, width, bottom_crop))
            logger.debug(f"Fallback crop: top={top_crop}, bottom={bottom_crop}")
        # Ensure cropped is RGBA
        if cropped.mode != 'RGBA':
            cropped = cropped.convert('RGBA')
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
                for frame_idx in range(frames_for_message):
                    frame_path = self._create_group_frame(group_messages, i + 1, current_frame)
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
        """Create a frame showing the specified number of messages from the group."""
        # Create a transparent frame
        frame = Image.new('RGBA', self.cropped_image.size, (0, 0, 0, 0))
        if messages_shown > 0:
            messages_to_show = group_messages[:messages_shown]
            if messages_to_show:
                first_msg_idx = messages_to_show[0]
                last_msg_idx = messages_to_show[-1]
                first_coord = self.message_coordinates[first_msg_idx]
                last_coord = self.message_coordinates[last_msg_idx]
                top_y = max(0, first_coord['y'] - 20)
                bottom_y = min(self.cropped_image.height, last_coord['y'] + last_coord['height'] + 20)
                cropped_portion = self.cropped_image.crop((0, top_y, self.cropped_image.width, bottom_y))
                # Ensure cropped_portion is RGBA
                if cropped_portion.mode != 'RGBA':
                    cropped_portion = cropped_portion.convert('RGBA')
                frame.paste(cropped_portion, (0, 0), mask=cropped_portion)
                logger.debug(f"Frame {frame_number}: Showing messages {[m+1 for m in messages_to_show]} (y={top_y}-{bottom_y})")
        frame_path = os.path.join(self.output_dir, f"frame_{frame_number:06d}.png")
        frame.save(frame_path)
        return frame_path

    def _create_empty_frame(self, frame_number: int) -> str:
        """Create an empty frame (for buffers)."""
        frame = Image.new('RGBA', self.cropped_image.size, (0, 0, 0, 0))
        frame_path = os.path.join(self.output_dir, f"frame_{frame_number:06d}.png")
        frame.save(frame_path)
        return frame_path

    def get_total_duration(self, audio_durations: List[float], start_buffer: float = 1.0, end_buffer: float = 3.0) -> float:
        """Calculate the total video duration including buffers."""
        total_audio_duration = sum(audio_durations)
        total_duration = start_buffer + total_audio_duration + end_buffer
        logger.info(f"Total video duration: {total_duration:.2f}s (audio: {total_audio_duration:.2f}s + buffers: {start_buffer + end_buffer:.2f}s)")
        return total_duration

    def cleanup_frames(self):
        """Clean up generated frame files."""
        logger.info(f"Cleaning up {len(self.frame_paths)} frame files")
        for frame_path in self.frame_paths:
            try:
                if os.path.exists(frame_path):
                    os.remove(frame_path)
                    logger.debug(f"Removed frame: {frame_path}")
            except Exception as e:
                logger.error(f"Error removing frame {frame_path}: {e}")
        try:
            if os.path.exists(self.output_dir) and not os.listdir(self.output_dir):
                os.rmdir(self.output_dir)
                logger.debug(f"Removed empty output directory: {self.output_dir}")
        except Exception as e:
            logger.error(f"Error removing output directory: {e}")

    def get_frame_info(self) -> Dict:
        """Get information about the generated frames."""
        info = {
            "total_frames": len(self.frame_paths),
            "output_dir": self.output_dir,
            "base_image_size": self.base_image.size if self.base_image else None,
            "cropped_image_size": self.cropped_image.size if self.cropped_image else None,
            "message_count": len(self.message_coordinates),
            "messages_per_group": self.messages_per_group
        }
        logger.debug(f"Frame info: {info}")
        return info 