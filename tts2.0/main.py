#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script principal de automação para geração de vozes por personagem com múltiplas vozes
"""

import sys
import argparse
import json
from pathlib import Path

# Garantir que podemos importar os módulos locais
try:
    from character_voice_generator import CharacterVoiceGenerator
    from config import PATHS, find_file_in_project, get_available_voice_files
except ImportError as e:
    # Se não conseguir importar, tentar adicionar o diretório atual ao path
    import os
    current_dir = Path(__file__).parent.absolute()
    sys.path.insert(0, str(current_dir))
    
    try:
        from character_voice_generator import CharacterVoiceGenerator
        from config import PATHS, find_file_in_project, get_available_voice_files
    except ImportError:
        print(f"[ERROR] Não foi possível importar módulos necessários: {e}")
        print(f"[INFO] Certifique-se de estar executando da pasta tts2.0 ou que todos os arquivos estão presentes")
        sys.exit(1)

def main():
    """Função principal de automação"""
    parser = argparse.ArgumentParser(
        description='Geração automática de vozes por personagem com suporte a múltiplas vozes',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Processar arquivo JSON padrão
  python main.py

  # Especificar arquivo JSON personalizado
  python main.py --json-file conversa.json

  # Usar voz padrão específica
  python main.py --default-voice minha_voz.wav

  # Mapear vozes específicas por personagem
  python main.py --voice-map aluno:voz_aluno.wav professora:voz_professora.wav

  # Gerar sem clonagem de voz
  python main.py --no-voice-cloning

  # Gerar apenas um personagem específico
  python main.py --character aluno

  # Gerar texto personalizado com voz específica
  python main.py --text "Olá mundo" --output teste.wav --voice voz_especifica.wav

  # Listar vozes disponíveis
  python main.py --list-voices

  # Modo silencioso
  python main.py --quiet

  # Relatório detalhado
  python main.py --verbose --export-report relatorio.json
        """
    )
    
    # Argumentos principais
    parser.add_argument(
        '--json-file', '-j',
        default='exemplo-mensagens.json',
        help='Arquivo JSON com mensagens (padrão: exemplo-mensagens.json)'
    )
    
    parser.add_argument(
        '--default-voice', '-dv',
        default=None,
        help=f'Arquivo de voz padrão (padrão: {PATHS["reference_audio"]})'
    )
    
    parser.add_argument(
        '--output-dir', '-o',
        default=None,
        help=f'Diretório de saída (padrão: {PATHS["output_dir"]})'
    )
    
    # Configuração de múltiplas vozes
    parser.add_argument(
        '--voice-map', '-vm',
        nargs='*',
        help='Mapear vozes por personagem: personagem:arquivo.wav (ex: aluno:voz_aluno.wav)'
    )
    
    parser.add_argument(
        '--no-auto-detect',
        action='store_true',
        help='Desabilitar detecção automática de vozes'
    )
    
    parser.add_argument(
        '--list-voices',
        action='store_true',
        help='Listar todas as vozes disponíveis e sair'
    )
    
    # Opções de geração
    parser.add_argument(
        '--character', '-c',
        help='Gerar apenas para um personagem específico (ID do personagem)'
    )
    
    parser.add_argument(
        '--no-voice-cloning',
        action='store_true',
        help='Desabilitar clonagem de voz (usar TTS básico)'
    )
    
    # Modo de texto único
    parser.add_argument(
        '--text', '-t',
        help='Gerar áudio para texto específico (modo single)'
    )
    
    parser.add_argument(
        '--output', '-out',
        help='Arquivo de saída para modo de texto único'
    )
    
    parser.add_argument(
        '--voice', '-v',
        help='Arquivo de voz específico para modo de texto único'
    )
    
    # Opções de relatório
    parser.add_argument(
        '--export-report',
        help='Exportar relatório de geração para arquivo JSON'
    )
    
    parser.add_argument(
        '--list-characters',
        action='store_true',
        help='Listar personagens disponíveis no JSON e sair'
    )
    
    parser.add_argument(
        '--validate-only',
        action='store_true',
        help='Apenas validar configuração do sistema e sair'
    )
    
    parser.add_argument(
        '--show-voice-mapping',
        action='store_true',
        help='Mostrar mapeamento atual de vozes e sair'
    )
    
    # Opções de output
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Modo silencioso (menos output)'
    )
    
    parser.add_argument(
        '--verbose', '-vb',
        action='store_true',
        help='Modo verboso (mais detalhes)'
    )
    
    args = parser.parse_args()
    
    # Configurar nível de output
    if args.quiet:
        import logging
        logging.basicConfig(level=logging.ERROR)
    elif args.verbose:
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    # Processar mapeamento de vozes
    voice_mapping = {}
    if args.voice_map:
        for mapping in args.voice_map:
            if ':' in mapping:
                char_id, voice_file = mapping.split(':', 1)
                voice_mapping[char_id.strip()] = voice_file.strip()
            else:
                print(f"[WARNING] Formato de mapeamento inválido: {mapping}")
                print("[INFO] Use o formato: personagem:arquivo.wav")
    
    # Inicializar gerador
    try:
        print("="*60)
        print("AUTOMAÇÃO DE GERAÇÃO DE VOZES COM MÚLTIPLAS VOZES")
        print("="*60)
        
        # Modo de listar vozes disponíveis
        if args.list_voices:
            return handle_list_voices_mode()
        
        generator = CharacterVoiceGenerator(
            default_reference_audio=args.default_voice,
            output_base_dir=args.output_dir,
            voice_mapping=voice_mapping,
            auto_detect_voices=not args.no_auto_detect
        )
        
        # Modo de validação apenas
        if args.validate_only:
            print("\n[INFO] Validando configuração do sistema...")
            if generator.validate_setup():
                print("[OK] Sistema pronto para uso")
                return 0
            else:
                print("[ERROR] Sistema com problemas")
                return 1
        
        # Modo de texto único
        if args.text:
            return handle_single_text_mode(generator, args)
        
        # Carregar mensagens JSON
        if not generator.load_messages_from_json(args.json_file):
            print(f"[ERROR] Falha ao carregar {args.json_file}")
            return 1
        
        # Modo de listar personagens
        if args.list_characters:
            return handle_list_characters_mode(generator)
        
        # Modo de mostrar mapeamento de vozes
        if args.show_voice_mapping:
            return handle_show_voice_mapping_mode(generator)
        
        # Validar configuração
        if not generator.validate_setup():
            print("[ERROR] Sistema não está configurado corretamente")
            return 1
        
        # Executar geração
        use_voice_cloning = not args.no_voice_cloning
        
        if args.character:
            return handle_single_character_mode(generator, args.character, use_voice_cloning)
        else:
            return handle_all_characters_mode(generator, use_voice_cloning, args)
        
    except KeyboardInterrupt:
        print("\n\n[INFO] Operação cancelada pelo usuário")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Erro inesperado: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

