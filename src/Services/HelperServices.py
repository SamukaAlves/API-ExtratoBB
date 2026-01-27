from datetime import datetime, timedelta
import json

class ServicosGerais:
    def abrir_config(self, tipo=''):
        arquivo = 'config/config.json' if not tipo else 'config/configRestrito.json'
        with open(arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def pega_d_menos_x_dias(self, dias, data_especifica=None):
        """
        dias=1: retorna a data 1 dia antes de data_especifica
        dias=0: retorna lista de datas desde data_especifica até HOJE
        """
        hoje = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        if data_especifica:
            if isinstance(data_especifica, str):
                data_base = datetime.strptime(data_especifica, '%Y-%m-%d')
            else:
                data_base = data_especifica
        else:
            data_base = hoje
        
        if dias == 1:
            # Retorna [data_base - 1 dia]
            resultado = data_base - timedelta(days=1)
            return [resultado]
        
        elif dias == 0:
            # Lista desde data_base até hoje (inclusive)
            lista_datas = []
            data_atual = data_base
            
            while data_atual <= hoje:
                lista_datas.append(data_atual)
                data_atual += timedelta(days=1)
            
            print(f"Período: {lista_datas[0].strftime('%d/%m/%Y') if lista_datas else 'vazio'} até {lista_datas[-1].strftime('%d/%m/%Y') if lista_datas else 'vazio'}")
            print(f"Total de dias: {len(lista_datas)}")
            return lista_datas
        
        else:
            resultado = data_base - timedelta(days=dias)
            return [resultado]