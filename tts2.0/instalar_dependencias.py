#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Instalador de Dependências - Sistema TTS com Clonagem de Voz
Instala todas as dependências necessárias para Python 3.12+
"""

import subprocess
import sys
import os
from pathlib import Path

def executar_comando(comando, descricao):
    """Executa comando e mostra resultado"""
    print(f"\n[INFO] {descricao}...")
    print(f"[CMD] {comando}")
    
    try:
        result = subprocess.run(comando, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[OK] {descricao} - Sucesso!")
            if result.stdout.strip():
                print(f"[OUTPUT] {result.stdout.strip()}")
        else:
            print(f"[WARNING] {descricao} - Aviso:")
            if result.stderr.strip():
                print(f"[STDERR] {result.stderr.strip()}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"[ERROR] Erro em {descricao}: {e}")
        return False

def verificar_python():
    """Verifica versão do Python"""
    print("=" * 60)
    print("INSTALADOR SISTEMA TTS - CLONAGEM DE VOZ")
    print("=" * 60)
    
    versao = sys.version_info
    print(f"[INFO] Python {versao.major}.{versao.minor}.{versao.micro}")
    
    if versao.major < 3 or (versao.major == 3 and versao.minor < 9):
        print("[ERROR] Python 3.9+ necessário!")
        return False
    
    print("[OK] Versão do Python compatível")
    return True

def instalar_dependencias_basicas():
    """Instala dependências básicas"""
    print("\n" + "=" * 50)
    print("INSTALANDO DEPENDÊNCIAS BÁSICAS")
    print("=" * 50)
    
    # Atualizar pip
    executar_comando(
        f'"{sys.executable}" -m pip install --upgrade pip',
        "Atualizando pip"
    )
    
    # Dependências básicas
    deps_basicas = [
        "torch",
        "torchaudio", 
        "numpy",
        "scipy",
        "requests",
        "packaging"
    ]
    
    for dep in deps_basicas:
        executar_comando(
            f'"{sys.executable}" -m pip install "{dep}"',
            f"Instalando {dep}"
        )

def instalar_tts():
    """Instala Coqui TTS"""
    print("\n" + "=" * 50)
    print("INSTALANDO COQUI TTS")
    print("=" * 50)
    
    # Tentar versão mais recente primeiro
    sucesso = executar_comando(
        f'"{sys.executable}" -m pip install coqui-tts>=0.27.0',
        "Instalando Coqui TTS (versão nova)"
    )
    
    if not sucesso:
        print("[INFO] Tentando versão alternativa...")
        sucesso = executar_comando(
            f'"{sys.executable}" -m pip install TTS',
            "Instalando TTS (versão padrão)"
        )
    
    return sucesso

def instalar_audio():
    """Instala bibliotecas de áudio"""
    print("\n" + "=" * 50)
    print("INSTALANDO BIBLIOTECAS DE ÁUDIO")
    print("=" * 50)
    
    # Dependências de áudio
    deps_audio = [
        "pydub",
        "soundfile", 
        "librosa",
        "audioread",
        "resampy"
    ]
    
    for dep in deps_audio:
        executar_comando(
            f'"{sys.executable}" -m pip install "{dep}"',
            f"Instalando {dep}"
        )

def instalar_extras():
    """Instala dependências extras opcionais"""
    print("\n" + "=" * 50)
    print("INSTALANDO EXTRAS OPCIONAIS")
    print("=" * 50)
    
    # TTS alternativo
    executar_comando(
        f'"{sys.executable}" -m pip install pyttsx3',
        "Instalando pyttsx3 (TTS básico)"
    )
    
    # Reprodução de áudio
    executar_comando(
        f'"{sys.executable}" -m pip install pygame',
        "Instalando pygame (reprodução)"
    )
    
    executar_comando(
        f'"{sys.executable}" -m pip install playsound',
        "Instalando playsound (reprodução)"
    )

def testar_instalacao():
    """Testa se a instalação funcionou"""
    print("\n" + "=" * 50)
    print("TESTANDO INSTALAÇÃO")
    print("=" * 50)
    
    testes = [
        ("import torch", "PyTorch"),
        ("import numpy", "NumPy"), 
        ("import scipy", "SciPy"),
        ("from TTS.api import TTS", "Coqui TTS"),
        ("import pydub", "PyDub"),
        ("import soundfile", "SoundFile"),
        ("import pyttsx3", "pyttsx3")
    ]
    
    sucessos = 0
    for codigo, nome in testes:
        try:
            exec(codigo)
            print(f"[OK] {nome}")
            sucessos += 1
        except ImportError as e:
            print(f"[WARNING] {nome} - {e}")
        except Exception as e:
            print(f"[ERROR] {nome} - {e}")
    
    print(f"\n[INFO] {sucessos}/{len(testes)} bibliotecas funcionando")
    
    if sucessos >= 4:  # TTS + básicas
        print("[OK] Instalação suficiente para TTS básico!")
        return True
    else:
        print("[WARNING] Algumas bibliotecas faltando - pode haver limitações")
        return False

def main():
    """Função principal"""
    try:
        if not verificar_python():
            return False
        
        print("\n[INFO] Iniciando instalação das dependências...")
        print("[INFO] Isso pode demorar alguns minutos...")
        
        # Instalar em etapas
        instalar_dependencias_basicas()
        instalar_tts() 
        instalar_audio()
        instalar_extras()
        
        # Testar
        if testar_instalacao():
            print("\n" + "=" * 60)
            print("INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
            print("=" * 60)
            print("\nPróximos passos:")
            print("1. Execute: python usar_minha_voz.py")
            print("2. O sistema converterá automaticamente seu arquivo WAV")
            print("3. Digite o texto para síntese com sua voz")
            print("\nArquivo de referência: 'Vídeo sem título ‐ Feito com o Clipchamp.wav'")
            return True
        else:
            print("\n[WARNING] Instalação parcial - algumas funcionalidades podem não funcionar")
            return False
            
    except KeyboardInterrupt:
        print("\n[INFO] Instalação cancelada pelo usuário")
        return False
    except Exception as e:
        print(f"\n[ERROR] Erro na instalação: {e}")
        return False

if __name__ == "__main__":
    sucesso = main()
    
    print("\n" + "=" * 60)
    input("Pressione ENTER para continuar...")
    
    if sucesso:
        sys.exit(0)
    else:
        sys.exit(1) 