#!/usr/bin/env python3
"""
Storage Client for Local Storage Service
Handles file uploads to the Rust-based local storage service
"""

import os
import requests
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class LocalStorageClient:
    """Client for the local storage service"""
    
    def __init__(self, base_url: str = None):
        """Initialize storage client"""
        self.base_url = base_url or os.getenv('LOCAL_STORAGE_URL', 'http://192.168.1.218:30880')
        self.bucket = os.getenv('VOICE_STORAGE_BUCKET', 'voice-cloning')
        
    def upload_file(self, file_path: str, key: str = None, bucket: str = None) -> Optional[str]:
        """Upload a file to local storage service"""
        try:
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                return None
            
            # Generate key if not provided
            if not key:
                key = os.path.basename(file_path)
            
            # Use provided bucket or default
            target_bucket = bucket or self.bucket
            
            # Prepare the upload
            with open(file_path, 'rb') as f:
                files = {'file': f}
                data = {
                    'bucket': target_bucket,
                    'key': key
                }
                
                # Upload to local storage service
                response = requests.post(
                    f"{self.base_url}/upload",
                    files=files,
                    data=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"File uploaded successfully: {key} to bucket {target_bucket}")
                    return f"{target_bucket}/{key}"
                else:
                    logger.error(f"Upload failed: {response.status_code} - {response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error uploading file {file_path}: {e}")
            return None
    
    def download_file(self, key: str, bucket: str = None, output_path: str = None) -> Optional[str]:
        """Download a file from local storage service"""
        try:
            target_bucket = bucket or self.bucket
            
            # Download from local storage service
            response = requests.get(
                f"{self.base_url}/download/{key}",
                params={'bucket': target_bucket},
                timeout=30
            )
            
            if response.status_code == 200:
                # Save to output path if provided
                if output_path:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    logger.info(f"File downloaded to: {output_path}")
                    return output_path
                else:
                    # Return content as bytes
                    return response.content
            else:
                logger.error(f"Download failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error downloading file {key}: {e}")
            return None
    
    def delete_file(self, key: str, bucket: str = None) -> bool:
        """Delete a file from local storage service"""
        try:
            target_bucket = bucket or self.bucket
            
            response = requests.delete(
                f"{self.base_url}/delete/{key}",
                params={'bucket': target_bucket},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"File deleted successfully: {key}")
                return True
            else:
                logger.error(f"Delete failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting file {key}: {e}")
            return False
    
    def get_file_info(self, key: str, bucket: str = None) -> Optional[Dict[str, Any]]:
        """Get file metadata from local storage service"""
        try:
            target_bucket = bucket or self.bucket
            
            response = requests.get(
                f"{self.base_url}/info/{key}",
                params={'bucket': target_bucket},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Get info failed: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting file info for {key}: {e}")
            return None
    
    def health_check(self) -> bool:
        """Check if local storage service is healthy"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False

def test_storage_client():
    """Test the storage client functionality"""
    print("=== Testing Local Storage Client ===")
    
    client = LocalStorageClient()
    
    # Test health check
    if client.health_check():
        print("✅ Local storage service is healthy")
    else:
        print("❌ Local storage service is not available")
        return False
    
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
    
    return True

if __name__ == "__main__":
    test_storage_client() 