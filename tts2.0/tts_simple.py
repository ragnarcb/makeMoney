#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interface Simples para TTS Moderno - Python 3.12+
Versão: 2.0 - Compatível com Python 3.12

Sistema de Text-to-Speech simplificado usando os engines mais modernos
"""

import os
import sys
from pathlib import Path

try:
    from coqui_tts_engine import ModernTTSEngine
except ImportError:
    print("[ERROR] Não foi possível importar o engine TTS moderno")
    print("[INFO] Certifique-se de que coqui_tts_engine.py está no mesmo diretório")
    sys.exit(1)

def clear_screen():
    """Limpa a tela do terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    """Exibe cabeçalho do programa"""
    print("=" * 60)
    print("    SISTEMA TTS MODERNO - Python 3.12+")
    print("    Text-to-Speech com Coqui TTS & RealtimeTTS")
    print("=" * 60)
    print()

def print_menu():
    """Exibe o menu principal"""
    print("OPÇÕES DISPONÍVEIS:")
    print()
    print("1. [TEXTO] Sintetizar texto simples")
    print("2. [CLONE] Clonar voz com áudio de referência")
    print("3. [LISTA] Ver modelos disponíveis")
    print("4. [INFO]  Informações do sistema")
    print("5. [TESTE] Teste rápido do sistema")
    print("6. [SAIR]  Encerrar programa")
    print()

def get_user_input(prompt, default=None):
    """Obtém entrada do usuário com valor padrão"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        return input(f"{prompt}: ").strip()

def synthesize_simple_text(engine):
    """Sintetiza texto simples"""
    print("\n--- SÍNTESE DE TEXTO SIMPLES ---\n")
    
    # Obter texto
    text = get_user_input("Digite o texto para sintetizar")
    if not text:
        print("[ERROR] Texto não pode estar vazio!")
        return
    
    # Obter idioma
    language = get_user_input("Idioma (pt/en/es/fr)", "pt")
    
    # Obter velocidade
    try:
        speed = float(get_user_input("Velocidade da fala (0.5-2.0)", "1.0"))
    except ValueError:
        speed = 1.0
    
    try:
        print(f"\n[INFO] Sintetizando texto...")
        print(f"[INFO] Texto: {text[:50]}{'...' if len(text) > 50 else ''}")
        print(f"[INFO] Idioma: {language}")
        print(f"[INFO] Velocidade: {speed}x")
        
        output_path = engine.synthesize_text(
            text=text,
            language=language,
            speed=speed
        )
        
        print(f"[OK] Áudio gerado: {output_path}")
        
        # Perguntar se quer reproduzir
        play = get_user_input("Reproduzir áudio agora? (s/n)", "s").lower()
        if play == 's':
            engine.play_audio(output_path)
            
    except Exception as e:
        print(f"[ERROR] Erro na síntese: {e}")

def clone_voice(engine):
    """Clona voz usando áudio de referência"""
    print("\n--- CLONAGEM DE VOZ ---\n")
    
    # Obter arquivo de referência
    reference_file = get_user_input("Caminho do áudio de referência (.wav)")
    if not reference_file:
        print("[ERROR] Arquivo de referência é obrigatório!")
        return
    
    if not os.path.exists(reference_file):
        print(f"[ERROR] Arquivo não encontrado: {reference_file}")
        return
    
    # Obter texto
    text = get_user_input("Digite o texto para falar com a voz clonada")
    if not text:
        print("[ERROR] Texto não pode estar vazio!")
        return
    
    try:
        print(f"\n[INFO] Clonando voz...")
        print(f"[INFO] Referência: {reference_file}")
        print(f"[INFO] Texto: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        output_path = engine.clone_voice(
            text=text,
            reference_audio=reference_file
        )
        
        print(f"[OK] Voz clonada: {output_path}")
        
        # Perguntar se quer reproduzir
        play = get_user_input("Reproduzir áudio agora? (s/n)", "s").lower()
        if play == 's':
            engine.play_audio(output_path)
            
    except Exception as e:
        print(f"[ERROR] Erro na clonagem: {e}")

def list_models(engine):
    """Lista modelos disponíveis"""
    print("\n--- MODELOS DISPONÍVEIS ---\n")
    
    try:
        models = engine.list_available_models()
        
        if models:
            print("Modelos TTS encontrados:")
            print()
            for i, model in enumerate(models[:20], 1):  # Primeiros 20
                print(f"  {i:2d}. {model}")
            
            if len(models) > 20:
                print(f"\n... e mais {len(models) - 20} modelos")
        else:
            print("Nenhum modelo encontrado ou listagem não suportada")
            
    except Exception as e:
        print(f"[ERROR] Erro ao listar modelos: {e}")

def show_system_info(engine):
    """Mostra informações do sistema"""
    print("\n--- INFORMAÇÕES DO SISTEMA ---\n")
    
    try:
        info = engine.get_system_info()
        
        print("Configuração atual:")
        print()
        for key, value in info.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")
            
    except Exception as e:
        print(f"[ERROR] Erro ao obter informações: {e}")

def quick_test(engine):
    """Teste rápido do sistema"""
    print("\n--- TESTE RÁPIDO ---\n")
    
    test_text = "Olá! Este é um teste rápido do sistema de síntese de voz."
    
    try:
        print(f"[INFO] Executando teste com texto: '{test_text}'")
        
        output_path = engine.synthesize_text(
            text=test_text,
            language="pt"
        )
        
        print(f"[OK] Teste concluído! Arquivo: {output_path}")
        
        # Reproduzir automaticamente
        print("[INFO] Reproduzindo áudio de teste...")
        engine.play_audio(output_path)
        
        print("[OK] Teste concluído com sucesso!")
        
    except Exception as e:
        print(f"[ERROR] Erro no teste: {e}")

def main():
    """Função principal"""
    clear_screen()
    print_header()
    
    # Inicializar engine TTS
    print("[INFO] Inicializando sistema TTS moderno...")
    print("[INFO] Isso pode demorar alguns segundos na primeira execução...")
    print()
    
    try:
        engine = ModernTTSEngine()
        print("[OK] Sistema TTS inicializado com sucesso!")
        print()
        
        # Loop principal
        while True:
            print_menu()
            
            choice = get_user_input("Escolha uma opção (1-6)", "1")
            
            if choice == "1":
                synthesize_simple_text(engine)
                
            elif choice == "2":
                clone_voice(engine)
                
            elif choice == "3":
                list_models(engine)
                
            elif choice == "4":
                show_system_info(engine)
                
            elif choice == "5":
                quick_test(engine)
                
            elif choice == "6":
                print("\n[INFO] Encerrando programa...")
                break
                
            else:
                print(f"\n[WARNING] Opção inválida: {choice}")
            
            print("\n" + "-" * 60)
            input("Pressione ENTER para continuar...")
            clear_screen()
            print_header()
    
    except KeyboardInterrupt:
        print("\n\n[INFO] Programa interrompido pelo usuário")
        
    except Exception as e:
        print(f"\n[ERROR] Erro ao inicializar sistema TTS: {e}")
        print("[INFO] Verifique se as dependências estão instaladas:")
        print("       pip install -r requirements.txt")
    
    finally:
        print("\n[INFO] Obrigado por usar o Sistema TTS Moderno!")

if __name__ == "__main__":
    main() 