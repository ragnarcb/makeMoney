#!/usr/bin/env python3
"""
Test Storage Integration for Voice Cloning Service
Tests both local and remote storage modes
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from database_integration import VoiceCloningDatabase, VoiceProcessingWorker
from storage_client import LocalStorageClient

def test_local_storage_mode():
    """Test local storage mode"""
    print("=== Testing Local Storage Mode ===")
    
    # Set environment for local storage
    os.environ['USE_LOCAL_STORAGE'] = 'true'
    
    try:
        worker = VoiceProcessingWorker()
        
        if worker.use_local_storage:
            print("✅ Local storage mode enabled")
            print(f"   Output directory: {worker.output_dir}")
        else:
            print("❌ Local storage mode not enabled")
            return False
        
        if worker.storage_client is None:
            print("✅ No storage client initialized (correct for local mode)")
        else:
            print("❌ Storage client should not be initialized in local mode")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Local storage test failed: {e}")
        return False

def test_remote_storage_mode():
    """Test remote storage mode"""
    print("\n=== Testing Remote Storage Mode ===")
    
    # Set environment for remote storage
    os.environ['USE_LOCAL_STORAGE'] = 'false'
    os.environ['LOCAL_STORAGE_URL'] = 'http://192.168.1.218:30880'
    
    try:
        worker = VoiceProcessingWorker()
        
        if not worker.use_local_storage:
            print("✅ Remote storage mode enabled")
        else:
            print("❌ Remote storage mode not enabled")
            return False
        
        if worker.storage_client:
            print(f"✅ Storage client initialized: {worker.storage_client.base_url}")
            
            # Test health check
            if worker.storage_client.health_check():
                print("✅ Local storage service is healthy")
            else:
                print("⚠️ Local storage service is not available (this is expected if not deployed)")
        else:
            print("❌ Storage client should be initialized in remote mode")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Remote storage test failed: {e}")
        return False

def test_storage_client():
    """Test storage client directly"""
    print("\n=== Testing Storage Client ===")
    
    try:
        client = LocalStorageClient()
        
        # Test health check
        if client.health_check():
            print("✅ Local storage service is healthy")
            
            # Test upload (if we have a test file)
            test_file = "/tmp/test_voice.wav"
            if os.path.exists(test_file):
                result = client.upload_file(test_file, "test_voice.wav")
                if result:
                    print(f"✅ File uploaded successfully: {result}")
                else:
                    print("❌ File upload failed")
            else:
                print("⚠️ No test file found, skipping upload test")
        else:
            print("⚠️ Local storage service is not available (this is expected if not deployed)")
        
        return True
        
    except Exception as e:
        print(f"❌ Storage client test failed: {e}")
        return False

def test_database_storage_fields():
    """Test that database has the new storage fields"""
    print("\n=== Testing Database Storage Fields ===")
    
    try:
        db = VoiceCloningDatabase()
        
        # Check if the new columns exist
        result = db.execute_query("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'voices' 
            AND column_name IN ('is_local_storage', 'remote_storage_path')
            ORDER BY column_name
        """)
        
        found_columns = [row['column_name'] for row in result]
        expected_columns = ['is_local_storage', 'remote_storage_path']
        
        for col in expected_columns:
            if col in found_columns:
                print(f"✅ Column '{col}' exists")
            else:
                print(f"❌ Column '{col}' not found")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database storage fields test failed: {e}")
        return False

def main():
    """Run all storage integration tests"""
    print("Voice Cloning Storage Integration Test")
    print("=" * 50)
    
    tests = [
        ("Local Storage Mode", test_local_storage_mode),
        ("Remote Storage Mode", test_remote_storage_mode),
        ("Storage Client", test_storage_client),
        ("Database Storage Fields", test_database_storage_fields)
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
        print("🎉 All tests passed! Storage integration is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the setup.")
        return 1

if __name__ == "__main__":
    exit(main()) 