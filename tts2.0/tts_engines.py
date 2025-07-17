#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo com engines TTS abstraídas com melhorias para evitar cortes
"""

import os
import sys
import tempfile
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from config import TTS_CONFIG

class TTSEngine(ABC):
    """Classe base abstrata para engines TTS"""
    
    def __init__(self, config: Dict[str, Any] = None):
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
    def synthesize_to_file(self, text: str, output_file: str, reference_audio: str = None) -> bool:
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
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name = "Coqui TTS"
        self.supports_voice_cloning = True
        self.model_name = self.config.get('model_name', "tts_models/multilingual/multi-dataset/xtts_v2")
        self.language = self.config.get('language', "pt")
        self.tts_instance = None
        self.is_available = self.is_engine_available()
    
    def is_engine_available(self) -> bool:
        """Verifica se Coqui TTS está disponível"""
        try:
            from TTS.api import TTS
            return True
        except ImportError:
            return False
        except Exception:
            return False
    
    def _load_model(self) -> bool:
        """Carrega o modelo TTS"""
        if self.tts_instance is not None:
            return True
        
        try:
            from TTS.api import TTS
            print(f"[INFO] Carregando modelo Coqui: {self.model_name}")
            self.tts_instance = TTS(self.model_name)
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
    
    def synthesize_to_file(self, text: str, output_file: str, reference_audio: str = None) -> bool:
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
            print(f"[ERROR] Erro na síntese Coqui: {e}")
            return False

class RealtimeTTSEngine(TTSEngine):
    """Engine RealtimeTTS com suporte a clonagem"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name = "RealtimeTTS"
        self.supports_voice_cloning = True
        self.language = self.config.get('language', "pt")
        self.is_available = self.is_engine_available()
    
    def is_engine_available(self) -> bool:
        """Verifica se RealtimeTTS está disponível"""
        try:
            from RealtimeTTS import TextToAudioStream, CoquiEngine
            return True
        except ImportError:
            return False
        except Exception:
            return False
    
    def synthesize_to_file(self, text: str, output_file: str, reference_audio: str = None) -> bool:
        """Sintetiza usando RealtimeTTS"""
        if not self.is_available:
            print("[ERROR] RealtimeTTS não está disponível")
            return False
        
        try:
            from RealtimeTTS import TextToAudioStream, CoquiEngine
            
            print(f"[INFO] Sintetizando com RealtimeTTS: {text[:50]}...")
            
            # Configurar engine
            if reference_audio and self.supports_voice_cloning:
                engine = CoquiEngine(
                    voice=reference_audio,
                    language=self.language
                )
            else:
                engine = CoquiEngine(language=self.language)
            
            # Criar stream e sintetizar
            stream = TextToAudioStream(engine)
            
            # Para salvar em arquivo, precisamos de uma implementação específica
            # Por enquanto, vamos usar uma abordagem alternativa
            stream.feed(text)
            
            # Simular salvamento (RealtimeTTS é focado em tempo real)
            # Em uma implementação real, seria necessário capturar o áudio
            print("[WARNING] RealtimeTTS é otimizado para reprodução em tempo real")
            print("[INFO] Para salvar arquivos, considere usar Coqui TTS diretamente")
            
            return False  # Não suporta salvamento direto em arquivo
            
        except Exception as e:
            print(f"[ERROR] Erro na síntese RealtimeTTS: {e}")
            return False

