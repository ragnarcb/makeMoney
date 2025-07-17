import os
import json
import argparse
import asyncio
import sys
from pathlib import Path

# Add screenshotter to path
sys.path.append(str(Path(__file__).parent.parent.parent / "screenshotter"))

def render_chat_images(messages, participants, out_dir, img_size=(1920, 1080)):
    """
    Use the existing screenshotter automation to generate WhatsApp images
    """
    os.makedirs(out_dir, exist_ok=True)
    
    # Import the automation class
    try:
        from whatsapp_screenshot_automation import WhatsAppScreenshotAutomation
    except ImportError as e:
        raise Exception(f"Could not import screenshotter: {e}. Make sure the screenshotter folder is available.")
    
    async def generate_screenshots():
        automation = WhatsAppScreenshotAutomation(headless=True, output_dir=out_dir)
        
        try:
            await automation.start_browser()
            await automation.navigate_to_app("http://localhost:8089")
            
            image_paths = []
            
            # Generate progressive screenshots (1 message, 2 messages, etc.)
            for i in range(1, len(messages) + 1):
                # TODO: Here you would need to inject the messages into the WhatsApp app
                # For now, we'll capture the current state
                
                # Capture full screen for this message count
                timestamp = f"progressive_{i:03d}"
                filename = f"whatsapp_{i}.png"
                
                # Use the existing capture method
                screenshot_path = await automation.capture_full_screen(filename)
                
                if screenshot_path:
                    image_paths.append(str(screenshot_path))
                else:
                    # Fallback: create a placeholder
                    placeholder_path = os.path.join(out_dir, filename)
                    create_placeholder_image(placeholder_path, f"Message {i}", img_size)
                    image_paths.append(placeholder_path)
            
            return image_paths
            
        finally:
            await automation.close()
    
    # Run the async function
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(generate_screenshots())

def create_placeholder_image(path, text, img_size):
    """Create a placeholder image when screenshot fails"""
    try:
        import numpy as np
        import cv2
        
        # Create a simple placeholder
        img = np.ones((img_size[0], img_size[1], 3), dtype=np.uint8) * 255
        cv2.putText(img, text, (50, img_size[0]//2), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,0,0), 3)
        cv2.imwrite(path, img)
        
    except ImportError:
        # If OpenCV is not available, create a simple text file
        with open(path + '.txt', 'w') as f:
            f.write(f"Placeholder for: {text}")

def get_chat_images(messages, participants, out_dir, use_external=True, api_url="http://localhost:3001/api/generate-screenshots", img_size=(1920, 1080)):
    """
    Abstraction for chat image generation.
    If use_external is True and api_url is provided, call the external API.
    Otherwise, use the local screenshotter automation.
    """
    if use_external and api_url:
        # Call external Node.js API
        import requests
        payload = {
            "messages": messages,
            "participants": participants,
            "outputDir": out_dir,
            "img_size": img_size
        }
        try:
            response = requests.post(api_url, json=payload, timeout=60)
            response.raise_for_status()
            result = response.json()
            if result.get("success"):
                return result["imagePaths"]
            else:
                raise Exception(f"API returned error: {result.get('error', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            print(f"Failed to call Node.js API: {e}")
            print("Falling back to screenshotter automation...")
            return render_chat_images(messages, participants, out_dir, img_size)
    else:
        # Use local screenshotter automation
        return render_chat_images(messages, participants, out_dir, img_size)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate WhatsApp images using screenshotter automation.")
    parser.add_argument("--json", required=True, help="Path to JSON file with messages list.")
    parser.add_argument("--out_dir", required=True, help="Directory to save output images.")
    parser.add_argument("--participants", nargs=2, default=["Ana", "Bruno"], help="Participant names.")
    args = parser.parse_args()

    with open(args.json, "r", encoding="utf-8") as f:
        messages = json.load(f)
    img_paths = render_chat_images(messages, args.participants, args.out_dir)
    print(json.dumps(img_paths, ensure_ascii=False, indent=2)) 