#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correção FFmpeg V2 - Detecção Avançada para Windows
Versão melhorada que tenta várias formas de encontrar FFmpeg
"""

import os
import sys
import subprocess
from pathlib import Path

def encontrar_ffmpeg_windows():
    """Tenta várias formas de encontrar FFmpeg no Windows"""
    print("=" * 50)
    print("PROCURANDO FFMPEG NO WINDOWS")
    print("=" * 50)
    
    # Método 1: PATH do sistema
    try:
        import shutil
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            print(f"[INFO] Método 1 - FFmpeg encontrado via PATH: {ffmpeg_path}")
            return test_ffmpeg_command("ffmpeg")
    except:
        pass
    
    # Método 2: Comando direto
    try:
        print("[INFO] Método 2 - Testando comando direto...")
        result = subprocess.run(["ffmpeg", "-version"], 
                              capture_output=True, text=True, timeout=10,
                              shell=True)  # Usar shell=True no Windows
        if result.returncode == 0:
            print("[OK] FFmpeg funciona com comando direto")
            return "ffmpeg"
    except Exception as e:
        print(f"[INFO] Comando direto falhou: {e}")
    
    # Método 3: Locais comuns no Windows
    locais_comuns = [
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        os.path.expanduser(r"~\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.1-full_build\bin\ffmpeg.exe"),
        os.path.expanduser(r"~\scoop\apps\ffmpeg\current\bin\ffmpeg.exe"),
        os.path.expanduser(r"~\chocolatey\lib\ffmpeg\tools\ffmpeg\bin\ffmpeg.exe")
    ]
    
    print("[INFO] Método 3 - Procurando em locais comuns...")
    for local in locais_comuns:
        if os.path.exists(local):
            print(f"[INFO] Encontrado: {local}")
            if test_ffmpeg_command(local):
                return local
    
    # Método 4: Procurar em todo o sistema (mais lento)
    print("[INFO] Método 4 - Busca ampla no sistema...")
    try:
        # Buscar em drives comuns
        for drive in ['C:', 'D:', 'E:']:
            if os.path.exists(drive):
                for root, dirs, files in os.walk(drive + '\\'):
                    if 'ffmpeg.exe' in files:
                        ffmpeg_candidate = os.path.join(root, 'ffmpeg.exe')
                        print(f"[INFO] Candidato encontrado: {ffmpeg_candidate}")
                        if test_ffmpeg_command(ffmpeg_candidate):
                            return ffmpeg_candidate
                    # Limitar busca para não demorar muito
                    if len(root.split('\\')) > 4:  # Não ir muito fundo
                        dirs.clear()
    except Exception as e:
        print(f"[WARNING] Busca ampla falhou: {e}")
    
    print("[ERROR] FFmpeg não encontrado em nenhum método")
    return None

def test_ffmpeg_command(command):
    """Testa se um comando ffmpeg funciona"""
    try:
        result = subprocess.run([command, "-version"], 
                              capture_output=True, text=True, timeout=15,
                              shell=True if os.name == 'nt' else False)
        if result.returncode == 0:
            version_line = result.stdout.split('\n')[0]
            print(f"[OK] Comando funciona: {command}")
            print(f"[INFO] {version_line}")
            return True
        else:
            print(f"[WARNING] Comando falhou: {command} - {result.stderr}")
            return False
    except Exception as e:
        print(f"[WARNING] Erro ao testar {command}: {e}")
        return False

def converter_com_ffmpeg_windows(ffmpeg_cmd, arquivo_entrada, arquivo_saida):
    """Converte arquivo usando ffmpeg no Windows"""
    print(f"\n[INFO] Convertendo arquivo...")
    print(f"[INFO] FFmpeg: {ffmpeg_cmd}")
    print(f"[INFO] Entrada: {arquivo_entrada}")
    print(f"[INFO] Saída: {arquivo_saida}")
    
    if not os.path.exists(arquivo_entrada):
        print(f"[ERROR] Arquivo de entrada não existe: {arquivo_entrada}")
        return False
    
    # Usar caminhos com aspas para lidar com espaços
    entrada_quoted = f'"{os.path.abspath(arquivo_entrada)}"'
    saida_quoted = f'"{os.path.abspath(arquivo_saida)}"'
    
    # Estratégia 1: Conversão padrão
    print("\n[INFO] Tentativa 1: Conversão padrão")
    cmd1 = f'{ffmpeg_cmd} -i {entrada_quoted} -ar 22050 -ac 1 -acodec pcm_s16le -f wav -y {saida_quoted}'
    
    if executar_comando_ffmpeg(cmd1, arquivo_saida):
        return True
    
    # Estratégia 2: Forçar recodificação
    print("\n[INFO] Tentativa 2: Recodificação forçada")
    cmd2 = f'{ffmpeg_cmd} -i {entrada_quoted} -vn -sn -ar 22050 -ac 1 -acodec pcm_s16le -f wav -y {saida_quoted}'
    
    if executar_comando_ffmpeg(cmd2, arquivo_saida):
        return True
    
    # Estratégia 3: Conversão em duas etapas
    print("\n[INFO] Tentativa 3: Conversão em etapas")
    temp_file = '"temp_audio.wav"'
    
    # Primeira etapa: extrair áudio
    cmd3a = f'{ffmpeg_cmd} -i {entrada_quoted} -vn -acodec pcm_s16le -y {temp_file}'
    
    try:
        result3a = subprocess.run(cmd3a, shell=True, capture_output=True, text=True, timeout=60)
        if result3a.returncode == 0 and os.path.exists("temp_audio.wav"):
            print("[INFO] Primeira etapa OK")
            
            # Segunda etapa: ajustar formato
            cmd3b = f'{ffmpeg_cmd} -i {temp_file} -ar 22050 -ac 1 -y {saida_quoted}'
            
            if executar_comando_ffmpeg(cmd3b, arquivo_saida):
                # Limpar arquivo temporário
                try:
                    os.remove("temp_audio.wav")
                except:
                    pass
                return True
        
        # Limpar arquivo temporário se criado
        try:
            os.remove("temp_audio.wav")
        except:
            pass
            
    except Exception as e:
        print(f"[WARNING] Conversão em etapas falhou: {e}")
    
    print("[ERROR] Todas as estratégias de conversão falharam")
    return False

def executar_comando_ffmpeg(comando, arquivo_esperado):
    """Executa comando ffmpeg e verifica resultado"""
    try:
        print(f"[CMD] {comando}")
        
        result = subprocess.run(comando, shell=True, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            # Verificar se arquivo foi criado
            arquivo_sem_aspas = arquivo_esperado.replace('"', '')
            if os.path.exists(arquivo_sem_aspas):
                tamanho = os.path.getsize(arquivo_sem_aspas)
                print(f"[OK] Conversão bem-sucedida! ({tamanho} bytes)")
                return True
            else:
                print("[WARNING] Comando executou mas arquivo não foi criado")
                return False
        else:
            print(f"[WARNING] Comando falhou:")
            if result.stderr:
                # Mostrar apenas parte do erro para não poluir
                stderr_lines = result.stderr.split('\n')[:5]
                print(f"[STDERR] {chr(10).join(stderr_lines)}")
            return False
            
    except subprocess.TimeoutExpired:
        print("[WARNING] Comando demorou muito (timeout)")
        return False
    except Exception as e:
        print(f"[WARNING] Erro na execução: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("    CORREÇÃO FFMPEG V2 - WINDOWS")
    print("=" * 60)
    
    # Encontrar FFmpeg
    ffmpeg_cmd = encontrar_ffmpeg_windows()
    
    if not ffmpeg_cmd:
        print("\n[ERROR] ❌ FFmpeg não foi encontrado!")
        print("\nPossíveis soluções:")
        print("1. Reinstalar FFmpeg e adicionar ao PATH")
        print("2. Baixar FFmpeg de https://ffmpeg.org/download.html")
        print("3. Usar chocolatey: choco install ffmpeg")
        print("4. Usar scoop: scoop install ffmpeg")
        input("\nPressione ENTER para continuar...")
        return False
    
    print(f"\n[OK] ✅ FFmpeg encontrado: {ffmpeg_cmd}")
    
    # Verificar arquivo original
    arquivo_original = "Vídeo sem título ‐ Feito com o Clipchamp.wav"
    
    if not os.path.exists(arquivo_original):
        print(f"\n[ERROR] Arquivo original não encontrado: {arquivo_original}")
        input("\nPressione ENTER para continuar...")
        return False
    
    tamanho_original = os.path.getsize(arquivo_original)
    print(f"\n[INFO] Arquivo original: {arquivo_original} ({tamanho_original:,} bytes)")
    
    # Tentar conversão
    arquivo_convertido = "voz_referencia_convertida_ffmpeg.wav"
    
    # Remover arquivo anterior se existir
    if os.path.exists(arquivo_convertido):
        try:
            os.remove(arquivo_convertido)
            print(f"[INFO] Arquivo anterior removido")
        except:
            pass
    
    print(f"\n[INFO] Iniciando conversão para: {arquivo_convertido}")
    
    if converter_com_ffmpeg_windows(ffmpeg_cmd, arquivo_original, arquivo_convertido):
        print(f"\n[SUCESSO] ✅ Conversão concluída!")
        print(f"[INFO] Arquivo convertido: {arquivo_convertido}")
        
        # Verificar arquivo convertido
        if os.path.exists(arquivo_convertido):
            tamanho_convertido = os.path.getsize(arquivo_convertido)
            print(f"[INFO] Tamanho convertido: {tamanho_convertido:,} bytes")
            
            # Testar se arquivo é válido
            if test_ffmpeg_command(f'{ffmpeg_cmd} -i "{arquivo_convertido}" -f null -'):
                print("[OK] ✅ Arquivo convertido é válido!")
            else:
                print("[WARNING] ⚠️ Arquivo pode ter problemas")
        
        print("\n[PRÓXIMOS PASSOS]")
        print("1. Execute: python usar_minha_voz.py")
        print("2. Escolha opção 1 (clonagem avançada)")
        print("3. O sistema usará automaticamente o arquivo convertido")
        
        return True
    
    else:
        print(f"\n[FALHA] ❌ Não foi possível converter o arquivo")
        print("\nPossíveis causas:")
        print("- Arquivo original pode estar corrompido")
        print("- Formato não suportado")
        print("- Problemas de permissão")
        return False

if __name__ == "__main__":
    try:
        sucesso = main()
        print("\n" + "=" * 60)
        input("Pressione ENTER para sair...")
        sys.exit(0 if sucesso else 1)
    except KeyboardInterrupt:
        print("\n\n[INFO] Operação cancelada pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Erro inesperado: {e}")
        input("Pressione ENTER para sair...")
        sys.exit(1) 