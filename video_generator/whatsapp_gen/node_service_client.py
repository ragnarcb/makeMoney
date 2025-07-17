import os
import json
import requests
from typing import List, Dict, Optional, Tuple
import sys

class NodeServiceClient:
    """Client for the Node.js WhatsApp screenshot service.
    Handles communication with the service and optional S3-like file retrieval.
    """
     
    def __init__(self, api_url: str = "http://localhost:3000", use_s3: bool = False, s3_config: Optional[Dict] = None):
        """Initialize the Node.js service client.
        
        Args:
            api_url: URL of the Node.js service
            use_s3: Whether to use S3 storage for files
            s3_config: S3 configuration (bucket, region, etc.)
        """
        self.api_url = api_url
        self.use_s3 = use_s3
        self.s3_config = s3_config or {}
        
    def get_screenshot_with_coordinates(self, messages: List[Dict], participants: List[str], 
                                      output_dir: str, img_size: Tuple[int, int] = (1920, 800)) -> Tuple[str, List[Dict]]:
        """Generate a single WhatsApp screenshot with message coordinates.
        
        Args:
            messages: List of message objects
            participants: List of participant names
            output_dir: Directory to save the screenshot
            img_size: Image size as (height, width)
            
        Returns:
            Tuple of (screenshot_path, message_coordinates)
        """
 
        payload = {
            "messages": messages,
            "participants": participants,
            "outputDir": output_dir,
            "img_size": img_size
        }
        
        try:
            print(f"Requesting screenshot from Node.js service: {len(messages)} messages")
            response = requests.post(f"{self.api_url}/api/generate-screenshots", 
                                   json=payload, timeout=120)
            response.raise_for_status()
            
            result = response.json()
            if not result.get("success"):
                raise Exception(f"Node.js service error: {result.get('error', 'Unknown error')}")
            
            # Get screenshot path
            image_paths = result.get("imagePaths", [])
            if not image_paths:
                raise Exception("No screenshot path returned from Node.js service")
            
            screenshot_path = image_paths[0]
            
            # Get message coordinates
            message_coordinates = result.get("messageCoordinates", [])
            if not message_coordinates:
                print("Warning: No message coordinates returned from Node.js service")
            
            print(f"Screenshot generated: {screenshot_path}")
            print(f"Message coordinates: {len(message_coordinates)} messages")
            
            return screenshot_path, message_coordinates
            
        except requests.exceptions.RequestException as e:
            print(f"Failed to communicate with Node.js service: {e}")
            raise Exception(f"Node.js service communication failed: {e}")
        except Exception as e:
            print(f"Screenshot generation failed: {e}")
            raise
    
    def get_file_from_s3(self, file_key: str, local_path: str) -> str:
        """Download a file from S3-like storage.
        
        Args:
            file_key: S3 file key
            local_path: Local path to save the file
            
        Returns:
            Local path of the downloaded file
        """
        if not self.use_s3:
            raise Exception("S3 storage is not enabled")
        
        # This is a placeholder - implement your S3 client here
        print(f"Would download {file_key} to {local_path}")
        
        # For now, return the local path as if file exists
        return local_path
    
    def upload_file_to_s3(self, local_path: str, file_key: str) -> str:
        """Upload a file to S3-like storage.
        
        Args:
            local_path: Local path of the file
            file_key: S3 file key
            
        Returns:
            S3 URL of the uploaded file
        """
        if not self.use_s3:
            raise Exception("S3 storage is not enabled")
        
        # This is a placeholder - implement your S3 client here
        print(f"Would upload {local_path} to {file_key}")
        
        # Return a mock S3 URL
        return f"https://your-bucket.s3.amazonaws.com/{file_key}"
    
    def health_check(self) -> bool:
        """Check if the Node.js service is healthy.
        
        Returns:
            True if service is healthy, False otherwise
        """
        try:
            response = requests.get(f"{self.api_url}/api/health", timeout=10)
            return response.status_code == 200
        except:
            return False 