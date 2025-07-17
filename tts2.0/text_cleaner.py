#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para limpeza e processamento de texto para TTS
"""

import re
from typing import List, Dict, Any
from config import TEXT_CLEANING

class TextCleaner:
    """Classe responsável pela limpeza e preparação de texto para TTS"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Inicializa o limpador de texto
        
        Args:
            config: Configurações de limpeza (usa TEXT_CLEANING se None)
        """
        self.config = config or TEXT_CLEANING
        
        # Padrão para detectar emojis
        self.emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # símbolos & pictogramas
            u"\U0001F680-\U0001F6FF"  # transporte & símbolos
            u"\U0001F1E0-\U0001F1FF"  # bandeiras (ISO 3166)
            u"\U00002702-\U000027B0"  # Dingbats
            u"\U000024C2-\U0001F251"  # enclosed characters
            u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "]+", flags=re.UNICODE)
        
        # Padrões para caracteres especiais (mais conservador)
        self.special_chars_pattern = re.compile(r'[^\w\s\.,!?;:\-\'\"()]')
        
        # Padrões para múltiplos espaços
        self.multiple_spaces_pattern = re.compile(r'\s+')
        
        # Padrões para pontuação problemática no TTS (mais específico)
        self.problematic_punctuation = re.compile(r'\.{3,}|…+')  # Apenas reticências múltiplas
    
    def remove_emojis(self, text: str) -> str:
        """Remove emojis do texto"""
        if not self.config.get('remove_emojis', True):
            return text
        return self.emoji_pattern.sub('', text)
    
    def remove_special_characters(self, text: str) -> str:
        """Remove caracteres especiais mantendo pontuação básica"""
        if not self.config.get('remove_special_chars', True):
            return text
        return self.special_chars_pattern.sub('', text)
    
    def normalize_punctuation(self, text: str) -> str:
        """Normaliza pontuação para melhor síntese TTS"""
        if not self.config.get('remove_dots', True):
            return text
        
        # Remove apenas reticências múltiplas, mantendo pontos finais importantes
        text = self.problematic_punctuation.sub('', text)
        
        # Substituir pontos finais por vírgulas para evitar cortes bruscos
        # mas manter o significado
        text = re.sub(r'\.(\s|$)', r',\1', text)
        
        # Remover pontuação que causa problemas específicos no TTS
        problematic_chars = ['…', '–', '—', '°', '™', '®', '©']
        for char in problematic_chars:
            text = text.replace(char, '')
        
        return text
    
    def add_speech_improvements(self, text: str) -> str:
        """Adiciona melhorias específicas para síntese de fala"""
        # Adicionar pausa pequena antes de pontuação importante
        text = re.sub(r'([,!?;:])', r' \1', text)
        
        # Adicionar espaço após pontuação se não houver
        text = re.sub(r'([,!?;:])([^\s])', r'\1 \2', text)
        
        # Garantir que frases terminem com uma pequena pausa
        if text.strip() and not text.strip().endswith(('!', '?', ':')):
            text = text.strip() + ' .'
        
        # Adicionar padding no final para evitar cortes
        text = text.strip() + ' '
        
        return text
    
    def fix_word_boundaries(self, text: str) -> str:
        """Corrige problemas de fronteiras de palavras"""
        # Garantir espaços corretos ao redor de hífen
        text = re.sub(r'(\w)-(\w)', r'\1 - \2', text)
        
        # Corrigir contrações comuns em português
        contractions = {
            'pra': 'para',
            'pro': 'para o',
            'pros': 'para os', 
            'pras': 'para as',
            'num': 'em um',
            'numa': 'em uma',
            'nuns': 'em uns',
            'numas': 'em umas',
            'dum': 'de um',
            'duma': 'de uma'
        }
        
        for contraction, expansion in contractions.items():
            # Usar word boundaries para evitar substituições incorretas
            pattern = r'\b' + re.escape(contraction) + r'\b'
            text = re.sub(pattern, expansion, text, flags=re.IGNORECASE)
        
        return text
    
    def normalize_spaces(self, text: str) -> str:
        """Normaliza espaços múltiplos"""
        if not self.config.get('normalize_spaces', True):
            return text
        
        # Normalizar múltiplos espaços para um só
        text = self.multiple_spaces_pattern.sub(' ', text)
        
        # Corrigir espaços antes de pontuação (exceto abertura)
        text = re.sub(r'\s+([,!?;:.\)])', r'\1', text)
        
        # Garantir espaço após pontuação de fechamento
        text = re.sub(r'([,!?;:.])([^\s])', r'\1 \2', text)
        
        return text.strip()
    
    def clean_text(self, text: str) -> str:
        """
        Aplica limpeza completa no texto com melhorias para TTS
        
        Args:
            text: Texto a ser limpo
            
        Returns:
            Texto limpo e otimizado para TTS
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Aplicar limpezas em sequência otimizada
        cleaned = text
        
        # 1. Remover emojis primeiro
        cleaned = self.remove_emojis(cleaned)
        
        # 2. Corrigir fronteiras de palavras antes de outras limpezas
        cleaned = self.fix_word_boundaries(cleaned)
        
        # 3. Remover caracteres especiais problemáticos
        cleaned = self.remove_special_characters(cleaned)
        
        # 4. Normalizar pontuação de forma inteligente
        cleaned = self.normalize_punctuation(cleaned)
        
        # 5. Adicionar melhorias específicas para fala
        cleaned = self.add_speech_improvements(cleaned)
        
        # 6. Normalizar espaços por último
        cleaned = self.normalize_spaces(cleaned)
        
        return cleaned
    
    def clean_message_batch(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Limpa o texto de uma lista de mensagens
        
        Args:
            messages: Lista de mensagens com campo 'texto'
            
        Returns:
            Lista de mensagens com texto limpo
        """
        cleaned_messages = []
        
        for message in messages:
            if not isinstance(message, dict):
                continue
                
            cleaned_message = message.copy()
            original_text = message.get('texto', '')
            cleaned_text = self.clean_text(original_text)
            
            # Adicionar campos de texto original e limpo
            cleaned_message['texto_original'] = original_text
            cleaned_message['texto'] = cleaned_text
            cleaned_message['texto_limpo'] = cleaned_text
            
            # Só adicionar se o texto limpo não estiver vazio
            if cleaned_text.strip():
                cleaned_messages.append(cleaned_message)
                
                # Debug info
                if len(original_text) != len(cleaned_text):
                    print(f"[DEBUG] Texto limpo: '{original_text}' → '{cleaned_text}'")
        
        return cleaned_messages
    
    def get_text_stats(self, original: str, cleaned: str) -> Dict[str, Any]:
        """
        Retorna estatísticas da limpeza de texto
        
        Args:
            original: Texto original
            cleaned: Texto limpo
            
        Returns:
            Dicionário com estatísticas
        """
        return {
            'original_length': len(original),
            'cleaned_length': len(cleaned),
            'chars_removed': len(original) - len(cleaned),
            'emojis_removed': len(self.emoji_pattern.findall(original)),
            'is_empty_after_cleaning': not bool(cleaned.strip()),
            'reduction_percentage': round(((len(original) - len(cleaned)) / max(len(original), 1)) * 100, 2),
            'has_speech_improvements': ' .' in cleaned or cleaned.endswith(' ')
        } 