import schedule
import time
import subprocess
import sys
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path

# Configuracao de logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'scheduler_bb.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class BBScheduler:
    def __init__(self):
        self.script_path = Path(__file__).parent / "BBController.py"
        self.python_exe = sys.executable
        self.execucoes_hoje = set()
        self.max_tentativas = 3
        self.intervalo_retry = 60  # segundos
        
        # Horarios de execucao (em dias uteis)
        self.horarios = ["09:00", "11:00", "12:30", "15:00", "17:00"]
        
        # Dias da semana (0=segunda, 4=sexta)
        self.dias_uteis = [0, 1, 2, 3, 4]
        
        logger.info("=" * 70)
        logger.info("Scheduler BB iniciado (modo residente)")
        logger.info(f"Horarios de execucao: {', '.join(self.horarios)}")
        logger.info(f"Dias da semana: {self.dias_uteis}")
        logger.info(f"Log: {log_dir / 'scheduler_bb.log'}")
        logger.info("=" * 70)
    
    def eh_dia_util(self):
        """Verifica se hoje e dia util"""
        return datetime.now().weekday() in self.dias_uteis
    
    def ja_executou_hoje(self, horario):
        """Verifica se ja executou neste horario hoje"""
        hoje = datetime.now().date()
        chave = f"{hoje}_{horario}"
        return chave in self.execucoes_hoje
    
    def marcar_execucao(self, horario):
        """Marca que executou neste horario"""
        hoje = datetime.now().date()
        chave = f"{hoje}_{horario}"
        self.execucoes_hoje.add(chave)
    
    def limpar_rastreamento_diario(self):
        """Limpa rastreamento a meia-noite"""
        self.execucoes_hoje.clear()
        logger.info("Limpando rastreamento diario...")
    
    def executar_bb_controller(self, horario):
        """Executa o BBController.py com retry"""
        
        # Verificar se e dia util
        if not self.eh_dia_util():
            logger.info(f"Pulando execucao - hoje nao e dia util")
            return
        
        # Verificar se ja executou neste horario hoje
        if self.ja_executou_hoje(horario):
            logger.info(f"Ja executado hoje as {horario}")
            return
        
        logger.info(f"Horario de execucao: {horario}")
        
        for tentativa in range(1, self.max_tentativas + 1):
            try:
                logger.info(f"Iniciando execucao do BB Controller (tentativa {tentativa}/{self.max_tentativas})")
                
                # Executar o script
                resultado = subprocess.run(
                    [self.python_exe, str(self.script_path)],
                    capture_output=True,
                    text=True,
                    cwd=self.script_path.parent,
                    timeout=1800  # 30 minutos de timeout
                )
                
                # Exibir saida
                if resultado.stdout:
                    print(resultado.stdout)
                
                if resultado.returncode == 0:
                    logger.info(f"Execucao concluida com sucesso!")
                    self.marcar_execucao(horario)
                    return
                else:
                    erro_msg = resultado.stderr if resultado.stderr else "Erro desconhecido"
                    logger.error(f"Erro na execucao: {erro_msg}")
                    
                    if tentativa < self.max_tentativas:
                        logger.info(f"Aguardando {self.intervalo_retry}s para nova tentativa...")
                        time.sleep(self.intervalo_retry)
                    
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout na tentativa {tentativa}")
                if tentativa < self.max_tentativas:
                    logger.info(f"Aguardando {self.intervalo_retry}s para nova tentativa...")
                    time.sleep(self.intervalo_retry)
                    
            except Exception as e:
                logger.error(f"Erro na tentativa {tentativa}: {e}")
                if tentativa < self.max_tentativas:
                    logger.info(f"Aguardando {self.intervalo_retry}s para nova tentativa...")
                    time.sleep(self.intervalo_retry)
        
        logger.error("Automacao falhou apos 3 tentativas")
    
    def agendar_execucoes(self):
        """Agenda todas as execucoes"""
        for horario in self.horarios:
            schedule.every().day.at(horario).do(
                self.executar_bb_controller, 
                horario=horario
            )
            logger.info(f"Agendado: {horario}")
        
        # Limpar rastreamento a meia-noite
        schedule.every().day.at("00:00").do(self.limpar_rastreamento_diario)
        
        logger.info("Configuracoes carregadas com sucesso")
    
    def iniciar(self):
        """Inicia o loop do scheduler"""
        self.agendar_execucoes()
        
        logger.info(f"\nProxima execucao: {schedule.next_run()}\n")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verifica a cada 1 minuto
                
        except KeyboardInterrupt:
            logger.info("\nScheduler interrompido pelo usuario")
        except Exception as e:
            logger.error(f"Erro critico no scheduler: {e}")
            raise

def main():
    print("=" * 40)
    print("  Scheduler BB - Extrato Bancario")
    print("=" * 40)
    print()
    print("Verificando dependencias...")
    
    # Verificar se BBController.py existe
    controller_path = Path(__file__).parent / "BBController.py"
    if not controller_path.exists():
        print(f"ERRO: Arquivo nao encontrado: {controller_path}")
        sys.exit(1)
    
    print()
    print("Iniciando Scheduler...")
    print()
    print("AVISO: O scheduler permanecera ativo em background")
    print("AVISO: Pressione Ctrl+C para interromper")
    print()
    
    scheduler = BBScheduler()
    scheduler.iniciar()

if __name__ == "__main__":
    main()