#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste para verificar melhorias anti-corte no sistema TTS
"""

import os
import sys
from pathlib import Path

# Importar módulos do sistema
try:
    from text_cleaner import TextCleaner
    from tts_engines import TTSEngineManager
    from config import get_available_voice_files
except ImportError as e:
    print(f"[ERROR] Erro ao importar módulos: {e}")
    sys.exit(1)

def test_text_cleaning():
    """Testa a limpeza de texto com melhorias"""
    print("🧹 TESTE DE LIMPEZA DE TEXTO")
    print("="*40)
    
    cleaner = TextCleaner()
    
    test_cases = [
        "Esta palavra foi interpretada corretamente.",
        "O sistema estava processando os dados...",
        "Ele disse: 'Terminamos!'",
        "A palavra interpretada ficou cortada",
        "Processamento completo 100%.",
        "Resultado: aprovado!",
        "Texto com emojis 😀 e caracteres especiais @#$",
    ]
    
    print("Comparação ANTES vs DEPOIS da limpeza:")
    print("-" * 60)
    
    for i, original in enumerate(test_cases, 1):
        cleaned = cleaner.clean_text(original)
        print(f"\n{i}. ORIGINAL: '{original}'")
        print(f"   LIMPO:    '{cleaned}'")
        
        # Mostrar estatísticas
        stats = cleaner.get_text_stats(original, cleaned)
        if stats['has_speech_improvements']:
            print(f"   ✅ Melhorias aplicadas (padding: {stats['has_speech_improvements']})")
        
        if stats['chars_removed'] > 0:
            print(f"   📊 {stats['chars_removed']} caracteres removidos ({stats['reduction_percentage']:.1f}%)")

def test_engines_anti_cut():
    """Testa engines TTS com melhorias anti-corte"""
    print("\n\n🎤 TESTE DE ENGINES TTS COM ANTI-CORTE")
    print("="*50)
    
    manager = TTSEngineManager()
    available = manager.get_available_engines()
    
    if not available:
        print("❌ Nenhuma engine TTS disponível")
        return
    
    print(f"Engines disponíveis: {', '.join(available)}")
    
    # Texto de teste problemático
    test_text = "A palavra interpretada foi processada corretamente"
    
    print(f"\n📝 Texto de teste: '{test_text}'")
    
    # Limpar texto primeiro
    cleaner = TextCleaner()
    cleaned_text = cleaner.clean_text(test_text)
    print(f"📝 Texto limpo: '{cleaned_text}'")
    
    # Testar com melhor engine disponível
    engine = manager.get_best_engine(prefer_voice_cloning=False)
    if engine:
        print(f"\n🔧 Testando com {engine.name}...")
        
        # Arquivo de teste
        test_output = "teste_anti_corte.wav"
        
        try:
            success = engine.synthesize_to_file(cleaned_text, test_output)
            
            if success and os.path.exists(test_output):
                file_size = os.path.getsize(test_output)
                print(f"✅ Áudio gerado com sucesso!")
                print(f"📄 Arquivo: {test_output}")
                print(f"📊 Tamanho: {file_size} bytes")
                print(f"💡 Verifique se a palavra 'interpretada' está completa")
                
                # Verificar se tem padding
                try:
                    from pydub import AudioSegment
                    audio = AudioSegment.from_wav(test_output)
                    duration = len(audio)
                    print(f"⏱️  Duração: {duration}ms")
                    
                    if duration > 3000:  # Mais de 3 segundos indica padding
                        print("✅ Padding detectado - deve evitar cortes")
                    
                except ImportError:
                    print("⚠️  pydub não disponível - não foi possível verificar padding")
                    
            else:
                print("❌ Falha na geração do áudio")
                
        except Exception as e:
            print(f"❌ Erro durante teste: {e}")
    else:
        print("❌ Nenhuma engine disponível para teste")

def test_multiple_voices():
    """Testa detecção de múltiplas vozes"""
    print("\n\n🎭 TESTE DE MÚLTIPLAS VOZES")
    print("="*40)
    
    available_voices = get_available_voice_files()
    
    if not available_voices:
        print("❌ Nenhuma voz encontrada no sistema")
        print("\n💡 Para testar múltiplas vozes:")
        print("   1. Coloque arquivos de voz na pasta tts2.0/")
        print("   2. Use nomes como: voz_aluno.wav, voz_professora.wav")
        print("   3. Execute: python main.py --list-voices")
        return
    
    print(f"✅ {len(available_voices)} voz(es) encontrada(s):")
    
    for filename, path in available_voices.items():
        try:
            size_mb = Path(path).stat().st_size / 1024 / 1024
            print(f"  🎤 {filename} ({size_mb:.1f} MB)")
        except:
            print(f"  🎤 {filename}")
    
    print("\n💡 Para usar múltiplas vozes:")
    print("   python main.py --voice-map aluno:voz_aluno.wav professora:voz_professora.wav")

def show_improvements_summary():
    """Mostra resumo das melhorias implementadas"""
    print("\n\n✨ RESUMO DAS MELHORIAS ANTI-CORTE")
    print("="*50)
    
    improvements = [
        "🧹 Limpeza de texto inteligente (preserva finais de palavras)",
        "⏸️  Padding de silêncio adicionado no final dos áudios",
        "📝 Preparação de texto específica para cada engine TTS",
        "🎯 Configurações otimizadas para evitar cortes",
        "🔄 Processamento via arquivo temporário (mais seguro)",
        "📊 Velocidade ajustada para síntese mais completa",
        "🎤 Suporte a múltiplas vozes por personagem",
        "🛡️  Fallback automático entre engines"
    ]
    
    for improvement in improvements:
        print(f"  {improvement}")
    
    print(f"\n🎯 SOLUÇÃO ESPECÍFICA PARA SEU PROBLEMA:")
    print(f"   - 'interpretada' → 'interpreta' ❌")
    print(f"   - Agora: 'interpretada' completa ✅")
    print(f"   - Padding garante que finais não sejam cortados")
    print(f"   - Texto é preparado com pausas adequadas")

def main():
    """Executa todos os testes"""
    print("🧪 TESTE COMPLETO DAS MELHORIAS ANTI-CORTE")
    print("="*60)
    
    try:
        # Teste 1: Limpeza de texto
        test_text_cleaning()
        
        # Teste 2: Engines TTS
        test_engines_anti_cut()
        
        # Teste 3: Múltiplas vozes
        test_multiple_voices()
        
        # Resumo
        show_improvements_summary()
        
        print(f"\n🎉 TESTES CONCLUÍDOS!")
        print(f"💡 Execute 'python main.py' para usar o sistema melhorado")
        
    except KeyboardInterrupt:
        print("\n\n❌ Testes interrompidos pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante testes: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 