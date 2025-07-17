#!/usr/bin/env python3
import json
import requests
import sys
import os

# Add video_generator to path
sys.path.append('video_generator')
from whatsapp_gen.chat_generator import generate_chat

def test_node_service():
    print("🧪 Testing Node.js WhatsApp Screenshot Service)
    print(= *50   
    # Generate messages using existing Python code
    print("📝 Generating test messages...")
    participants = ["Ana", "Bruno"]
    messages = generate_chat(participants)
    print(f"✅ Generated {len(messages)} messages)   # Save messages to JSON for inspection
    with open("test_messages.json,w, encoding="utf-8as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    print(💾 Saved messages to test_messages.json) # Test screenshot generation
    output_dir =test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    payload = {
 messages": messages,
     participants": participants,
  outputDir": output_dir,
        img_size": [19201080  }
    
    print(f"📸 Testing screenshot generation for {len(messages)} messages...")
    
    try:
        response = requests.post(
            http://localhost:31i/generate-screenshots",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print(f"✅ Generated {len(result['imagePaths'])} screenshots)             print("📁 Screenshots saved to:)               for path in result['imagePaths']:
                    print(f"   - {path}")
                    if os.path.exists(path):
                        size = os.path.getsize(path)
                        print(f     (File exists, {size} bytes)")
                    else:
                        print("     (FILE NOT FOUND))            return True
            else:
                print(f"❌ API error: {result.get('error')})            return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_node_service()
    if success:
        print("\n🎉 Test completed successfully!")
    else:
        print("\n💥 Test failed!")
        sys.exit(1)
