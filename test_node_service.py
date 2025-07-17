#!/usr/bin/env python3
"""
Test script to verify the Node.js WhatsApp image generation service
"""
import json
import requests
import os
import sys

# Add the video_generator to path so we can import the chat generator
sys.path.append('video_generator')
from whatsapp_gen.chat_generator import generate_chat

def test_node_service():
    # Generate test messages
    participants = ["Ana", "Bruno"]
    messages = generate_chat(participants)
    print(f"✅ Generated {len(messages)} messages")
    with open("test_messages.json", "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    print("💾 Saved messages to test_messages.json")

    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)

    payload = {
        "messages": messages,
        "participants": participants,
        "outputDir": output_dir,
        "img_size": [1920, 1080]
    }

    print(f"📸 Sending {len(messages)} messages to Node.js screenshot API...")
    try:
        response = requests.post(
            "http://localhost:3001/api/generate-screenshots",
            json=payload,
            timeout=120
        )
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                image_paths = result["imagePaths"]
                print(f"✅ Successfully generated {len(image_paths)} screenshots:")
                for path in image_paths:
                    abs_path = os.path.abspath(path)
                    if os.path.exists(abs_path):
                        size = os.path.getsize(abs_path)
                        print(f"   📸 {abs_path} ({size} bytes)")
                    else:
                        print(f"   ❌ {abs_path} (file not found)")
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

if __name__ == "__main__":
    success = test_node_service()
    if success:
        print("\n🎉 Node.js service test completed successfully!")
    else:
        print("\n💥 Node.js service test failed!")
        sys.exit(1) 