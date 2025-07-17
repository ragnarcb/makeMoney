#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo prático de uso do sistema TTS
Demonstra diferentes funcionalidades disponíveis
"""

import sys
import time
from pathlib import Path

# Adicionar o diretório atual ao path
sys.path.append(str(Path(__file__).parent))

try:
    from coqui_tts_engine import CoquiTTSEngine
except ImportError:
    print("[ERROR] Não foi possível importar o engine TTS")
    print("[INFO] Execute primeiro: python install_tts.py")
    sys.exit(1)


def exemplo_basico():
    """Exemplo básico de TTS"""
    print("\n" + "="*50)
    print("EXEMPLO 1: TTS BÁSICO")
    print("="*50)
    
    # Criar engine
    engine = CoquiTTSEngine(output_dir="exemplos_audio")
    
    # Carregar modelo português
    print("[INFO] Carregando modelo português...")
    if not engine.load_model(language="pt"):
        print("[ERROR] Falha ao carregar modelo")
        return
    
    # Texto de exemplo
    texto = """
    Olá! Este é um exemplo prático do sistema TTS usando Coqui AI.
    O texto está sendo convertido em fala de forma automática.
    Você pode usar este sistema para criar narrações, 
    assistentes virtuais, audiobooks e muito mais!
    """
    
    # Sintetizar
    print("[INFO] Sintetizando texto...")
    resultado = engine.synthesize_text(
        text=texto.strip(),
        output_filename="exemplo_basico.wav"
    )
    
    if resultado:
        print(f"[OK] Áudio salvo: {resultado}")
        
        # Reproduzir se possível
        reproduzir = input("Reproduzir áudio? (s/N): ").strip().lower() == 's'
        if reproduzir:
            engine.play_audio(resultado)
    
    return engine


def exemplo_multiplos_idiomas(engine):
    """Exemplo com múltiplos idiomas"""
    print("\n" + "="*50)
    print("EXEMPLO 2: MÚLTIPLOS IDIOMAS")
    print("="*50)
    
    # Textos em diferentes idiomas
    textos = {
        'pt': "Olá! Como você está hoje?",
        'en': "Hello! How are you today?",
        'es': "¡Hola! ¿Cómo estás hoy?",
        'fr': "Bonjour! Comment allez-vous aujourd'hui?"
    }
    
    for idioma, texto in textos.items():
        print(f"\n[INFO] Processando {idioma.upper()}: {texto}")
        
        # Carregar modelo para o idioma
        if engine.load_model(language=idioma):
            resultado = engine.synthesize_text(
                text=texto,
                output_filename=f"exemplo_{idioma}.wav"
            )
            
            if resultado:
                print(f"[OK] Áudio {idioma} salvo: {resultado.name}")
        else:
            print(f"[WARNING] Não foi possível carregar modelo para {idioma}")


def exemplo_voice_cloning(engine):
    """Exemplo de voice cloning"""
    print("\n" + "="*50)
    print("EXEMPLO 3: VOICE CLONING")
    print("="*50)
    
    print("[INFO] Para voice cloning, você precisa de:")
    print("- Arquivo WAV com 3-10 segundos de voz de referência")
    print("- Áudio limpo e claro")
    print()
    
    # Verificar se existe arquivo de exemplo
    arquivo_referencia = input("Caminho do arquivo WAV de referência (ou Enter para pular): ").strip()
    
    if not arquivo_referencia:
        print("[INFO] Pulando exemplo de voice cloning")
        return
    
    if not Path(arquivo_referencia).exists():
        print(f"[ERROR] Arquivo não encontrado: {arquivo_referencia}")
        return
    
    # Carregar modelo XTTS para voice cloning
    print("[INFO] Carregando modelo XTTS para voice cloning...")
    if not engine.load_model('tts_models/multilingual/multi-dataset/xtts_v2'):
        print("[ERROR] Falha ao carregar modelo XTTS")
        return
    
    # Texto para clonar
    texto_clone = """
    Esta é uma demonstração de clonagem de voz.
    O sistema está usando sua voz de referência 
    para gerar este áudio com uma voz similar.
    Incrível, não é mesmo?
    """
    
    # Executar voice cloning
    print("[INFO] Executando voice cloning...")
    resultado = engine.voice_cloning(
        text=texto_clone.strip(),
        speaker_wav_path=arquivo_referencia,
        output_filename="exemplo_voice_clone.wav",
        language="pt"
    )
    
    if resultado:
        print(f"[OK] Voice cloning concluído: {resultado}")
        
        reproduzir = input("Reproduzir resultado? (s/N): ").strip().lower() == 's'
        if reproduzir:
            engine.play_audio(resultado)


def exemplo_lote(engine):
    """Exemplo de processamento em lote"""
    print("\n" + "="*50)
    print("EXEMPLO 4: PROCESSAMENTO EM LOTE")
    print("="*50)
    
    # Lista de textos para processar
    textos_lote = [
        "Esta é a primeira frase do lote.",
        "Agora estamos processando a segunda frase.",
        "A terceira frase está sendo sintetizada.",
        "E finalmente, a quarta e última frase.",
        "Processamento em lote concluído com sucesso!"
    ]
    
    print(f"[INFO] Processando {len(textos_lote)} textos em lote...")
    
    # Carregar modelo português
    if not engine.load_model(language="pt"):
        print("[ERROR] Falha ao carregar modelo")
        return
    
    # Processar em lote
    resultados = engine.batch_synthesis(
        texts=textos_lote,
        prefix="lote_exemplo"
    )
    
    print(f"\n[OK] {len(resultados)} arquivos gerados")
    
    # Opção de reproduzir todos
    reproduzir_todos = input("Reproduzir todos os áudios? (s/N): ").strip().lower() == 's'
    
    if reproduzir_todos:
        for i, resultado in enumerate(resultados):
            print(f"\n[INFO] Reproduzindo {i+1}/{len(resultados)}: {resultado.name}")
            engine.play_audio(resultado)
            
            if i < len(resultados) - 1:  # Não pausar no último
                input("Pressione Enter para próximo...")


def exemplo_configuracoes_avancadas(engine):
    """Exemplo com configurações avançadas"""
    print("\n" + "="*50)
    print("EXEMPLO 5: CONFIGURAÇÕES AVANÇADAS")
    print("="*50)
    
    if not engine.load_model(language="pt"):
        print("[ERROR] Falha ao carregar modelo")
        return
    
    texto_base = "Esta é uma demonstração de diferentes configurações de velocidade."
    
    # Diferentes velocidades
    velocidades = [0.7, 1.0, 1.3, 1.6]
    
    for velocidade in velocidades:
        print(f"\n[INFO] Sintetizando com velocidade {velocidade}x...")
        
        resultado = engine.synthesize_text(
            text=f"Velocidade {velocidade}x. {texto_base}",
            output_filename=f"exemplo_velocidade_{velocidade}x.wav",
            speed=velocidade
        )
        
        if resultado:
            print(f"[OK] Áudio salvo: {resultado.name}")
    
    print("\n[INFO] Teste de configurações concluído!")
    print("[INFO] Compare os diferentes arquivos de áudio gerados")


def demonstracao_completa():
    """Executa demonstração completa do sistema"""
    print("="*60)
    print("DEMONSTRAÇÃO COMPLETA DO SISTEMA TTS")
    print("="*60)
    print()
    print("Esta demonstração mostrará todas as funcionalidades:")
    print("1. TTS Básico")
    print("2. Múltiplos Idiomas") 
    print("3. Voice Cloning")
    print("4. Processamento em Lote")
    print("5. Configurações Avançadas")
    print()
    
    continuar = input("Deseja continuar? (S/n): ").strip().lower() != 'n'
    if not continuar:
        print("[INFO] Demonstração cancelada")
        return
    
    try:
        # Exemplo 1: Básico
        engine = exemplo_basico()
        if not engine:
            return
        
        input("\nPressione Enter para continuar para o próximo exemplo...")
        
        # Exemplo 2: Múltiplos idiomas
        exemplo_multiplos_idiomas(engine)
        
        input("\nPressione Enter para continuar para o próximo exemplo...")
        
        # Exemplo 3: Voice cloning
        exemplo_voice_cloning(engine)
        
        input("\nPressione Enter para continuar para o próximo exemplo...")
        
        # Exemplo 4: Lote
        exemplo_lote(engine)
        
        input("\nPressione Enter para continuar para o próximo exemplo...")
        
        # Exemplo 5: Configurações avançadas
        exemplo_configuracoes_avancadas(engine)
        
        # Finalizar
        print("\n" + "="*60)
        print("DEMONSTRAÇÃO CONCLUÍDA!")
        print("="*60)
        print()
        print("Arquivos gerados:")
        output_dir = Path("exemplos_audio")
        if output_dir.exists():
            for arquivo in output_dir.glob("*.wav"):
                print(f"  - {arquivo}")
        
        print("\nO sistema TTS está pronto para uso!")
        print("Execute 'python tts_simple.py' para interface amigável")
        print("ou 'python coqui_tts_engine.py --help' para linha de comando")
        
    except KeyboardInterrupt:
        print("\n\n[INFO] Demonstração interrompida pelo usuário")
    except Exception as e:
        print(f"\n[ERROR] Erro durante demonstração: {e}")


def menu_exemplos():
    """Menu para escolher exemplos específicos"""
    while True:
        print("\n" + "="*40)
        print("EXEMPLOS PRÁTICOS TTS")
        print("="*40)
        print("1. TTS Básico")
        print("2. Múltiplos Idiomas")
        print("3. Voice Cloning")
        print("4. Processamento em Lote")
        print("5. Configurações Avançadas")
        print("6. Demonstração Completa")
        print("7. Sair")
        
        escolha = input("\nEscolha (1-7): ").strip()
        
        if escolha == '7':
            print("[INFO] Saindo...")
            break
        
        try:
            engine = CoquiTTSEngine(output_dir="exemplos_audio")
            
            if escolha == '1':
                exemplo_basico()
            elif escolha == '2':
                exemplo_multiplos_idiomas(engine)
            elif escolha == '3':
                exemplo_voice_cloning(engine)
            elif escolha == '4':
                exemplo_lote(engine)
            elif escolha == '5':
                exemplo_configuracoes_avancadas(engine)
            elif escolha == '6':
                demonstracao_completa()
                break
            else:
                print("[ERROR] Opção inválida")
                
        except KeyboardInterrupt:
            print("\n[INFO] Exemplo interrompido")
        except Exception as e:
            print(f"[ERROR] Erro no exemplo: {e}")


def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Exemplos práticos do sistema TTS")
    parser.add_argument("--demo", action="store_true", help="Executar demonstração completa")
    parser.add_argument("--exemplo", type=int, choices=[1,2,3,4,5], help="Executar exemplo específico")
    
    args = parser.parse_args()
    
    if args.demo:
        demonstracao_completa()
    elif args.exemplo:
        engine = CoquiTTSEngine(output_dir="exemplos_audio")
        if args.exemplo == 1:
            exemplo_basico()
        elif args.exemplo == 2:
            exemplo_multiplos_idiomas(engine)
        elif args.exemplo == 3:
            exemplo_voice_cloning(engine)
        elif args.exemplo == 4:
            exemplo_lote(engine)
        elif args.exemplo == 5:
            exemplo_configuracoes_avancadas(engine)
    else:
        menu_exemplos()


if __name__ == "__main__":
    main() 