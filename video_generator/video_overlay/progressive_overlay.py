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

    def _adjust_message_coordinates(self, top_padding: int):
        """Adjust message coordinates to account for the cropping offset."""
        for coord in self.message_coordinates:
            coord['y'] = coord['y'] - top_padding
        logger.debug(f"Adjusted message coordinates by {top_padding} pixels")

    def _crop_whatsapp_borders(self) -> Image.Image:
        """Automatically detect and crop WhatsApp borders to show only the chat area."""
        # Convert to RGBA if needed
        if self.base_image.mode != 'RGBA':
            self.base_image = self.base_image.convert('RGBA')
        width, height = self.base_image.size
        
        if self.message_coordinates:
            # Find the topmost and bottommost message positions
            top_y = min(coord['y'] for coord in self.message_coordinates)
            bottom_y = max(coord['y'] + coord['height'] for coord in self.message_coordinates)
            
            # Add 15px padding for top and bottom messages
            top_padding = max(0, top_y - 15)
            bottom_padding = min(height, bottom_y + 15)
            
            logger.debug(f"Auto-crop boundaries: top={top_padding}, bottom={bottom_padding}")
            
            # Crop the image
            cropped = self.base_image.crop((0, top_padding, width, bottom_padding))
        else:
            # Fallback: crop more aggressively to remove borders
            top_crop = int(height * 0.25)
            bottom_crop = int(height * 0.80)
            cropped = self.base_image.crop((0, top_crop, width, bottom_crop))
            top_padding = top_crop
            logger.debug(f"Fallback crop: top={top_crop}, bottom={bottom_crop}")
        
        # Remove the d7d2d2 colored borders (WhatsApp UI elements)
        cropped = self._remove_whatsapp_borders(cropped)
        
        # Ensure cropped is RGBA
        if cropped.mode != 'RGBA':
            cropped = cropped.convert('RGBA')
        
        # Adjust message coordinates to match the cropped image
        self._adjust_coordinates_for_cropping(top_padding)
        
        return cropped

    def _adjust_coordinates_for_cropping(self, top_padding: int):
        """Adjust message coordinates to match the cropped image."""
        for coord in self.message_coordinates:
            # Adjust Y coordinate to account for the cropping
            coord['y'] = coord['y'] - top_padding
        logger.debug(f"Adjusted message coordinates by {top_padding} pixels for cropping")

    def _remove_whatsapp_borders(self, image: Image.Image) -> Image.Image:
        """Remove WhatsApp UI borders with color d7d2d2."""
        # Convert to RGB for color detection
        rgb_image = image.convert('RGB')
        width, height = rgb_image.size
        
        # Define the border color (d7d2d2)
        border_color = (215, 210, 210)  # RGB equivalent of d7d2d2
        tolerance = 10  # Reduced tolerance to be less aggressive
        
        # Find the actual content boundaries by removing border-colored areas
        left_bound = 0
        right_bound = width
        
        # Scan from left to find first non-border pixel
        for x in range(width):
            if not self._is_border_color(rgb_image, x, height//2, border_color, tolerance):
                left_bound = x
                break
        
        # Scan from right to find last non-border pixel
        for x in range(width-1, -1, -1):
            if not self._is_border_color(rgb_image, x, height//2, border_color, tolerance):
                right_bound = x + 1
                break
        
        # Crop out the border areas
        cropped = image.crop((left_bound, 0, right_bound, height))
        logger.debug(f"Removed borders: left={left_bound}, right={right_bound}, new width={cropped.width}")
        
        # No coordinate adjustments needed
        
        return cropped
    
    def _is_border_color(self, image: Image.Image, x: int, y: int, target_color: tuple, tolerance: int) -> bool:
        """Check if a pixel is close to the border color."""
        try:
            pixel = image.getpixel((x, y))
            return all(abs(p - t) <= tolerance for p, t in zip(pixel, target_color))
        except IndexError:
            return False

    def _add_round_borders(self, image: Image.Image) -> Image.Image:
        """Add round borders to the message image."""
        # Create a new image with rounded corners
        width, height = image.size
        radius = 15 # radius
        
        # Create a mask for rounded corners
        mask = Image.new('L', (width, height), 0)
        draw = ImageDraw.Draw(mask)
        
        # Draw rounded rectangle mask
        draw.rounded_rectangle([(0, 0), (width-1, height-1)], radius=radius, fill=255)
        
        # Apply the mask to create rounded corners
        result = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        result.paste(image, (0, 0), mask=mask)
        
        return result

    def create_progressive_frames(self, audio_durations: List[float], fps: int = 30, 
                                 start_buffer: float = 1.0, end_buffer: float = 3.0, 
                                 pause_between_messages: float = 0.5) -> List[str]:
        """Create progressive frames with improved display logic.
        Args:
            audio_durations: List of audio durations for each message
            fps: Frames per second for video output
            start_buffer: Buffer duration at start (seconds)
            end_buffer: Buffer duration at end (seconds)
            pause_between_messages: Pause duration between messages (seconds)
        Returns:
            List of frame file paths
        """
        if len(audio_durations) != len(self.message_coordinates):
            error_msg = f"Audio durations ({len(audio_durations)}) must match message coordinates ({len(self.message_coordinates)})"
            logger.error(error_msg)
            raise ValueError(error_msg)
        logger.info(f"Creating progressive frames for {len(self.message_coordinates)} messages at {fps} FPS")
        logger.info(f"Buffers: start={start_buffer}s, end={end_buffer}s, pause={pause_between_messages}s")
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
                    # Show exactly the current message being spoken (i+1)
                    # For first message (i=0), show 1 message. For second message (i=1), show 2 messages, etc.
                    frame_path = self._create_group_frame(group_messages, i + 1, current_frame)
                    frame_paths.append(frame_path)
                    current_frame += 1
                # Add pause between messages (except after the last message in a group)
                if i < len(group_messages) - 1:
                    pause_frames = int(pause_between_messages * fps)
                    logger.debug(f"Adding {pause_frames} pause frames after message {msg_idx + 1}")
                    for pause_frame in range(pause_frames):
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
                
                # Calculate crop boundaries with natural spacing
                top_y = self._calculate_top_boundary(first_msg_idx, messages_to_show)
                bottom_y = self._calculate_bottom_boundary(last_msg_idx, messages_to_show)
                
                cropped_portion = self.cropped_image.crop((0, top_y, self.cropped_image.width, bottom_y))
                # Ensure cropped_portion is RGBA
                if cropped_portion.mode != 'RGBA':
                    cropped_portion = cropped_portion.convert('RGBA')
                
                # Add round borders to the messages
                frame_with_borders = self._add_round_borders(cropped_portion)
                
                frame.paste(frame_with_borders, (0, 0), mask=frame_with_borders)
                logger.debug(f"Frame {frame_number}: Showing messages {[m+1 for m in messages_to_show]} (y={top_y}-{bottom_y})")
        frame_path = os.path.join(self.output_dir, f"frame_{frame_number:06d}.png")
        frame.save(frame_path)
        return frame_path

    def _calculate_top_boundary(self, first_msg_idx: int, messages_to_show: List[int]) -> int:
        """Calculate the top boundary for cropping with natural spacing."""
        first_coord = self.message_coordinates[first_msg_idx]
        
        # If this is the first message in the group, add 15px padding above
        if first_msg_idx == messages_to_show[0]:
            return max(0, first_coord['y'] - 15)
        
        # If there's a previous message, cut halfway between them
        prev_msg_idx = first_msg_idx - 1
        if prev_msg_idx >= 0:
            prev_coord = self.message_coordinates[prev_msg_idx]
            prev_bottom = prev_coord['y'] + prev_coord['height']
            current_top = first_coord['y']
            distance = current_top - prev_bottom
            cut_point = prev_bottom + (distance // 2)
            return max(0, cut_point)
        
        # Fallback: 15px padding above
        return max(0, first_coord['y'] - 15)

    def _calculate_bottom_boundary(self, last_msg_idx: int, messages_to_show: List[int]) -> int:
        """Calculate the bottom boundary for cropping with natural spacing."""
        last_coord = self.message_coordinates[last_msg_idx]
        
        # If this is the last message in the group, add 15px padding below
        if last_msg_idx == messages_to_show[-1]:
            return min(self.cropped_image.height, last_coord['y'] + last_coord['height'] + 15)
        
        # If there's a next message, cut halfway between them
        next_msg_idx = last_msg_idx + 1
        if next_msg_idx < len(self.message_coordinates):
            next_coord = self.message_coordinates[next_msg_idx]
            current_bottom = last_coord['y'] + last_coord['height']
            next_top = next_coord['y']
            distance = next_top - current_bottom
            cut_point = current_bottom + (distance // 2)
            return min(self.cropped_image.height, cut_point)
        
        # Fallback: 15px padding below
        return min(self.cropped_image.height, last_coord['y'] + last_coord['height'] + 15)

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