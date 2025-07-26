#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo com engines TTS abstraídas com melhorias para evitar cortes
Apenas Coqui TTS - sem fallbacks ruins
"""

# Disable numba JIT and caching BEFORE any other imports
import os
os.environ['NUMBA_DISABLE_JIT'] = '1'
os.environ['NUMBA_CACHE_DIR'] = '/tmp/numba_cache'
os.environ['LIBROSA_CACHE_DIR'] = '/tmp/librosa_cache'
os.environ['LIBROSA_CACHE_LEVEL'] = '0'

import sys
import tempfile
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from config import TTS_CONFIG
import time

class AutoAcceptTTS:
    """Wrapper para TTS que aceita automaticamente prompts de licença"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name
        self._tts_instance = None
        
    def _create_tts_instance(self):
        """Cria instância TTS com aceitação automática de licença"""
        import TTS
        from TTS.api import TTS as TTSCore
        
        # Set environment variable to auto-accept license
        os.environ['COQUI_TOS_AGREED'] = '1'
        
        # Also handle stdin redirection as backup
        original_stdin = sys.stdin
        from io import StringIO
        sys.stdin = StringIO('y\n')
        
        try:
            self._tts_instance = TTSCore(self.model_name)
        finally:
            sys.stdin = original_stdin
    
    def tts_to_file(self, **kwargs):
        """Wrapper para tts_to_file com instância automática"""
        if self._tts_instance is None:
            self._create_tts_instance()
        return self._tts_instance.tts_to_file(**kwargs)

class TTSEngine(ABC):
    """Classe base abstrata para engines TTS"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa a engine TTS
        
        Args:
            config: Configurações da engine
        """
        self.config = config or TTS_CONFIG
        self.is_available = False
        self.name = "Unknown"
        self.supports_voice_cloning = False
    
    @abstractmethod
    def is_engine_available(self) -> bool:
        """Verifica se a engine está disponível no sistema"""
        pass
    
    @abstractmethod
    def synthesize_to_file(self, text: str, output_file: str, reference_audio: Optional[str] = None) -> bool:
        """
        Sintetiza texto para arquivo
        
        Args:
            text: Texto a ser sintetizado
            output_file: Arquivo de saída
            reference_audio: Arquivo de áudio de referência (para clonagem)
            
        Returns:
            True se sucesso, False se falha
        """
        pass
    
    def validate_output(self, output_file: str) -> bool:
        """Valida se o arquivo de saída foi criado corretamente"""
        return os.path.exists(output_file) and os.path.getsize(output_file) > 100
    
    def add_audio_padding(self, audio_file: str, padding_ms: int = 500) -> bool:
        """
        Adiciona padding (silêncio) no final do áudio para evitar cortes
        
        Args:
            audio_file: Arquivo de áudio
            padding_ms: Padding em milissegundos
            
        Returns:
            True se sucesso
        """
        try:
            from pydub import AudioSegment
            from pydub.silence import generate_silence
            
            # Carregar áudio
            audio = AudioSegment.from_wav(audio_file)
            
            # Criar silêncio
            silence = generate_silence(duration=padding_ms)
            
            # Adicionar padding no final
            audio_with_padding = audio + silence
            
            # Salvar de volta
            audio_with_padding.export(audio_file, format="wav")
            
            print(f"[INFO] Padding de {padding_ms}ms adicionado ao áudio")
            return True
            
        except ImportError:
            print("[WARNING] pydub não disponível - padding não aplicado")
            return False
        except Exception as e:
            print(f"[WARNING] Erro ao adicionar padding: {e}")
            return False

