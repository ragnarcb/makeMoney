import os
from gtts import gTTS

def generate_tts(messages, out_dir, lang='pt-br'):
    os.makedirs(out_dir, exist_ok=True)
    audio_paths = []
    for i, msg in enumerate(messages):
        text = msg['text']
        tts = gTTS(text, lang=lang, slow=False)
        audio_path = os.path.join(out_dir, f"tts_msg_{i}.mp3")
        tts.save(audio_path)
        audio_paths.append(audio_path)
    # TODO: Use a TTS service that supports gender for true male/female voices
    return audio_paths 