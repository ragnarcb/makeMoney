# Sistema Modular de Geração de Vozes por Personagem

Sistema automatizado e modular para geração de áudios de texto-para-fala (TTS) com clonagem de voz, processando conversas JSON e gerando áudios separados por personagem.

## 🎯 Características Principais

- **Modular e Reutilizável**: Código separado em classes especializadas
- **Multi-Engine**: Suporte automático para Coqui TTS, RealtimeTTS e pyttsx3
- **Limpeza Inteligente**: Remove emojis, caracteres especiais e elementos que causam problemas no TTS
- **Clonagem de Voz**: Usa arquivo de referência para clonar voz
- **Personagens Genéricos**: Funciona com qualquer JSON de conversa, não limitado a aluno/professora
- **Processamento de Áudio**: Conversão automática para formatos compatíveis
- **Automação Completa**: Interface de linha de comando completa

## 📁 Estrutura dos Arquivos

```
tts2.0/
├── config.py                      # Configurações centralizadas
├── text_cleaner.py                # Limpeza e processamento de texto
├── audio_processor.py             # Processamento e conversão de áudio
├── tts_engines.py                 # Engines TTS abstraídas
├── character_voice_generator.py   # Classe principal do sistema
├── main.py                        # Script de automação
├── README_NOVO_SISTEMA.md         # Este arquivo
└── exemplo-mensagens.json         # Arquivo de exemplo
```

## 🚀 Instalação e Dependências

### Dependências Principais
```bash
# TTS com clonagem (recomendado)
pip install coqui-tts

# TTS básico (fallback)
pip install pyttsx3

# Processamento de áudio
pip install pydub soundfile librosa

# Opcional: RealtimeTTS
pip install RealtimeTTS
```

### FFmpeg (Recomendado)
- Windows: Baixar de https://ffmpeg.org/
- Linux: `sudo apt install ffmpeg`
- macOS: `brew install ffmpeg`

## 🎮 Como Usar

### 1. Uso Básico (Automático)
```bash
# Processar arquivo JSON padrão com todas as configurações automáticas
python main.py

# Ver informações sobre engines disponíveis
python main.py
```

### 2. Especificar Arquivos
```bash
# Usar arquivo JSON personalizado
python main.py --json-file minha_conversa.json

# Usar áudio de referência específico
python main.py --reference-audio minha_voz.wav

# Definir diretório de saída
python main.py --output-dir ./audios_gerados
```

### 3. Controle de Personagens
```bash
# Listar personagens disponíveis no JSON
python main.py --list-characters

# Gerar apenas um personagem específico
python main.py --character aluno
python main.py --character professora
python main.py --character personagem_customizado
```

### 4. Opções de Geração
```bash
# Desabilitar clonagem de voz (usar TTS básico)
python main.py --no-voice-cloning

# Gerar texto personalizado
python main.py --text "Olá, este é um teste" --output teste.wav
```

### 5. Relatórios e Validação
```bash
# Apenas validar sistema (não gerar áudios)
python main.py --validate-only

# Exportar relatório de geração
python main.py --export-report relatorio.json

# Modo silencioso
python main.py --quiet

# Modo verboso
python main.py --verbose
```

## 📋 Formato do JSON

O sistema aceita qualquer JSON com a seguinte estrutura:

```json
{
  "mensagens": [
    {
      "id": "1",
      "texto": "Texto da mensagem aqui",
      "usuario": {
        "id": "personagem_id",
        "nome": "Nome do Personagem"
      },
      "timestamp": "2024-01-15T14:30:00Z"
    }
  ]
}
```

### Personagens Suportados
- **Qualquer ID de personagem**: O sistema é genérico e funciona com qualquer ID
- **Múltiplos personagens**: Suporta quantos personagens existirem no JSON
- **Nomes personalizados**: Cada personagem pode ter nome diferente

## 🗂️ Estrutura de Saída

```
generated_audio/
├── personagem1/
│   ├── msg_1_personagem1.wav
│   ├── msg_3_personagem1.wav
│   └── msg_5_personagem1.wav
├── personagem2/
│   ├── msg_2_personagem2.wav
│   ├── msg_4_personagem2.wav
│   └── msg_6_personagem2.wav
└── generation_report.json
```

