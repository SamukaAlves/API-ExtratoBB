from datetime import datetime
import json
import os

class MasterSQLComunication:
    def __init__(self):
        self.log_file = 'config/ultima_execucao.json'
    
    def ultima_execucao(self, id_bot):
        # Tenta ler do arquivo de log
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
                    ultima = data.get(str(id_bot), '2026-02-20')
                    print(f"Última execução registrada: {ultima}")
                    return ultima
            except:
                pass
        
        # Primeira execução: começa de 1º de janeiro de 2026
        print(f"Primeira execução - começando de: 2026-01-01")
        return '2026-01-01'
    
    def upload_log(self, id_bot, erro=None):
        if erro:
            print(f"Erro: {erro}")
        else:
            # Salva a data de hoje como última execução
            hoje = datetime.now().strftime('%Y-%m-%d')
            
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {}
            
            data[str(id_bot)] = hoje
            
            os.makedirs('config', exist_ok=True)
            with open(self.log_file, 'w') as f:
                json.dump(data, f, indent=4)
            
            print(f"✅Execução bem-sucedida registrada para {hoje}")