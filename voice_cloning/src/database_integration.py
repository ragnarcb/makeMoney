#!/usr/bin/env python3
"""
Database Integration for Voice Cloning Service
Handles the integration with PostgreSQL database for voice processing workflow
"""

import psycopg2
import psycopg2.extras
import uuid
import json
import os
import time
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import storage client
try:
    from storage_client import LocalStorageClient
except ImportError:
    LocalStorageClient = None

# Database connection parameters from environment
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "192.168.1.218")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "30432"))
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres123")
DATABASE_NAME = os.getenv("DATABASE_NAME", "video_voice_integration")

class VoiceCloningDatabase:
    """Database manager for voice cloning service"""
    
    def __init__(self):
        self.connection_params = {
            'host': POSTGRES_HOST,
            'port': POSTGRES_PORT,
            'user': POSTGRES_USER,
            'password': POSTGRES_PASSWORD,
            'database': DATABASE_NAME
        }
    
    def get_connection(self):
        """Get a database connection"""
        return psycopg2.connect(**self.connection_params)
    
    def execute_query(self, query: str, params: tuple = None, fetch: bool = True):
        """Execute a query and return results"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
            else:
                conn.commit()
                result = cursor.rowcount
            
            cursor.close()
            return result
        finally:
            conn.close()
    
    def get_pending_voice_requests(self) -> List[Dict]:
        """Get all pending voice requests that need processing"""
        query = """
            SELECT v.*, vm.voice_file, vm.voice_id as mapping_voice_id
            FROM voices v
            LEFT JOIN voice_mappings vm ON v.voice_mapping_id = vm.id
            WHERE v.status = 'pending'
            ORDER BY v.created_at ASC
        """
        return self.execute_query(query)
    
    def create_voice_request(self, video_id: str, character_name: str, text_content: str, voice_mapping_id: str = None) -> str:
        """Create a new voice request and return the voice ID"""
        voice_id = str(uuid.uuid4())
        
        query = """
            INSERT INTO voices (id, video_id, voice_mapping_id, character_name, text_content, status)
            VALUES (%s, %s, %s, %s, %s, 'pending')
            RETURNING id
        """
        
        self.execute_query(
            query,
            (voice_id, video_id, voice_mapping_id, character_name, text_content),
            fetch=False
        )
        
        return voice_id
    
    def start_processing_voice(self, voice_id: str) -> bool:
        """Mark a voice request as processing"""
        query = """
            UPDATE voices 
            SET status = 'processing', processing_started_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s AND status = 'pending'
        """
        result = self.execute_query(query, (voice_id,), fetch=False)
        return result > 0
    
    def complete_voice_processing(self, voice_id: str, output_audio_path: str) -> bool:
        """Mark a voice request as completed with the output path"""
        query = """
            UPDATE voices 
            SET status = 'completed', 
                output_audio_path = %s, 
                processing_completed_at = CURRENT_TIMESTAMP, 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        result = self.execute_query(query, (output_audio_path, voice_id), fetch=False)
        return result > 0
    
    def complete_voice_processing_with_storage(self, voice_id: str, output_audio_path: str, is_local: bool, remote_path: str = None) -> bool:
        """Mark voice as completed with storage information"""
        query = """
            UPDATE voices 
            SET status = 'completed', 
                output_audio_path = %s, 
                is_local_storage = %s,
                remote_storage_path = %s,
                processing_completed_at = CURRENT_TIMESTAMP, 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        result = self.execute_query(query, (output_audio_path, is_local, remote_path, voice_id), fetch=False)
        return result > 0
    
    def fail_voice_processing(self, voice_id: str, error_message: str) -> bool:
        """Mark a voice request as failed with error message"""
        query = """
            UPDATE voices 
            SET status = 'failed', 
                error_message = %s, 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """
        result = self.execute_query(query, (error_message, voice_id), fetch=False)
        return result > 0
    
    def get_voice_request(self, voice_id: str) -> Optional[Dict]:
        """Get a specific voice request with mapping info"""
        query = """
            SELECT v.*, vm.voice_file, vm.voice_id as mapping_voice_id
            FROM voices v
            LEFT JOIN voice_mappings vm ON v.voice_mapping_id = vm.id
            WHERE v.id = %s
        """
        result = self.execute_query(query, (voice_id,))
        return result[0] if result else None
    
    def get_video_voices_status(self, video_id: str) -> Dict[str, Any]:
        """Get the status of all voices for a video"""
        query = """
            SELECT 
                COUNT(*) as total_voices,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_voices,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_voices,
                COUNT(CASE WHEN status IN ('pending', 'processing') THEN 1 END) as pending_voices
            FROM voices 
            WHERE video_id = %s
        """
        result = self.execute_query(query, (video_id,))
        return result[0] if result else {}
    
    def check_all_voices_completed(self, video_id: str) -> bool:
        """Check if all voices for a video are completed"""
        status = self.get_video_voices_status(video_id)
        return status.get('total_voices', 0) > 0 and status.get('completed_voices', 0) == status.get('total_voices', 0)
    
    def get_voice_mapping(self, voice_id: str) -> Optional[Dict]:
        """Get voice mapping by voice_id"""
        query = "SELECT * FROM voice_mappings WHERE voice_id = %s"
        result = self.execute_query(query, (voice_id,))
        return result[0] if result else None
    
    def get_default_voice_mapping(self) -> Optional[Dict]:
        """Get the default voice mapping"""
        query = "SELECT * FROM voice_mappings WHERE is_default = TRUE LIMIT 1"
        result = self.execute_query(query)
        return result[0] if result else None

class VoiceProcessingWorker:
    """Worker class that handles the voice processing workflow"""
    
    def __init__(self):
        self.db = VoiceCloningDatabase()
        self.output_dir = os.getenv("OUTPUT_DIR", "/tmp/voice_cloning_output")
        
        # Storage configuration
        self.use_local_storage = os.getenv("USE_LOCAL_STORAGE", "true").lower() == "true"
        self.storage_client = None
        
        # Initialize storage client if remote storage is enabled
        if not self.use_local_storage and LocalStorageClient:
            self.storage_client = LocalStorageClient()
            print(f"Remote storage enabled: {self.storage_client.base_url}")
        else:
            print(f"Local storage enabled: {self.output_dir}")
        
    def process_pending_voices(self):
        """Main method to process all pending voice requests"""
        print("Checking for pending voice requests...")
        
        pending_voices = self.db.get_pending_voice_requests()
        if not pending_voices:
            print("No pending voice requests found.")
            return
        
        print(f"Found {len(pending_voices)} pending voice requests")
        
        for voice_request in pending_voices:
            try:
                self.process_single_voice(voice_request)
            except Exception as e:
                print(f"Error processing voice {voice_request['id']}: {e}")
                self.db.fail_voice_processing(voice_request['id'], str(e))
    
    def process_single_voice(self, voice_request: Dict):
        """Process a single voice request"""
        voice_id = voice_request['id']
        video_id = voice_request['video_id']
        character_name = voice_request['character_name']
        text_content = voice_request['text_content']
        
        print(f"Processing voice request {voice_id} for character '{character_name}'")
        
        # Start processing
        if not self.db.start_processing_voice(voice_id):
            print(f"Failed to start processing voice {voice_id}")
            return
        
        try:
            # Get voice mapping
            voice_mapping = None
            if voice_request['voice_mapping_id']:
                voice_mapping = self.db.get_voice_mapping(voice_request['mapping_voice_id'])
            
            if not voice_mapping:
                voice_mapping = self.db.get_default_voice_mapping()
                print(f"Using default voice mapping for {character_name}")
            
            if not voice_mapping:
                raise Exception("No voice mapping available")
            
            # Generate output path
            output_filename = f"{voice_id}_{character_name}.wav"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # TODO: Here you would call your actual TTS processing
            # For now, we'll simulate the processing
            print(f"Would process text: '{text_content}'")
            print(f"Using voice file: {voice_mapping['voice_file']}")
            print(f"Output path: {output_path}")
            
            # Simulate processing time
            time.sleep(2)
            
            # Handle storage (local or remote)
            final_path = output_path
            remote_path = None
            is_local = True
            
            if not self.use_local_storage and self.storage_client:
                # Upload to remote storage
                print(f"Uploading {output_path} to remote storage...")
                remote_path = self.storage_client.upload_file(output_path, f"{voice_id}_{character_name}.wav")
                
                if remote_path:
                    final_path = remote_path
                    is_local = False
                    print(f"File uploaded to remote storage: {remote_path}")
                else:
                    print("Failed to upload to remote storage, keeping local file")
            
            # Mark as completed with storage info
            if self.db.complete_voice_processing_with_storage(voice_id, final_path, is_local, remote_path):
                print(f"Successfully completed voice processing for {voice_id}")
                
                # Check if all voices for this video are completed
                if self.db.check_all_voices_completed(video_id):
                    print(f"All voices completed for video {video_id}")
            else:
                raise Exception("Failed to update voice status to completed")
                
        except Exception as e:
            print(f"Error processing voice {voice_id}: {e}")
            self.db.fail_voice_processing(voice_id, str(e))
    
    def run_continuous_processing(self, interval_seconds: int = 30):
        """Run continuous processing with specified interval"""
        print(f"Starting continuous voice processing (interval: {interval_seconds}s)")
        
        while True:
            try:
                self.process_pending_voices()
                time.sleep(interval_seconds)
            except KeyboardInterrupt:
                print("Stopping voice processing...")
                break
            except Exception as e:
                print(f"Error in continuous processing: {e}")
                time.sleep(interval_seconds)

def test_database_connection():
    """Test database connection and basic functionality"""
    try:
        db = VoiceCloningDatabase()
        
        # Test connection
        conn = db.get_connection()
        conn.close()
        print("✓ Database connection successful")
        
        # Test voice mappings
        mappings = db.execute_query("SELECT COUNT(*) as count FROM voice_mappings")
        print(f"✓ Found {mappings[0]['count']} voice mappings")
        
        # Test pending voices
        pending = db.get_pending_voice_requests()
        print(f"✓ Found {len(pending)} pending voice requests")
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

if __name__ == "__main__":
    # Test mode
    if test_database_connection():
        print("Database integration test passed!")
    else:
        print("Database integration test failed!")
        exit(1) 