## 🧹 Limpeza de Texto

O sistema automaticamente remove/processa:

- ✅ **Emojis**: 😀🎉💯 → (removidos)
- ✅ **Caracteres especiais**: @#$%^& → (removidos)
- ✅ **Pontos finais**: "Olá." → "Olá" (evita TTS falar "ponto")
- ✅ **Reticências**: "..." → (removido)
- ✅ **Espaços múltiplos**: "texto   espaçado" → "texto espaçado"
- ✅ **Pontuação problemática**: Normaliza para TTS natural

## ⚙️ Engines TTS Suportadas

### 1. Coqui TTS (Recomendado)
- **Clonagem de voz**: ✅ Sim
- **Qualidade**: ⭐⭐⭐⭐⭐
- **Idiomas**: Multilíngue
- **Instalação**: `pip install coqui-tts`

### 2. RealtimeTTS
- **Clonagem de voz**: ✅ Sim
- **Qualidade**: ⭐⭐⭐⭐
- **Tempo real**: ✅ Otimizado
- **Instalação**: `pip install RealtimeTTS`

### 3. pyttsx3 (Fallback)
- **Clonagem de voz**: ❌ Não
- **Qualidade**: ⭐⭐⭐
- **Compatibilidade**: ⭐⭐⭐⭐⭐
- **Instalação**: `pip install pyttsx3`

## 🔧 Configuração Avançada

### Personalizar Configurações
Edite o arquivo `config.py` para ajustar:

```python
# Configurações de áudio
AUDIO_CONFIG = {
    'sample_rate': 22050,
    'channels': 1,
    'format': 'wav',
    'bit_depth': 16,
}

# Configurações de limpeza
TEXT_CLEANING = {
    'remove_emojis': True,
    'remove_special_chars': True,
    'remove_dots': True,
}
```

## 🐛 Solução de Problemas

### Engine TTS não encontrada
```bash
# Verificar engines disponíveis
python main.py

# Instalar Coqui TTS
pip install coqui-tts

# Instalar fallback
pip install pyttsx3
```

### Erro de conversão de áudio
```bash
# Instalar dependências de áudio
pip install pydub soundfile

# Instalar FFmpeg no sistema
# Windows: baixar de ffmpeg.org
# Linux: sudo apt install ffmpeg
```

### Arquivo de referência não encontrado
```bash
# Verificar se arquivo existe
ls "Vídeo sem título ‐ Feito com o Clipchamp.wav"

# Usar arquivo específico
python main.py --reference-audio meu_audio.wav
```

### JSON não carregado
```bash
# Verificar formato do JSON
python -m json.tool exemplo-mensagens.json

# Especificar caminho completo
python main.py --json-file /caminho/completo/arquivo.json
```

## 🔄 Migração do Sistema Antigo

### Principais Mudanças
1. **Modular**: Código separado em classes reutilizáveis
2. **Genérico**: Não limitado a aluno/professora
3. **Automatizado**: Interface de linha de comando completa
4. **Limpo**: Melhor limpeza de texto
5. **Robusto**: Múltiplas engines com fallback automático

### Como Migrar
1. Mantenha seus arquivos JSON no mesmo formato
2. Use o novo `main.py` em vez do script antigo
3. Configure `config.py` se necessário
4. Execute com `python main.py`

## 📊 Exemplo de Relatório

```json
{
  "timestamp": "2024-01-15T14:30:00",
  "statistics": {
    "total_messages": 10,
    "total_characters": 2,
    "successful_generations": 9,
    "failed_generations": 1,
    "success_rate": 90.0
  },
  "characters": {
    "aluno": {"name": "Lucas", "message_count": 5},
    "professora": {"name": "Prof. Marina", "message_count": 5}
  }
}
```

## 🤝 Contribuição

O sistema foi projetado para ser facilmente extensível:

1. **Novas engines TTS**: Herde de `TTSEngine` em `tts_engines.py`
2. **Processamento customizado**: Modifique `TextCleaner`
3. **Formatos de áudio**: Estenda `AudioProcessor`
4. **Novos recursos**: Adicione ao `CharacterVoiceGenerator`

## 📝 Licença

Sistema desenvolvido para uso educacional e pessoal. Respeite as licenças das dependências utilizadas (Coqui TTS, etc.). 