#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para processamento e conversão de áudio
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
from config import AUDIO_CONFIG, PATHS

class AudioProcessor:
    """Classe responsável pelo processamento e conversão de áudio"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o processador de áudio
        
        Args:
            config: Configurações de áudio (usa AUDIO_CONFIG se None)
        """
        self.config = config or AUDIO_CONFIG
        self.sample_rate = self.config['sample_rate']
        self.channels = self.config['channels']
        self.format = self.config['format']
        self.min_file_size = self.config['min_file_size']
    
    def validate_audio_file(self, file_path: str) -> Tuple[bool, str]:
        """
        Valida se o arquivo de áudio existe e tem tamanho mínimo
        
        Args:
            file_path: Caminho para o arquivo
            
        Returns:
            (is_valid, message)
        """
        if not os.path.exists(file_path):
            return False, f"Arquivo não encontrado: {file_path}"
        
        file_size = os.path.getsize(file_path)
        if file_size < self.min_file_size:
            return False, f"Arquivo muito pequeno: {file_size} bytes (mínimo: {self.min_file_size})"
        
        return True, f"Arquivo válido: {file_size} bytes"
    
    def convert_with_pydub(self, input_file: str, output_file: str) -> bool:
        """
        Converte áudio usando pydub
        
        Args:
            input_file: Arquivo de entrada
            output_file: Arquivo de saída
            
        Returns:
            True se sucesso, False se falha
        """
        try:
            from pydub import AudioSegment
            
            print(f"[INFO] Convertendo com pydub: {input_file} -> {output_file}")
            
            # Carregar áudio original
            audio = AudioSegment.from_file(input_file)
            
            print(f"[INFO] Áudio original - Canais: {audio.channels}, "
                  f"Sample Rate: {audio.frame_rate}, Duração: {len(audio)}ms")
            
            # Converter para formato compatível
            audio_converted = audio.set_frame_rate(self.sample_rate).set_channels(self.channels)
            
            # Normalizar volume
            if audio_converted.max_possible_amplitude > 0:
                audio_converted = audio_converted.normalize()
            
            # Salvar
            audio_converted.export(
                output_file, 
                format=self.format,
                parameters=["-ac", str(self.channels), "-ar", str(self.sample_rate)]
            )
            
            is_valid, msg = self.validate_audio_file(output_file)
            if is_valid:
                print(f"[OK] Conversão pydub bem-sucedida: {msg}")
                return True
            else:
                print(f"[ERROR] Arquivo convertido inválido: {msg}")
                return False
                
        except ImportError:
            print("[WARNING] pydub não disponível")
            return False
        except Exception as e:
            print(f"[ERROR] Erro no pydub: {e}")
            return False
    
    def convert_with_soundfile(self, input_file: str, output_file: str) -> bool:
        """
        Converte áudio usando soundfile
        
        Args:
            input_file: Arquivo de entrada
            output_file: Arquivo de saída
            
        Returns:
            True se sucesso, False se falha
        """
        try:
            import soundfile as sf
            import numpy as np
            
            print(f"[INFO] Convertendo com soundfile: {input_file} -> {output_file}")
            
            # Ler áudio
            data, original_sr = sf.read(input_file, dtype='float32')
            print(f"[INFO] Áudio original - Shape: {data.shape}, Sample Rate: {original_sr}")
            
            # Converter para mono se necessário
            if len(data.shape) > 1 and data.shape[1] > 1:
                data = np.mean(data, axis=1)
                print("[INFO] Convertido para mono")
            
            # Resample se necessário
            if original_sr != self.sample_rate:
                try:
                    import librosa
                    data = librosa.resample(data, orig_sr=original_sr, target_sr=self.sample_rate)
                    print(f"[INFO] Resampling com librosa: {original_sr} -> {self.sample_rate}Hz")
                except ImportError:
                    # Resampling simples sem librosa
                    factor = self.sample_rate / original_sr
                    new_length = int(len(data) * factor)
                    data = np.interp(np.linspace(0, len(data), new_length), np.arange(len(data)), data)
                    print(f"[INFO] Resampling simples: {original_sr} -> {self.sample_rate}Hz")
            
            # Normalizar
            if np.max(np.abs(data)) > 0:
                data = data / np.max(np.abs(data)) * 0.9
            
            # Salvar
            sf.write(output_file, data, self.sample_rate, format='WAV', subtype='PCM_16')
            
            is_valid, msg = self.validate_audio_file(output_file)
            if is_valid:
                print(f"[OK] Conversão soundfile bem-sucedida: {msg}")
                return True
            else:
                print(f"[ERROR] Arquivo convertido inválido: {msg}")
                return False
                
        except ImportError:
            print("[WARNING] soundfile não disponível")
            return False
        except Exception as e:
            print(f"[ERROR] Erro no soundfile: {e}")
            return False
    
    def convert_with_ffmpeg(self, input_file: str, output_file: str) -> bool:
        """
        Converte áudio usando ffmpeg
        
        Args:
            input_file: Arquivo de entrada
            output_file: Arquivo de saída
            
        Returns:
            True se sucesso, False se falha
        """
        try:
            # Verificar se ffmpeg está disponível
            ffmpeg_path = shutil.which("ffmpeg")
            if not ffmpeg_path:
                print("[WARNING] FFmpeg não encontrado no PATH")
                return False
            
            print(f"[INFO] Convertendo com ffmpeg: {input_file} -> {output_file}")
            print(f"[INFO] FFmpeg encontrado em: {ffmpeg_path}")
            
            # Usar caminhos absolutos
            input_abs = os.path.abspath(input_file)
            output_abs = os.path.abspath(output_file)
            
            # Comando ffmpeg
            cmd = [
                "ffmpeg", "-i", input_abs,
                "-ar", str(self.sample_rate),
                "-ac", str(self.channels),
                "-acodec", "pcm_s16le",
                "-f", self.format,
                "-y",  # Sobrescrever
                output_abs
            ]
            
            print(f"[CMD] {' '.join(cmd)}")
            
            # Executar com timeout
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                is_valid, msg = self.validate_audio_file(output_abs)
                if is_valid:
                    print(f"[OK] Conversão ffmpeg bem-sucedida: {msg}")
                    return True
                else:
                    print(f"[ERROR] Arquivo convertido inválido: {msg}")
                    return False
            else:
                print(f"[ERROR] FFmpeg falhou (código {result.returncode})")
                if result.stderr:
                    print(f"[STDERR] {result.stderr[:200]}...")
                return False
                
        except subprocess.TimeoutExpired:
            print("[ERROR] FFmpeg timeout")
            return False
        except FileNotFoundError:
            print("[WARNING] FFmpeg não encontrado")
            return False
        except Exception as e:
            print(f"[ERROR] Erro no ffmpeg: {e}")
            return False
    
    def convert_audio(self, input_file: str, output_file: str) -> Tuple[bool, Optional[str]]:
        """
        Converte áudio tentando diferentes métodos
        
        Args:
            input_file: Arquivo de entrada
            output_file: Arquivo de saída
            
        Returns:
            (success, converted_file_path)
        """
        # Validar arquivo de entrada
        is_valid, msg = self.validate_audio_file(input_file)
        if not is_valid:
            print(f"[ERROR] {msg}")
            return False, None
        
        print(f"[INFO] Iniciando conversão de áudio: {input_file}")
        
        # Tentar métodos em ordem de preferência
        conversion_methods = [
            ("FFmpeg", self.convert_with_ffmpeg),
            ("pydub", self.convert_with_pydub),
            ("soundfile", self.convert_with_soundfile),
        ]
        
        for method_name, method_func in conversion_methods:
            print(f"\n[INFO] Tentando conversão com {method_name}...")
            
            if method_func(input_file, output_file):
                print(f"[OK] Conversão bem-sucedida com {method_name}")
                return True, output_file
            else:
                print(f"[WARNING] Conversão falhou com {method_name}")
                # Remover arquivo parcial se existir
                if os.path.exists(output_file):
                    try:
                        os.remove(output_file)
                    except:
                        pass
        
        print("[ERROR] Todos os métodos de conversão falharam")
        print("[INFO] Métodos disponíveis:")
        print("  - FFmpeg: instalar no sistema")
        print("  - pydub: pip install pydub")
        print("  - soundfile: pip install soundfile")
        
        return False, None
    
    def prepare_reference_audio(self, reference_file: str) -> Tuple[bool, Optional[str]]:
        """
        Prepara arquivo de áudio de referência para uso com TTS
        
        Args:
            reference_file: Arquivo de referência original
            
        Returns:
            (success, prepared_file_path)
        """
        # Verificar arquivo original
        is_valid, msg = self.validate_audio_file(reference_file)
        if not is_valid:
            return False, None
        
        print(f"[OK] Arquivo de referência encontrado: {msg}")
        
        # Verificar se já existe versão convertida pelo FFmpeg
        ffmpeg_converted = PATHS['ffmpeg_converted']
        if os.path.exists(ffmpeg_converted):
            is_valid, msg = self.validate_audio_file(ffmpeg_converted)
            if is_valid:
                print(f"[OK] Usando arquivo já convertido pelo FFmpeg: {msg}")
                return True, ffmpeg_converted
        
        # Verificar se já existe versão convertida padrão
        standard_converted = PATHS['converted_audio']
        if os.path.exists(standard_converted):
            is_valid, msg = self.validate_audio_file(standard_converted)
            if is_valid:
                print(f"[INFO] Usando arquivo já convertido: {msg}")
                return True, standard_converted
        
        # Tentar converter
        print("[INFO] Convertendo arquivo para formato compatível...")
        success, converted_file = self.convert_audio(reference_file, ffmpeg_converted)
        
        if success:
            return True, converted_file
        else:
            print("[WARNING] Conversão falhou - usando arquivo original")
            return True, reference_file
    
    def get_audio_info(self, file_path: str) -> Dict[str, Any]:
        """
        Obtém informações sobre arquivo de áudio
        
        Args:
            file_path: Caminho do arquivo
            
        Returns:
            Dicionário com informações do áudio
        """
        info = {
            'exists': os.path.exists(file_path),
            'size_bytes': 0,
            'duration_seconds': None,
            'sample_rate': None,
            'channels': None,
            'format': None
        }
        
        if not info['exists']:
            return info
        
        info['size_bytes'] = os.path.getsize(file_path)
        
        # Tentar obter informações detalhadas
        try:
            import soundfile as sf
            with sf.SoundFile(file_path) as f:
                info['duration_seconds'] = len(f) / f.samplerate
                info['sample_rate'] = f.samplerate
                info['channels'] = f.channels
                info['format'] = f.format
        except:
            # Fallback usando pydub
            try:
                from pydub import AudioSegment
                audio = AudioSegment.from_file(file_path)
                info['duration_seconds'] = len(audio) / 1000.0
                info['sample_rate'] = audio.frame_rate
                info['channels'] = audio.channels
                info['format'] = 'Unknown'
            except:
                pass
        
        return info 