#!/usr/bin/env python3
"""
Test script to verify the Node.js WhatsApp image generation service (single request, local and upload modes)
"""
import json
import requests
import os
import sys
from PIL import Image, ImageDraw

# Add the video_generator to path so we can import the chat generator
sys.path.append('video_generator')
#from whatsapp_gen.chat_generator import generate_chat

API_URL = "http://localhost:3001"


def print_health_and_queue():
    try:
        health = requests.get(f"{API_URL}/api/health", timeout=10).json()
        print(f"\n🩺 Health: {json.dumps(health, indent=2)}")
    except Exception as e:
        print(f"❌ Could not fetch health: {e}")
    try:
        queue = requests.get(f"{API_URL}/api/queue/status", timeout=10).json()
        print(f"📊 Queue: {json.dumps(queue, indent=2)}")
    except Exception as e:
        print(f"❌ Could not fetch queue status: {e}")


def create_message_boundary_visualization(screenshot_path, message_coordinates):
    try:
        # Open the original screenshot
        img = Image.open(screenshot_path)
        draw = ImageDraw.Draw(img)

        print(f"\n🎨 Creating message boundary visualization...")
        print(f"📏 Image size: {img.size}")
        print(f"📍 Found {len(message_coordinates)} message coordinates:")

        # Draw red lines at message boundaries
        for i, coord in enumerate(message_coordinates):
            y = coord['y']
            height = coord['height']
            width = coord['width']
            from_name = coord['from']
            text = coord['text'][:30] if len(coord['text']) > 30 else coord['text']

            # Draw top boundary (red line)
            draw.line([(0, y), (width, y)], fill='red', width=2)

            # Draw bottom boundary (red line)
            draw.line([(0, y + height), (width, y + height)], fill='red', width=2)

            # Draw left boundary (red line)
            draw.line([(0, y), (0, y + height)], fill='red', width=2)

            # Draw right boundary (red line)
            draw.line([(width, y), (width, y + height)], fill='red', width=2)

            # Add text label
            label = f"{i}: {from_name} - {text}"
            draw.text((5, y + 5), label, fill='red')

            print(f"   📍 Message {i}: Y={y}, H={height}, W={width}, From={from_name}")

        # Save visualization
        base_path = os.path.splitext(screenshot_path)[0]
        viz_path = f"{base_path}_with_boundaries.png"
        img.save(viz_path)

        print(f"✅ Visualization saved: {viz_path}")
        return viz_path

    except Exception as e:
        print(f"❌ Error creating visualization: {e}")
        return None


def test_single_screenshot(messages, participants, output_dir):
    payload = {
        "messages": messages,
        "participants": participants,
        "outputDir": output_dir,
        "img_size": [1920, 1080]
    }
    print(f"\n📸 Testing single screenshot endpoint...")
    try:
        response = requests.post(f"{API_URL}/api/generate-screenshots", json=payload, timeout=120)
        if response.status_code == 200:
            result = response.json()
            print(f"🔍 Result: {json.dumps(result, indent=2)}")
            if result.get("success"):
                image_paths = result.get("imagePaths") or []
                image_urls = result.get("imageUrls") or []
                message_coordinates = result.get("messageCoordinates") or []

                if image_paths:
                    print(f"✅ Local mode: {len(image_paths)} screenshot(s) generated:")
                    for path in image_paths:
                        abs_path = os.path.abspath(path)
                        if os.path.exists(abs_path):
                            size = os.path.getsize(abs_path)
                            print(f"   📸 {abs_path} ({size} bytes)")

                            # Create visualization if we have coordinates
                            if message_coordinates:
                                viz_path = create_message_boundary_visualization(abs_path, message_coordinates)
                                if viz_path:
                                    viz_size = os.path.getsize(viz_path)
                                    print(f"   🎨 {viz_path} ({viz_size} bytes)")
                        else:
                            print(f"   ❌ {abs_path} (file not found)")

                if image_urls:
                    print(f"✅ Upload mode: {len(image_urls)} screenshot(s) uploaded:")
                    for url in image_urls:
                        print(f"   ☁️ {url}")

                if message_coordinates:
                    print(f"✅ Message coordinates extracted: {len(message_coordinates)} messages")
                else:
                    print(f"⚠️  No message coordinates found in response")

                return True
            else:
                print(f"❌ API returned error: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False


def main():
    # Generate test messages
    participants = ["Ana", "Bruno"]
    with open("test_messages.json", "r", encoding="utf-8") as f:
        messages = json.load(f)
    # messages =  #generate_chat(participants)
    # print(f"✅ Generated {len(messages)} messages")
    # with open("test_messages.json", "w", encoding="utf-8") as f:
    #     json.dump(messages, f, ensure_ascii=False, indent=2)
    # print("💾 Saved messages to test_messages.json")

    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)

    print_health_and_queue()

    single_ok = test_single_screenshot(messages, participants, output_dir)

    print_health_and_queue()

    if single_ok:
        print("\n🎉 Node.js service test (single request) completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Node.js service test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 