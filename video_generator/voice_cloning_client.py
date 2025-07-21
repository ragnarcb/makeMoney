#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voice Cloning Service Client for Video Generator
Communicates with voice_cloning microservice via jobber queues and database
"""

import os
import json
import time
import uuid
import requests
import pika
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class VoiceCloningServiceClient:
    """Client for communicating with voice_cloning microservice"""
    
    def __init__(self, video_id: str, jobber_url: str = None, database_config: Dict = None):
        """Initialize the voice cloning client"""
        self.video_id = video_id
        self.jobber_url = jobber_url or os.getenv('JOBBER_URL', 'http://localhost:8080')
        
        # Database configuration
        self.db_config = database_config or {
            'host': os.getenv('POSTGRES_HOST', '192.168.1.218'),
            'port': int(os.getenv('POSTGRES_PORT', '30432')),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'postgres123'),
            'database': os.getenv('DATABASE_NAME', 'video_voice_integration')
        }
        
        # RabbitMQ configuration for jobber
        self.rabbitmq_config = {
            'host': os.getenv('RABBITMQ_HOST', 'localhost'),
            'port': int(os.getenv('RABBITMQ_PORT', '5672')),
            'user': os.getenv('RABBITMQ_USER', 'guest'),
            'password': os.getenv('RABBITMQ_PASSWORD', 'guest'),
            'vhost': os.getenv('RABBITMQ_VHOST', '/')
        }
    
    def _get_database_connection(self):
        """Get database connection"""
        try:
            import psycopg2
            import psycopg2.extras
            
            conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                database=self.db_config['database']
            )
            return conn
        except ImportError:
            logger.error("psycopg2 not installed. Install with: pip install psycopg2-binary")
            return None
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return None
    
    def _send_voice_request_to_jobber(self, messages: List[Dict], participants: List[str], 
                                     voice_mapping: Dict[str, str] = None) -> str:
        """Send voice generation request to jobber queue"""
        try:
            # Create jobber request
            jobber_request = {
                'id': str(uuid.uuid4()),
                'type': 'voice_cloning',
                'video_id': self.video_id,
                'messages': messages,
                'participants': participants,
                'voice_mapping': voice_mapping or {},
                'use_voice_cloning': True,
                'output_dir': f'/tmp/voice_cloning_output/{self.video_id}',
                'timestamp': datetime.now().isoformat()
            }
            
            # Send to jobber via RabbitMQ
            credentials = pika.PlainCredentials(
                self.rabbitmq_config['user'], 
                self.rabbitmq_config['password']
            )
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq_config['host'],
                port=self.rabbitmq_config['port'],
                virtual_host=self.rabbitmq_config['vhost'],
                credentials=credentials
            )
            
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            # Declare jobber queue
            channel.queue_declare(queue='jobber-requests', durable=True)
            
            # Publish message
            channel.basic_publish(
                exchange='',
                routing_key='jobber-requests',
                body=json.dumps(jobber_request),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # make message persistent
                )
            )
            
            connection.close()
            
            logger.info(f"Sent voice request to jobber: {jobber_request['id']}")
            return jobber_request['id']
            
        except Exception as e:
            logger.error(f"Failed to send voice request to jobber: {e}")
            raise
    
    def _create_voice_requests_in_database(self, messages: List[Dict], participants: List[str],
                                          voice_mapping: Dict[str, str] = None) -> List[str]:
        """Create voice requests in database for tracking"""
        conn = self._get_database_connection()
        if not conn:
            raise Exception("Cannot connect to database")
        
        try:
            cursor = conn.cursor()
            voice_ids = []
            
            for i, message in enumerate(messages):
                voice_id = str(uuid.uuid4())
                
                # Get voice mapping for this participant
                voice_mapping_id = None
                if voice_mapping and message.get('from') in voice_mapping:
                    # You might need to create or get voice mapping ID from database
                    # For now, we'll use a placeholder
                    voice_mapping_id = f"mapping_{message.get('from')}"
                
                # Insert voice request
                cursor.execute("""
                    INSERT INTO voices (id, video_id, voice_mapping_id, character_name, text_content, status)
                    VALUES (%s, %s, %s, %s, %s, 'pending')
                """, (
                    voice_id,
                    self.video_id,
                    voice_mapping_id,
                    message.get('from'),
                    message.get('text'),
                ))
                
                voice_ids.append(voice_id)
            
            conn.commit()
            logger.info(f"Created {len(voice_ids)} voice requests in database")
            return voice_ids
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create voice requests in database: {e}")
            raise
        finally:
            conn.close()
    
    def _wait_for_voices_completion(self, max_wait_time: int = 300) -> bool:
        """Wait for all voices to be completed in database"""
        start_time = time.time()
        
        while time.time() - start_time < max_wait_time:
            conn = self._get_database_connection()
            if not conn:
                logger.error("Cannot connect to database")
                return False
            
            try:
                cursor = conn.cursor()
                
                # Check status of all voices for this video
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_voices,
                        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_voices,
                        COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_voices
                    FROM voices 
                    WHERE video_id = %s
                """, (self.video_id,))
                
                result = cursor.fetchone()
                total_voices = result[0]
                completed_voices = result[1]
                failed_voices = result[2]
                
                if failed_voices > 0:
                    logger.error(f"Some voice requests failed: {failed_voices}/{total_voices}")
                    return False
                
                if completed_voices == total_voices and total_voices > 0:
                    logger.info(f"All voice requests completed: {completed_voices}/{total_voices}")
                    return True
                
                logger.info(f"Waiting for voices: {completed_voices}/{total_voices} completed")
                time.sleep(5)  # Wait 5 seconds before checking again
                
            except Exception as e:
                logger.error(f"Error checking voice status: {e}")
                return False
            finally:
                conn.close()
        
        logger.error(f"Timeout waiting for voice completion after {max_wait_time} seconds")
        return False
    
    def _get_completed_audio_paths(self) -> List[str]:
        """Get paths of completed audio files from database"""
        conn = self._get_database_connection()
        if not conn:
            raise Exception("Cannot connect to database")
        
        try:
            cursor = conn.cursor()
            
            # Get completed voice requests with output paths
            cursor.execute("""
                SELECT output_audio_path, character_name
                FROM voices 
                WHERE video_id = %s AND status = 'completed'
                ORDER BY created_at ASC
            """, (self.video_id,))
            
            results = cursor.fetchall()
            audio_paths = []
            
            for output_path, character_name in results:
                if output_path:
                    audio_paths.append(output_path)
                    logger.debug(f"Found audio for {character_name}: {output_path}")
            
            logger.info(f"Retrieved {len(audio_paths)} completed audio paths")
            return audio_paths
            
        except Exception as e:
            logger.error(f"Failed to get audio paths from database: {e}")
            raise
        finally:
            conn.close()
    
    def generate_tts(self, messages: List[Dict], participants: List[str], 
                    output_dir: str, voice_mapping: Dict[str, str] = None,
                    use_voice_cloning: bool = True, lang: str = 'pt-br') -> List[str]:
        """Generate TTS audio using voice_cloning microservice"""
        try:
            logger.info(f"Starting TTS generation for video {self.video_id}")
            
            # Step 1: Create voice requests in database
            logger.info("Creating voice requests in database...")
            voice_ids = self._create_voice_requests_in_database(messages, participants, voice_mapping)
            
            # Step 2: Send request to jobber queue
            logger.info("Sending voice request to jobber queue...")
            jobber_request_id = self._send_voice_request_to_jobber(messages, participants, voice_mapping)
            
            # Step 3: Wait for completion
            logger.info("Waiting for voice generation to complete...")
            if not self._wait_for_voices_completion():
                raise Exception("Voice generation failed or timed out")
            
            # Step 4: Get completed audio paths
            logger.info("Retrieving completed audio paths...")
            audio_paths = self._get_completed_audio_paths()
            
            if not audio_paths:
                raise Exception("No audio files were generated")
            
            logger.success(f"TTS generation completed: {len(audio_paths)} audio files")
            return audio_paths
            
        except Exception as e:
            logger.error(f"TTS generation failed: {e}")
            raise
    
    def health_check(self) -> bool:
        """Check if voice cloning service is healthy"""
        try:
            # Check database connection
            conn = self._get_database_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()
            conn.close()
            
            # Check RabbitMQ connection
            credentials = pika.PlainCredentials(
                self.rabbitmq_config['user'], 
                self.rabbitmq_config['password']
            )
            parameters = pika.ConnectionParameters(
                host=self.rabbitmq_config['host'],
                port=self.rabbitmq_config['port'],
                virtual_host=self.rabbitmq_config['vhost'],
                credentials=credentials
            )
            
            connection = pika.BlockingConnection(parameters)
            connection.close()
            
            logger.info("Voice cloning service health check passed")
            return True
            
        except Exception as e:
            logger.error(f"Voice cloning service health check failed: {e}")
            return False 