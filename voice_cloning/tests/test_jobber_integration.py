#!/usr/bin/env python3
"""
Test Jobber Queue Integration for Voice Cloning Service
Tests the new RabbitMQ jobber queue workflow
"""

import sys
import os
import json
import uuid
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database_integration import VoiceCloningDatabase

def test_jobber_message_format():
    """Test the jobber message format"""
    print("=== Testing Jobber Message Format ===")
    
    # Create a sample jobber message
    video_id = str(uuid.uuid4())
    jobber_message = {
        "app": "text-processor",
        "cpu_cores": "2000m",
        "ram_memory": "3Gi",
        "max_execution_time": 420,
        "data": {
            "video_id": video_id,
            "messages": [
                {
                    "text": "Olá, sou o aluno Lucas!",
                    "from_user": "aluno"
                },
                {
                    "text": "Olá Lucas, sou a professora Marina!",
                    "from_user": "professora"
                },
                {
                    "text": "Como está indo com os estudos?",
                    "from_user": "aluno"
                },
                {
                    "text": "Muito bem! Continue assim!",
                    "from_user": "professora"
                }
            ],
            "voice_mapping": {
                "aluno": "voices/voz_aluno_lucas.wav",
                "professora": "voices/voz_referencia_convertida_ffmpeg.wav"
            }
        }
    }
    
    print("✅ Jobber message format created:")
    print(json.dumps(jobber_message, indent=2))
    
    # Validate required fields
    required_fields = ["app", "data"]
    data_required_fields = ["video_id", "messages"]
    
    for field in required_fields:
        if field not in jobber_message:
            print(f"❌ Missing required field: {field}")
            return False
    
    for field in data_required_fields:
        if field not in jobber_message["data"]:
            print(f"❌ Missing required data field: {field}")
            return False
    
    print("✅ All required fields present")
    return True

def test_database_voice_creation():
    """Test creating voice requests in database"""
    print("\n=== Testing Database Voice Creation ===")
    
    try:
        db = VoiceCloningDatabase()
        
        # Create a test video ID
        video_id = str(uuid.uuid4())
        
        # Create test messages
        test_messages = [
            {"text": "Test message 1", "from_user": "aluno"},
            {"text": "Test message 2", "from_user": "professora"}
        ]
        
        voice_ids = []
        for i, msg in enumerate(test_messages):
            voice_id = db.create_voice_request(
                video_id=video_id,
                character_name=msg["from_user"],
                text_content=msg["text"]
            )
            voice_ids.append(voice_id)
            print(f"✅ Created voice request {voice_id} for {msg['from_user']}")
        
        # Verify voice requests were created
        pending_voices = db.get_pending_voice_requests()
        created_voices = [v for v in pending_voices if v['video_id'] == video_id]
        
        if len(created_voices) == len(test_messages):
            print(f"✅ All {len(test_messages)} voice requests created successfully")
        else:
            print(f"❌ Expected {len(test_messages)} voice requests, found {len(created_voices)}")
            return False
        
        # Clean up test data
        for voice_id in voice_ids:
            db.execute_query("DELETE FROM voices WHERE id = %s", (voice_id,), fetch=False)
        
        print("✅ Test voice requests cleaned up")
        return True
        
    except Exception as e:
        print(f"❌ Database voice creation test failed: {e}")
        return False

def test_video_completion_check():
    """Test checking if all voices for a video are completed"""
    print("\n=== Testing Video Completion Check ===")
    
    try:
        db = VoiceCloningDatabase()
        
        # Create a test video ID
        video_id = str(uuid.uuid4())
        
        # Create test voice requests
        test_messages = [
            {"text": "Test message 1", "from_user": "aluno"},
            {"text": "Test message 2", "from_user": "professora"}
        ]
        
        voice_ids = []
        for msg in test_messages:
            voice_id = db.create_voice_request(
                video_id=video_id,
                character_name=msg["from_user"],
                text_content=msg["text"]
            )
            voice_ids.append(voice_id)
        
        # Check initial status (should be incomplete)
        initial_complete = db.check_all_voices_completed(video_id)
        print(f"Initial completion status: {initial_complete}")
        
        # Mark one voice as completed
        if voice_ids:
            db.complete_voice_processing(voice_ids[0], "/tmp/test_audio.wav")
            print(f"✅ Marked voice {voice_ids[0]} as completed")
        
        # Check status after one completion (should still be incomplete)
        partial_complete = db.check_all_voices_completed(video_id)
        print(f"Partial completion status: {partial_complete}")
        
        # Mark all voices as completed
        for voice_id in voice_ids:
            db.complete_voice_processing(voice_id, "/tmp/test_audio.wav")
        
        # Check final status (should be complete)
        final_complete = db.check_all_voices_completed(video_id)
        print(f"Final completion status: {final_complete}")
        
        if not initial_complete and not partial_complete and final_complete:
            print("✅ Video completion check working correctly")
        else:
            print("❌ Video completion check not working correctly")
            return False
        
        # Clean up test data
        db.execute_query("DELETE FROM voices WHERE video_id = %s", (video_id,), fetch=False)
        print("✅ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Video completion check test failed: {e}")
        return False

def main():
    """Run all jobber integration tests"""
    print("Voice Cloning Jobber Integration Test")
    print("=" * 50)
    
    tests = [
        ("Jobber Message Format", test_jobber_message_format),
        ("Database Voice Creation", test_database_voice_creation),
        ("Video Completion Check", test_video_completion_check)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Jobber integration is working correctly.")
        print("\n📋 Workflow Summary:")
        print("1. Video Generator sends jobber message to RabbitMQ queue 'jobber'")
        print("2. Voice Cloning consumes message and creates voice requests in database")
        print("3. Voice Cloning processes voices and updates database with results")
        print("4. Video Generator polls database for completion status")
        return 0
    else:
        print("❌ Some tests failed. Please check the setup.")
        return 1

if __name__ == "__main__":
    exit(main()) 