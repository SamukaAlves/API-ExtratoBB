# 🤖 Scheduler BB - Automação de Extratos Bancários

Solução de **agendamento residente** para executar a automação de extratos do Banco do Brasil em horários pré-configurados.

---

## 📋 Funcionalidades

✅ **Execução Automática**: Executa em horários pré-configurados (ex: 09:00, 12:00, 15:00)  
✅ **Dias Úteis**: Roda apenas de segunda a sexta  
✅ **Sistema de Retry**: Tenta novamente em caso de falha (até 3 tentativas)  
✅ **Logging Detalhado**: Registra todas as ações em `logs/scheduler_bb.log`  
✅ **Rastreamento de Sessão**: Atualiza última execução após sucesso  
✅ **Modo Residente**: Mantém-se ativo indefinidamente  

---

## 🚀 Como Usar

### 1️⃣ Iniciar o Scheduler

**Opção A: Via arquivo .bat (recomendado no Windows)**
```bash
executar_scheduler.bat
```

**Opção B: Linha de comando**
```bash
python scheduler_bb.py
```

### 2️⃣ Configurar Horários

Edite o arquivo `config/config.json`:

```json
{
    "scheduler": {
        "horarios_execucao": ["09:00", "12:00", "15:00"],
        "dias_semana": [0, 1, 2, 3, 4],
        "max_tentativas": 3,
        "intervalo_retry_segundos": 60,
        "intervalo_verificacao_segundos": 30
    }
}
```

**Explicação dos campos:**
- `horarios_execucao`: Horários em que a automação executa (formato 24h)
- `dias_semana`: 0=Seg, 1=Ter, 2=Qua, 3=Qui, 4=Sex, 5=Sab, 6=Dom
- `max_tentativas`: Quantas vezes tenta se falhar
- `intervalo_retry_segundos`: Segundos entre tentativas
- `intervalo_verificacao_segundos`: Intervalo de verificação de horário

### 3️⃣ Monitorar Execução

**Arquivo de log:**
```bash
logs/scheduler_bb.log
```

**Exemplo de saída:**
```
2026-02-09 09:00:05 - INFO - ⏰ Horário de execução: 09:00
2026-02-09 09:00:06 - INFO - 🚀 Iniciando execução do BB Controller (tentativa 1/3)
2026-02-09 09:01:23 - INFO - 🏦 Processando carteira: carteira_1
2026-02-09 09:02:45 - INFO - 📤 Enviando para Teams...
2026-02-09 09:02:48 - INFO - ✅ Extrato enviado para o Teams!
2026-02-09 09:02:49 - INFO - ✅ Processo concluído com sucesso!
```

---

## ⚙️ Arquitetura

```
scheduler_bb.py (NOVO)
    ↓
    └─→ BBController.py (existente)
        ├─→ ExtratoBBServices.py
        ├─→ TeamsService.py (MODIFICADO)
        │   ├─→ Processa Excel
        │   ├─→ Monta Adaptive Card
        │   ├─→ Envia para Teams
        │   └─→ Atualiza última execução ✨
        └─→ MasterSQLComunication.py
```

---

## 🔧 Integração com BBController

O `scheduler_bb.py` executa a mesma lógica do `BBController.py`, mas em loop residente:

1. **Verifica a hora atual**
2. **Se é horário de execução**, chama `executar_bb_controller()`
3. **Sistema de retry** em caso de erro
4. **Rastreia execuções** para não duplicar no mesmo dia/horário
5. **Volta ao sono** por 30 segundos e repete

---

## 📝 Principais Mudanças

### ✨ TeamsService.py
```python
# ANTES
teams_service = TeamsService(webhook_url)

# DEPOIS
teams_service = TeamsService(webhook_url, id_bot)

# Agora atualiza automaticamente última execução após sucesso
```

### 📄 BBController.py
```python
# Atualizado para passar id_bot
teams_service = TeamsService(webhook_url, id_bot)
```

### 📋 config/config.json
```json
// NOVO: Seção scheduler com configurações
"scheduler": {
    "horarios_execucao": ["09:00", "12:00", "15:00"],
    ...
}
```

---

## 🛑 Parar a Execução

**No terminal:**
```
Pressione Ctrl+C
```

---

## 📊 Exemplos de Configuração

### Exemplo 1: Executor a manhã toda (8h, 9h, 10h, 11h)
```json
"horarios_execucao": ["08:00", "09:00", "10:00", "11:00"]
```

### Exemplo 2: Apenas de segunda, quarta e sexta
```json
"dias_semana": [0, 2, 4]  // segunda (0), quarta (2), sexta (4)
```

### Exemplo 3: Máximo de 5 tentativas com intervalo de 2 minutos
```json
"max_tentativas": 5,
"intervalo_retry_segundos": 120
```

---

## 🐛 Troubleshooting

### "Python não encontrado"
- Instale Python (https://www.python.org/)
- Adicione Python ao PATH

### "ModuleNotFoundError"
- Instale dependências:
```bash
pip install -r requirements.txt
```

### "Webhook não configurado"
- Verifique `config/configRestrito.json`
- Certifique-se que Teams webhook está preenchido

### Logs vazios
- Verifique pasta `logs/` existe
- Verifique permissões de escrita

---

## 📞 Suporte

Se precisar ajustar:
1. Horários de execução
2. Dias da semana
3. Número de tentativas
4. Intervalo entre verificações

Edite `config/config.json` ✏️

---

**Status:** ✅ Pronto para produção  
**Versão:** 1.0  
**Data:** 09/02/2026
