#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de instalação automática das dependências do sistema TTS
"""

import subprocess
import sys
import os
import shutil

def run_command(command, description, optional=False):
    """Executa um comando e reporta o resultado"""
    print(f"\n📦 {description}...")
    try:
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        if result.returncode == 0:
            print(f"✅ {description} - Sucesso")
            return True
        else:
            print(f"❌ {description} - Falhou")
            if result.stderr:
                print(f"Erro: {result.stderr}")
            if not optional:
                return False
            else:
                print("⚠️ Dependência opcional - continuando...")
                return True
    except Exception as e:
        print(f"❌ {description} - Erro: {e}")
        return False if not optional else True

def check_python_version():
    """Verifica se a versão do Python é adequada"""
    print("🐍 Verificando versão do Python...")
    version = sys.version_info
    
    if version.major >= 3 and version.minor >= 7:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requer Python 3.7+")
        return False

def check_ffmpeg():
    """Verifica se FFmpeg está instalado"""
    print("\n🎵 Verificando FFmpeg...")
    ffmpeg_path = shutil.which("ffmpeg")
    
    if ffmpeg_path:
        print(f"✅ FFmpeg encontrado em: {ffmpeg_path}")
        return True
    else:
        print("❌ FFmpeg não encontrado")
        print("💡 Instale o FFmpeg:")
        print("   Windows: Baixe de https://ffmpeg.org/")
        print("   Linux: sudo apt install ffmpeg")
        print("   macOS: brew install ffmpeg")
        return False

def install_basic_dependencies():
    """Instala dependências básicas"""
    print("\n📚 Instalando dependências básicas...")
    
    basic_packages = [
        "pydub",
        "soundfile", 
        "numpy",
        "pathlib"
    ]
    
    for package in basic_packages:
        success = run_command(f"pip install {package}", f"Instalando {package}")
        if not success:
            return False
    
    return True

def install_tts_engines():
    """Instala engines TTS"""
    print("\n🎤 Instalando engines TTS...")
    
    # pyttsx3 (básico, sempre tentar instalar)
    run_command("pip install pyttsx3", "pyttsx3 (TTS básico)")
    
    # Coqui TTS (opcional, mas recomendado)
    print("\n🔥 Tentando instalar Coqui TTS (recomendado para clonagem)...")
    coqui_success = run_command("pip install coqui-tts", "Coqui TTS", optional=True)
    
    if not coqui_success:
        print("⚠️ Coqui TTS falhou - isso é normal em alguns sistemas")
        print("💡 Você ainda pode usar pyttsx3 para TTS básico")
    
    # RealtimeTTS (muito opcional)
    print("\n⚡ Tentando instalar RealtimeTTS (opcional)...")
    run_command("pip install RealtimeTTS", "RealtimeTTS", optional=True)
    
    return True

def install_audio_processing():
    """Instala bibliotecas de processamento de áudio"""
    print("\n🎶 Instalando bibliotecas de processamento de áudio...")
    
    audio_packages = [
        "librosa",
        "scipy"
    ]
    
    for package in audio_packages:
        run_command(f"pip install {package}", f"Instalando {package}", optional=True)
    
    return True

def create_directories():
    """Cria diretórios necessários"""
    print("\n📁 Criando diretórios...")
    
    directories = [
        "generated_audio",
        "temp_audio"
    ]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Diretório criado: {directory}")
        except Exception as e:
            print(f"❌ Erro ao criar {directory}: {e}")
    
    return True

def test_installation():
    """Testa a instalação"""
    print("\n🧪 Testando instalação...")
    
    try:
        # Testar imports básicos
        import pydub
        print("✅ pydub")
    except ImportError:
        print("❌ pydub não disponível")
    
    try:
        import soundfile
        print("✅ soundfile")
    except ImportError:
        print("❌ soundfile não disponível")
    
    try:
        import pyttsx3
        print("✅ pyttsx3")
    except ImportError:
        print("❌ pyttsx3 não disponível")
    
    try:
        from TTS.api import TTS
        print("✅ Coqui TTS")
    except ImportError:
        print("⚠️ Coqui TTS não disponível (opcional)")
    
    try:
        from RealtimeTTS import TextToAudioStream
        print("✅ RealtimeTTS")
    except ImportError:
        print("⚠️ RealtimeTTS não disponível (opcional)")
    
    # Testar sistema completo se possível
    try:
        print("\n🔍 Testando sistema completo...")
        import test_system
        print("✅ Sistema de teste disponível")
        print("💡 Execute: python test_system.py")
    except ImportError:
        print("⚠️ Sistema de teste não encontrado")
    
    return True

def main():
    """Função principal de instalação"""
    print("="*60)
    print("🚀 INSTALADOR DO SISTEMA TTS MODULAR")
    print("="*60)
    print("Este script irá instalar todas as dependências necessárias")
    print("para o sistema de geração de vozes por personagem.")
    print()
    
    # Verificar Python
    if not check_python_version():
        print("\n❌ Versão do Python incompatível")
        return 1
    
    # Verificar FFmpeg
    ffmpeg_ok = check_ffmpeg()
    if not ffmpeg_ok:
        response = input("\nFFmpeg não encontrado. Continuar mesmo assim? (s/n): ")
        if response.lower() != 's':
            print("❌ Instalação cancelada")
            return 1
    
    # Instalar dependências
    steps = [
        ("Dependências básicas", install_basic_dependencies),
        ("Engines TTS", install_tts_engines),
        ("Processamento de áudio", install_audio_processing),
        ("Criação de diretórios", create_directories),
        ("Teste da instalação", test_installation)
    ]
    
    print(f"\n📋 Executando {len(steps)} etapas de instalação...")
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        try:
            success = step_func()
            if success:
                print(f"✅ {step_name} - Concluído")
            else:
                print(f"❌ {step_name} - Falhou")
                failed_steps.append(step_name)
        except Exception as e:
            print(f"❌ {step_name} - Erro: {e}")
            failed_steps.append(step_name)
    
    # Relatório final
    print("\n" + "="*60)
    print("📊 RELATÓRIO DE INSTALAÇÃO")
    print("="*60)
    
    if not failed_steps:
        print("🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO!")
        print("\n✅ Sistema pronto para uso")
        print("\n💡 Próximos passos:")
        print("   python test_system.py          # Testar sistema")
        print("   python main.py --help          # Ver opções")
        print("   python main.py --validate-only # Validar configuração")
        print("   python main.py                 # Processar JSON padrão")
        return 0
    else:
        print(f"⚠️ INSTALAÇÃO PARCIAL - {len(failed_steps)} etapa(s) falharam:")
        for step in failed_steps:
            print(f"   - {step}")
        
        print("\n🔧 Soluções possíveis:")
        print("   - Execute novamente como administrador")
        print("   - Verifique conexão com internet")
        print("   - Instale FFmpeg manualmente")
        print("   - Use: pip install --user <pacote>")
        
        print("\n⚠️ Você ainda pode usar funcionalidades básicas")
        print("   python test_system.py  # Ver o que funciona")
        
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Instalação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
        sys.exit(1) 