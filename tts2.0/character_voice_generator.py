#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo principal para geração de vozes por personagem com suporte a múltiplas vozes
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from config import PATHS, ensure_directory_exists, find_file_in_project, auto_detect_character_voices, get_available_voice_files
from text_cleaner import TextCleaner
from audio_processor import AudioProcessor
from tts_engines import TTSEngineManager

@dataclass
class Character:
    """Representa um personagem da conversa"""
    id: str
    name: str
    messages: List[Dict[str, Any]]
    voice_file: Optional[str] = None  # Arquivo de voz específico para este personagem
    audio_count: int = 0
    
    def __post_init__(self):
        """Inicialização após criação"""
        self.audio_count = len([msg for msg in self.messages if msg.get('texto', '').strip()])

@dataclass
class GenerationStats:
    """Estatísticas de geração de áudio"""
    total_messages: int = 0
    total_characters: int = 0
    successful_generations: int = 0
    failed_generations: int = 0
    characters_stats: Dict[str, int] = None
    voice_usage_stats: Dict[str, int] = None  # Estatísticas de uso de vozes
    
    def __post_init__(self):
        if self.characters_stats is None:
            self.characters_stats = {}
        if self.voice_usage_stats is None:
            self.voice_usage_stats = {}
    
    @property
    def success_rate(self) -> float:
        """Taxa de sucesso em porcentagem"""
        total = self.successful_generations + self.failed_generations
        return (self.successful_generations / total * 100) if total > 0 else 0.0

