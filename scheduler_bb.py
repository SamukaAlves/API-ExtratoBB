import schedule
import time
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_PATH = Path(__file__).parent / "BBController.py"
PYTHON_EXE = sys.executable

HORARIOS = ["09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00"]
DIAS_UTEIS = [0, 1, 2, 3, 4]  # segunda a sexta

executados_hoje = set()

def eh_dia_util():
    return datetime.now().weekday() in DIAS_UTEIS

def executar_script(horario):
    hoje = datetime.now().date()
    chave = f"{hoje}_{horario}"

    if not eh_dia_util():
        print("Hoje não é dia útil. Pulando execução.")
        return

    if chave in executados_hoje:
        print(f"Já executado hoje às {horario}")
        return

    print(f"Executando BBController.py às {horario}")

    try:
        resultado = subprocess.run(
            [PYTHON_EXE, str(SCRIPT_PATH)],
            cwd=SCRIPT_PATH.parent,
            capture_output=True,
            text=True,
            timeout=1800
        )

        if resultado.stdout:
            print(resultado.stdout)

        if resultado.returncode == 0:
            print("Execução concluída com sucesso")
            executados_hoje.add(chave)
        else:
            print("Erro na execução:")
            print(resultado.stderr)

    except Exception as e:
        print(f"Falha ao executar: {e}")

def limpar_controle_diario():
    executados_hoje.clear()
    print("Controle diário resetado")

# agenda horários
for h in HORARIOS:
    schedule.every().day.at(h).do(executar_script, horario=h)
    print(f"Agendado: {h}")

# limpa controle à meia-noite
schedule.every().day.at("00:00").do(limpar_controle_diario)

print("Scheduler iniciado...")

while True:
    schedule.run_pending()
    time.sleep(30)