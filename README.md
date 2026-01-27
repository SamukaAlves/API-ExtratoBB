# API-ExtratoBB

Automação para baixar extratos da conta corrente do Banco do Brasil, processar os arquivos Excel e enviar um resumo formatado para um canal do **Microsoft Teams** via webhook.

## O que faz

- Acessa o portal do BB (autoatendimento PJ, Chave J)
- Faz login e navega até os relatórios de extrato
- Baixa **PDF** e **Excel** por carteira e por dia
- Processa o Excel do **dia atual**: extrai saldo anterior, lançamentos e saldo atual
- Envia um extrato compacto e legível para o Teams (incluindo visualização em celular)
- Registra última execução em `config/ultima_execucao.json`

## Estrutura do projeto

```
API-ExtratoBB/
├── BBController.py          # Orquestra login, download e envio ao Teams
├── executar_bb.bat          # Atalho para rodar no Windows
├── config/
│   ├── config.json          # URL do site do BB (público)
│   ├── configRestrito.json  # Carteiras, credenciais e webhook Teams (sensível)
│   └── ultima_execucao.json # Última data processada por bot
├── downloaded_files/       # PDF/Excel baixados (ex.: pasta de trabalho)
├── src/
│   ├── Automacao/ExtratoBancoDoBrasil/Services/
│   │   └── ExtratoBBServices.py  # Selenium: login, relatórios, download
│   ├── Repository/
│   │   └── masterSQLCom.py       # Leitura/gravação de última execução
│   └── Services/
│       ├── TeamsService.py       # Processa Excel e envia para Teams
│       ├── WebServices.py        # Driver do navegador (SeleniumBase)
│       └── HelperServices.py    # Config e datas
└── requirements.txt
```

## Pré-requisitos

- **Python 3.10+**
- **Chrome** (ou Edge/Firefox) instalado para a automação
- Conta PJ no Banco do Brasil com acesso por Chave J
- Webhook do Teams configurado no canal de destino

## Instalação

1. Clone ou copie o projeto e entre na pasta:

   ```bash
   cd API-ExtratoBB
   ```

2. Crie um ambiente virtual (recomendado):

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. Instale as dependências:

   ```bash
   pip install -r requirements.txt
   ```

4. Ajuste os arquivos de configuração:
   - **config/config.json** – já deve conter a URL do BB
   - **config/configRestrito.json** – coloque:
     - credenciais das carteiras (chave J, senhas)
     - webhook do Teams em `banco_do_brasil.teams.webhook_url`

## Uso

### Windows (batch)

```batch
executar_bb.bat
```

Ajuste o caminho dentro do `.bat` se o projeto estiver em outro diretório.

### Linha de comando

```bash
python BBController.py
```

O script:

- Faz login por carteira
- Baixa PDF e Excel dos dias configurados (a partir da última execução)
- Para o **dia de hoje**, se existir Excel:
  - Processa o extrato (colunas do layout BB: Histórico em H, Valor em I, C/D em J, etc.)
  - Formata em texto compacto (~58 caracteres de largura)
  - Envia para o webhook do Teams

## Formato da mensagem no Teams

O extrato enviado tem:

- Cabeçalho: agência, conta, período
- Tabela de lançamentos: Data, Histórico, Doc, Valor R$
- Saldo anterior e saldo atual (da coluna I e da linha “Saldo” com valor em B)
- Datas de débito de juros e IOF (quando existirem)

Layout pensado para ficar alinhado, sem quebrar a largura no celular e com colunas bem separadas.

## Configuração restrita

Em `config/configRestrito.json` é onde ficam dados sensíveis. Exemplo de estrutura (valores são ilustrativos):

```json
{
  "banco_do_brasil": {
    "teams": {
      "webhook_url": "https://outlook.office.com/webhook/..."
    },
    "carteiras": {
      "JUSMP": {
        "chave_j": "...",
        "senhabb": "...",
        "senha8bb": "...",
        "num_conta": "..."
      }
    }
  }
}
```

**Importante:** não versionar `configRestrito.json` com credenciais reais. O arquivo já está no `.gitignore` e não será enviado ao GitHub.

## Subir para o GitHub (ignorando configRestrito)

O projeto já usa um **`.gitignore`** que ignora:

- **config/configRestrito.json** – credenciais e webhook (nunca sobe)
- **downloaded_files/** – PDFs e Excels baixados
- **venv/**, **__pycache__/** – ambiente Python e cache

Para publicar no repositório:

1. Crie o repositório no GitHub (ex.: `API-ExtratoBB`).

2. Na pasta do projeto, inicialize o Git (se ainda não tiver):
   ```bash
   git init
   git add .
   git status   # confira: configRestrito.json NÃO deve aparecer
   ```

3. Faça o primeiro commit e envie:
   ```bash
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/API-ExtratoBB.git
   git push -u origin main
   ```

Quem clonar o repositório precisará **criar localmente** o arquivo `config/configRestrito.json` com as credenciais e o webhook (use o exemplo da seção “Configuração restrita” acima como modelo).

## Licença

Uso interno. Ajuste conforme a política da sua organização.
