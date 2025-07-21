#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kubernetes Microservice for Video Generator Queue Consumer
Supports RabbitMQ and Mock mode for development
"""

import os
import json
import time
import signal
import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import pika

# Add current directory to path for imports
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

from main import main as video_generator_main
import argparse

# Configure logging
log_file = os.getenv('LOG_FILE', '/var/log/video-generator-service.log')

# Create log handlers
handlers = [logging.StreamHandler(sys.stdout)]

# Add file handler if we can write to the log file
try:
    # Ensure log directory exists
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    handlers.append(logging.FileHandler(log_file))
    print(f"Logging to file: {log_file}")
except (PermissionError, OSError) as e:
    print(f"Could not create log file {log_file}: {e}")
    print("Logging to console only")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s:%(funcName)s:%(lineno)d - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)

class RabbitMQConsumer:
    """RabbitMQ consumer for video generation requests"""
    
    def __init__(self, host: str, port: int, user: str, password: str, vhost: str, queue_name: str):
        """Initialize RabbitMQ consumer"""
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.vhost = vhost
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        
    def connect(self):
        """Connect to RabbitMQ"""
        try:
            # Create connection parameters
            credentials = pika.PlainCredentials(self.user, self.password)
            parameters = pika.ConnectionParameters(
                host=self.host,
                port=self.port,
                virtual_host=self.vhost,
                credentials=credentials,
                heartbeat=600,
                blocked_connection_timeout=300
            )
            
            # Establish connection
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            
            # Declare queue
            self.channel.queue_declare(queue=self.queue_name, durable=True)
            
            logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
            return True
            
        except ImportError:
            logger.error("pika library not installed. Install with: pip install pika")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
    
    def consume_message(self) -> Optional[Dict[str, Any]]:
        """Consume a single message from the queue"""
        try:
            if not self.channel:
                logger.error("Not connected to RabbitMQ")
                return None
            
            # Get a single message
            method_frame, header_frame, body = self.channel.basic_get(queue=self.queue_name, auto_ack=False)
            
            if method_frame:
                try:
                    # Parse message
                    message = json.loads(body.decode('utf-8'))
                    logger.info(f"Received message: {message.get('id', 'unknown')}")
                    
                    # Acknowledge message
                    self.channel.basic_ack(delivery_tag=method_frame.delivery_tag)
                    
                    return message
                    
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse message: {e}")
                    # Reject malformed message
                    self.channel.basic_nack(delivery_tag=method_frame.delivery_tag, requeue=False)
                    return None
            else:
                logger.info("No messages in queue")
                return None
                
        except Exception as e:
            logger.error(f"Error consuming message: {e}")
            return None
    
    def delete_queue(self):
        """Delete the queue after processing"""
        try:
            if self.channel:
                self.channel.queue_delete(queue=self.queue_name)
                logger.info(f"Deleted queue: {self.queue_name}")
        except Exception as e:
            logger.error(f"Failed to delete queue: {e}")
    
    def close(self):
        """Close RabbitMQ connection"""
        try:
            if self.connection and not self.connection.is_closed:
                self.connection.close()
                logger.info("RabbitMQ connection closed")
        except Exception as e:
            logger.error(f"Error closing RabbitMQ connection: {e}")

class MockMessageConsumer:
    """Mock message consumer for development testing"""
    
    def __init__(self, queue_name: str):
        """Initialize mock consumer"""
        self.queue_name = queue_name
        
    def connect(self):
        """Mock connection - always succeeds"""
        logger.info(f"Mock mode: Connected to queue {self.queue_name}")
        return True
    
    def consume_message(self) -> Optional[Dict[str, Any]]:
        """Return a mock message for testing"""
        logger.info("Mock mode: Returning test message")
        
        return {
            'id': 'mock-video-request-1',
            'type': 'video_generation',
            'prompt': 'Uma conversa engraçada entre Ana e Bruno sobre tecnologia',
            'participants': ['Ana', 'Bruno'],
            'node_url': 'http://localhost:3001',
            'voice_cloning_dir': '/app/voice_cloning',
            'messages_per_group': 4,
            'start_buffer': 1.0,
            'end_buffer': 3.0,
            'voice_mapping': {
                'Ana': '/app/voice_cloning/voices/voz_aluno_lucas.wav',
                'Bruno': '/app/voice_cloning/voices/voz_referencia_convertida_ffmpeg.wav'
            },
            'use_voice_cloning': True
        }
    
    def delete_queue(self):
        """Mock queue deletion"""
        logger.info(f"Mock mode: Deleted queue {self.queue_name}")
    
    def close(self):
        """Mock connection close"""
        logger.info("Mock mode: Connection closed")

class VideoGeneratorQueueConsumer:
    """Queue consumer for video generation requests - One message per queue"""
    
    def __init__(self):
        """Initialize the queue consumer"""
        # Jobber will inject the temporary queue name via CONSUMER_QUEUE_NAME
        self.queue_name = os.getenv('CONSUMER_QUEUE_NAME', 'video-generator-queue')

        if os.getenv('USE_MOCK_MODE', 'false').lower() == 'true':
            self.queue_name = 'video-generator-queue'  # Use mock queue for testing

        self.running = False
        self.message_consumer = None
        
        # Initialize message consumer (RabbitMQ or Mock)
        self._initialize_message_consumer()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def _initialize_message_consumer(self):
        """Initialize message consumer (RabbitMQ or Mock)"""
        try:
            if os.getenv('USE_MOCK_MODE', 'false').lower() == 'true':
                logger.info("Initializing Mock Message Consumer")
                self.message_consumer = MockMessageConsumer(self.queue_name)
            else:
                logger.info("Initializing RabbitMQ Message Consumer")
                
                # Get RabbitMQ configuration from environment
                rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
                rabbitmq_port = int(os.getenv('RABBITMQ_PORT', '5672'))
                rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
                rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'guest')
                rabbitmq_vhost = os.getenv('RABBITMQ_VHOST', '/')
                
                self.message_consumer = RabbitMQConsumer(
                    host=rabbitmq_host,
                    port=rabbitmq_port,
                    user=rabbitmq_user,
                    password=rabbitmq_password,
                    vhost=rabbitmq_vhost,
                    queue_name=self.queue_name
                )
                
        except Exception as e:
            logger.error(f"Failed to initialize message consumer: {e}")
            raise
    
    def _process_single_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single video generation message"""
        try:
            logger.info(f"Processing video generation request: {message.get('id', 'unknown')}")
            
            # Extract parameters from message
            video_id = message.get('video_id', str(uuid.uuid4()))
            prompt = message.get('prompt')
            participants = message.get('participants', ['Ana', 'Bruno'])
            node_url = message.get('node_url', 'http://localhost:3001')
            voice_cloning_dir = message.get('voice_cloning_dir', '/app/voice_cloning')
            messages_per_group = message.get('messages_per_group', 4)
            start_buffer = message.get('start_buffer', 1.0)
            end_buffer = message.get('end_buffer', 3.0)
            voice_mapping = message.get('voice_mapping', {})
            use_voice_cloning = message.get('use_voice_cloning', True)
            
            # Build command line arguments for video generator
            args = []
            
            args.extend(['--video-id', video_id])
            
            if prompt:
                args.extend(['--prompt', prompt])
            
            args.extend(['--participants'] + participants)
            args.extend(['--node-url', node_url])
            args.extend(['--voice-cloning-dir', voice_cloning_dir])
            args.extend(['--messages-per-group', str(messages_per_group)])
            args.extend(['--start-buffer', str(start_buffer)])
            args.extend(['--end-buffer', str(end_buffer)])
            
            if voice_mapping:
                for participant, voice_file in voice_mapping.items():
                    args.extend(['--voice-mapping', f'{participant}:{voice_file}'])
            
            if not use_voice_cloning:
                args.append('--no-voice-cloning')
            
            # Set up sys.argv for the video generator main function
            sys.argv = ['video_generator'] + args
            
            logger.info(f"Running video generator with args: {args}")
            
            # Run the video generator
            start_time = time.time()
            video_generator_main()
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Check if output video was created
            output_video_path = "output_with_overlay.mp4"
            if os.path.exists(output_video_path):
                file_size = os.path.getsize(output_video_path)
                logger.info(f"✅ Video generated successfully: {output_video_path} ({file_size} bytes)")
                
                return {
                    'success': True,
                    'output_video_path': output_video_path,
                    'file_size': file_size,
                    'processing_time': processing_time,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"❌ Output video not found: {output_video_path}")
                return {
                    'success': False,
                    'error': 'Output video file not found',
                    'processing_time': processing_time,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error in video generation: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _consume_single_message(self):
        """Consume a single message from the queue and delete queue after processing"""
        logger.info(f"Waiting for message in queue: {self.queue_name}")
        
        try:
            # Connect to message queue
            if not self.message_consumer.connect():
                logger.error("Failed to connect to message queue")
                return {'success': False, 'error': 'Connection failed'}
            
            # Consume one message
            message = self.message_consumer.consume_message()
            
            if not message:
                logger.info("No message received, exiting")
                return {'success': False, 'error': 'No message received'}
            
            # Process the message
            logger.info(f"Processing message: {message['id']}")
            result = self._process_single_message(message)
            
            if result['success']:
                logger.info(f"✅ Video generation completed successfully: {result.get('output_video_path', 'unknown')}")
            else:
                logger.error(f"❌ Video generation failed: {result.get('error', 'Unknown error')}")
            
            # Delete the queue after processing
            logger.info(f"🗑️ Deleting queue: {self.queue_name}")
            self.message_consumer.delete_queue()
            
            return result
            
        finally:
            # Close connection
            self.message_consumer.close()
    
    def start(self):
        """Start the queue consumer - process one message and exit"""
        logger.info("Starting Video Generator Queue Consumer (Single Message Mode)...")
        self.running = True
        
        try:
            # Process one message and exit
            result = self._consume_single_message()
            
            # Exit after processing
            logger.info("Message processing completed, shutting down...")
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            logger.error(f"Error in queue consumer: {e}")
        finally:
            self.running = False
            logger.info("Queue consumer stopped")

def main():
    """Main entry point"""
    consumer = VideoGeneratorQueueConsumer()
    logger.info("Starting in QUEUE MODE - processing messages from RabbitMQ")
    consumer.start()

if __name__ == "__main__":
    main() 