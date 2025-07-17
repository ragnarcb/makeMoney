#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Teste - Sistema TTS com Clonagem de Voz
Verifica se tudo está funcionando corretamente
"""

import os
import sys
from pathlib import Path

def teste_arquivo_referencia():
    """Testa se o arquivo de referência existe"""
    print("=" * 50)
    print("TESTE 1: ARQUIVO DE REFERÊNCIA")
    print("=" * 50)
    
    arquivo = "Vídeo sem título ‐ Feito com o Clipchamp.wav"
    
    if os.path.exists(arquivo):
        tamanho = os.path.getsize(arquivo)
        print(f"[OK] Arquivo encontrado: {arquivo}")
        print(f"[INFO] Tamanho: {tamanho:,} bytes ({tamanho/1024:.1f} KB)")
        
        if tamanho > 10000:  # Pelo menos 10KB
            print("[OK] Tamanho adequado para TTS")
            return True
        else:
            print("[WARNING] Arquivo muito pequeno - pode não funcionar bem")
            return False
    else:
        print(f"[ERROR] Arquivo não encontrado: {arquivo}")
        print("[INFO] Certifique-se de que o arquivo está na pasta tts2.0")
        return False

def teste_dependencias():
    """Testa se as dependências estão instaladas"""
    print("\n" + "=" * 50)
    print("TESTE 2: DEPENDÊNCIAS")
    print("=" * 50)
    
    dependencias = [
        ("torch", "PyTorch"),
        ("numpy", "NumPy"),
        ("TTS", "Coqui TTS"),
        ("pydub", "PyDub (conversão de áudio)"),
        ("soundfile", "SoundFile (conversão de áudio)"),
        ("pyttsx3", "pyttsx3 (TTS básico)")
    ]
    
    sucessos = 0
    for modulo, nome in dependencias:
        try:
            __import__(modulo)
            print(f"[OK] {nome}")
            sucessos += 1
        except ImportError:
            print(f"[MISSING] {nome}")
    
    print(f"\n[INFO] {sucessos}/{len(dependencias)} dependências instaladas")
    
    if sucessos >= 3:  # Pelo menos as básicas
        print("[OK] Dependências suficientes para funcionar")
        return True
    else:
        print("[WARNING] Muitas dependências faltando")
        print("[AÇÃO] Execute: python instalar_dependencias.py")
        return False

def teste_conversao_audio():
    """Testa se a conversão de áudio funciona"""
    print("\n" + "=" * 50)
    print("TESTE 3: CONVERSÃO DE ÁUDIO")
    print("=" * 50)
    
    arquivo_original = "Vídeo sem título ‐ Feito com o Clipchamp.wav"
    arquivo_convertido = "teste_conversao.wav"
    
    if not os.path.exists(arquivo_original):
        print("[SKIP] Arquivo original não encontrado - pulando teste")
        return False
    
    try:
        # Importar função de conversão
        sys.path.append(os.path.dirname(__file__))
        from usar_minha_voz import converter_audio_para_compativel
        
        print("[INFO] Testando conversão de áudio...")
        
        # Tentar converter
        sucesso = converter_audio_para_compativel(arquivo_original, arquivo_convertido)
        
        if sucesso and os.path.exists(arquivo_convertido):
            tamanho = os.path.getsize(arquivo_convertido)
            print(f"[OK] Conversão funcionou: {arquivo_convertido} ({tamanho} bytes)")
            
            # Limpar arquivo de teste
            try:
                os.remove(arquivo_convertido)
                print("[INFO] Arquivo de teste removido")
            except:
                pass
            
            return True
        else:
            print("[ERROR] Conversão falhou")
            return False
            
    except ImportError as e:
        print(f"[ERROR] Erro ao importar função: {e}")
        return False
    except Exception as e:
        print(f"[ERROR] Erro na conversão: {e}")
        return False

def teste_modelo_tts():
    """Testa se o modelo TTS pode ser carregado"""
    print("\n" + "=" * 50)
    print("TESTE 4: MODELO TTS")
    print("=" * 50)
    
    try:
        from TTS.api import TTS
        
        print("[INFO] Tentando carregar modelo XTTS...")
        
        try:
            tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2")
            print("[OK] Modelo XTTS carregado com sucesso")
            
            # Testar informações do modelo
            if hasattr(tts, 'model_name'):
                print(f"[INFO] Modelo: {tts.model_name}")
            
            return True
            
        except Exception as e:
            print(f"[WARNING] Erro ao carregar modelo: {e}")
            print("[INFO] Modelo será baixado na primeira execução")
            return False
        
    except ImportError:
        print("[ERROR] Coqui TTS não está instalado")
        print("[AÇÃO] Execute: pip install coqui-tts")
        return False

def teste_sistema_completo():
    """Executa todos os testes"""
    print("=" * 60)
    print("    TESTE COMPLETO DO SISTEMA TTS")
    print("=" * 60)
    
    testes = [
        ("Arquivo de Referência", teste_arquivo_referencia),
        ("Dependências", teste_dependencias),
        ("Conversão de Áudio", teste_conversao_audio),
        ("Modelo TTS", teste_modelo_tts)
    ]
    
    resultados = []
    
    for nome, funcao in testes:
        try:
            resultado = funcao()
            resultados.append((nome, resultado))
        except Exception as e:
            print(f"[ERROR] Erro no teste {nome}: {e}")
            resultados.append((nome, False))
    
    # Resumo
    print("\n" + "=" * 60)
    print("    RESUMO DOS TESTES")
    print("=" * 60)
    
    sucessos = 0
    for nome, resultado in resultados:
        status = "[OK]" if resultado else "[FALHOU]"
        print(f"{status:10} {nome}")
        if resultado:
            sucessos += 1
    
    print(f"\n[INFO] {sucessos}/{len(resultados)} testes passaram")
    
    # Diagnóstico final
    if sucessos == len(resultados):
        print("\n[SUCESSO] ✅ Sistema completamente funcional!")
        print("Próximo passo: Execute 'python usar_minha_voz.py'")
    elif sucessos >= 2:
        print("\n[PARCIAL] ⚠️ Sistema parcialmente funcional")
        print("Algumas funcionalidades podem não funcionar perfeitamente")
        print("Você pode tentar usar mesmo assim")
    else:
        print("\n[FALHA] ❌ Sistema com muitos problemas")
        print("Execute primeiro: python instalar_dependencias.py")
    
    return sucessos == len(resultados)

def main():
    """Função principal"""
    try:
        sucesso = teste_sistema_completo()
        
        print("\n" + "=" * 60)
        input("Pressione ENTER para continuar...")
        
        return sucesso
        
    except KeyboardInterrupt:
        print("\n\n[INFO] Teste interrompido pelo usuário")
        return False
    except Exception as e:
        print(f"\n[ERROR] Erro inesperado: {e}")
        return False

if __name__ == "__main__":
    main() 