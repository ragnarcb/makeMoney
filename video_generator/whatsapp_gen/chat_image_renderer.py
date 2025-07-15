import os
import numpy as np
import cv2
import json
import argparse
import requests  # For future use

def create_whatsapp_header(participants, img_size):
    """Create a WhatsApp-style header with profile info"""
    header_height = 120
    header = np.ones((header_height, img_size[1], 3), dtype=np.uint8) * 240  # Light gray background
    
    # Add back arrow
    cv2.putText(header, "<", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 2)
    
    # Add profile picture placeholder (circle)
    center_x = img_size[1] // 2
    cv2.circle(header, (center_x, 60), 25, (0, 150, 0), -1)  # Green circle
    
    # Add name
    name = f"{participants[0]} & {participants[1]}"
    cv2.putText(header, name, (center_x - 100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # Add "Online" status
    cv2.putText(header, "Online", (center_x - 50, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 150, 0), 2)
    
    # Add call buttons
    cv2.putText(header, "📞", (img_size[1] - 80, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    cv2.putText(header, "📹", (img_size[1] - 40, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    return header

def create_message_bubble(text, sender, is_sender, img_size):
    """Create a WhatsApp-style message bubble"""
    # Estimate bubble size based on text length
    text_width = len(text) * 15  # Rough estimate
    bubble_width = min(max(text_width, 200), img_size[1] - 100)
    bubble_height = 60
    
    if is_sender:
        # Green bubble (right side)
        bubble = np.ones((bubble_height, bubble_width, 3), dtype=np.uint8) * [0, 150, 0]
        x_offset = img_size[1] - bubble_width - 20
    else:
        # Gray bubble (left side)
        bubble = np.ones((bubble_height, bubble_width, 3), dtype=np.uint8) * [240, 240, 240]
        x_offset = 20
    
    # Add text to bubble
    cv2.putText(bubble, text, (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    
    return bubble, x_offset, bubble_height

def render_chat_images(messages, participants, out_dir, img_size=(1920, 1080)):
    """Render progressive WhatsApp chat images with header and message bubbles"""
    os.makedirs(out_dir, exist_ok=True)
    
    # Create header
    header = create_whatsapp_header(participants, img_size)
    
    img_paths = []
    for i in range(1, len(messages) + 1):
        # Create full image with header
        full_img = np.ones((img_size[0], img_size[1], 3), dtype=np.uint8) * 255  # White background
        
        # Add header
        full_img[:header.shape[0], :] = header
        
        # Add messages progressively
        y_offset = header.shape[0] + 20
        for j in range(i):
            msg = messages[j]
            text = msg['text']
            sender = msg['from']
            is_sender = (sender == participants[0])  # First participant is sender
            
            bubble, x_offset, bubble_height = create_message_bubble(text, sender, is_sender, img_size)
            
            # Add bubble to image
            if y_offset + bubble_height < img_size[0]:
                full_img[y_offset:y_offset + bubble_height, x_offset:x_offset + bubble.shape[1]] = bubble
                y_offset += bubble_height + 10
        
        # Save composite image
        out_path = os.path.join(out_dir, f"chat_progressive_{i}.png")
        cv2.imwrite(out_path, full_img)
        img_paths.append(out_path)
    
    return img_paths

def get_chat_images(messages, participants, out_dir, use_external=False, api_url=None, img_size=(1920, 1080)):
    """
    Abstraction for chat image generation.
    If use_external is True and api_url is provided, call the external API.
    Otherwise, use the local render_chat_images.
    """
    if use_external and api_url:
        # Example: POST to external API
        response = requests.post(api_url, json={"messages": messages, "participants": participants, "out_dir": out_dir, "img_size": img_size})
        response.raise_for_status()
        return response.json()["image_paths"]
    else:
        return render_chat_images(messages, participants, out_dir, img_size)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render WhatsApp chat images from JSON messages.")
    parser.add_argument("--json", required=True, help="Path to JSON file with messages list.")
    parser.add_argument("--out_dir", required=True, help="Directory to save output images.")
    parser.add_argument("--participants", nargs=2, default=["Ana", "Bruno"], help="Participant names.")
    args = parser.parse_args()

    with open(args.json, "r", encoding="utf-8") as f:
        messages = json.load(f)
    img_paths = render_chat_images(messages, args.participants, args.out_dir)
    print(json.dumps(img_paths, ensure_ascii=False, indent=2)) 