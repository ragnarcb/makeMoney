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
                is_valid, msg = self.validate_audio_file(output_file)
                if is_valid:
                    print(f"[OK] Conversão ffmpeg bem-sucedida: {msg}")
                    return True
                else:
                    print(f"[ERROR] Arquivo convertido inválido: {msg}")
                    return False
            else:
                print(f"[ERROR] FFmpeg falhou: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("[ERROR] FFmpeg timeout")
            return False
        except Exception as e:
            print(f"[ERROR] Erro no ffmpeg: {e}")
            return False
    
    def convert_audio(self, input_file: str, output_file: str) -> Tuple[bool, Optional[str]]:
        """
        Converte áudio usando o melhor método disponível
        
        Args:
            input_file: Arquivo de entrada
            output_file: Arquivo de saída
            
        Returns:
            (success, output_path)
        """
        # Verificar arquivo de entrada
        if not os.path.exists(input_file):
            return False, None
        
        # Criar diretório de saída se necessário
        output_dir = os.path.dirname(output_file)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # Tentar métodos em ordem de preferência
        methods = [
            ("pydub", self.convert_with_pydub),
            ("soundfile", self.convert_with_soundfile),
            ("ffmpeg", self.convert_with_ffmpeg)
        ]
        
        for method_name, method_func in methods:
            try:
                if method_func(input_file, output_file):
                    return True, output_file
            except Exception as e:
                print(f"[WARNING] Método {method_name} falhou: {e}")
                continue
        
        print("[ERROR] Todos os métodos de conversão falharam")
        return False, None
    
    def prepare_reference_audio(self, reference_file: str) -> Tuple[bool, Optional[str]]:
        """
        Prepara áudio de referência para clonagem de voz
        
        Args:
            reference_file: Arquivo de áudio de referência
            
        Returns:
            (success, prepared_file_path)
        """
        if not os.path.exists(reference_file):
            print(f"[ERROR] Arquivo de referência não encontrado: {reference_file}")
            return False, None
        
        # Verificar se já está no formato correto
        file_ext = Path(reference_file).suffix.lower()
        if file_ext == '.wav':
            # Verificar se já está no formato correto
            try:
                import soundfile as sf
                data, sr = sf.read(reference_file)
                if sr == self.sample_rate and data.shape[1] == self.channels if len(data.shape) > 1 else True:
                    print(f"[INFO] Arquivo já está no formato correto: {reference_file}")
                    return True, reference_file
            except:
                pass
        
        # Converter para formato correto
        output_file = str(Path(reference_file).with_suffix('.wav'))
        
        print(f"[INFO] Preparando áudio de referência: {reference_file}")
        success, converted_file = self.convert_audio(reference_file, output_file)
        
        if success:
            print(f"[OK] Áudio de referência preparado: {converted_file}")
            return True, converted_file
        else:
            print(f"[ERROR] Falha ao preparar áudio de referência: {reference_file}")
            return False, None
    
    def get_audio_info(self, file_path: str) -> Dict[str, Any]:
        """
        Obtém informações sobre um arquivo de áudio
        
        Args:
            file_path: Caminho para o arquivo
            
        Returns:
            Dicionário com informações do áudio
        """
        info = {
            'file_path': file_path,
            'exists': os.path.exists(file_path),
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0
        }
        
        if not info['exists']:
            return info
        
        # Tentar obter informações técnicas
        try:
            import soundfile as sf
            data, sr = sf.read(file_path)
            info.update({
                'sample_rate': sr,
                'channels': data.shape[1] if len(data.shape) > 1 else 1,
                'duration_seconds': len(data) / sr,
                'duration_ms': (len(data) / sr) * 1000
            })
        except:
            info['error'] = "Não foi possível ler informações técnicas"
        
        return info 