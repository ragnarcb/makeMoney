#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Voice Cloning Queue Consumer - TTS 2.0
Processa jobs de clonagem de voz da fila RabbitMQ
"""

# Disable numba JIT and caching BEFORE any other imports
import os
os.environ['NUMBA_DISABLE_JIT'] = '1'
os.environ['NUMBA_CACHE_DIR'] = '/tmp'
os.environ['LIBROSA_CACHE_DIR'] = '/tmp'
os.environ['LIBROSA_CACHE_LEVEL'] = '0'

# Aggressive monkey-patching to disable librosa caching
import sys
import types

# Create a dummy cache manager that does nothing
class DummyCacheManager:
    def __init__(self, *args, **kwargs):
        pass
    def __getattr__(self, name):
        return lambda *args, **kwargs: None

# Monkey-patch librosa cache before any imports
def disable_librosa_cache():
    try:
        import librosa._cache
        librosa._cache.cache = DummyCacheManager()
    except:
        pass

# Call the function immediately
disable_librosa_cache()

import json
import time
import signal
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import logging
from datetime import datetime
import pika

# Add current directory to path for imports
import sys
current_dir = Path(__file__).parent.absolute()
sys.path.insert(0, str(current_dir))

# Install Coqui TTS if not available
def ensure_coqui_tts_installed():
    """Ensure Coqui TTS is installed at runtime"""
    try:
        import TTS
        print(f"[OK] Coqui TTS already available: {TTS.__version__}")
        return True
    except ImportError:
        print("[INFO] Coqui TTS not found, installing...")
        try:
            # Install Coqui TTS
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "--no-cache-dir", "coqui-tts==0.27.0"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Verify installation
            import TTS
            print(f"[OK] Coqui TTS installed successfully: {TTS.__version__}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to install Coqui TTS: {e}")
            return False

# Ensure Coqui TTS is available before importing other modules
if not ensure_coqui_tts_installed():
    print("[ERROR] Cannot proceed without Coqui TTS")
    sys.exit(1)

from character_voice_generator import CharacterVoiceGenerator
from config import PATHS, find_file_in_project, get_available_voice_files
from database_integration import VoiceProcessingWorker, VoiceCloningDatabase
from storage_client import LocalStorageClient

# Configure logging
log_file = os.getenv('LOG_FILE', '/var/log/voice-cloning-service.log')

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
    """RabbitMQ consumer for TTS requests"""
    
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
            'id': 'mock-request-1',
            'type': 'batch',
            'messages': [
                {'text': 'Olá, sou o aluno Lucas!', 'from_user': 'aluno'},
                {'text': 'Olá Lucas, sou a professora Marina!', 'from_user': 'professora'},
                {'text': 'Como está indo com os estudos?', 'from_user': 'aluno'},
                {'text': 'Muito bem! Continue assim!', 'from_user': 'professora'}
            ],
            'voice_mapping': {
                'aluno': '/home/silent/Documents/Computarias/makeMoney/voice_cloning/voices/voz_aluno_lucas.wav',
                'professora': '/home/silent/Documents/Computarias/makeMoney/voice_cloning/voices/voz_referencia_convertida_ffmpeg.wav'
            },
            'output_dir': '/home/silent/Documents/Computarias/makeMoney/voice_cloning/src/generated_audio',
            'use_voice_cloning': True
        }
    
    def delete_queue(self):
        """Mock queue deletion"""
        logger.info(f"Mock mode: Deleted queue {self.queue_name}")
    
    def close(self):
        """Mock connection close"""
        logger.info("Mock mode: Connection closed")

class VoiceCloningQueueConsumer:
    """Queue consumer for voice cloning TTS requests - One message per queue"""
    
    def __init__(self):
        """Initialize the queue consumer"""
        # Jobber will inject the temporary queue name via CONSUMER_QUEUE_NAME
        self.queue_name = os.getenv('CONSUMER_QUEUE_NAME', 'voice-cloning-queue')

        if os.getenv('USE_MOCK_MODE', 'false').lower() == 'true':
            self.queue_name = 'voice-cloning-queue'  # Use mock queue for testing
        

        self.tts_generator = None
        self.running = False
        self.message_consumer = None
        
        # Initialize TTS generator
        self._initialize_tts_generator()
        
        # Initialize message consumer (RabbitMQ or Mock)
        self._initialize_message_consumer()
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False
    
    def _initialize_tts_generator(self):
        """Initialize the TTS generator with TTS 2.0 logic"""
        try:
            logger.info("Initializing Voice Cloning TTS generator with TTS 2.0...")
            
            # Get output directory from environment or use default
            output_dir = os.getenv('OUTPUT_DIR', PATHS["output_dir"])
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            self.tts_generator = CharacterVoiceGenerator(
                default_reference_audio="",  # Will auto-detect
                output_base_dir=output_dir,
                voice_mapping={},
                auto_detect_voices=True
            )
            
            logger.info("Voice Cloning TTS generator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Voice Cloning TTS generator: {e}")
            raise
    
    def _initialize_message_consumer(self):
        """Initialize message consumer (RabbitMQ or Mock)"""
        # Check if we should use mock mode

        if len(sys.argv) > 1:
            use_mock = sys.argv[1] == 'mock'
        else:
            use_mock = os.getenv('USE_MOCK_MODE', 'false').lower() == 'true'
        
        if use_mock:
            logger.info("Using Mock Message Consumer for development")
            self.message_consumer = MockMessageConsumer(self.queue_name)
        else:
            # Use RabbitMQ
            rabbitmq_host = os.getenv('RABBITMQ_HOST', 'localhost')
            rabbitmq_port = int(os.getenv('RABBITMQ_PORT', '5672'))
            rabbitmq_user = os.getenv('RABBITMQ_USER', 'guest')
            rabbitmq_password = os.getenv('RABBITMQ_PASSWORD', 'guest')
            rabbitmq_vhost = os.getenv('RABBITMQ_VHOST', '/')
            
            logger.info(f"Using RabbitMQ Consumer: {rabbitmq_host}:{rabbitmq_port}")
            self.message_consumer = RabbitMQConsumer(
                host=rabbitmq_host,
                port=rabbitmq_port,
                user=rabbitmq_user,
                password=rabbitmq_password,
                vhost=rabbitmq_vhost,
                queue_name=self.queue_name
            )
    
    def _process_single_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single TTS generation request
        
        Args:
            message: The message from the queue
            
        Returns:
            Processing result
        """
        try:
            start_time = time.time()
            logger.info(f"Processing TTS request: {message.get('id', 'unknown')}")
            
            # Check if this is a voice cloning request (from jobber)
            if 'video_id' in message and 'messages' in message:
                return self._process_jobber_message(message)
            
            # Extract request data for legacy format
            request_type = message.get('type', 'batch')
            
            logger.info(f"Request type: {request_type}")
            
            if request_type == 'single':
                return self._process_single_tts(message)
            else:
                return self._process_batch_tts(message)
                
        except Exception as e:
            logger.error(f"Error processing TTS request: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _process_jobber_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a message from the temporary queue created by jobber
        
        Expected format (this is what jobber sends to the temporary queue):
        {
            "video_id": "uuid",
            "messages": [...],
            "voice_mapping": {...}
        }
        """
        try:
            logger.info("Processing voice cloning request from jobber")
            
            # Extract data from message (jobber already extracted the 'data' part)
            video_id = message.get('video_id')
            messages = message.get('messages', [])
            voice_mapping = message.get('voice_mapping', {})
            
            if not video_id:
                raise ValueError("Missing video_id in message")
            
            logger.info(f"Processing voice requests for video: {video_id}")
            logger.info(f"Number of messages to process: {len(messages)}")
            
            # Initialize database and storage
            db = VoiceCloningDatabase()
            storage_client = None
            
            # Check if we should use remote storage
            use_local_storage = os.getenv("USE_LOCAL_STORAGE", "true").lower() == "true"
            if not use_local_storage:
                storage_client = LocalStorageClient()
                logger.info("Using remote storage for voice files")
            
            # Process each message and create voice requests in database
            voice_ids = []
            for i, msg in enumerate(messages):
                try:
                    # Create voice request in database
                    voice_id = db.create_voice_request(
                        video_id=video_id,
                        character_name=msg.get('from_user', f'character_{i}'),
                        text_content=msg.get('text', ''),
                        voice_mapping_id=None  # Will be resolved during processing
                    )
                    voice_ids.append(voice_id)
                    logger.info(f"Created voice request {voice_id} for message {i}")
                    
                except Exception as e:
                    logger.error(f"Failed to create voice request for message {i}: {e}")
            
            if not voice_ids:
                raise Exception("No voice requests were created")
            
            # Process the voice requests
            worker = VoiceProcessingWorker()
            worker.process_pending_voices()
            
            # Check if all voices are completed
            if db.check_all_voices_completed(video_id):
                logger.info(f"All voice processing completed for video {video_id}")
                return {
                    'success': True,
                    'video_id': video_id,
                    'message': 'Voice processing completed successfully',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.warning(f"Some voice processing failed for video {video_id}")
                return {
                    'success': False,
                    'video_id': video_id,
                    'error': 'Some voice processing failed',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error processing voice cloning request: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _process_single_tts(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process single TTS request"""
        try:
            text = message.get('text', '')
            voice_file = message.get('voice_file')
            output_filename = message.get('output_filename', 'single_tts.wav')
            output_dir = message.get('output_dir', '/tmp/voice_cloning_output')
            
            # Create output directory
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, output_filename)
            
            logger.info(f"Generating single TTS: '{text[:50]}...'")
            
            # Generate audio using TTS 2.0 logic
            success = self.tts_generator.generate_single_audio(
                text=text,
                output_file=output_path,
                character_voice=voice_file or "",
                use_voice_cloning=True
            )
            
            if success:
                file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0
                logger.info(f"Single TTS generated successfully: {output_path} ({file_size} bytes)")
                
                return {
                    'success': True,
                    'audio_path': output_path,
                    'file_size': file_size,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'error': 'Failed to generate audio',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error in single TTS: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _process_batch_tts(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Process batch TTS request"""
        try:
            messages = message.get('messages', [])
            voice_mapping = message.get('voice_mapping', {})
            output_dir = message.get('output_dir', '/tmp/voice_cloning_output')
            use_voice_cloning = message.get('use_voice_cloning', True)
            
            # Create temporary JSON file
            temp_json_path = os.path.join(output_dir, f"temp_messages_{int(time.time())}.json")
            os.makedirs(output_dir, exist_ok=True)
            
            # Convert messages to the format expected by voice cloning system
            voice_cloning_messages = []
            for i, msg in enumerate(messages):
                voice_cloning_message = {
                    "id": i,
                    "texto": msg.get('text', ''),
                    "usuario": {
                        "id": msg.get('from_user', 'unknown').lower(),
                        "nome": msg.get('from_user', 'unknown')
                    }
                }
                voice_cloning_messages.append(voice_cloning_message)
            
            # Save to temporary JSON file
            with open(temp_json_path, 'w', encoding='utf-8') as f:
                json.dump({"mensagens": voice_cloning_messages}, f, ensure_ascii=False, indent=2)
            
            # Load messages into TTS generator
            if not self.tts_generator.load_messages_from_json(temp_json_path):
                return {
                    'success': False,
                    'error': 'Failed to load messages',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Apply voice mapping if provided
            if voice_mapping:
                for character_id, voice_file in voice_mapping.items():
                    self.tts_generator.set_character_voice(character_id, voice_file)
            
            # Generate audio for all characters using TTS 2.0 logic
            stats = self.tts_generator.generate_all_characters_audio(use_voice_cloning=use_voice_cloning)
            
            # Clean up temporary file
            try:
                os.remove(temp_json_path)
            except:
                pass
            
            if stats.successful_generations == 0:
                return {
                    'success': False,
                    'error': 'No audio files were generated successfully',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Collect generated audio paths
            audio_paths = []
            for char_id, character in self.tts_generator.get_characters().items():
                char_dir = os.path.join(output_dir, char_id)
                if os.path.exists(char_dir):
                    for file in os.listdir(char_dir):
                        if file.endswith('.wav'):
                            audio_paths.append(os.path.join(char_dir, file))
            
            logger.info(f"Batch TTS completed: {len(audio_paths)} audio files generated")
            
            return {
                'success': True,
                'audio_paths': audio_paths,
                'stats': {
                    'total_messages': stats.total_messages,
                    'successful_generations': stats.successful_generations,
                    'failed_generations': stats.failed_generations,
                    'success_rate': stats.success_rate
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in batch TTS: {e}")
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
                logger.info(f"✅ Message processed successfully: {result.get('audio_paths', [])}")
            else:
                logger.error(f"❌ Message processing failed: {result.get('error', 'Unknown error')}")
            
            # Delete the queue after processing
            logger.info(f"🗑️ Deleting queue: {self.queue_name}")
            self.message_consumer.delete_queue()
            
            return result
            
        finally:
            # Close connection
            self.message_consumer.close()
    
    def start(self):
        """Start the queue consumer - process one message and exit"""
        logger.info("Starting Voice Cloning Queue Consumer (Single Message Mode)...")
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
    
    def start_database_mode(self):
        """Start the queue consumer in database mode - continuously process voice requests from database"""
        logger.info("Starting Voice Cloning Queue Consumer (Database Mode)...")
        self.running = True
        
        try:
            # Initialize database worker
            worker = VoiceProcessingWorker()
            
            # Run continuous processing
            worker.run_continuous_processing(interval_seconds=30)
            
        except KeyboardInterrupt:
            logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            logger.error(f"Error in database mode: {e}")
        finally:
            self.running = False
            logger.info("Database mode stopped")

def main():
    """Main entry point"""
    import sys
    
    # Check if database mode is requested
    use_database_mode = os.getenv('USE_DATABASE_MODE', 'false').lower() == 'true'
    
    consumer = VoiceCloningQueueConsumer()
    
    if use_database_mode:
        logger.info("Starting in DATABASE MODE - processing voice requests from PostgreSQL")
        consumer.start_database_mode()
    else:
        logger.info("Starting in QUEUE MODE - processing messages from RabbitMQ")
        consumer.start()

if __name__ == "__main__":
    main() 