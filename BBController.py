import sys
# forçar saída UTF-8 no console Windows para evitar UnicodeEncodeError
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

# interceptar todas as chamadas a print e remover acentos/caracteres especiais
import builtins, unicodedata, re
_orig_print = print

def _sanitize_text(s: str) -> str:
    # normaliza e elimina marcas de acentuação
    nfkd = unicodedata.normalize('NFKD', s)
    no_accents = ''.join(c for c in nfkd if not unicodedata.combining(c))
    # filtra para ascii imprimível (32-126)
    return re.sub(r"[^\x20-\x7E]", '', no_accents)


def _print(*args, **kwargs):
    new_args = [ _sanitize_text(str(a)) for a in args ]
    return _orig_print(*new_args, **kwargs)

builtins.print = _print

sys.path.append("")
import traceback
import os
from datetime import datetime

from src.Automacao.ExtratoBancoDoBrasil.Services.ExtratoBBServices import ExtratosBB 
from src.Repository.masterSQLCom import MasterSQLComunication
from src.Services.TeamsService import TeamsService

id_bot = 2
sql_con = MasterSQLComunication()
ultima_exe = sql_con.ultima_execucao(id_bot)

try:
    if __name__ == '__main__':
        bancoBB = ExtratosBB(ultima_exe, 'downloaded_files')
        
        # Inicializar serviço do Teams
        webhook_url = bancoBB.config_restrito.get('teams', {}).get('webhook_url', '')
        teams_service = TeamsService(webhook_url, id_bot)
        
        # Data de hoje
        hoje = datetime.now().date()
        
        for carteira, dados in bancoBB.config_restrito['carteiras'].items():
            print(f"\n{'='*60}")
            print(f" Processando carteira: {carteira}")
            print(f"{'='*60}\n")
            
            bancoBB.fazer_login(dados['chave_j'], dados['senhabb'], dados['senha8bb'])
            bancoBB.acessar_relatorios()

            for dia in bancoBB.dias_atualizar:
                print(f"\n Processando dia: {dia.strftime('%d/%m/%Y')}")
                
                bancoBB.selecionar_dia_extratos(dia)
                mes = dia.strftime('%m')
                # decide base de armazenamento: usa 'carteira' se existir ou fallback para 'restrito'
                base_path = bancoBB.config_restrito['enderecos'].get('carteira') or bancoBB.config_restrito['enderecos'].get('restrito')
                pasta_final = os.path.abspath(f"{base_path}/Extratos_Bancarios/{carteira}/{dia.year}/{mes}")
                
                bancoBB.login_fundo(dados['num_conta'], dados['senha8bb'])
                
                # Download PDF
                bancoBB.fazer_download(carteira, pasta_final, 'Pdf')
                
                # Download Excel
                nome_excel = f"Extrato_BB_{carteira}_{dia.strftime('%d_%m_%Y')}.xlsx"
                caminho_excel = os.path.join(pasta_final, nome_excel)
                bancoBB.fazer_download(carteira, pasta_final, 'Excel')
                
                # Processar e enviar APENAS extrato de HOJE
                if dia.date() == hoje and os.path.exists(caminho_excel):
                    print(f" Processando extrato de hoje...")
                    dados_extrato = teams_service.processar_excel_extrato(caminho_excel)
                    
                    if dados_extrato:
                        if webhook_url:
                            print(f" Enviando para Teams...")
                            teams_service.enviar_extrato_teams(dados_extrato, carteira)
                        else:
                            print(f" Webhook não configurado - extrato não enviado")

            bancoBB.sair_sessao()

        bancoBB.fecha_navegador()
        sql_con.upload_log(id_bot)
        print(f"\n Processo concluído!")

except Exception as e:
    print(f"\n Erro: {e}")
    erro_completo = traceback.format_exc()
    sql_con.upload_log(id_bot, "1 - " + str(e) + " " + erro_completo)
    
    if 'teams_service' in locals() and webhook_url:
        teams_service.enviar_mensagem_erro(erro_completo)