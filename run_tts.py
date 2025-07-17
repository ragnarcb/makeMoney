#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de execução do sistema TTS a partir da raiz do projeto
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Executa o sistema TTS da pasta correta"""
    # Determinar caminho da pasta tts2.0
    project_root = Path(__file__).parent.absolute()
    tts_dir = project_root / 'tts2.0'
    main_script = tts_dir / 'main.py'
    
    # Verificar se os arquivos existem
    if not tts_dir.exists():
        print(f"[ERROR] Pasta tts2.0 não encontrada em: {project_root}")
        return 1
    
    if not main_script.exists():
        print(f"[ERROR] Script main.py não encontrado em: {tts_dir}")
        return 1
    
    # Mudar para o diretório tts2.0 e executar
    try:
        print(f"[INFO] Executando sistema TTS de: {tts_dir}")
        
        # Usar subprocess para manter o diretório correto
        cmd = [sys.executable, str(main_script)] + sys.argv[1:]
        
        result = subprocess.run(
            cmd,
            cwd=str(tts_dir),
            text=True
        )
        
        return result.returncode
        
    except KeyboardInterrupt:
        print("\n[INFO] Operação cancelada pelo usuário")
        return 1
    except Exception as e:
        print(f"[ERROR] Erro ao executar sistema TTS: {e}")
        return 1

if __name__ == "__main__":
    # Mostrar informações se executado sem argumentos
    if len(sys.argv) == 1:
        print("="*60)
        print("SISTEMA TTS MODULAR COM MÚLTIPLAS VOZES")
        print("="*60)
        print("Este script executa o sistema TTS da pasta tts2.0")
        print()
        print("Uso:")
        print("  python run_tts.py --help                    # Ver todas as opções")
        print("  python run_tts.py --list-voices             # Listar vozes disponíveis")
        print("  python run_tts.py --list-characters         # Listar personagens do JSON")
        print("  python run_tts.py --show-voice-mapping      # Ver mapeamento de vozes")
        print()
        print("Exemplos:")
        print("  python run_tts.py                           # Processar JSON padrão")
        print("  python run_tts.py --json-file conversa.json # JSON personalizado")
        print("  python run_tts.py --voice-map aluno:voz_aluno.wav professora:voz_prof.wav")
        print("  python run_tts.py --character aluno         # Apenas um personagem")
        print("  python run_tts.py --text 'Olá' --output ola.wav --voice voz.wav")
        print()
        print("Testes:")
        print("  python tts2.0/test_anti_corte.py            # Testar melhorias anti-corte")
        print("="*60)
        
        # Mostrar status do sistema
        try:
            tts_dir = Path(__file__).parent / 'tts2.0'
            if (tts_dir / 'main.py').exists():
                print("\n✅ Sistema TTS encontrado e pronto para uso")
            else:
                print("\n❌ Sistema TTS não encontrado")
        except:
            print("\n❌ Erro ao verificar sistema")
    
    exit_code = main()
    sys.exit(exit_code) 