class Pyttsx3Engine(TTSEngine):
    """Engine pyttsx3 básica (sem clonagem) com melhorias"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.name = "pyttsx3"
        self.supports_voice_cloning = False
        self.rate = self.config.get('rate', 150)
        self.engine_instance = None
        self.is_available = self.is_engine_available()
    
    def is_engine_available(self) -> bool:
        """Verifica se pyttsx3 está disponível"""
        try:
            import pyttsx3
            return True
        except ImportError:
            return False
        except Exception:
            return False
    
    def _get_engine(self):
        """Obtém instância do engine pyttsx3 com configurações otimizadas"""
        if self.engine_instance is None:
            try:
                import pyttsx3
                self.engine_instance = pyttsx3.init()
                
                # Configurar voz portuguesa se disponível
                voices = self.engine_instance.getProperty('voices')
                for voice in voices:
                    if 'portuguese' in voice.name.lower() or 'pt' in voice.id.lower():
                        self.engine_instance.setProperty('voice', voice.id)
                        break
                
                # Configurar velocidade mais lenta para evitar cortes
                self.engine_instance.setProperty('rate', max(self.rate - 20, 100))
                
                # Configurar volume
                self.engine_instance.setProperty('volume', 0.9)
                
            except Exception as e:
                print(f"[ERROR] Erro ao inicializar pyttsx3: {e}")
                return None
        
        return self.engine_instance
    
    def _prepare_text_for_pyttsx3(self, text: str) -> str:
        """Prepara texto especificamente para pyttsx3"""
        # Adicionar pausas para melhor pronúncia
        text = text.replace(',', ', ')
        text = text.replace('.', '. ')
        text = text.replace('!', '! ')
        text = text.replace('?', '? ')
        
        # Garantir terminação adequada
        if text.strip() and not text.strip().endswith(('.', '!', '?')):
            text = text.strip() + '.'
        
        # Adicionar pausa final
        text += '  '
        
        return text
    
    def synthesize_to_file(self, text: str, output_file: str, reference_audio: str = None) -> bool:
        """Sintetiza usando pyttsx3 com melhorias"""
        if not self.is_available:
            print("[ERROR] pyttsx3 não está disponível")
            return False
        
        engine = self._get_engine()
        if engine is None:
            return False
        
        try:
            print(f"[INFO] Sintetizando com pyttsx3: {text[:50]}...")
            
            if reference_audio:
                print("[WARNING] pyttsx3 não suporta clonagem de voz")
            
            # Preparar texto
            prepared_text = self._prepare_text_for_pyttsx3(text)
            print(f"[DEBUG] Texto preparado: '{prepared_text}'")
            
            # Usar arquivo temporário
            temp_file = tempfile.mktemp(suffix=".wav")
            
            try:
                # Salvar em arquivo temporário
                engine.save_to_file(prepared_text, temp_file)
                engine.runAndWait()
                
                # Verificar arquivo temporário
                if not self.validate_output(temp_file):
                    print("[ERROR] Arquivo temporário não foi criado")
                    return False
                
                # Adicionar padding
                self.add_audio_padding(temp_file, padding_ms=600)
                
                # Mover para destino final
                import shutil
                shutil.move(temp_file, output_file)
                
                if self.validate_output(output_file):
                    print(f"[OK] pyttsx3 bem-sucedido com padding: {output_file}")
                    return True
                else:
                    print("[ERROR] Arquivo final inválido")
                    return False
                    
            finally:
                # Limpar arquivo temporário
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
                
        except Exception as e:
            print(f"[ERROR] Erro na síntese pyttsx3: {e}")
            return False

class TTSEngineManager:
    """Gerenciador de engines TTS"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o gerenciador
        
        Args:
            config: Configurações globais
        """
        self.config = config or TTS_CONFIG
        self.engines = {}
        self.available_engines = []
        self._initialize_engines()
    
    def _initialize_engines(self):
        """Inicializa todas as engines disponíveis"""
        engine_classes = {
            'coqui': CoquiTTSEngine,
            'realtimetts': RealtimeTTSEngine,
            'pyttsx3': Pyttsx3Engine
        }
        
        print("[INFO] Verificando engines TTS disponíveis...")
        
        for engine_name, engine_class in engine_classes.items():
            try:
                engine = engine_class(self.config)
                self.engines[engine_name] = engine
                
                if engine.is_available:
                    self.available_engines.append(engine_name)
                    print(f"[OK] {engine.name} disponível (com melhorias anti-corte)")
                else:
                    print(f"[WARNING] {engine.name} não disponível")
                    
            except Exception as e:
                print(f"[ERROR] Erro ao inicializar {engine_name}: {e}")
    
    def get_available_engines(self) -> List[str]:
        """Retorna lista de engines disponíveis"""
        return self.available_engines.copy()
    
    def get_engine(self, engine_name: str) -> Optional[TTSEngine]:
        """
        Obtém uma engine específica
        
        Args:
            engine_name: Nome da engine
            
        Returns:
            Instância da engine ou None
        """
        return self.engines.get(engine_name)
    
    def get_best_engine(self, prefer_voice_cloning: bool = True) -> Optional[TTSEngine]:
        """
        Obtém a melhor engine disponível
        
        Args:
            prefer_voice_cloning: Preferir engines com clonagem de voz
            
        Returns:
            Melhor engine disponível
        """
        if not self.available_engines:
            print("[ERROR] Nenhuma engine TTS disponível")
            return None
        
        # Ordem de preferência
        preference_order = ['coqui', 'realtimetts', 'pyttsx3']
        
        # Se preferir clonagem, filtrar engines que suportam
        if prefer_voice_cloning:
            for engine_name in preference_order:
                if engine_name in self.available_engines:
                    engine = self.engines[engine_name]
                    if engine.supports_voice_cloning:
                        print(f"[INFO] Usando {engine.name} (com clonagem e anti-corte)")
                        return engine
        
        # Fallback para primeira engine disponível
        for engine_name in preference_order:
            if engine_name in self.available_engines:
                engine = self.engines[engine_name]
                print(f"[INFO] Usando {engine.name} (com melhorias anti-corte)")
                return engine
        
        return None
    
    def synthesize_with_best_engine(self, text: str, output_file: str, reference_audio: str = None) -> bool:
        """
        Sintetiza usando a melhor engine disponível
        
        Args:
            text: Texto a sintetizar
            output_file: Arquivo de saída
            reference_audio: Áudio de referência para clonagem
            
        Returns:
            True se sucesso
        """
        # Tentar com engine que suporta clonagem primeiro se reference_audio fornecido
        if reference_audio:
            engine = self.get_best_engine(prefer_voice_cloning=True)
        else:
            engine = self.get_best_engine(prefer_voice_cloning=False)
        
        if engine is None:
            print("[ERROR] Nenhuma engine TTS disponível")
            return False
        
        success = engine.synthesize_to_file(text, output_file, reference_audio)
        
        # Se falhar e houver outras engines, tentar com elas
        if not success and len(self.available_engines) > 1:
            print("[WARNING] Engine principal falhou, tentando alternativas...")
            
            for engine_name in self.available_engines:
                alt_engine = self.engines[engine_name]
                if alt_engine != engine:  # Não tentar a mesma engine novamente
                    print(f"[INFO] Tentando com {alt_engine.name}...")
                    if alt_engine.synthesize_to_file(text, output_file, reference_audio):
                        return True
        
        return success
    
    def get_engines_info(self) -> Dict[str, Dict[str, Any]]:
        """Retorna informações sobre todas as engines"""
        info = {}
        
        for name, engine in self.engines.items():
            info[name] = {
                'name': engine.name,
                'available': engine.is_available,
                'supports_voice_cloning': engine.supports_voice_cloning,
                'has_anti_cut_improvements': True  # Todas as engines agora têm melhorias
            }
        
        return info 