class CharacterVoiceGenerator:
    """Classe principal para geração de vozes por personagem com múltiplas vozes"""
    
    def __init__(self, default_reference_audio: str = None, output_base_dir: str = None, 
                 voice_mapping: Dict[str, str] = None, auto_detect_voices: bool = True):
        """
        Inicializa o gerador de vozes
        
        Args:
            default_reference_audio: Arquivo de áudio de referência padrão
            output_base_dir: Diretório base para saída dos áudios
            voice_mapping: Mapeamento manual de personagem -> arquivo de voz
            auto_detect_voices: Se deve detectar vozes automaticamente
        """
        # Configurar caminhos
        self.default_reference_audio = default_reference_audio or PATHS['reference_audio']
        self.output_base_dir = output_base_dir or PATHS['output_dir']
        
        # Configurar vozes
        self.voice_mapping = voice_mapping or {}
        self.auto_detect_voices = auto_detect_voices
        self.detected_voices = {}
        self.available_voices = {}
        
        # Inicializar componentes
        self.text_cleaner = TextCleaner()
        self.audio_processor = AudioProcessor()
        self.tts_manager = TTSEngineManager()
        
        # Estado interno
        self.characters = {}
        self.messages = []
        self.prepared_voices = {}  # Cache de vozes preparadas
        self.stats = GenerationStats()
        
        # Preparar ambiente
        self._setup_environment()
    
    def _setup_environment(self):
        """Configura o ambiente de trabalho"""
        # Garantir que diretórios existem
        ensure_directory_exists(self.output_base_dir)
        
        # Descobrir vozes disponíveis
        self.available_voices = get_available_voice_files()
        print(f"[INFO] Vozes disponíveis encontradas: {len(self.available_voices)}")
        for filename, path in self.available_voices.items():
            print(f"  🎤 {filename}")
        
        # Preparar voz padrão se fornecida
        if self.default_reference_audio:
            default_path = find_file_in_project(self.default_reference_audio)
            if default_path:
                success, prepared_audio = self.audio_processor.prepare_reference_audio(default_path)
                if success:
                    self.prepared_voices['_default'] = prepared_audio
                    print(f"[OK] Voz padrão preparada: {prepared_audio}")
                else:
                    print(f"[WARNING] Falha ao preparar voz padrão: {default_path}")
            else:
                print(f"[WARNING] Voz padrão não encontrada: {self.default_reference_audio}")
    
    def load_messages_from_json(self, json_path: str) -> bool:
        """
        Carrega mensagens de arquivo JSON
        
        Args:
            json_path: Caminho para arquivo JSON
            
        Returns:
            True se sucesso
        """
        try:
            # Procurar arquivo em múltiplos locais
            json_file = find_file_in_project(json_path)
            
            if json_file is None:
                print(f"[ERROR] Arquivo JSON não encontrado: {json_path}")
                return False
            
            print(f"[INFO] Carregando mensagens de: {json_file}")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.messages = data.get('mensagens', [])
            print(f"[OK] {len(self.messages)} mensagens carregadas")
            
            # Limpar textos das mensagens
            self.messages = self.text_cleaner.clean_message_batch(self.messages)
            print(f"[INFO] {len(self.messages)} mensagens válidas após limpeza")
            
            # Extrair personagens
            self._extract_characters()
            
            # Detectar vozes para personagens
            if self.auto_detect_voices:
                self._auto_detect_character_voices()
            
            # Aplicar mapeamento manual
            self._apply_voice_mapping()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Erro ao carregar JSON: {e}")
            return False
    
    def _extract_characters(self):
        """Extrai personagens únicos das mensagens"""
        self.characters = {}
        
        for message in self.messages:
            user_data = message.get('usuario', {})
            char_id = user_data.get('id', 'unknown')
            char_name = user_data.get('nome', char_id)
            
            # Normalizar ID do personagem
            char_id = char_id.lower().strip()
            
            # Criar ou atualizar personagem
            if char_id not in self.characters:
                self.characters[char_id] = Character(
                    id=char_id,
                    name=char_name,
                    messages=[]
                )
            
            # Adicionar mensagem ao personagem
            self.characters[char_id].messages.append(message)
        
        # Atualizar contadores
        for character in self.characters.values():
            character.audio_count = len([msg for msg in character.messages if msg.get('texto', '').strip()])
        
        print(f"[INFO] Personagens extraídos:")
        for char_id, character in self.characters.items():
            print(f"  - {character.name} ({char_id}): {character.audio_count} mensagens")
    
    def _auto_detect_character_voices(self):
        """Detecta automaticamente vozes para os personagens"""
        if not self.characters:
            return
        
        character_ids = list(self.characters.keys())
        self.detected_voices = auto_detect_character_voices(character_ids)
        
        # Aplicar vozes detectadas aos personagens
        for char_id, voice_path in self.detected_voices.items():
            if char_id in self.characters:
                self.characters[char_id].voice_file = voice_path
                print(f"[AUTO] Voz atribuída a {self.characters[char_id].name}: {Path(voice_path).name}")
    
    def _apply_voice_mapping(self):
        """Aplica mapeamento manual de vozes"""
        for char_id, voice_filename in self.voice_mapping.items():
            if char_id in self.characters:
                # Procurar arquivo de voz
                voice_path = find_file_in_project(voice_filename)
                if voice_path:
                    self.characters[char_id].voice_file = voice_path
                    print(f"[MANUAL] Voz atribuída a {self.characters[char_id].name}: {voice_filename}")
                else:
                    print(f"[WARNING] Voz não encontrada para {char_id}: {voice_filename}")
    
    def set_character_voice(self, character_id: str, voice_file: str) -> bool:
        """
        Define voz específica para um personagem
        
        Args:
            character_id: ID do personagem
            voice_file: Arquivo de voz
            
        Returns:
            True se sucesso
        """
        if character_id not in self.characters:
            print(f"[ERROR] Personagem não encontrado: {character_id}")
            return False
        
        voice_path = find_file_in_project(voice_file)
        if not voice_path:
            print(f"[ERROR] Arquivo de voz não encontrado: {voice_file}")
            return False
        
        self.characters[character_id].voice_file = voice_path
        print(f"[OK] Voz definida para {self.characters[character_id].name}: {Path(voice_path).name}")
        return True
    
    def _prepare_character_voice(self, character_id: str) -> Optional[str]:
        """
        Prepara a voz de um personagem para uso
        
        Args:
            character_id: ID do personagem
            
        Returns:
            Caminho para arquivo de voz preparado ou None
        """
        character = self.characters.get(character_id)
        if not character:
            return None
        
        # Verificar se já foi preparada
        cache_key = f"char_{character_id}"
        if cache_key in self.prepared_voices:
            return self.prepared_voices[cache_key]
        
        # Usar voz específica do personagem
        if character.voice_file:
            success, prepared_voice = self.audio_processor.prepare_reference_audio(character.voice_file)
            if success:
                self.prepared_voices[cache_key] = prepared_voice
                print(f"[OK] Voz de {character.name} preparada: {Path(prepared_voice).name}")
                return prepared_voice
            else:
                print(f"[WARNING] Falha ao preparar voz de {character.name}")
        
        # Fallback para voz padrão
        if '_default' in self.prepared_voices:
            print(f"[INFO] Usando voz padrão para {character.name}")
            return self.prepared_voices['_default']
        
        print(f"[WARNING] Nenhuma voz disponível para {character.name}")
        return None
    
    def get_characters(self) -> Dict[str, Character]:
        """Retorna dicionário de personagens"""
        return self.characters.copy()
    
    def get_character_voice_info(self) -> Dict[str, Dict[str, Any]]:
        """Retorna informações sobre vozes dos personagens"""
        info = {}
        
        for char_id, character in self.characters.items():
            voice_info = {
                'character_name': character.name,
                'voice_file': character.voice_file,
                'voice_available': character.voice_file is not None,
                'voice_prepared': f"char_{char_id}" in self.prepared_voices
            }
            
            if character.voice_file:
                voice_info['voice_filename'] = Path(character.voice_file).name
                voice_info['voice_size'] = os.path.getsize(character.voice_file) if os.path.exists(character.voice_file) else 0
            
            info[char_id] = voice_info
        
        return info
    
    def generate_audio_for_character(self, character_id: str, use_voice_cloning: bool = True) -> Tuple[int, int]:
        """
        Gera áudios para um personagem específico
        
        Args:
            character_id: ID do personagem
            use_voice_cloning: Se deve usar clonagem de voz
            
        Returns:
            (sucessos, falhas)
        """
        if character_id not in self.characters:
            print(f"[ERROR] Personagem não encontrado: {character_id}")
            return 0, 0
        
        character = self.characters[character_id]
        print(f"\n[INFO] Gerando áudios para {character.name} ({character_id})")
        
        # Preparar voz do personagem
        reference_audio = None
        if use_voice_cloning:
            reference_audio = self._prepare_character_voice(character_id)
            if reference_audio:
                print(f"[INFO] Usando voz específica: {Path(reference_audio).name}")
            else:
                print(f"[WARNING] Voz não disponível, usando TTS básico")
        
        # Criar diretório do personagem
        char_output_dir = os.path.join(self.output_base_dir, character_id)
        ensure_directory_exists(char_output_dir)
        
        sucessos = 0
        falhas = 0
        
        for i, message in enumerate(character.messages, 1):
            msg_id = message.get('id', f'msg_{i}')
            texto = message.get('texto', '').strip()
            
            if not texto:
                print(f"[WARNING] Mensagem {msg_id} vazia - ignorando")
                continue
            
            # Nome do arquivo
            output_file = os.path.join(char_output_dir, f"msg_{msg_id}_{character_id}.wav")
            
            print(f"\n[{i}/{len(character.messages)}] Processando mensagem {msg_id}")
            print(f"[INFO] Texto: {texto[:60]}{'...' if len(texto) > 60 else ''}")
            print(f"[INFO] Arquivo: {output_file}")
            if reference_audio:
                print(f"[INFO] Voz: {Path(reference_audio).name}")
            
            try:
                # Gerar áudio
                success = self.tts_manager.synthesize_with_best_engine(
                    text=texto,
                    output_file=output_file,
                    reference_audio=reference_audio
                )
                
                if success:
                    sucessos += 1
                    print(f"[OK] Áudio gerado: {output_file}")
                    
                    # Atualizar estatísticas de uso de voz
                    voice_key = Path(reference_audio).name if reference_audio else "tts_basico"
                    self.stats.voice_usage_stats[voice_key] = self.stats.voice_usage_stats.get(voice_key, 0) + 1
                else:
                    falhas += 1
                    print(f"[ERROR] Falha ao gerar: {output_file}")
                
            except Exception as e:
                falhas += 1
                print(f"[ERROR] Erro na mensagem {msg_id}: {e}")
        
        print(f"\n[SUMMARY] {character.name}: {sucessos} sucessos, {falhas} falhas")
        return sucessos, falhas
    
    def generate_all_characters_audio(self, use_voice_cloning: bool = True) -> GenerationStats:
        """
        Gera áudios para todos os personagens
        
        Args:
            use_voice_cloning: Se deve usar clonagem de voz
            
        Returns:
            Estatísticas de geração
        """
        print(f"\n{'='*60}")
        print(f"GERAÇÃO COMPLETA DE ÁUDIOS COM MÚLTIPLAS VOZES")
        print(f"{'='*60}")
        print(f"Total de personagens: {len(self.characters)}")
        print(f"Clonagem de voz: {'Ativada' if use_voice_cloning else 'Desativada'}")
        print(f"Diretório de saída: {self.output_base_dir}")
        
        # Mostrar mapeamento de vozes
        voice_info = self.get_character_voice_info()
        print(f"\n📋 Mapeamento de vozes:")
        for char_id, info in voice_info.items():
            voice_status = "✅" if info['voice_available'] else "❌"
            voice_name = info.get('voice_filename', 'Nenhuma')
            print(f"  {voice_status} {info['character_name']}: {voice_name}")
        
        # Resetar estatísticas
        self.stats = GenerationStats()
        self.stats.total_characters = len(self.characters)
        self.stats.total_messages = len(self.messages)
        
        # Gerar para cada personagem
        for char_id, character in self.characters.items():
            print(f"\n{'-'*40}")
            print(f"Processando {character.name} ({char_id})")
            print(f"{'-'*40}")
            
            sucessos, falhas = self.generate_audio_for_character(char_id, use_voice_cloning)
            
            # Atualizar estatísticas
            self.stats.successful_generations += sucessos
            self.stats.failed_generations += falhas
            self.stats.characters_stats[char_id] = sucessos
        
        # Relatório final
        self._print_final_report()
        
        return self.stats
    
    def generate_single_audio(self, text: str, output_file: str, character_voice: str = None, use_voice_cloning: bool = True) -> bool:
        """
        Gera um único áudio a partir de texto
        
        Args:
            text: Texto a ser sintetizado
            output_file: Arquivo de saída
            character_voice: Arquivo de voz específico a usar
            use_voice_cloning: Se deve usar clonagem de voz
            
        Returns:
            True se sucesso
        """
        # Limpar texto
        cleaned_text = self.text_cleaner.clean_text(text)
        if not cleaned_text.strip():
            print("[ERROR] Texto vazio após limpeza")
            return False
        
        print(f"[INFO] Gerando áudio único:")
        print(f"[INFO] Texto original: {text}")
        print(f"[INFO] Texto limpo: {cleaned_text}")
        print(f"[INFO] Arquivo: {output_file}")
        
        # Garantir que diretório existe
        output_dir = os.path.dirname(output_file)
        if output_dir:
            ensure_directory_exists(output_dir)
        
        # Determinar voz a usar
        reference_audio = None
        if use_voice_cloning:
            if character_voice:
                # Usar voz específica fornecida
                voice_path = find_file_in_project(character_voice)
                if voice_path:
                    success, prepared_voice = self.audio_processor.prepare_reference_audio(voice_path)
                    if success:
                        reference_audio = prepared_voice
                        print(f"[INFO] Usando voz específica: {Path(character_voice).name}")
                    else:
                        print(f"[WARNING] Falha ao preparar voz: {character_voice}")
                else:
                    print(f"[WARNING] Voz não encontrada: {character_voice}")
            
            # Fallback para voz padrão
            if not reference_audio and '_default' in self.prepared_voices:
                reference_audio = self.prepared_voices['_default']
                print(f"[INFO] Usando voz padrão")
        
        # Gerar áudio
        return self.tts_manager.synthesize_with_best_engine(
            text=cleaned_text,
            output_file=output_file,
            reference_audio=reference_audio
        )
    
    def _print_final_report(self):
        """Imprime relatório final de geração com informações de vozes"""
        print(f"\n{'='*60}")
        print(f"RELATÓRIO FINAL DE GERAÇÃO COM MÚLTIPLAS VOZES")
        print(f"{'='*60}")
        print(f"Total de mensagens: {self.stats.total_messages}")
        print(f"Total de personagens: {self.stats.total_characters}")
        print(f"Sucessos: {self.stats.successful_generations}")
        print(f"Falhas: {self.stats.failed_generations}")
        print(f"Taxa de sucesso: {self.stats.success_rate:.1f}%")
        print(f"")
        print(f"Sucessos por personagem:")
        
        for char_id, character in self.characters.items():
            sucessos = self.stats.characters_stats.get(char_id, 0)
            total = character.audio_count
            taxa = (sucessos / total * 100) if total > 0 else 0
            voice_name = Path(character.voice_file).name if character.voice_file else "TTS Básico"
            print(f"  - {character.name}: {sucessos}/{total} ({taxa:.1f}%) - Voz: {voice_name}")
        
        print(f"")
        print(f"Uso de vozes:")
        for voice, count in self.stats.voice_usage_stats.items():
            print(f"  - {voice}: {count} áudios")
        
        print(f"")
        print(f"Estrutura de saída:")
        print(f"  {self.output_base_dir}/")
        for char_id in self.characters.keys():
            print(f"  ├── {char_id}/")
        print(f"{'='*60}")
    
    def list_available_voices(self):
        """Lista todas as vozes disponíveis no sistema"""
        print(f"\n🎤 VOZES DISPONÍVEIS NO SISTEMA")
        print(f"{'='*40}")
        
        if not self.available_voices:
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
            return
        
        print(f"Total: {len(self.available_voices)} arquivo(s)")
        print("-" * 40)
        
        for filename, path in self.available_voices.items():
            file_size = os.path.getsize(path) / 1024 / 1024  # MB
            print(f"📄 {filename}")
            print(f"   📍 {path}")
            print(f"   📊 {file_size:.1f} MB")
            print("-" * 20)
    
    def validate_setup(self) -> bool:
        """
        Valida se o sistema está configurado corretamente
        
        Returns:
            True se tudo está ok
        """
        issues = []
        
        # Verificar engines TTS
        available_engines = self.tts_manager.get_available_engines()
        if not available_engines:
            issues.append("Nenhuma engine TTS disponível")
        
        # Verificar mensagens carregadas
        if not self.messages:
            issues.append("Nenhuma mensagem carregada")
        
        # Verificar personagens
        if not self.characters:
            issues.append("Nenhum personagem encontrado")
        
        # Verificar se pelo menos uma voz está disponível
        has_voice = False
        if '_default' in self.prepared_voices:
            has_voice = True
        else:
            for character in self.characters.values():
                if character.voice_file:
                    has_voice = True
                    break
        
        if not has_voice:
            issues.append("Nenhuma voz disponível (nem padrão nem específica)")
        
        if issues:
            print("[ERROR] Problemas na configuração:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        else:
            print("[OK] Sistema configurado corretamente")
            return True 