#!/usr/bin/env python3
"""
Test script to verify the Node.js WhatsApp image generation service
"""

import requests
import json
import time
import os

def test_node_service():
    """Test the Node.js service with sample messages"""
    
    # Sample messages in the format expected by the React app
    sample_messages = [
        {
            "id": "1",
            "texto": "Oi! Como você está? 😊",
            "usuario": {
                "id": "user1",
                "nome": "Ana"
            },
            "timestamp": "2024-01-15T14:30:00Z",
            "isMine": False
        },
        {
            "id": "2", 
            "texto": "Oi Ana! Estou bem, e você? 😄",
            "usuario": {
                "id": "user2",
                "nome": "Bruno"
            },
            "timestamp": "2024-01-15T14:31:00Z",
            "isMine": True
        },
        {
            "id": "3",
            "texto": "Ótimo! Quer conversar sobre tecnologia? 💻",
            "usuario": {
                "id": "user1",
                "nome": "Ana"
            },
            "timestamp": "2024-01-15T14:32:00Z",
            "isMine": False
        }
    ]
    
    participants = ["Ana", "Bruno"]
    output_dir = "test_output"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Test payload
    payload = {
        "messages": sample_messages,
        "participants": participants,
        "outputDir": output_dir,
        "img_size": [1920, 1080]
    }
    
    print("🧪 Testing Node.js WhatsApp Image Generation Service")
    print(f"📤 Sending {len(sample_messages)} messages to service...")
    
    try:
        # Test health endpoint first
        health_response = requests.get("http://localhost:3001/api/health", timeout=10)
        if health_response.status_code == 200:
            print("✅ Health check passed")
        else:
            print("❌ Health check failed")
            return False
            
        # Send screenshot generation request
        response = requests.post(
            "http://localhost:3001/api/generate-screenshots",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                image_paths = result["imagePaths"]
                print(f"✅ Successfully generated {len(image_paths)} screenshots:")
                for path in image_paths:
                    if os.path.exists(path):
                        print(f"   📸 {path}")
                    else:
                        print(f"   ❌ {path} (file not found)")
                return True
            else:
                print(f"❌ API returned error: {result.get('error', 'Unknown error')}")
                return False
        else:
            print(f"❌ HTTP {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Node.js service on http://localhost:3001")
        print("   Make sure the service is running: docker-compose up")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_node_service()
    if success:
        print("\n🎉 Node.js service test completed successfully!")
    else:
        print("\n💥 Node.js service test failed!")
        exit(1) 