def handle_list_voices_mode():
    """Lida com modo de listagem de vozes disponíveis"""
    print(f"\n🎤 VOZES DISPONÍVEIS NO SISTEMA")
    print(f"{'='*40}")
    
    available_voices = get_available_voice_files()
    
    if not available_voices:
        print("❌ Nenhuma voz encontrada")
        print("\n💡 Coloque arquivos de voz nos seguintes locais:")
        print("  - tts2.0/")
        print("  - tts2.0/voices/")
        print("  - ./")
        print("  - ./voices/")
        print("\n🎯 Nomeação automática de vozes:")
        print("  - voz_personagem.wav")
        print("  - voice_personagem.wav")
        print("  - personagem_voice.wav")
        print("  - personagem.wav")
        return 1
    
    print(f"Total: {len(available_voices)} arquivo(s)")
    print("-" * 40)
    
    for filename, path in available_voices.items():
        try:
            file_size = Path(path).stat().st_size / 1024 / 1024  # MB
            print(f"📄 {filename}")
            print(f"   📍 {path}")
            print(f"   📊 {file_size:.1f} MB")
            print("-" * 20)
        except Exception as e:
            print(f"📄 {filename} (erro ao ler: {e})")
    
    print("\n💡 Uso:")
    print("  python main.py --voice-map aluno:voz_aluno.wav professora:voz_professora.wav")
    print("  python main.py --default-voice voz_padrao.wav")
    
    return 0

