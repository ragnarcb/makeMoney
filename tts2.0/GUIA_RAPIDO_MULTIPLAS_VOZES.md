# 🎤 Guia Rápido: Sistema TTS com Múltiplas Vozes

## 🚀 Como Usar (Método Mais Simples)

### 1. Execução da Raiz do Projeto
```bash
# Se estiver na pasta raiz do projeto
python run_tts.py

# Ver opções disponíveis
python run_tts.py --help
```

### 2. Execução da Pasta tts2.0
```bash
cd tts2.0
python main.py
```

## 🎯 Funcionalidades Principais

### ✅ Sistema Detecta Vozes Automaticamente

**Padrões de Nomeação Automática:**
- `voz_aluno.wav` → personagem "aluno"
- `voice_professora.wav` → personagem "professora"  
- `cliente_voice.wav` → personagem "cliente"
- `moderador.wav` → personagem "moderador"

**Onde colocar os arquivos de voz:**
- `tts2.0/` (pasta principal)
- `tts2.0/voices/` (subpasta)
- `./voices/` (se executar da raiz)

### 🎪 Comandos Essenciais

```bash
# 1. Ver vozes disponíveis no sistema
python run_tts.py --list-voices

# 2. Ver personagens no JSON
python run_tts.py --list-characters --json-file exemplo_multiplos_personagens.json

# 3. Ver mapeamento atual de vozes
python run_tts.py --show-voice-mapping --json-file exemplo_multiplos_personagens.json

# 4. Processar JSON com detecção automática
python run_tts.py --json-file exemplo_multiplos_personagens.json

# 5. Mapear vozes manualmente
python run_tts.py --voice-map aluno:voz_aluno.wav professora:voz_professora.wav cliente:voz_cliente.wav
```

## 📂 Exemplo Prático Completo

### Estrutura de Arquivos Recomendada:
```
makeMoney/
├── run_tts.py                    # Script da raiz
├── tts2.0/
│   ├── main.py                   # Script principal
│   ├── exemplo_multiplos_personagens.json
│   ├── voz_aluno.wav            # Voz do Lucas
│   ├── voz_professora.wav       # Voz da Prof. Marina
│   ├── voz_moderador.wav        # Voz do Dr. Carlos
│   ├── voz_cliente.wav          # Voz do Roberto
│   └── voz_pesquisador.wav      # Voz da Dra. Ana
```

### Comando Completo:
```bash
# Da raiz do projeto
python run_tts.py \
  --json-file exemplo_multiplos_personagens.json \
  --export-report relatorio_multiplas_vozes.json \
  --verbose
```

## 🎭 Exemplos por Cenário

### Cenário 1: Detecção Automática (Mais Fácil)
```bash
# 1. Coloque as vozes com nomes corretos:
#    - voz_aluno.wav
#    - voz_professora.wav  
#    - voz_moderador.wav

# 2. Execute:
python run_tts.py --json-file exemplo_multiplos_personagens.json

# ✅ Sistema detecta automaticamente!
```

### Cenário 2: Mapeamento Manual
```bash
# Se os arquivos têm nomes diferentes
python run_tts.py \
  --json-file exemplo_multiplos_personagens.json \
  --voice-map \
    aluno:lucas_voice.wav \
    professora:marina_prof.wav \
    moderador:carlos_doutor.wav \
    cliente:roberto_cliente.wav \
    pesquisador:ana_doutora.wav
```

### Cenário 3: Personagem Específico
```bash
# Gerar apenas áudios do aluno Lucas
python run_tts.py \
  --json-file exemplo_multiplos_personagens.json \
  --character aluno
```

### Cenário 4: Texto Personalizado com Voz Específica  
```bash
# Falar texto com voz específica
python run_tts.py \
  --text "Esta é uma mensagem personalizada" \
  --voice voz_aluno.wav \
  --output mensagem_personalizada.wav
```

## 📊 Verificação e Debug

### Ver Status do Sistema:
```bash
# Verificar engines TTS disponíveis
python run_tts.py

# Validar configuração completa
python run_tts.py --validate-only
```

### Diagnóstico de Problemas:
```bash
# Ver logs detalhados
python run_tts.py --verbose --json-file exemplo_multiplos_personagens.json

# Ver apenas mapeamento sem gerar áudios
python run_tts.py --show-voice-mapping --json-file exemplo_multiplos_personagens.json
```

## 🗂️ Estrutura de Saída

```
generated_audio/
├── aluno/
│   ├── msg_2_aluno.wav          # "Bom dia! Estou muito animado..."
│   ├── msg_6_aluno.wav          # "Concordo plenamente..."
│   └── msg_11_aluno.wav         # "Posso ajudar com a documentação..."
├── professora/
│   ├── msg_3_professora.wav     # "Olá a todos! Vamos começar..."
│   ├── msg_7_professora.wav     # "Excelente trabalho!..."
│   └── msg_12_professora.wav    # "Ótima ideia! Vamos dividir..."
├── moderador/
│   ├── msg_1_moderador.wav      # "Olá pessoal! Sejam bem-vindos..."
│   ├── msg_8_moderador.wav      # "Temos alguma dúvida..."
│   └── msg_13_moderador.wav     # "Perfeito! Então está decidido..."
├── cliente/
│   ├── msg_4_cliente.wav        # "Perfeito! Tenho algumas questões..."
│   ├── msg_9_cliente.wav        # "Sim, gostaria de entender..."
│   └── msg_14_cliente.wav       # "Agradeço a participação..."
└── pesquisador/
    ├── msg_5_pesquisador.wav    # "Vou apresentar os resultados..."
    ├── msg_10_pesquisador.wav   # "Baseado nos nossos estudos..."
    └── msg_15_pesquisador.wav   # "Foi um prazer contribuir..."
```

## ⚡ Instalação Rápida

```bash
# Instalar dependências automaticamente
cd tts2.0
python install_dependencies.py

# Testar sistema
python test_system.py

# Usar sistema
python main.py --list-voices
```

## 🎯 Casos de Uso Comuns

### Para Podcasts/Vídeos:
```bash
python run_tts.py \
  --json-file minha_conversa.json \
  --voice-map host:voz_host.wav convidado:voz_convidado.wav
```

### Para Audiolivros:
```bash
python run_tts.py \
  --json-file capitulos.json \
  --voice-map narrador:voz_narrador.wav personagem1:voz_p1.wav
```

### Para Apresentações:
```bash
python run_tts.py \
  --json-file apresentacao.json \
  --voice-map apresentador:voz_formal.wav
```

## 🔧 Dicas Importantes

1. **Formatos de áudio suportados:** WAV, MP3, FLAC, M4A, OGG
2. **Qualidade recomendada:** 22050 Hz, Mono, WAV
3. **Tamanho dos arquivos:** O sistema converte automaticamente
4. **Múltiplas vozes:** Cada personagem pode ter sua própria voz
5. **Fallback:** Se não encontrar voz específica, usa voz padrão ou TTS básico

## 🆘 Solução de Problemas

### "Módulos não encontrados":
```bash
# Execute da pasta correta ou use o script da raiz
python run_tts.py  # Da raiz
# OU
cd tts2.0 && python main.py  # Da pasta tts2.0
```

### "Nenhuma voz encontrada":
```bash
# Ver onde colocar vozes
python run_tts.py --list-voices

# Verificar nomes dos arquivos
ls *.wav  # Ver arquivos de áudio disponíveis
```

### "Engine TTS não disponível":
```bash
# Instalar dependências
python install_dependencies.py
```

---

**🎉 Sistema pronto! Agora você pode ter vozes diferentes para cada personagem!** 