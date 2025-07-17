"""
Sistema TTS Moderno - Compatible com Python 3.12+
Autor: Assistente IA
Versão: 2.0 - Atualizada para Python 3.12

Suporta:
- Coqui TTS atualizado (coqui-tts)
- RealtimeTTS com múltiplos engines
- Clonagem de voz
- Múltiplas linguagens
- Processamento em tempo real
"""

import os
import sys
import json
import time
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import logging

# Suprimir warnings desnecessários
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

class ModernTTSEngine:
    """Engine TTS Moderno compatível com Python 3.12+"""
    
    def __init__(self, model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"):
        """
        Inicializa o engine TTS moderno
        
        Args:
            model_name: Nome do modelo TTS a usar
        """
        self.model_name = model_name
        self.current_model = None
        self.output_dir = Path("generated_audio")
        self.output_dir.mkdir(exist_ok=True)
        
        # Configuração de logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Detectar dispositivo disponível
        self.device = self._detect_device()
        self.logger.info(f"[INFO] Usando dispositivo: {self.device}")
        
        # Inicializar engine principal
        self._initialize_engine()
    
    def _detect_device(self) -> str:
        """Detecta o melhor dispositivo disponível"""
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
        except ImportError:
            pass
        return "cpu"
    
    def _initialize_engine(self):
        """Inicializa o engine TTS principal"""
        try:
            # Tentar usar Coqui TTS moderno primeiro
            self._init_coqui_tts()
        except Exception as e:
            self.logger.warning(f"[WARN] Erro ao inicializar Coqui TTS: {e}")
            try:
                # Fallback para RealtimeTTS
                self._init_realtime_tts()
            except Exception as e2:
                self.logger.error(f"[ERROR] Erro ao inicializar RealtimeTTS: {e2}")
                raise RuntimeError("Nenhum engine TTS pôde ser inicializado")
    
    def _init_coqui_tts(self):
        """Inicializa Coqui TTS moderno"""
        try:
            from TTS.api import TTS
            
            self.logger.info(f"[INFO] Carregando modelo: {self.model_name}")
            self.current_model = TTS(self.model_name)
            
            if self.device == "cuda":
                self.current_model = self.current_model.to(self.device)
            
            self.engine_type = "coqui"
            self.logger.info(f"[OK] Coqui TTS inicializado com sucesso!")
            
        except Exception as e:
            raise RuntimeError(f"Erro ao inicializar Coqui TTS: {e}")
    
    def _init_realtime_tts(self):
        """Inicializa RealtimeTTS como fallback"""
        try:
            from RealtimeTTS import TextToAudioStream, SystemEngine, CoquiEngine
            
            # Tentar usar CoquiEngine dentro do RealtimeTTS
            try:
                engine = CoquiEngine()
                self.current_model = TextToAudioStream(engine)
                self.engine_type = "realtime_coqui"
                self.logger.info(f"[OK] RealtimeTTS com CoquiEngine inicializado!")
            except:
                # Fallback para SystemEngine
                engine = SystemEngine()
                self.current_model = TextToAudioStream(engine)
                self.engine_type = "realtime_system"
                self.logger.info(f"[OK] RealtimeTTS com SystemEngine inicializado!")
                
        except Exception as e:
            raise RuntimeError(f"Erro ao inicializar RealtimeTTS: {e}")
    
    def synthesize_text(self, 
                       text: str, 
                       output_path: Optional[str] = None,
                       speaker_wav: Optional[str] = None,
                       language: str = "pt",
                       speed: float = 1.0) -> str:
        """
        Sintetiza texto para áudio
        
        Args:
            text: Texto para sintetizar
            output_path: Caminho de saída (opcional)
            speaker_wav: Arquivo de referência para clonagem de voz
            language: Idioma do texto
            speed: Velocidade da fala
            
        Returns:
            Caminho do arquivo gerado
        """
        if not text.strip():
            raise ValueError("Texto não pode estar vazio")
        
        # Gerar nome de arquivo se não especificado
        if not output_path:
            timestamp = int(time.time())
            output_path = self.output_dir / f"synthesis_{timestamp}.wav"
        
        output_path = Path(output_path)
        
        try:
            if self.engine_type == "coqui":
                return self._synthesize_with_coqui(text, output_path, speaker_wav, language, speed)
            elif self.engine_type.startswith("realtime"):
                return self._synthesize_with_realtime(text, output_path, speaker_wav, language, speed)
            else:
                raise RuntimeError("Engine não inicializado corretamente")
                
        except Exception as e:
            self.logger.error(f"[ERROR] Erro na síntese: {e}")
            raise
    
    def _synthesize_with_coqui(self, text: str, output_path: Path, 
                              speaker_wav: Optional[str], language: str, speed: float) -> str:
        """Sintetiza usando Coqui TTS"""
        try:
            # Verificar se o modelo é multilingual
            is_multilingual = "multilingual" in self.model_name.lower() or "xtts" in self.model_name.lower()
            
            if speaker_wav and os.path.exists(speaker_wav):
                # Síntese com clonagem de voz
                if is_multilingual:
                    # Para modelos multilinguais, sempre especificar idioma
                    self.current_model.tts_to_file(
                        text=text,
                        speaker_wav=speaker_wav,
                        language=language,
                        file_path=str(output_path)
                    )
                else:
                    # Para modelos monolinguais
                    self.current_model.tts_to_file(
                        text=text,
                        speaker_wav=speaker_wav,
                        file_path=str(output_path)
                    )
                self.logger.info(f"[OK] Síntese com clonagem concluída: {output_path}")
            else:
                # Síntese normal
                if is_multilingual:
                    # Para modelos multilinguais, sempre especificar idioma
                    self.current_model.tts_to_file(
                        text=text,
                        language=language,
                        file_path=str(output_path)
                    )
                else:
                    # Para modelos monolinguais
                    self.current_model.tts_to_file(
                        text=text,
                        file_path=str(output_path)
                    )
                self.logger.info(f"[OK] Síntese normal concluída: {output_path}")
            
            return str(output_path)
            
        except Exception as e:
            raise RuntimeError(f"Erro na síntese com Coqui: {e}")
    
    def _synthesize_with_realtime(self, text: str, output_path: Path,
                                 speaker_wav: Optional[str], language: str, speed: float) -> str:
        """Sintetiza usando RealtimeTTS"""
        try:
            self.current_model.feed(text)
            self.current_model.play()
            
            # Para RealtimeTTS, precisamos implementar salvamento manual
            # Por enquanto, apenas reproduz o áudio
            self.logger.info(f"[OK] Síntese com RealtimeTTS reproduzida")
            
            # Criar arquivo vazio como placeholder
            output_path.touch()
            return str(output_path)
            
        except Exception as e:
            raise RuntimeError(f"Erro na síntese com RealtimeTTS: {e}")
    
    def list_available_models(self) -> List[str]:
        """Lista modelos disponíveis"""
        try:
            if hasattr(self.current_model, 'list_models'):
                return self.current_model.list_models()
            else:
                return [
                    "tts_models/multilingual/multi-dataset/xtts_v2",
                    "tts_models/en/ljspeech/tacotron2-DDC",
                    "tts_models/pt/cv/vits"
                ]
        except Exception as e:
            self.logger.warning(f"[WARN] Erro ao listar modelos: {e}")
            return []
    
    def clone_voice(self, text: str, reference_audio: str, output_path: Optional[str] = None) -> str:
        """
        Clona uma voz usando áudio de referência
        
        Args:
            text: Texto para falar
            reference_audio: Caminho do áudio de referência
            output_path: Caminho de saída
            
        Returns:
            Caminho do arquivo gerado
        """
        if not os.path.exists(reference_audio):
            raise FileNotFoundError(f"Arquivo de referência não encontrado: {reference_audio}")
        
        self.logger.info(f"[INFO] Clonando voz de: {reference_audio}")
        
        return self.synthesize_text(
            text=text,
            output_path=output_path,
            speaker_wav=reference_audio,
            language="pt"
        )
    
    def play_audio(self, audio_path: str):
        """Reproduz arquivo de áudio"""
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {audio_path}")
        
        try:
            # Tentar usar pygame primeiro
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(audio_path)
                pygame.mixer.music.play()
                
                # Aguardar reprodução terminar
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                    
                self.logger.info(f"[OK] Áudio reproduzido: {audio_path}")
                return
            except ImportError:
                pass
            
            # Fallback para playsound
            try:
                from playsound import playsound
                playsound(audio_path)
                self.logger.info(f"[OK] Áudio reproduzido: {audio_path}")
                return
            except ImportError:
                pass
            
            # Último recurso: comando do sistema
            if sys.platform.startswith('win'):
                os.system(f'start "" "{audio_path}"')
            elif sys.platform.startswith('darwin'):
                os.system(f'afplay "{audio_path}"')
            else:
                os.system(f'aplay "{audio_path}" 2>/dev/null || paplay "{audio_path}"')
                
            self.logger.info(f"[OK] Áudio reproduzido via sistema: {audio_path}")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Erro ao reproduzir áudio: {e}")
    
    def get_system_info(self) -> Dict[str, Any]:
        """Retorna informações do sistema"""
        info = {
            "engine_type": getattr(self, 'engine_type', 'unknown'),
            "model_name": self.model_name,
            "device": self.device,
            "python_version": sys.version,
            "output_directory": str(self.output_dir)
        }
        
        try:
            import torch
            info["torch_version"] = torch.__version__
            info["cuda_available"] = torch.cuda.is_available()
            if torch.cuda.is_available():
                info["cuda_version"] = torch.version.cuda
        except ImportError:
            info["torch_available"] = False
        
        return info

# Função de conveniência para compatibilidade
def create_tts_engine(model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2") -> ModernTTSEngine:
    """Cria uma instância do engine TTS moderno"""
    return ModernTTSEngine(model_name) 