class CoquiTTSEngine(TTSEngine):
    """Engine Coqui TTS com suporte a clonagem de voz e melhorias anti-corte"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.name = "Coqui TTS"
        self.supports_voice_cloning = True
        self.model_name = self.config.get('model_name', "tts_models/multilingual/multi-dataset/xtts_v2")
        self.language = self.config.get('language', "pt")
        self.tts_instance: Optional[Any] = None
        self.is_available = self.is_engine_available()
    
    def is_engine_available(self) -> bool:
        """Verifica se Coqui TTS está disponível"""
        try:
            import TTS
            from TTS.api import TTS as TTSCore
            return True
        except ImportError as e:
            print(f"[DEBUG] ImportError: {e}")
            return False
        except Exception as e:
            print(f"[DEBUG] Exception: {e}")
            return False
    
    def _load_model(self) -> bool:
        """Carrega o modelo TTS"""
        if self.tts_instance is not None:
            return True
        
        try:
            print(f"[INFO] Carregando modelo Coqui: {self.model_name}")
            
            # Use the auto-accept wrapper
            self.tts_instance = AutoAcceptTTS(self.model_name)
            print("[OK] Modelo Coqui carregado com sucesso")
            return True
                
        except Exception as e:
            print(f"[ERROR] Erro ao carregar modelo Coqui: {e}")
            return False
    
    def _prepare_text_for_synthesis(self, text: str) -> str:
        """Prepara texto especificamente para Coqui TTS"""
        # Garantir que o texto termine adequadamente
        text = text.strip()
        
        # Adicionar pausa no final se não houver pontuação
        if text and not text.endswith(('.', '!', '?', ',')):
            text += ','
        
        # Adicionar um pequeno espaço no final para dar tempo ao modelo
        text += '   '
        
        return text
    
    def synthesize_to_file(self, text: str, output_file: str, reference_audio: Optional[str] = None) -> bool:
        """Sintetiza usando Coqui TTS com melhorias anti-corte"""
        if not self.is_available:
            print("[ERROR] Coqui TTS não está disponível")
            return False
        
        if not self._load_model():
            return False
        
        try:
            # Preparar texto para síntese
            prepared_text = self._prepare_text_for_synthesis(text)
            print(f"[INFO] Sintetizando com Coqui TTS: {text[:50]}...")
            print(f"[DEBUG] Texto preparado: '{prepared_text}'")
            
            # Usar arquivo temporário primeiro
            temp_file = tempfile.mktemp(suffix=".wav")
            
            try:
                if reference_audio and self.supports_voice_cloning:
                    # Usar clonagem de voz com configurações melhoradas
                    self.tts_instance.tts_to_file(
                        text=prepared_text,
                        speaker_wav=reference_audio,
                        language=self.language,
                        file_path=temp_file,
                        speed=1.0,  # Velocidade normal para evitar cortes
                        # Adicionar configurações específicas se disponíveis
                    )
                else:
                    # Usar voz padrão
                    self.tts_instance.tts_to_file(
                        text=prepared_text,
                        file_path=temp_file
                    )
                
                # Verificar se arquivo temporário foi criado
                if not self.validate_output(temp_file):
                    print("[ERROR] Arquivo temporário não foi criado corretamente")
                    return False
                
                # Adicionar padding para evitar cortes
                self.add_audio_padding(temp_file, padding_ms=800)
                
                # Mover arquivo temporário para o destino final
                import shutil
                shutil.move(temp_file, output_file)
                
                if self.validate_output(output_file):
                    print(f"[OK] Coqui TTS bem-sucedido com padding: {output_file}")
                    return True
                else:
                    print("[ERROR] Arquivo de saída final inválido")
                    return False
                    
            finally:
                # Limpar arquivo temporário se ainda existir
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                        
        except Exception as e:
            print(f"[ERROR] Erro na síntese Coqui TTS: {e}")
            return False

class TTSEngineManager:
    """Gerenciador de engines TTS - apenas Coqui TTS"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Inicializa o gerenciador de engines
        
        Args:
            config: Configurações TTS
        """
        self.config = config or TTS_CONFIG
        self.engines: Dict[str, TTSEngine] = {}
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Inicializa as engines disponíveis - apenas Coqui TTS"""
        print("[INFO] Inicializando engines TTS...")
        
        # Apenas Coqui TTS - sem fallbacks ruins
        coqui_engine = CoquiTTSEngine(self.config)
        if coqui_engine.is_available:
            self.engines['coqui'] = coqui_engine
            print("[OK] Coqui TTS inicializado")
        else:
            print("[ERROR] Coqui TTS não está disponível")
            raise RuntimeError("Coqui TTS não está disponível - instale com: pip install coqui-tts")
    
    def get_available_engines(self) -> List[str]:
        """Retorna lista de engines disponíveis"""
        return list(self.engines.keys())
    
    def get_engine(self, engine_name: str) -> Optional[TTSEngine]:
        """Retorna uma engine específica"""
        return self.engines.get(engine_name)
    
    def get_best_engine(self, prefer_voice_cloning: bool = True) -> Optional[TTSEngine]:
        """
        Retorna a melhor engine disponível
        
        Args:
            prefer_voice_cloning: Se deve preferir engines com clonagem de voz
            
        Returns:
            Melhor engine disponível
        """
        if not self.engines:
            print("[ERROR] Nenhuma engine TTS disponível")
            return None
        
        # Apenas Coqui TTS - sempre a melhor opção
        if 'coqui' in self.engines:
            return self.engines['coqui']
        
        # Se não houver Coqui, não há opção válida
        print("[ERROR] Coqui TTS não está disponível")
        return None
    
    def synthesize_with_best_engine(self, text: str, output_file: str, reference_audio: Optional[str] = None) -> bool:
        """
        Sintetiza usando a melhor engine disponível
        
        Args:
            text: Texto para sintetizar
            output_file: Arquivo de saída
            reference_audio: Arquivo de referência para clonagem
            
        Returns:
            True se sucesso
        """
        engine = self.get_best_engine()
        if not engine:
            print("[ERROR] Nenhuma engine TTS disponível")
            return False
        
        return engine.synthesize_to_file(text, output_file, reference_audio)
    
    def get_engines_info(self) -> Dict[str, Dict[str, Any]]:
        """Retorna informações sobre as engines disponíveis"""
        info = {}
        for name, engine in self.engines.items():
            info[name] = {
                'name': engine.name,
                'available': engine.is_available,
                'supports_voice_cloning': engine.supports_voice_cloning
            }
        return info 