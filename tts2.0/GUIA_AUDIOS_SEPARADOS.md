# GUIA - ÁUDIOS SEPARADOS POR MENSAGEM

## 📋 **Funcionalidades Implementadas**

### ✅ **1. Limpeza Automática de Texto**
- Remove **emojis** automaticamente (😅, 🔥, 💋, etc.)
- Remove **pontos** (.) para evitar que o TTS fale "ponto"
- Remove **reticências** (...) excessivas
- Limpa espaços múltiplos

**Exemplo:**
```
Texto original: "Oi professora! Preciso muito da sua ajuda com a matéria... 😅"
Texto limpo:    "Oi professora! Preciso muito da sua ajuda com a matéria"
```

### ✅ **2. Geração de Áudios Individuais por Personagem**
**Menu Principal → Opção 3 → Opção 4**

- Gera arquivos separados para cada mensagem
- Nomeia com ID da mensagem
- Cria pasta específica para o personagem

**Estrutura gerada:**
```
audios_aluno/
├── msg_1_aluno.wav
├── msg_3_aluno.wav
├── msg_5_aluno.wav
└── msg_7_aluno.wav
```

### ✅ **3. Geração COMPLETA da Conversa**
**Menu Principal → Opção 4**

- Gera TODOS os áudios de uma vez
- Separa por personagem em subpastas
- Relatório completo de geração

**Estrutura gerada:**
```
audios_conversa_completa/
├── aluno/
│   ├── msg_1_aluno.wav
│   ├── msg_3_aluno.wav
│   ├── msg_5_aluno.wav
│   ├── msg_7_aluno.wav
│   └── msg_9_aluno.wav
└── professora/
    ├── msg_2_professora.wav
    ├── msg_4_professora.wav
    ├── msg_6_professora.wav
    ├── msg_8_professora.wav
    └── msg_10_professora.wav
```

## 🎯 **Como Usar**

### **Para um personagem específico:**
1. Execute: `python usar_minha_voz.py`
2. Escolha opção **3** (JSON)
3. Escolha o personagem (1=Aluno, 2=Professora)
4. Escolha opção **4** (Gerar todos separados)

### **Para conversa completa:**
1. Execute: `python usar_minha_voz.py`
2. Escolha opção **4** (LOTE)
3. Aguarde o processamento

## 📊 **Relatório de Geração**

O sistema gera relatórios detalhados:

```
============================================================
RELATÓRIO COMPLETO DE GERAÇÃO
============================================================
Total de mensagens processadas: 10
Sucessos totais: 10
Erros totais: 0

Sucessos - Aluno Lucas: 5
Sucessos - Professora Marina: 5

Pasta principal: audios_conversa_completa
  ├── aluno/ (5 arquivos)
  └── professora/ (5 arquivos)
============================================================
```

## 🔧 **Recursos Técnicos**

- **Sistema TTS:** Coqui TTS (clonagem) ou pyttsx3 (fallback)
- **Formato:** WAV, 22050Hz, Mono
- **Fallback:** Sistema básico se Coqui TTS falhar
- **Validação:** Verifica arquivos gerados (>1KB para clonagem, >100B para básico)

## 📝 **Benefícios**

1. **Áudios organizados** por ID e personagem
2. **Texto limpo** sem emojis e pontos
3. **Relatórios detalhados** de progresso
4. **Fallback automático** se bibliotecas falharem
5. **Estrutura organizada** de pastas

## 🚀 **Próximos Passos**

Após gerar os áudios, você pode:
- Usar nos vídeos do makeMoney
- Importar no sistema de overlay
- Combinar com as imagens do WhatsApp clone
- Criar vídeos automaticamente 