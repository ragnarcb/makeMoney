#!/usr/bin/env python3
"""
Test Database Integration for Voice Cloning Service
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database_integration import VoiceCloningDatabase, VoiceProcessingWorker, test_database_connection

def test_basic_functionality():
    """Test basic database functionality"""
    print("=== Testing Database Integration ===")
    
    # Test connection
    if not test_database_connection():
        print("❌ Database connection failed")
        return False
    
    print("✅ Database connection successful")
    
    # Test database operations
    db = VoiceCloningDatabase()
    
    # Test voice mappings
    mappings = db.execute_query("SELECT COUNT(*) as count FROM voice_mappings")
    print(f"✅ Found {mappings[0]['count']} voice mappings")
    
    # Test pending voices
    pending = db.get_pending_voice_requests()
    print(f"✅ Found {len(pending)} pending voice requests")
    
    # Test voice processing worker
    worker = VoiceProcessingWorker()
    print("✅ Voice processing worker initialized")
    
    return True

def test_voice_processing_simulation():
    """Test voice processing simulation"""
    print("\n=== Testing Voice Processing Simulation ===")
    
    try:
        worker = VoiceProcessingWorker()
        
        # This will process any pending voices in the database
        worker.process_pending_voices()
        
        print("✅ Voice processing simulation completed")
        return True
        
    except Exception as e:
        print(f"❌ Voice processing simulation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Voice Cloning Database Integration Test")
    print("=" * 50)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Voice Processing Simulation", test_voice_processing_simulation)
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
        print("🎉 All tests passed! Database integration is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the database setup.")
        return 1

if __name__ == "__main__":
    exit(main()) 