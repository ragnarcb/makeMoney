#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clonagem de Voz Usando Arquivo Local
Sistema TTS que usa o arquivo WAV da pasta como referência

Arquivo de referência: "Vídeo sem título ‐ Feito com o Clipchamp.wav"
"""

import os
import sys
import subprocess
import json
import re
from pathlib import Path

# Configuração do arquivo de referência
ARQUIVO_VOZ_REFERENCIA = "tts2.0\Vídeo sem título ‐ Feito com o Clipchamp.wav"
ARQUIVO_VOZ_CONVERTIDO = "voz_referencia_convertida.wav"
ARQUIVO_JSON_MENSAGENS = "exemplo-mensagens.json"

def converter_audio_para_compativel(arquivo_original, arquivo_saida):
    """Converte áudio para formato compatível com Coqui TTS"""
    print(f"[INFO] Iniciando conversão de áudio...")
    print(f"[INFO] Origem: {arquivo_original}")
    print(f"[INFO] Destino: {arquivo_saida}")
    
    try:
        # Verificar se arquivo original existe
        if not os.path.exists(arquivo_original):
            print(f"[ERROR] Arquivo não encontrado: {arquivo_original}")
            return False
        
        # Tentar usar pydub primeiro (mais confiável)
        try:
            from pydub import AudioSegment
            
            print(f"[INFO] Usando pydub para conversão...")
            
            # Carregar áudio original - detectar formato automaticamente
            audio = AudioSegment.from_file(arquivo_original)
            
            print(f"[INFO] Áudio carregado - Canais: {audio.channels}, Sample Rate: {audio.frame_rate}, Duração: {len(audio)}ms")
            
            # Converter para formato compatível com Coqui TTS:
            # - 22050 Hz sample rate (padrão Coqui)
            # - Mono (1 canal)
            # - 16-bit WAV format
            audio_convertido = audio.set_frame_rate(22050).set_channels(1)
            
            # Normalizar volume se necessário
            if audio_convertido.max_possible_amplitude > 0:
                audio_convertido = audio_convertido.normalize()
            
            # Salvar em formato WAV
            audio_convertido.export(arquivo_saida, format="wav", parameters=["-ac", "1", "-ar", "22050"])
            
            # Verificar se arquivo foi criado
            if os.path.exists(arquivo_saida):
                tamanho = os.path.getsize(arquivo_saida)
                print(f"[OK] Áudio convertido com pydub: {arquivo_saida} ({tamanho} bytes)")
                return True
            else:
                print("[ERROR] Arquivo convertido não foi criado")
                return False
            
        except ImportError:
            print("[WARNING] pydub não disponível, tentando soundfile...")
            
        except Exception as e:
            print(f"[WARNING] Erro com pydub: {e}, tentando soundfile...")
            
        # Tentar usar soundfile
        try:
            import soundfile as sf
            import numpy as np
            
            print(f"[INFO] Usando soundfile para conversão...")
            
            # Ler áudio original
            data, samplerate = sf.read(arquivo_original, dtype='float32')
            
            print(f"[INFO] Áudio lido - Shape: {data.shape}, Sample Rate: {samplerate}")
            
            # Converter para mono se necessário
            if len(data.shape) > 1 and data.shape[1] > 1:
                data = np.mean(data, axis=1)
                print("[INFO] Convertido para mono")
            
            # Resample para 22050 se necessário
            if samplerate != 22050:
                try:
                    import librosa
                    data = librosa.resample(data, orig_sr=samplerate, target_sr=22050)
                    print("[INFO] Resampling para 22050Hz com librosa")
                except ImportError:
                    print("[WARNING] librosa não disponível para resampling")
                    # Usar resampling simples (não ideal mas funciona)
                    factor = 22050 / samplerate
                    new_length = int(len(data) * factor)
                    data = np.interp(np.linspace(0, len(data), new_length), np.arange(len(data)), data)
                    print("[INFO] Resampling simples para 22050Hz")
            
            # Normalizar
            if np.max(np.abs(data)) > 0:
                data = data / np.max(np.abs(data)) * 0.9
            
            # Salvar em formato compatível
            sf.write(arquivo_saida, data, 22050, format='WAV', subtype='PCM_16')
            
            if os.path.exists(arquivo_saida):
                tamanho = os.path.getsize(arquivo_saida)
                print(f"[OK] Áudio convertido com soundfile: {arquivo_saida} ({tamanho} bytes)")
                return True
            else:
                print("[ERROR] Arquivo convertido não foi criado")
                return False
            
        except ImportError:
            print("[WARNING] soundfile não disponível, tentando ffmpeg...")
            
        except Exception as e:
            print(f"[WARNING] Erro com soundfile: {e}, tentando ffmpeg...")
            
        # Tentar usar ffmpeg via subprocess
        try:
            import subprocess
            
            print(f"[INFO] Usando ffmpeg para conversão...")
            
            cmd = [
                "ffmpeg", "-i", arquivo_original,
                "-ar", "22050",     # Sample rate
                "-ac", "1",         # Mono
                "-acodec", "pcm_s16le",  # 16-bit PCM
                "-f", "wav",        # WAV format
                "-y",               # Overwrite
                arquivo_saida
            ]
            
            print(f"[CMD] {' '.join(cmd)}")
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                if os.path.exists(arquivo_saida):
                    tamanho = os.path.getsize(arquivo_saida)
                    print(f"[OK] Áudio convertido com ffmpeg: {arquivo_saida} ({tamanho} bytes)")
                    return True
                else:
                    print("[ERROR] FFmpeg executou mas arquivo não foi criado")
                    return False
            else:
                print(f"[WARNING] FFmpeg falhou:")
                print(f"[STDERR] {result.stderr}")
                
        except FileNotFoundError:
            print("[WARNING] FFmpeg não encontrado no sistema")
        except Exception as e:
            print(f"[WARNING] Erro com FFmpeg: {e}")
        
        print("[ERROR] Todas as tentativas de conversão falharam")
        print("[INFO] Certifique-se de ter pelo menos uma dessas bibliotecas instaladas:")
        print("  - pydub: pip install pydub")
        print("  - soundfile: pip install soundfile")
        print("  - ffmpeg: instalar no sistema")
        return False
        
    except Exception as e:
        print(f"[ERROR] Erro geral na conversão: {e}")
        return False

def tentar_conversao_com_ffmpeg(arquivo_entrada, arquivo_saida):
    """Tenta conversão usando FFmpeg diretamente (detecção corrigida)"""
    try:
        import shutil
        import subprocess
        
        # Verificar se ffmpeg está disponível no PATH
        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            print("[INFO] FFmpeg não encontrado no PATH")
            return False
        
        print(f"[INFO] FFmpeg encontrado em: {ffmpeg_path}")
        
        # Usar caminhos absolutos
        entrada_abs = os.path.abspath(arquivo_entrada)
        saida_abs = os.path.abspath(arquivo_saida)
        
        # Comando ffmpeg otimizado
        cmd = [
            "ffmpeg",
            "-i", entrada_abs,
            "-ar", "22050",        # Sample rate
            "-ac", "1",            # Mono
            "-acodec", "pcm_s16le", # 16-bit PCM
            "-f", "wav",           # WAV format
            "-y",                  # Overwrite
            saida_abs
        ]
        
        print(f"[INFO] Executando FFmpeg...")
        print(f"[CMD] {' '.join(cmd)}")
        
        # Executar com timeout
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            if os.path.exists(saida_abs):
                tamanho = os.path.getsize(saida_abs)
                print(f"[OK] FFmpeg conversão bem-sucedida: {arquivo_saida} ({tamanho} bytes)")
                return True
            else:
                print("[WARNING] FFmpeg executou mas arquivo não foi criado")
                return False
        else:
            print(f"[WARNING] FFmpeg falhou:")
            if result.stderr:
                print(f"[STDERR] {result.stderr[:200]}...")  # Primeiros 200 chars
            return False
            
    except subprocess.TimeoutExpired:
        print("[WARNING] FFmpeg timeout - arquivo muito grande ou problema")
        return False
    except ImportError:
        print("[INFO] Módulo shutil não disponível")
        return False
    except Exception as e:
        print(f"[WARNING] Erro ao tentar FFmpeg: {e}")
        return False

def verificar_arquivo_referencia():
    """Verifica se o arquivo de referência existe"""
    arquivo_path = Path(ARQUIVO_VOZ_REFERENCIA)
    if not arquivo_path.exists():
        print(f"[ERROR] Arquivo de referência não encontrado: {ARQUIVO_VOZ_REFERENCIA}")
        print("[INFO] Certifique-se de que o arquivo está na pasta tts2.0")
        return False, None
    
    print(f"[OK] Arquivo de referência encontrado: {ARQUIVO_VOZ_REFERENCIA}")
    print(f"[INFO] Tamanho: {arquivo_path.stat().st_size / 1024:.1f} KB")
    
    # Verificar se existe arquivo convertido pelo script de correção ffmpeg
    arquivo_ffmpeg = "voz_referencia_convertida_ffmpeg.wav"
    if os.path.exists(arquivo_ffmpeg):
        tamanho_ffmpeg = os.path.getsize(arquivo_ffmpeg)
        print(f"[OK] Encontrado arquivo convertido pelo FFmpeg: {arquivo_ffmpeg} ({tamanho_ffmpeg} bytes)")
        return True, arquivo_ffmpeg
    
    # Verificar arquivo convertido padrão
    arquivo_convertido_path = Path(ARQUIVO_VOZ_CONVERTIDO)
    if arquivo_convertido_path.exists():
        print(f"[INFO] Usando arquivo já convertido: {ARQUIVO_VOZ_CONVERTIDO}")
        return True, ARQUIVO_VOZ_CONVERTIDO
    
    # Tentar converter com FFmpeg primeiro se estiver disponível
    print(f"[INFO] Tentando conversão com FFmpeg...")
    if tentar_conversao_com_ffmpeg(ARQUIVO_VOZ_REFERENCIA, arquivo_ffmpeg):
        print(f"[OK] Conversão com FFmpeg bem-sucedida!")
        return True, arquivo_ffmpeg
    
    # Fallback para outros métodos
    print(f"[INFO] FFmpeg falhou, tentando outros métodos...")
    if converter_audio_para_compativel(ARQUIVO_VOZ_REFERENCIA, ARQUIVO_VOZ_CONVERTIDO):
        return True, ARQUIVO_VOZ_CONVERTIDO
    else:
        print("[INFO] Usando arquivo original (pode causar problemas)")
        return True, ARQUIVO_VOZ_REFERENCIA

def carregar_mensagens_json():
    """Carrega as mensagens do arquivo JSON"""
    try:
        # Tentar caminho relativo primeiro
        caminho_json = Path(ARQUIVO_JSON_MENSAGENS)
        if not caminho_json.exists():
            # Tentar caminho absoluto
            caminho_json = Path("../front/whatsapp-clone/public/exemplo-mensagens.json")
            if not caminho_json.exists():
                # Tentar na pasta atual
                caminho_json = Path("exemplo-mensagens.json")
                if not caminho_json.exists():
                    print(f"[ERROR] Arquivo JSON não encontrado: {ARQUIVO_JSON_MENSAGENS}")
                    return None
        
        print(f"[INFO] Carregando mensagens de: {caminho_json}")
        
        with open(caminho_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        
        mensagens = dados.get('mensagens', [])
        print(f"[OK] {len(mensagens)} mensagens carregadas")
        return mensagens
        
    except Exception as e:
        print(f"[ERROR] Erro ao carregar JSON: {e}")
        return None

def extrair_falas_por_personagem(mensagens):
    """Extrai as falas separadas por personagem"""
    if not mensagens:
        return {}, {}
    
    falas_aluno = []
    falas_professora = []
    
    for msg in mensagens:
        usuario_id = msg.get('usuario', {}).get('id', '')
        texto = msg.get('texto', '').strip()
        
        if texto:
            if 'aluno' in usuario_id.lower():
                falas_aluno.append(texto)
            elif 'professora' in usuario_id.lower():
                falas_professora.append(texto)
    
    print(f"[INFO] Falas do aluno: {len(falas_aluno)}")
    print(f"[INFO] Falas da professora: {len(falas_professora)}")
    
    return falas_aluno, falas_professora

def escolher_personagem_e_falar(arquivo_referencia):
    """Permite escolher personagem e falar suas falas"""
    print("\n[INFO] Carregando conversa do WhatsApp...")
    
    # Carregar mensagens
    mensagens = carregar_mensagens_json()
    if not mensagens:
        print("[ERROR] Não foi possível carregar as mensagens")
        return
    
    # Extrair falas por personagem
    falas_aluno, falas_professora = extrair_falas_por_personagem(mensagens)
    
    if not falas_aluno and not falas_professora:
        print("[ERROR] Nenhuma fala encontrada no JSON")
        return
    
    # Escolher personagem
    print("\nESCOLHA O PERSONAGEM:")
    if falas_aluno:
        print(f"1. Aluno Lucas ({len(falas_aluno)} falas)")
    if falas_professora:
        print(f"2. Professora Marina ({len(falas_professora)} falas)")
    print("3. Voltar ao menu principal")
    
    escolha = input("\nEscolha o personagem (1-3): ").strip()
    
    falas_escolhidas = []
    nome_personagem = ""
    
    if escolha == "1" and falas_aluno:
        falas_escolhidas = falas_aluno
        nome_personagem = "Aluno Lucas"
    elif escolha == "2" and falas_professora:
        falas_escolhidas = falas_professora
        nome_personagem = "Professora Marina"
    elif escolha == "3":
        return
    else:
        print("[ERROR] Opção inválida")
        return
    
    if not falas_escolhidas:
        print("[ERROR] Nenhuma fala disponível para este personagem")
        return
    
    print(f"\n[INFO] Personagem escolhido: {nome_personagem}")
    print(f"[INFO] Total de falas: {len(falas_escolhidas)}")
    
    # Mostrar opções de reprodução
    print("\nOPÇÕES DE REPRODUÇÃO:")
    print("1. Falar todas as falas em sequência")
    print("2. Escolher uma fala específica")
    print("3. Falar texto personalizado")
    print("4. Gerar TODOS os áudios separados (com IDs)")
    print("5. Voltar")
    
    opcao = input("\nEscolha uma opção (1-5): ").strip()
    
    if opcao == "1":
        # Falar todas as falas
        texto_completo = " ... ".join(falas_escolhidas)
        print(f"\n[INFO] Falando todas as {len(falas_escolhidas)} falas do {nome_personagem}")
        sintetizar_com_voz_clonada(arquivo_referencia, texto_completo, nome_personagem)
        
    elif opcao == "2":
        # Escolher fala específica
        print(f"\nFALAS DISPONÍVEIS DO {nome_personagem.upper()}:")
        for i, fala in enumerate(falas_escolhidas, 1):
            preview = fala[:60] + "..." if len(fala) > 60 else fala
            print(f"{i:2d}. {preview}")
        
        try:
            num_fala = int(input(f"\nEscolha uma fala (1-{len(falas_escolhidas)}): "))
            if 1 <= num_fala <= len(falas_escolhidas):
                fala_escolhida = falas_escolhidas[num_fala - 1]
                print(f"\n[INFO] Fala escolhida: {fala_escolhida}")
                sintetizar_com_voz_clonada(arquivo_referencia, fala_escolhida, nome_personagem)
            else:
                print("[ERROR] Número inválido")
        except ValueError:
            print("[ERROR] Digite um número válido")
            
    elif opcao == "3":
        # Texto personalizado
        texto_custom = input(f"\nDigite o texto para {nome_personagem} falar: ").strip()
        if texto_custom:
            sintetizar_com_voz_clonada(arquivo_referencia, texto_custom, nome_personagem)
        else:
            print("[ERROR] Texto não pode estar vazio")
            
    elif opcao == "4":
        # Gerar todos os áudios separados
        gerar_todos_audios_separados(arquivo_referencia, nome_personagem)
        
    elif opcao == "5":
        return
    else:
        print("[ERROR] Opção inválida")

def gerar_todos_audios_separados(arquivo_referencia, nome_personagem):
    """Gera arquivos de áudio separados para todas as mensagens do personagem"""
    print(f"\n[INFO] Gerando todos os áudios do {nome_personagem}...")
    
    # Carregar mensagens novamente para ter acesso aos IDs
    mensagens = carregar_mensagens_json()
    if not mensagens:
        print("[ERROR] Não foi possível carregar mensagens")
        return
    
    # Filtrar mensagens do personagem escolhido
    if "aluno" in nome_personagem.lower():
        filtro_id = "aluno"
    elif "professora" in nome_personagem.lower():
        filtro_id = "professora"
    else:
        print("[ERROR] Personagem não reconhecido")
        return
    
    mensagens_personagem = []
    for msg in mensagens:
        usuario_id = msg.get('usuario', {}).get('id', '')
        if filtro_id in usuario_id.lower():
            mensagens_personagem.append(msg)
    
    if not mensagens_personagem:
        print(f"[ERROR] Nenhuma mensagem encontrada para {nome_personagem}")
        return
    
    print(f"[INFO] Encontradas {len(mensagens_personagem)} mensagens")
    print(f"[INFO] Gerando arquivos separados...")
    
    # Criar pasta para os áudios se não existir
    pasta_audios = f"audios_{filtro_id}"
    if not os.path.exists(pasta_audios):
        os.makedirs(pasta_audios)
        print(f"[INFO] Pasta criada: {pasta_audios}")
    
    sucessos = 0
    erros = 0
    
    for i, msg in enumerate(mensagens_personagem, 1):
        msg_id = msg.get('id', f'msg_{i}')
        texto = msg.get('texto', '').strip()
        
        if not texto:
            print(f"[WARNING] Mensagem {msg_id} vazia - ignorando")
            continue
        
        # Limpar texto
        texto_limpo = limpar_texto(texto)
        if not texto_limpo:
            print(f"[WARNING] Mensagem {msg_id} vazia após limpeza - ignorando")
            continue
        
        # Nome do arquivo
        nome_arquivo = f"{pasta_audios}/msg_{msg_id}_{filtro_id}.wav"
        
        print(f"\n[{i}/{len(mensagens_personagem)}] Processando mensagem {msg_id}")
        print(f"[INFO] Texto: {texto[:60]}{'...' if len(texto) > 60 else ''}")
        print(f"[INFO] Texto limpo: {texto_limpo[:60]}{'...' if len(texto_limpo) > 60 else ''}")
        print(f"[INFO] Arquivo: {nome_arquivo}")
        
        try:
            # Tentar gerar áudio
            if gerar_audio_individual(arquivo_referencia, texto_limpo, nome_arquivo):
                sucessos += 1
                print(f"[OK] Áudio gerado: {nome_arquivo}")
            else:
                erros += 1
                print(f"[ERROR] Falha ao gerar: {nome_arquivo}")
                
        except Exception as e:
            erros += 1
            print(f"[ERROR] Erro na mensagem {msg_id}: {e}")
    
    # Relatório final
    print(f"\n{'='*50}")
    print(f"RELATÓRIO DE GERAÇÃO - {nome_personagem}")
    print(f"{'='*50}")
    print(f"Total de mensagens: {len(mensagens_personagem)}")
    print(f"Sucessos: {sucessos}")
    print(f"Erros: {erros}")
    print(f"Pasta de saída: {pasta_audios}")
    print(f"{'='*50}")
    
    if sucessos > 0:
        print(f"\n[OK] {sucessos} arquivos de áudio gerados com sucesso!")
        print(f"[INFO] Verifique a pasta: {pasta_audios}")
    
    if erros > 0:
        print(f"[WARNING] {erros} arquivos falharam na geração")

def gerar_audio_individual(arquivo_referencia, texto, output_file):
    """Gera um único arquivo de áudio"""
    try:
        # Tentar usar Coqui TTS primeiro
        try:
            from TTS.api import TTS
            
            model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
            tts = TTS(model_name)
            
            tts.tts_to_file(
                text=texto,
                speaker_wav=arquivo_referencia,
                language="pt",
                file_path=output_file
            )
            
            # Verificar se arquivo foi criado e tem tamanho válido
            if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
                return True
            else:
                return False
                
        except ImportError:
            print("[WARNING] Coqui TTS não disponível - usando TTS básico")
            return gerar_audio_basico(texto, output_file)
        except Exception as e:
            print(f"[WARNING] Erro com Coqui TTS: {e} - usando TTS básico")
            return gerar_audio_basico(texto, output_file)
            
    except Exception as e:
        print(f"[ERROR] Erro geral na geração: {e}")
        return False

def gerar_audio_basico(texto, output_file):
    """Gera áudio usando pyttsx3 como fallback"""
    try:
        import pyttsx3
        
        engine = pyttsx3.init()
        
        # Configurar voz portuguesa se disponível
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'portuguese' in voice.name.lower() or 'pt' in voice.id.lower():
                engine.setProperty('voice', voice.id)
                break
        
        engine.setProperty('rate', 150)
        engine.save_to_file(texto, output_file)
        engine.runAndWait()
        
        # Verificar se arquivo foi criado
        if os.path.exists(output_file) and os.path.getsize(output_file) > 100:
            return True
        else:
            return False
            
    except ImportError:
        print("[ERROR] pyttsx3 não disponível")
        return False
    except Exception as e:
        print(f"[ERROR] Erro no TTS básico: {e}")
        return False

def gerar_todos_audios_completos(arquivo_referencia):
    """Gera todos os áudios da conversa separados por ID"""
    print("\n[INFO] Gerando TODOS os áudios da conversa...")
    
    # Carregar mensagens
    mensagens = carregar_mensagens_json()
    if not mensagens:
        print("[ERROR] Não foi possível carregar mensagens")
        return
    
    print(f"[INFO] Encontradas {len(mensagens)} mensagens no total")
    
    # Criar pasta principal para os áudios
    pasta_principal = "audios_conversa_completa"
    if not os.path.exists(pasta_principal):
        os.makedirs(pasta_principal)
        print(f"[INFO] Pasta criada: {pasta_principal}")
    
    # Criar subpastas para cada personagem
    pasta_aluno = f"{pasta_principal}/aluno"
    pasta_professora = f"{pasta_principal}/professora"
    
    if not os.path.exists(pasta_aluno):
        os.makedirs(pasta_aluno)
    if not os.path.exists(pasta_professora):
        os.makedirs(pasta_professora)
    
    sucessos_total = 0
    erros_total = 0
    sucessos_aluno = 0
    sucessos_professora = 0
    
    for i, msg in enumerate(mensagens, 1):
        msg_id = msg.get('id', f'msg_{i}')
        texto = msg.get('texto', '').strip()
        usuario_id = msg.get('usuario', {}).get('id', '').lower()
        nome_usuario = msg.get('usuario', {}).get('nome', 'Desconhecido')
        
        if not texto:
            print(f"[WARNING] Mensagem {msg_id} vazia - ignorando")
            continue
        
        # Limpar texto
        texto_limpo = limpar_texto(texto)
        if not texto_limpo:
            print(f"[WARNING] Mensagem {msg_id} vazia após limpeza - ignorando")
            continue
        
        # Determinar pasta e nome do arquivo
        if 'aluno' in usuario_id:
            pasta_destino = pasta_aluno
            prefixo = "aluno"
        elif 'professora' in usuario_id:
            pasta_destino = pasta_professora
            prefixo = "professora"
        else:
            print(f"[WARNING] Personagem não reconhecido na mensagem {msg_id}: {usuario_id}")
            continue
        
        # Nome do arquivo com ID da mensagem
        nome_arquivo = f"{pasta_destino}/msg_{msg_id}_{prefixo}.wav"
        
        print(f"\n[{i}/{len(mensagens)}] Processando {nome_usuario} - ID: {msg_id}")
        print(f"[INFO] Texto: {texto[:60]}{'...' if len(texto) > 60 else ''}")
        print(f"[INFO] Texto limpo: {texto_limpo[:60]}{'...' if len(texto_limpo) > 60 else ''}")
        print(f"[INFO] Arquivo: {nome_arquivo}")
        
        try:
            # Tentar gerar áudio
            if gerar_audio_individual(arquivo_referencia, texto_limpo, nome_arquivo):
                sucessos_total += 1
                if 'aluno' in usuario_id:
                    sucessos_aluno += 1
                else:
                    sucessos_professora += 1
                print(f"[OK] Áudio gerado: {nome_arquivo}")
            else:
                erros_total += 1
                print(f"[ERROR] Falha ao gerar: {nome_arquivo}")
                
        except Exception as e:
            erros_total += 1
            print(f"[ERROR] Erro na mensagem {msg_id}: {e}")
    
    # Relatório final completo
    print(f"\n{'='*60}")
    print(f"RELATÓRIO COMPLETO DE GERAÇÃO")
    print(f"{'='*60}")
    print(f"Total de mensagens processadas: {len(mensagens)}")
    print(f"Sucessos totais: {sucessos_total}")
    print(f"Erros totais: {erros_total}")
    print(f"")
    print(f"Sucessos - Aluno Lucas: {sucessos_aluno}")
    print(f"Sucessos - Professora Marina: {sucessos_professora}")
    print(f"")
    print(f"Pasta principal: {pasta_principal}")
    print(f"  ├── aluno/ ({sucessos_aluno} arquivos)")
    print(f"  └── professora/ ({sucessos_professora} arquivos)")
    print(f"{'='*60}")
    
    if sucessos_total > 0:
        print(f"\n[OK] {sucessos_total} arquivos de áudio gerados com sucesso!")
        print(f"[INFO] Estrutura de pastas:")
        print(f"       {pasta_principal}/")
        print(f"       ├── aluno/")
        print(f"       └── professora/")
    
    if erros_total > 0:
        print(f"[WARNING] {erros_total} arquivos falharam na geração")

def limpar_texto(texto):
    """Remove emojis e caracteres especiais do texto, mas preserva entonação natural"""
    # Padrão para detectar emojis e outros caracteres especiais
    padrao_emoji = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # símbolos & pictogramas
        u"\U0001F680-\U0001F6FF"  # transporte & símbolos
        u"\U0001F1E0-\U0001F1FF"  # bandeiras
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    # Remover emojis
    texto_limpo = padrao_emoji.sub('', texto)
    
    # Remover múltiplos espaços
    texto_limpo = ' '.join(texto_limpo.split())
    
    # MELHORADO: Tratamento inteligente de pontuação
    # ===============================================
    
    # 1. Preservar abreviações importantes (não remover seus pontos)
    abreviacoes = ['Dr.', 'Dra.', 'Sr.', 'Sra.', 'Prof.', 'Profa.', 'etc.', 'ex.', 'vs.', 'p.ex.']
    marcadores_abrev = {}
    for i, abrev in enumerate(abreviacoes):
        marcador = f"__ABREV_{i}__"
        if abrev in texto_limpo:
            texto_limpo = texto_limpo.replace(abrev, marcador)
            marcadores_abrev[marcador] = abrev
    
    # 2. Remover apenas reticências múltiplas problemáticas
    texto_limpo = re.sub(r'\.{3,}', '', texto_limpo)  # Remove ... .... etc
    texto_limpo = texto_limpo.replace('…', '')  # Remove ellipsis unicode
    
    # 3. TÉCNICA INTELIGENTE: Substituir pontos finais por vírgulas para manter entonação
    # Isso evita que o TTS fale "ponto" mas mantém a pausa natural
    texto_limpo = re.sub(r'\.(\s+|$)', r',\1', texto_limpo)  # Ponto final → vírgula
    
    # 4. Remover pontos isolados ou problemáticos (que não são finais)
    texto_limpo = re.sub(r'(\s)\.(\s)', r'\1\2', texto_limpo)  # Remove pontos no meio
    
    # 5. Para frases que terminariam abruptamente, adicionar pausa natural
    if texto_limpo.strip() and not texto_limpo.strip().endswith((',', '!', '?', ':')):
        texto_limpo = texto_limpo.strip() + ','
    
    # 6. Restaurar abreviações importantes
    for marcador, abrev_original in marcadores_abrev.items():
        # Restaurar mas substituir ponto por vírgula para evitar TTS falar "ponto"
        abrev_segura = abrev_original.replace('.', ',')
        texto_limpo = texto_limpo.replace(marcador, abrev_segura)
    
    # 7. Adicionar melhorias específicas para TTS
    # Garantir pausas pequenas antes de pontuação importante
    texto_limpo = re.sub(r'([,!?;:])', r' \1', texto_limpo)
    
    # Garantir espaço após pontuação
    texto_limpo = re.sub(r'([,!?;:])([^\s])', r'\1 \2', texto_limpo)
    
    # 8. Normalizar espaços finais
    texto_limpo = re.sub(r'\s+([,!?])', r'\1', texto_limpo)
    
    # 9. Adicionar padding no final para evitar cortes bruscos
    if texto_limpo.strip():
        texto_limpo = texto_limpo.strip() + ' '
    
    return texto_limpo.strip()

def sintetizar_com_voz_clonada(arquivo_referencia, texto, personagem=""):
    """Sintetiza texto usando voz clonada"""
    if not texto.strip():
        print("[ERROR] Texto vazio")
        return
        
    # Limpar texto antes de sintetizar
    texto_limpo = limpar_texto(texto)
    print(f"[INFO] Texto original: {texto}")
    print(f"[INFO] Texto limpo: {texto_limpo}")
    
    print(f"\n[INFO] Sintetizando texto do {personagem}...")
    print(f"[INFO] Texto limpo para sintetizar: {texto_limpo[:100]}{'...' if len(texto_limpo) > 100 else ''}")
    print(f"[INFO] Arquivo de referência: {arquivo_referencia}")
    
    try:
        # Tentar usar RealtimeTTS primeiro
        try:
            from RealtimeTTS import TextToAudioStream, CoquiEngine
            
            print("[INFO] Usando RealtimeTTS...")
            engine = CoquiEngine(
                voice=arquivo_referencia,
                language="pt"
            )
            
            stream = TextToAudioStream(engine)
            print("[INFO] Reproduzindo...")
            stream.feed(texto_limpo)
            stream.play()
            print("[OK] Reprodução concluída!")
            return
            
        except ImportError:
            print("[WARNING] RealtimeTTS não disponível, tentando Coqui TTS...")
        except Exception as e:
            print(f"[WARNING] Erro com RealtimeTTS: {e}")
        
        # Tentar Coqui TTS
        try:
            from TTS.api import TTS
            
            print("[INFO] Usando Coqui TTS...")
            model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
            tts = TTS(model_name)
            
            # Nome do arquivo de saída baseado no personagem
            nome_arquivo = personagem.lower().replace(" ", "_").replace(".", "")
            output_file = f"voz_{nome_arquivo}.wav"
            
            print("[INFO] Sintetizando...")
            tts.tts_to_file(
                text=texto_limpo,
                speaker_wav=arquivo_referencia,
                language="pt",
                file_path=output_file
            )
            
            print(f"[OK] Áudio salvo: {output_file}")
            
            # Reproduzir
            if os.path.exists(output_file):
                reproduzir = input("Reproduzir áudio agora? (s/n): ").strip().lower()
                if reproduzir == 's':
                    try:
                        if sys.platform.startswith('win'):
                            os.system(f'start "" "{output_file}"')
                        else:
                            os.system(f'xdg-open "{output_file}"')
                    except:
                        print(f"[INFO] Abra manualmente: {output_file}")
            
        except ImportError:
            print("[ERROR] Coqui TTS não instalado")
            usar_sistema_simples_com_texto(texto)
        except Exception as e:
            print(f"[ERROR] Erro com Coqui TTS: {e}")
            usar_sistema_simples_com_texto(texto)
            
    except Exception as e:
        print(f"[ERROR] Erro na síntese: {e}")

def usar_sistema_simples_com_texto(texto):
    """Usar pyttsx3 com texto específico"""
    try:
        import pyttsx3
        
        # Limpar texto antes de sintetizar
        texto_limpo = limpar_texto(texto)
        print(f"[INFO] Texto original: {texto}")
        print(f"[INFO] Texto limpo: {texto_limpo}")
        print("[INFO] Usando TTS básico...")
        engine = pyttsx3.init()
        
        # Configurar voz portuguesa se disponível
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'portuguese' in voice.name.lower() or 'pt' in voice.id.lower():
                engine.setProperty('voice', voice.id)
                break
        
        engine.setProperty('rate', 150)
        
        output_file = "voz_simples.wav"
        engine.save_to_file(texto_limpo, output_file)
        engine.runAndWait()
        
        print(f"[OK] Áudio básico salvo: {output_file}")
        
    except ImportError:
        print("[ERROR] pyttsx3 não disponível")
    except Exception as e:
        print(f"[ERROR] Erro no TTS básico: {e}")

def usar_sistema_simples():
    """Usar sistema TTS simples (pyttsx3) como fallback"""
    try:
        import pyttsx3
        
        print("\n[INFO] Usando sistema TTS básico como alternativa...")
        print("[WARNING] Voice cloning não disponível neste modo")
        
        # Obter texto
        texto = input("\nDigite o texto para sintetizar: ").strip()
        if not texto:
            print("[ERROR] Texto não pode estar vazio!")
            return
        
        # Configurar TTS
        engine = pyttsx3.init()
        
        # Configurar voz (tentar português se disponível)
        voices = engine.getProperty('voices')
        for voice in voices:
            if 'portuguese' in voice.name.lower() or 'pt' in voice.id.lower():
                engine.setProperty('voice', voice.id)
                break
        
        # Configurar velocidade
        engine.setProperty('rate', 150)  # Velocidade mais natural
        
        # Sintetizar
        print(f"\n[INFO] Sintetizando: {texto[:50]}{'...' if len(texto) > 50 else ''}")
        
        # Salvar arquivo
        output_file = "voz_sintetizada.wav"
        engine.save_to_file(texto, output_file)
        engine.runAndWait()
        
        print(f"[OK] Áudio salvo: {output_file}")
        
        # Reproduzir
        reproduzir = input("Reproduzir áudio agora? (s/n): ").strip().lower()
        if reproduzir == 's':
            try:
                os.system(f'start "" "{output_file}"')
            except:
                print("[INFO] Abra manualmente o arquivo:", output_file)
                
    except ImportError:
        print("[ERROR] pyttsx3 não está instalado")
        print("[INFO] Execute: pip install pyttsx3")
    except Exception as e:
        print(f"[ERROR] Erro no TTS básico: {e}")

def usar_sistema_moderno(arquivo_referencia):
    """Usar sistema TTS moderno com clonagem de voz"""
    
    # Garantir que temos arquivo compatível
    print(f"\n[INFO] Preparando arquivo de referência...")
    print(f"[INFO] Arquivo recebido: {arquivo_referencia}")
    
    # Verificar se arquivo existe
    if not os.path.exists(arquivo_referencia):
        print(f"[ERROR] Arquivo não encontrado: {arquivo_referencia}")
        print("[INFO] Tentando sistema básico...")
        usar_sistema_simples()
        return
    
    # Verificar se é o arquivo convertido ou original
    arquivo_final = arquivo_referencia
    if arquivo_referencia == ARQUIVO_VOZ_REFERENCIA:
        # É o arquivo original - tentar converter
        print("[INFO] Detectado arquivo original - convertendo para formato compatível...")
        if converter_audio_para_compativel(ARQUIVO_VOZ_REFERENCIA, ARQUIVO_VOZ_CONVERTIDO):
            arquivo_final = ARQUIVO_VOZ_CONVERTIDO
            print(f"[OK] Usando arquivo convertido: {arquivo_final}")
        else:
            print("[WARNING] Conversão falhou - tentando usar arquivo original")
            arquivo_final = ARQUIVO_VOZ_REFERENCIA
    
    # Verificar se arquivo final existe e tem tamanho válido
    if os.path.exists(arquivo_final):
        tamanho = os.path.getsize(arquivo_final)
        print(f"[INFO] Arquivo final: {arquivo_final} ({tamanho} bytes)")
        if tamanho < 1000:  # Menos de 1KB provavelmente é inválido
            print("[WARNING] Arquivo muito pequeno - pode estar corrompido")
    else:
        print(f"[ERROR] Arquivo final não existe: {arquivo_final}")
        usar_sistema_simples()
        return
    
    try:
        # Tentar importar realtimetts primeiro
        try:
            from RealtimeTTS import TextToAudioStream, CoquiEngine
            usar_realtimetts = True
            print("[INFO] Usando RealtimeTTS para clonagem de voz...")
        except ImportError:
            usar_realtimetts = False
            print("[WARNING] RealtimeTTS não disponível")
        
        if usar_realtimetts:
            # Usar RealtimeTTS com clonagem
            texto = input("\nDigite o texto para falar com sua voz clonada: ").strip()
            if not texto:
                print("[ERROR] Texto não pode estar vazio!")
                return
            
            print(f"\n[INFO] Preparando clonagem com RealtimeTTS...")
            print(f"[INFO] Referência: {arquivo_final}")
            print(f"[INFO] Texto: {texto[:50]}{'...' if len(texto) > 50 else ''}")
            
            try:
                # Configurar engine com clonagem
                engine = CoquiEngine(
                    voice=arquivo_final,  # Usar arquivo convertido
                    language="pt"
                )
                
                # Criar stream
                stream = TextToAudioStream(engine)
                
                # Sintetizar e reproduzir
                print("[INFO] Sintetizando com voz clonada...")
                stream.feed(texto)
                stream.play()
                
                print("[OK] Clonagem de voz concluída!")
                
            except Exception as e:
                print(f"[ERROR] Erro na clonagem com RealtimeTTS: {e}")
                print("[INFO] Tentando método Coqui TTS direto...")
                # Continuar para tentar Coqui TTS
                usar_realtimetts = False
        
        if not usar_realtimetts:
            # Tentar usar Coqui TTS diretamente
            try:
                from TTS.api import TTS
                
                print("[INFO] Usando Coqui TTS para clonagem...")
                
                # Obter texto
                texto = input("\nDigite o texto para falar com sua voz clonada: ").strip()
                if not texto:
                    print("[ERROR] Texto não pode estar vazio!")
                    return
                
                print(f"\n[INFO] Carregando modelo XTTS para clonagem...")
                print(f"[INFO] Arquivo de referência: {arquivo_final}")
                print(f"[INFO] Texto a sintetizar: {texto[:100]}{'...' if len(texto) > 100 else ''}")
                
                # Verificar se modelo é multilingual
                model_name = "tts_models/multilingual/multi-dataset/xtts_v2"
                print(f"[INFO] Carregando modelo: {model_name}")
                
                try:
                    tts = TTS(model_name)
                    print("[OK] Modelo carregado com sucesso")
                    
                    print("[INFO] Iniciando síntese com clonagem...")
                    output_file = "voz_clonada.wav"
                    
                    # Sintetizar com parâmetros específicos para XTTS
                    tts.tts_to_file(
                        text=texto,
                        speaker_wav=arquivo_final,  # Usar arquivo convertido
                        language="pt",              # Idioma português
                        file_path=output_file
                    )
                    
                    print(f"[OK] Voz clonada salva: {output_file}")
                    
                    # Verificar se arquivo foi criado
                    if os.path.exists(output_file):
                        tamanho_saida = os.path.getsize(output_file)
                        print(f"[INFO] Arquivo gerado: {tamanho_saida} bytes")
                        
                        # Reproduzir
                        reproduzir = input("\nReproduzir áudio agora? (s/n): ").strip().lower()
                        if reproduzir == 's':
                            try:
                                if sys.platform.startswith('win'):
                                    os.system(f'start "" "{output_file}"')
                                else:
                                    os.system(f'xdg-open "{output_file}"')
                                print("[OK] Reproduzindo áudio...")
                            except Exception as e:
                                print(f"[WARNING] Erro ao reproduzir: {e}")
                                print(f"[INFO] Abra manualmente: {output_file}")
                    else:
                        print("[ERROR] Arquivo de saída não foi criado")
                    
                except Exception as e:
                    error_msg = str(e)
                    print(f"[ERROR] Erro na síntese com Coqui TTS: {error_msg}")
                    
                    # Verificar tipos específicos de erro
                    if "Format not recognised" in error_msg:
                        print("\n[DIAGNÓSTICO] Problema de formato de áudio detectado")
                        print("- O arquivo pode estar em formato incompatível")
                        print("- Tentando nova conversão...")
                        
                        # Tentar conversão forçada
                        novo_arquivo = "voz_ref_forcada.wav"
                        if converter_audio_para_compativel(arquivo_final, novo_arquivo):
                            print(f"[INFO] Tentando novamente com: {novo_arquivo}")
                            try:
                                tts.tts_to_file(
                                    text=texto,
                                    speaker_wav=novo_arquivo,
                                    language="pt",
                                    file_path=output_file
                                )
                                print("[OK] Sucesso com arquivo reconvertido!")
                            except Exception as e2:
                                print(f"[ERROR] Ainda com erro: {e2}")
                                print("[INFO] Usando sistema básico...")
                                usar_sistema_simples()
                        else:
                            print("[ERROR] Conversão forçada falhou")
                            usar_sistema_simples()
                    
                    elif "speaker_wav" in error_msg or "speaker_id" in error_msg:
                        print("\n[DIAGNÓSTICO] Erro de configuração de speaker")
                        print("- Tentando com configurações alternativas...")
                        usar_sistema_simples()
                    
                    else:
                        print(f"\n[DIAGNÓSTICO] Erro geral: {error_msg}")
                        print("[INFO] Usando sistema básico...")
                        usar_sistema_simples()
                
            except ImportError as e:
                print(f"[WARNING] Coqui TTS não disponível: {e}")
                print("[INFO] Execute: pip install coqui-tts")
                usar_sistema_simples()
            except Exception as e:
                print(f"[ERROR] Erro ao configurar Coqui TTS: {e}")
                print("[INFO] Tentando sistema básico...")
                usar_sistema_simples()
                
    except Exception as e:
        print(f"[ERROR] Erro geral no sistema moderno: {e}")
        usar_sistema_simples()

def main():
    """Função principal"""
    print("=" * 60)
    print("    CLONAGEM DE VOZ - USAR ARQUIVO LOCAL")
    print("=" * 60)
    print()
    
    # Verificar arquivo de referência
    arquivo_ok, arquivo_para_usar = verificar_arquivo_referencia()
    if not arquivo_ok:
        return
    
    print("\nEste script irá clonar a voz do arquivo de referência")
    print("e permitir que você fale qualquer texto com essa voz.")
    print()
    
    # Escolher método
    print("OPÇÕES DISPONÍVEIS:")
    print("1. [MODERNO] Clonagem avançada (requer bibliotecas TTS)")
    print("2. [BÁSICO]  Síntese simples (sem clonagem)")
    print("3. [JSON]    Usar falas da conversa WhatsApp (aluno/professora)")
    print("4. [LOTE]    Gerar TODOS os áudios da conversa separados")
    print("5. [SAIR]    Cancelar")
    print()
    
    escolha = input("Escolha uma opção (1-5): ").strip()
    
    if escolha == "1":
        usar_sistema_moderno(arquivo_para_usar)
    elif escolha == "2":
        usar_sistema_simples()
    elif escolha == "3":
        escolher_personagem_e_falar(arquivo_para_usar)
    elif escolha == "4":
        gerar_todos_audios_completos(arquivo_para_usar)
    elif escolha == "5":
        print("\n[INFO] Operação cancelada")
    else:
        print(f"[ERROR] Opção inválida: {escolha}")
    
    print("\n[INFO] Script finalizado!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Script interrompido pelo usuário")
    except Exception as e:
        print(f"\n[ERROR] Erro inesperado: {e}") 