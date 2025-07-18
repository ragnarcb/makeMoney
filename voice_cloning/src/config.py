#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurações do Sistema de Clonagem de Voz
"""

import os
import sys
from pathlib import Path

# Configurações de áudio
AUDIO_CONFIG = {
    'sample_rate': 22050,
    'channels': 1,
    'format': 'wav',
    'bit_depth': 16,
    'min_file_size': 1000,  # bytes
}

# Configurações de TTS
TTS_CONFIG = {
    'model_name': "tts_models/multilingual/multi-dataset/xtts_v2",
    'language': "pt",
    'rate': 150,  # para pyttsx3
    'timeout': 60,  # segundos
    'auto_accept_license': True,  # Auto-accept license prompts
}

# Configurações de paralelismo
PARALLEL_CONFIG = {
    'enabled': False,  # Desabilitado para microservice (processa uma mensagem por vez)
    'max_workers': 2,  # Número máximo de workers paralelos
    'chunk_size': 1,   # Tamanho do chunk para processamento paralelo
}

# Caminhos padrão
PATHS = {
    'reference_audio': "Vídeo sem título ‐ Feito com o Clipchamp.wav",
    'converted_audio': "voz_referencia_convertida.wav",
    'ffmpeg_converted': "voz_referencia_convertida_ffmpeg.wav",
    'output_dir': "generated_audio",
    'temp_dir': "temp_audio",
    'voices_dir': "voices",  # Diretório para múltiplas vozes
}

# Configurações de limpeza de texto
TEXT_CLEANING = {
    'remove_emojis': True,
    'remove_special_chars': True,
    'remove_dots': True,
    'remove_ellipsis': True,
    'normalize_spaces': True,
    'remove_punctuation_speech': ['.', '..', '...'],
}

# Engines TTS disponíveis por prioridade
TTS_ENGINES = [
    'coqui',
    'realtimetts',
    'pyttsx3'
]

# Configuração de múltiplas vozes
VOICE_MAPPING = {
    # Formato: "character_id": "voice_file.wav"
    # Exemplo:
    # "aluno": "voz_aluno.wav",
    # "professora": "voz_professora.wav",
    # "medico": "voz_medico.wav"
}

# Configuração de busca automática de vozes
VOICE_AUTO_DETECTION = {
    'enabled': True,
    'patterns': [
        'voz_{character_id}.wav',
        'voice_{character_id}.wav',
        '{character_id}_voice.wav',
        '{character_id}.wav'
    ],
    'search_directories': [
        '.',  # Diretório atual
        'voices',  # Subdiretório voices
        '../voices',  # Diretório voices na pasta pai
        'tts2.0',  # Se executando da raiz
        'tts2.0/voices'
    ]
}

def get_script_directory():
    """Retorna o diretório onde este script está localizado"""
    return Path(__file__).parent.absolute()

def get_project_root():
    """Retorna o diretório raiz do projeto"""
    script_dir = get_script_directory()
    # Se estamos em tts2.0, o projeto root é o pai
    if script_dir.name == 'tts2.0':
        return script_dir.parent
    return script_dir

def get_full_path(relative_path: str) -> str:
    """Retorna caminho completo baseado no diretório do script"""
    return str(get_script_directory() / relative_path)

def find_file_in_project(filename: str) -> str | None:
    """
    Procura um arquivo no projeto, tentando diferentes localizações
    
    Args:
        filename: Nome do arquivo a procurar
        
    Returns:
        Caminho completo do arquivo se encontrado, None caso contrário
    """
    search_paths = [
        get_script_directory() / filename,  # No diretório do script
        get_project_root() / filename,      # Na raiz do projeto
        get_project_root() / 'tts2.0' / filename,  # Na pasta tts2.0
        Path(filename)  # Caminho absoluto se fornecido
    ]
    
    for path in search_paths:
        if path.exists():
            return str(path.absolute())
    
    return None

def ensure_directory_exists(path: str) -> None:
    """Garante que o diretório existe"""
    Path(path).mkdir(parents=True, exist_ok=True)

def get_available_voice_files() -> dict:
    """
    Retorna dicionário com arquivos de voz disponíveis no sistema
    
    Returns:
        Dict com padrão: {"filename": "full_path"}
    """
    voice_files = {}
    
    # Extensões de áudio suportadas
    audio_extensions = ['.wav', '.mp3', '.flac', '.m4a', '.ogg']
    
    # Diretórios para procurar vozes
    search_dirs = [
        get_script_directory(),
        get_script_directory() / 'voices',
        get_project_root(),
        get_project_root() / 'voices',
        get_project_root() / 'tts2.0'
    ]
    
    for search_dir in search_dirs:
        if search_dir.exists():
            for file_path in search_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() in audio_extensions:
                    # Filtrar apenas arquivos que parecem ser vozes
                    filename = file_path.name.lower()
                    if any(keyword in filename for keyword in ['voz', 'voice', 'audio', 'som']):
                        voice_files[file_path.name] = str(file_path.absolute())
    
    return voice_files

def auto_detect_character_voices(character_ids: list) -> dict:
    """
    Detecta automaticamente vozes para personagens baseado em padrões
    
    Args:
        character_ids: Lista de IDs de personagens
        
    Returns:
        Dict mapeando character_id -> voice_file_path
    """
    if not VOICE_AUTO_DETECTION['enabled']:
        return {}
    
    detected_voices = {}
    available_voices = get_available_voice_files()
    
    for char_id in character_ids:
        # Tentar cada padrão de nome
        for pattern in VOICE_AUTO_DETECTION['patterns']:
            expected_filename = pattern.format(character_id=char_id)
            
            # Procurar arquivo que corresponde ao padrão
            for voice_filename, voice_path in available_voices.items():
                if voice_filename.lower() == expected_filename.lower():
                    detected_voices[char_id] = voice_path
                    print(f"🎤 Voz detectada para {char_id}: {voice_filename}")
                    break
            
            if char_id in detected_voices:
                break
    
    return detected_voices

def setup_python_path():
    """Configura o Python path para permitir imports relativos"""
    script_dir = get_script_directory()
    
    # Adicionar diretório do script ao Python path se não estiver
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))
    
    # Adicionar diretório pai se estivermos em tts2.0
    if script_dir.name == 'tts2.0':
        parent_dir = script_dir.parent
        if str(parent_dir) not in sys.path:
            sys.path.insert(0, str(parent_dir))

# Configurar Python path automaticamente
setup_python_path() 