#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correção para Problema de FFmpeg
Corrige a detecção e uso do FFmpeg no Windows
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def verificar_ffmpeg():
    """Verifica se ffmpeg está disponível"""
    print("=" * 50)
    print("VERIFICANDO FFMPEG")
    print("=" * 50)
    
    # Verificar se ffmpeg está no PATH
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        print(f"[OK] FFmpeg encontrado em: {ffmpeg_path}")
        
        # Testar execução
        try:
            result = subprocess.run(["ffmpeg", "-version"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                print(f"[OK] {version_line}")
                return True
            else:
                print(f"[ERROR] FFmpeg não executa: {result.stderr}")
                return False
        except Exception as e:
            print(f"[ERROR] Erro ao testar FFmpeg: {e}")
            return False
    else:
        print("[ERROR] FFmpeg não encontrado no PATH")
        return False

def converter_arquivo_com_ffmpeg_corrigido(arquivo_entrada, arquivo_saida):
    """Converte arquivo usando ffmpeg com tratamento correto do Windows"""
    print(f"\n[INFO] Convertendo com FFmpeg corrigido...")
    print(f"[INFO] Entrada: {arquivo_entrada}")
    print(f"[INFO] Saída: {arquivo_saida}")
    
    try:
        # Verificar se arquivo existe
        if not os.path.exists(arquivo_entrada):
            print(f"[ERROR] Arquivo não encontrado: {arquivo_entrada}")
            return False
        
        # Usar caminhos absolutos para evitar problemas
        entrada_abs = os.path.abspath(arquivo_entrada)
        saida_abs = os.path.abspath(arquivo_saida)
        
        print(f"[INFO] Entrada absoluta: {entrada_abs}")
        print(f"[INFO] Saída absoluta: {saida_abs}")
        
        # Comando ffmpeg com parâmetros específicos para Windows
        cmd = [
            "ffmpeg",
            "-i", entrada_abs,          # Arquivo de entrada
            "-ar", "22050",             # Sample rate 22050 Hz
            "-ac", "1",                 # Mono (1 canal)
            "-acodec", "pcm_s16le",     # Codec PCM 16-bit
            "-f", "wav",                # Formato WAV
            "-y",                       # Sobrescrever arquivo
            saida_abs                   # Arquivo de saída
        ]
        
        print(f"[CMD] {' '.join(cmd)}")
        
        # Executar comando
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            if os.path.exists(saida_abs):
                tamanho = os.path.getsize(saida_abs)
                print(f"[OK] Conversão bem-sucedida!")
                print(f"[INFO] Arquivo gerado: {arquivo_saida} ({tamanho} bytes)")
                return True
            else:
                print("[ERROR] Comando executou mas arquivo não foi criado")
                return False
        else:
            print(f"[ERROR] FFmpeg falhou:")
            print(f"[STDOUT] {result.stdout}")
            print(f"[STDERR] {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("[ERROR] FFmpeg demorou muito (timeout)")
        return False
    except Exception as e:
        print(f"[ERROR] Erro na conversão: {e}")
        return False

def verificar_tipo_arquivo(arquivo):
    """Verifica informações sobre o arquivo"""
    print(f"\n[INFO] Analisando arquivo: {arquivo}")
    
    if not os.path.exists(arquivo):
        print("[ERROR] Arquivo não existe")
        return False
    
    tamanho = os.path.getsize(arquivo)
    print(f"[INFO] Tamanho: {tamanho:,} bytes ({tamanho/1024:.1f} KB)")
    
    # Tentar usar ffprobe para verificar formato
    try:
        cmd = [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            arquivo
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("[OK] Arquivo reconhecido pelo ffprobe")
            # Exibir informações básicas
            output = result.stdout
            if "duration" in output:
                print("[INFO] Arquivo contém informações de duração")
            if "audio" in output:
                print("[INFO] Contém stream de áudio")
            return True
        else:
            print(f"[WARNING] ffprobe falhou: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"[WARNING] Erro ao usar ffprobe: {e}")
        return False

def tentar_conversao_multipla(arquivo_original):
    """Tenta várias estratégias de conversão"""
    print("\n" + "=" * 50)
    print("CONVERSÃO MÚLTIPLA COM FFMPEG")
    print("=" * 50)
    
    arquivo_saida = "voz_referencia_convertida_ffmpeg.wav"
    
    # Remover arquivo de saída se existir
    if os.path.exists(arquivo_saida):
        try:
            os.remove(arquivo_saida)
            print(f"[INFO] Arquivo anterior removido: {arquivo_saida}")
        except:
            pass
    
    # Estratégia 1: Conversão direta
    print("\n[INFO] Tentativa 1: Conversão direta")
    if converter_arquivo_com_ffmpeg_corrigido(arquivo_original, arquivo_saida):
        print("[OK] Conversão direta funcionou!")
        return arquivo_saida
    
    # Estratégia 2: Conversão com re-encoding forçado
    print("\n[INFO] Tentativa 2: Re-encoding completo")
    try:
        cmd = [
            "ffmpeg",
            "-i", os.path.abspath(arquivo_original),
            "-ar", "22050",
            "-ac", "1",
            "-acodec", "pcm_s16le",
            "-f", "wav",
            "-vn",                      # Sem vídeo
            "-sn",                      # Sem legendas
            "-y",
            os.path.abspath(arquivo_saida)
        ]
        
        print(f"[CMD] {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0 and os.path.exists(arquivo_saida):
            tamanho = os.path.getsize(arquivo_saida)
            print(f"[OK] Re-encoding funcionou! ({tamanho} bytes)")
            return arquivo_saida
        else:
            print(f"[WARNING] Re-encoding falhou: {result.stderr}")
    except Exception as e:
        print(f"[WARNING] Erro no re-encoding: {e}")
    
    # Estratégia 3: Conversão em duas etapas
    print("\n[INFO] Tentativa 3: Conversão em duas etapas")
    try:
        # Primeiro converter para formato intermediário
        temp_file = "temp_intermediario.wav"
        
        cmd1 = [
            "ffmpeg",
            "-i", os.path.abspath(arquivo_original),
            "-acodec", "pcm_s16le",
            "-y",
            os.path.abspath(temp_file)
        ]
        
        result1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=60)
        
        if result1.returncode == 0 and os.path.exists(temp_file):
            print("[INFO] Primeira etapa OK - convertendo para formato final")
            
            cmd2 = [
                "ffmpeg",
                "-i", os.path.abspath(temp_file),
                "-ar", "22050",
                "-ac", "1",
                "-y",
                os.path.abspath(arquivo_saida)
            ]
            
            result2 = subprocess.run(cmd2, capture_output=True, text=True, timeout=60)
            
            # Limpar arquivo temporário
            try:
                os.remove(temp_file)
            except:
                pass
            
            if result2.returncode == 0 and os.path.exists(arquivo_saida):
                tamanho = os.path.getsize(arquivo_saida)
                print(f"[OK] Conversão em duas etapas funcionou! ({tamanho} bytes)")
                return arquivo_saida
            else:
                print(f"[WARNING] Segunda etapa falhou: {result2.stderr}")
        else:
            print(f"[WARNING] Primeira etapa falhou: {result1.stderr}")
            
    except Exception as e:
        print(f"[WARNING] Erro na conversão duas etapas: {e}")
    
    print("[ERROR] Todas as estratégias de conversão falharam")
    return None

def main():
    """Função principal"""
    print("=" * 60)
    print("    CORREÇÃO FFMPEG PARA TTS")
    print("=" * 60)
    
    # Verificar ffmpeg
    if not verificar_ffmpeg():
        print("\n[ERROR] FFmpeg não está funcionando corretamente")
        input("Pressione ENTER para continuar...")
        return False
    
    # Verificar arquivo original
    arquivo_original = "Vídeo sem título ‐ Feito com o Clipchamp.wav"
    
    if not os.path.exists(arquivo_original):
        print(f"\n[ERROR] Arquivo não encontrado: {arquivo_original}")
        input("Pressione ENTER para continuar...")
        return False
    
    # Verificar tipo do arquivo
    verificar_tipo_arquivo(arquivo_original)
    
    # Tentar conversão
    arquivo_convertido = tentar_conversao_multipla(arquivo_original)
    
    if arquivo_convertido:
        print(f"\n[SUCESSO] ✅ Arquivo convertido: {arquivo_convertido}")
        print("\nAgora você pode usar o sistema TTS:")
        print("1. O arquivo convertido será detectado automaticamente")
        print("2. Execute: python usar_minha_voz.py")
        print("3. Escolha opção 1 (clonagem avançada)")
        
        # Testar o arquivo convertido
        print(f"\n[INFO] Testando arquivo convertido...")
        if verificar_tipo_arquivo(arquivo_convertido):
            print("[OK] Arquivo convertido é válido!")
        else:
            print("[WARNING] Arquivo convertido pode ter problemas")
        
        return True
    else:
        print("\n[FALHA] ❌ Não foi possível converter o arquivo")
        print("\nPossíveis causas:")
        print("- Arquivo pode estar corrompido")
        print("- Formato não suportado pelo FFmpeg")
        print("- Problemas de permissão")
        return False

if __name__ == "__main__":
    try:
        sucesso = main()
        print("\n" + "=" * 60)
        input("Pressione ENTER para continuar...")
        sys.exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        print("\n\n[INFO] Operação cancelada")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Erro inesperado: {e}")
        input("Pressione ENTER para continuar...")
        sys.exit(1) 