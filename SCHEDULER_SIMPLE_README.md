# 🛠 Scheduler 

Este documento descreve a versão mais enxuta do `scheduler_bb.py`, que não depende de arquivos de configuração externos e executa o `BBController.py` em horários pré‑definidos.

---

## ⚙️ Comportamento

- Usa a biblioteca [schedule](https://pypi.org/project/schedule/) para agendar tarefas em horário fixo.
- Horários e dias úteis são definidos diretamente no código por listas (`HORARIOS` e `DIAS_UTEIS`).
- Mantém um conjunto em memória (`executados_hoje`) para evitar rodar múltiplas vezes no mesmo dia/horário.
- Na virada do dia (`00:00`) o controle diário é resetado automaticamente.
- Dispara o script `BBController.py` via subprocesso Python, capturando saída e exibindo no console.
- Ignora sábados e domingos; imprime mensagens de debug simples no console.

---

## 📝 Constantes relevantes

```python
HORARIOS = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
DIAS_UTEIS = [0, 1, 2, 3, 4]  # segunda a sexta
```

Edite essas listas caso deseje alterar os horários ou permitir fins de semana.

## 🚀 Execução

Inicie o scheduler simplesmente com:

```bash
python scheduler_bb.py
```

Não há parâmetros nem arquivos de configuração adicionais.

---

## 🧰 Requisitos

- Python (mesma versão usada pelo projeto)
- Pacote `schedule` (instale via `pip install schedule` se necessário)

---

## 🛑 Parada

Abrir o terminal e pressionar `Ctrl+C`.

---

Esta documentação complementa o README principal e pode ser mantida junto caso a versão simplificada seja utilizada em ambientes de teste ou desenvolvimento rápido.