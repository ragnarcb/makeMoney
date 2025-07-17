# Automação de Captura WhatsApp com Playwright

Este sistema permite capturar mensagens do WhatsApp Clone de forma automatizada usando Playwright.

## Recursos

- **Captura Individual**: Cada mensagem é capturada separadamente
- **Captura de Tela Completa**: Screenshot de toda a conversa (com scroll automático)
- **Captura por Scroll**: Captura a tela em partes com scroll automático ou imagem única
- **Modo Headless**: Execução em segundo plano sem interface gráfica
- **Relatórios**: Geração automática de relatórios JSON com detalhes das capturas

## Instalação

### Pré-requisitos

- Python 3.7+
- Node.js (para executar o WhatsApp Clone)

### Instalação Automática

O sistema instalará automaticamente as dependências necessárias:

```bash
cd print
python run_capture.py
```

### Instalação Manual

```bash
# Instalar Playwright
pip install playwright

# Instalar browser Chromium
playwright install chromium
```

## Uso

### 1. Modo Interativo (Recomendado)

Execute o script helper para um menu interativo:

```bash
python run_capture.py
```

### 2. Comandos Diretos

#### Captura Individual (mensagem por mensagem)
```bash
python whatsapp_screenshot_automation.py --mode individual --headless --include-header
```

#### Captura de Tela Completa
```bash
python whatsapp_screenshot_automation.py --mode full --headless --include-header
```

#### Captura por Scroll
```bash
python whatsapp_screenshot_automation.py --mode scroll --headless --include-header
```

### 3. Parâmetros Disponíveis

| Parâmetro | Descrição | Padrão |
|-----------|-----------|---------|
| `--mode` | Modo de captura (individual, full, scroll) | individual |
| `--url` | URL da aplicação WhatsApp | http://localhost:8089 |
| `--output` | Diretório de saída | screenshots |
| `--headless` | Executar sem interface gráfica | false |
| `--include-header` | Incluir captura do header | false |
| `--scroll-amount` | Quantidade de scroll em pixels | 300 |
| `--scroll-delay` | Delay entre scrolls em ms | 1000 |

## Estrutura de Saída

O sistema cria um diretório com timestamp contendo:

```
screenshots_20240115_143000/
├── header.png                    # Header do WhatsApp (se solicitado)
├── message_001_20240115_143001.png  # Mensagem 1
├── message_002_20240115_143002.png  # Mensagem 2
├── ...
└── capture_report.json           # Relatório detalhado
```

## Configuração do Ambiente

### 1. Iniciar o WhatsApp Clone

```bash
cd front/whatsapp-clone
npm start
```

### 2. Executar a Automação

```bash
cd print
python run_capture.py
```

## Exemplos de Uso

### Captura Individual com Header
```bash
python whatsapp_screenshot_automation.py \
  --mode individual \
  --include-header \
  --output capturas_individuais
```

### Captura por Scroll Personalizada
```bash
python whatsapp_screenshot_automation.py \
  --mode scroll \
  --scroll-amount 500 \
  --scroll-delay 2000 \
  --headless \
  --output capturas_scroll
```

### Captura de URL Específica
```bash
python whatsapp_screenshot_automation.py \
  --mode full \
  --url http://localhost:8089 \
  --headless
```

## Solução de Problemas

### Erro: "Aplicação não encontrada"
- Verifique se o WhatsApp Clone está rodando na URL especificada
- Confirme que a URL está correta (padrão: http://localhost:8089)

### Erro: "Nenhuma mensagem encontrada"
- Verifique se as mensagens estão sendo renderizadas corretamente
- Confirme que os seletores CSS estão corretos (.message-wrapper)

### Erro: "Browser não encontrado"
- Execute: `playwright install chromium`
- Verifique se o Playwright foi instalado corretamente

### Problemas de Codificação no Windows
- O sistema foi configurado para usar caracteres ASCII simples
- Evite emojis no terminal do Windows

## Relatório de Captura

O arquivo `capture_report.json` contém:

```json
{
  "timestamp": "2024-01-15T14:30:00",
  "total_screenshots": 15,
  "output_directory": "screenshots_20240115_143000",
  "screenshots": [
    {
      "filename": "header.png",
      "path": "screenshots_20240115_143000/header.png",
      "size": 45678,
      "created": "2024-01-15T14:30:01"
    }
  ]
}
```

## Arquivos do Sistema

- `whatsapp_screenshot_automation.py`: Script principal de automação
- `run_capture.py`: Script helper com menu interativo
- `requirements.txt`: Dependências do projeto
- `README.md`: Esta documentação

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes. 