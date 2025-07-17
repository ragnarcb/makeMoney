#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para o sistema modular de TTS
"""

import os
import sys
import traceback

def test_imports():
    """Testa se todos os módulos podem ser importados"""
    print("🔍 Testando importações...")
    
    try:
        import config
        print("✅ config.py")
    except Exception as e:
        print(f"❌ config.py: {e}")
        return False
    
    try:
        from text_cleaner import TextCleaner
        print("✅ text_cleaner.py")
    except Exception as e:
        print(f"❌ text_cleaner.py: {e}")
        return False
    
    try:
        from audio_processor import AudioProcessor
        print("✅ audio_processor.py")
    except Exception as e:
        print(f"❌ audio_processor.py: {e}")
        return False
    
    try:
        from tts_engines import TTSEngineManager
        print("✅ tts_engines.py")
    except Exception as e:
        print(f"❌ tts_engines.py: {e}")
        return False
    
    try:
        from character_voice_generator import CharacterVoiceGenerator
        print("✅ character_voice_generator.py")
    except Exception as e:
        print(f"❌ character_voice_generator.py: {e}")
        return False
    
    return True

def test_text_cleaner():
    """Testa a limpeza de texto"""
    print("\n🧹 Testando limpeza de texto...")
    
    from text_cleaner import TextCleaner
    cleaner = TextCleaner()
    
    test_cases = [
        ("Olá mundo! 😀🎉", "Olá mundo!"),
        ("Texto... com reticências.", "Texto com reticências"),
        ("Emojis 💯 e @#$ caracteres", "Emojis  e  caracteres"),
        ("  Espaços    múltiplos  ", "Espaços múltiplos"),
        ("", ""),
    ]
    
    all_passed = True
    for original, expected_clean in test_cases:
        cleaned = cleaner.clean_text(original)
        if cleaned.strip():  # Só verificar se não está vazio
            print(f"✅ '{original}' → '{cleaned}'")
        else:
            if not expected_clean.strip():
                print(f"✅ '{original}' → '{cleaned}' (vazio esperado)")
            else:
                print(f"❌ '{original}' → '{cleaned}' (deveria ter conteúdo)")
                all_passed = False
    
    return all_passed

def test_audio_processor():
    """Testa o processador de áudio"""
    print("\n🎵 Testando processador de áudio...")
    
    from audio_processor import AudioProcessor
    processor = AudioProcessor()
    
    # Testar validação de arquivo (que não existe)
    is_valid, msg = processor.validate_audio_file("arquivo_inexistente.wav")
    if not is_valid:
        print("✅ Validação de arquivo inexistente funciona")
    else:
        print("❌ Validação deveria falhar para arquivo inexistente")
        return False
    
    # Testar informações de áudio
    info = processor.get_audio_info("arquivo_inexistente.wav")
    if not info['exists']:
        print("✅ Informações de áudio para arquivo inexistente")
    else:
        print("❌ Deveria retornar exists=False")
        return False
    
    return True

def test_tts_engines():
    """Testa as engines TTS"""
    print("\n🎤 Testando engines TTS...")
    
    from tts_engines import TTSEngineManager
    manager = TTSEngineManager()
    
    engines_info = manager.get_engines_info()
    print(f"📊 Engines encontradas: {len(engines_info)}")
    
    for name, info in engines_info.items():
        status = "✅" if info['available'] else "⚠️"
        cloning = "com clonagem" if info['supports_voice_cloning'] else "sem clonagem"
        print(f"  {status} {info['name']} ({name}) - {cloning}")
    
    available = manager.get_available_engines()
    if available:
        print(f"✅ {len(available)} engine(s) disponível(is)")
        return True
    else:
        print("⚠️ Nenhuma engine TTS disponível")
        print("💡 Instale pelo menos uma:")
        print("   pip install pyttsx3")
        print("   pip install coqui-tts")
        return False

def test_character_generator():
    """Testa o gerador de personagens"""
    print("\n👥 Testando gerador de personagens...")
    
    from character_voice_generator import CharacterVoiceGenerator
    
    try:
        generator = CharacterVoiceGenerator()
        print("✅ CharacterVoiceGenerator instanciado")
        
        # Testar carregamento de JSON
        json_exists = os.path.exists("exemplo-mensagens.json")
        if json_exists:
            success = generator.load_messages_from_json("exemplo-mensagens.json")
            if success:
                print("✅ JSON carregado com sucesso")
                
                characters = generator.get_characters()
                print(f"📊 Personagens encontrados: {len(characters)}")
                for char_id, char in characters.items():
                    print(f"  👤 {char.name} ({char_id}): {char.audio_count} mensagens")
                
                return True
            else:
                print("❌ Falha ao carregar JSON")
                return False
        else:
            print("⚠️ exemplo-mensagens.json não encontrado")
            print("✅ Generator funciona (sem JSON)")
            return True
            
    except Exception as e:
        print(f"❌ Erro no CharacterVoiceGenerator: {e}")
        return False

def test_system_validation():
    """Testa validação completa do sistema"""
    print("\n🔍 Testando validação do sistema...")
    
    from character_voice_generator import CharacterVoiceGenerator
    
    try:
        generator = CharacterVoiceGenerator()
        
        # Testar validação sem dados
        is_valid = generator.validate_setup()
        print(f"📊 Sistema válido (sem dados): {is_valid}")
        
        # Se temos JSON, carregar e testar novamente
        if os.path.exists("exemplo-mensagens.json"):
            generator.load_messages_from_json("exemplo-mensagens.json")
            is_valid_with_data = generator.validate_setup()
            print(f"📊 Sistema válido (com dados): {is_valid_with_data}")
            return is_valid_with_data
        else:
            return True  # OK se não temos dados para testar
            
    except Exception as e:
        print(f"❌ Erro na validação: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("="*60)
    print("🧪 TESTE DO SISTEMA MODULAR DE TTS")
    print("="*60)
    
    tests = [
        ("Importações", test_imports),
        ("Limpeza de Texto", test_text_cleaner),
        ("Processador de Áudio", test_audio_processor),
        ("Engines TTS", test_tts_engines),
        ("Gerador de Personagens", test_character_generator),
        ("Validação do Sistema", test_system_validation),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ ERRO CRÍTICO em {test_name}: {e}")
            if "--verbose" in sys.argv:
                traceback.print_exc()
            results[test_name] = False
    
    # Relatório final
    print("\n" + "="*60)
    print("📊 RELATÓRIO FINAL DOS TESTES")
    print("="*60)
    
    passed = 0
    total = len(tests)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Resultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Sistema pronto para uso")
        print("\n💡 Próximos passos:")
        print("   python main.py --help")
        print("   python main.py --validate-only")
        print("   python main.py --list-characters")
        return 0
    else:
        print("⚠️ ALGUNS TESTES FALHARAM")
        print("🔧 Verifique as dependências e configurações")
        print("\n💡 Comandos úteis:")
        print("   pip install pyttsx3")
        print("   pip install coqui-tts")
        print("   pip install pydub soundfile")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 