def handle_single_text_mode(generator, args):
    """Lida com modo de texto único"""
    print(f"\n[INFO] Modo de texto único")
    print(f"[INFO] Texto: {args.text}")
    
    # Definir arquivo de saída
    output_file = args.output or "audio_personalizado.wav"
    
    # Gerar áudio
    use_voice_cloning = not args.no_voice_cloning
    success = generator.generate_single_audio(
        text=args.text,
        output_file=output_file,
        character_voice=args.voice,
        use_voice_cloning=use_voice_cloning
    )
    
    if success:
        print(f"[OK] Áudio gerado: {output_file}")
        return 0
    else:
        print("[ERROR] Falha na geração")
        return 1

def handle_list_characters_mode(generator):
    """Lida com modo de listagem de personagens"""
    print(f"\n[INFO] Personagens disponíveis:")
    
    characters = generator.get_characters()
    if not characters:
        print("[WARNING] Nenhum personagem encontrado")
        return 1
    
    print(f"\nTotal de personagens: {len(characters)}")
    print("-" * 40)
    
    for char_id, character in characters.items():
        voice_status = "🎤" if character.voice_file else "❌"
        voice_name = Path(character.voice_file).name if character.voice_file else "Nenhuma"
        
        print(f"ID: {char_id}")
        print(f"Nome: {character.name}")
        print(f"Mensagens: {character.audio_count}")
        print(f"Voz: {voice_status} {voice_name}")
        print("-" * 20)
    
    return 0

def handle_show_voice_mapping_mode(generator):
    """Lida com modo de mostrar mapeamento de vozes"""
    print(f"\n📋 MAPEAMENTO ATUAL DE VOZES")
    print(f"{'='*40}")
    
    voice_info = generator.get_character_voice_info()
    
    if not voice_info:
        print("❌ Nenhum personagem carregado")
        return 1
    
    for char_id, info in voice_info.items():
        voice_status = "✅" if info['voice_available'] else "❌"
        voice_name = info.get('voice_filename', 'Nenhuma')
        
        print(f"{voice_status} {info['character_name']} ({char_id})")
        print(f"   Voz: {voice_name}")
        
        if info['voice_available']:
            voice_size = info.get('voice_size', 0) / 1024 / 1024  # MB
            print(f"   Tamanho: {voice_size:.1f} MB")
        
        print("-" * 20)
    
    # Mostrar vozes não utilizadas
    available_voices = get_available_voice_files()
    used_voices = set()
    for info in voice_info.values():
        if info.get('voice_filename'):
            used_voices.add(info['voice_filename'])
    
    unused_voices = set(available_voices.keys()) - used_voices
    if unused_voices:
        print(f"\n⚠️ Vozes disponíveis mas não utilizadas:")
        for voice in unused_voices:
            print(f"   🎤 {voice}")
        print("\n💡 Dica: Use --voice-map para mapear vozes aos personagens")
    
    return 0

def handle_single_character_mode(generator, character_id, use_voice_cloning):
    """Lida com modo de personagem único"""
    print(f"\n[INFO] Modo de personagem único: {character_id}")
    
    characters = generator.get_characters()
    if character_id not in characters:
        print(f"[ERROR] Personagem '{character_id}' não encontrado")
        print(f"[INFO] Personagens disponíveis: {list(characters.keys())}")
        return 1
    
    # Mostrar informações da voz do personagem
    voice_info = generator.get_character_voice_info()
    char_voice_info = voice_info.get(character_id, {})
    
    if char_voice_info.get('voice_available'):
        print(f"[INFO] Voz do personagem: {char_voice_info.get('voice_filename')}")
    else:
        print(f"[WARNING] Personagem sem voz específica - usando padrão ou TTS básico")
    
    # Gerar áudios para o personagem
    sucessos, falhas = generator.generate_audio_for_character(character_id, use_voice_cloning)
    
    # Relatório
    character = characters[character_id]
    total = sucessos + falhas
    taxa = (sucessos / total * 100) if total > 0 else 0
    
    print(f"\n[SUMMARY] {character.name}:")
    print(f"  Sucessos: {sucessos}")
    print(f"  Falhas: {falhas}")
    print(f"  Taxa de sucesso: {taxa:.1f}%")
    
    return 0 if falhas == 0 else 1

