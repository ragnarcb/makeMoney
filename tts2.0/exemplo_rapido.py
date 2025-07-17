#!/usr/bin/env python3
"""Exemplo rápido de uso do Coqui TTS"""

from TTS.api import TTS

# Inicializar TTS
print("Carregando modelo...")
tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2")

# Sintetizar texto
texto = "Olá! Este é um teste do Coqui TTS em português."
tts.tts_to_file(text=texto, file_path="teste_rapido.wav")

print("Áudio salvo como teste_rapido.wav")