def handle_all_characters_mode(generator, use_voice_cloning, args):
    """Lida com modo de todos os personagens"""
    print(f"\n[INFO] Modo de todos os personagens")
    
    # Gerar para todos
    stats = generator.generate_all_characters_audio(use_voice_cloning)
    
    # Exportar relatório se solicitado
    if args.export_report:
        export_detailed_report(generator, stats, args.export_report)
    
    # Retornar código baseado no sucesso
    return 0 if stats.failed_generations == 0 else 1

def export_detailed_report(generator, stats, output_file):
    """Exporta relatório detalhado em JSON"""
    try:
        import datetime
        
        voice_info = generator.get_character_voice_info()
        engines_info = generator.tts_manager.get_engines_info()
        
        report = {
            'timestamp': datetime.datetime.now().isoformat(),
            'system_info': {
                'multiple_voices_enabled': True,
                'voice_auto_detection': generator.auto_detect_voices,
                'available_engines': generator.tts_manager.get_available_engines(),
                'engines_details': engines_info
            },
            'voice_mapping': {
                char_id: {
                    'character_name': info['character_name'],
                    'voice_file': info.get('voice_filename', None),
                    'voice_available': info['voice_available'],
                    'voice_size_mb': info.get('voice_size', 0) / 1024 / 1024 if info.get('voice_size') else 0
                }
                for char_id, info in voice_info.items()
            },
            'statistics': {
                'total_messages': stats.total_messages,
                'total_characters': stats.total_characters,
                'successful_generations': stats.successful_generations,
                'failed_generations': stats.failed_generations,
                'success_rate': stats.success_rate,
                'characters_stats': stats.characters_stats,
                'voice_usage_stats': stats.voice_usage_stats
            },
            'characters': {
                char_id: {
                    'name': char.name,
                    'message_count': char.audio_count,
                    'voice_file': char.voice_file,
                    'messages': [
                        {
                            'id': msg.get('id'),
                            'texto_original': msg.get('texto_original', ''),
                            'texto_limpo': msg.get('texto_limpo', ''),
                            'timestamp': msg.get('timestamp')
                        }
                        for msg in char.messages
                    ]
                }
                for char_id, char in generator.characters.items()
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"[OK] Relatório detalhado exportado: {output_file}")
        
    except Exception as e:
        print(f"[ERROR] Erro ao exportar relatório: {e}")

def show_engines_info():
    """Mostra informações sobre engines TTS disponíveis"""
    print("\n[INFO] Verificando engines TTS disponíveis...")
    
    try:
        from tts_engines import TTSEngineManager
        manager = TTSEngineManager()
        
        engines_info = manager.get_engines_info()
        available_engines = manager.get_available_engines()
        
        print(f"\nEngines disponíveis: {len(available_engines)}")
        print("-" * 40)
        
        for name, info in engines_info.items():
            status = "✓ DISPONÍVEL" if info['available'] else "✗ INDISPONÍVEL"
            cloning = "Com clonagem" if info['supports_voice_cloning'] else "Sem clonagem"
            print(f"{info['name']} ({name}): {status} - {cloning}")
        
        if not available_engines:
            print("\n[WARNING] Nenhuma engine TTS disponível!")
            print("[INFO] Instale pelo menos uma das opções:")
            print("  - Coqui TTS: pip install coqui-tts")
            print("  - RealtimeTTS: pip install RealtimeTTS")
            print("  - pyttsx3: pip install pyttsx3")
        
        # Mostrar vozes disponíveis
        available_voices = get_available_voice_files()
        print(f"\n🎤 Vozes encontradas: {len(available_voices)}")
        if available_voices:
            for filename in list(available_voices.keys())[:5]:  # Mostrar apenas 5
                print(f"   - {filename}")
            if len(available_voices) > 5:
                print(f"   ... e mais {len(available_voices) - 5}")
        
    except Exception as e:
        print(f"[ERROR] Erro ao verificar sistema: {e}")

if __name__ == "__main__":
    # Mostrar informações das engines se executado diretamente
    if len(sys.argv) == 1:
        show_engines_info()
        print("\n" + "="*60)
        print("Use --help para ver todas as opções disponíveis")
        print("Use --list-voices para ver vozes disponíveis")
        print("="*60)
        sys.exit(0)
    
    exit_code = main()
    sys.exit(exit_code) 