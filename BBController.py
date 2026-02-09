import sys
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
        teams_service = TeamsService(webhook_url)
        
        # Data de hoje
        hoje = datetime.now().date()
        
        for carteira, dados in bancoBB.config_restrito['carteiras'].items():
            print(f"\n{'='*60}")
            print(f"🏦 Processando carteira: {carteira}")
            print(f"{'='*60}\n")
            
            bancoBB.fazer_login(dados['chave_j'], dados['senhabb'], dados['senha8bb'])
            bancoBB.acessar_relatorios()

            for dia in bancoBB.dias_atualizar:
                print(f"\n📅 Processando dia: {dia.strftime('%d/%m/%Y')}")
                
                bancoBB.selecionar_dia_extratos(dia)
                pasta_final = os.path.abspath(f"{bancoBB.config_restrito['enderecos']['carteira']}/{dia.year}")
                
                bancoBB.login_fundo(dados['num_conta'], dados['senha8bb'])
                
                # Download PDF
                bancoBB.fazer_download(carteira, pasta_final, 'Pdf')
                
                # Download Excel
                nome_excel = f"Extrato_BB_{carteira}_{dia.strftime('%d_%m_%Y')}.xlsx"
                caminho_excel = os.path.join(pasta_final, nome_excel)
                bancoBB.fazer_download(carteira, pasta_final, 'Excel')
                
                # Processar e enviar APENAS extrato de HOJE
                if dia.date() == hoje and os.path.exists(caminho_excel):
                    print(f"📊 Processando extrato de hoje...")
                    dados_extrato = teams_service.processar_excel_extrato(caminho_excel)
                    
                    if dados_extrato:
                        if webhook_url:
                            print(f"📤 Enviando para Teams...")
                            teams_service.enviar_extrato_teams(dados_extrato, carteira)
                        else:
                            print(f"⚠️  Webhook não configurado - extrato não enviado")

            bancoBB.sair_sessao()

        bancoBB.fecha_navegador()
        sql_con.upload_log(id_bot)
        print(f"\n✅ Processo concluído!")

except Exception as e:
    print(f"\n❌ Erro: {e}")
    erro_completo = traceback.format_exc()
    sql_con.upload_log(id_bot, "1 - " + str(e) + " " + erro_completo)
    
    if 'teams_service' in locals() and webhook_url:
        teams_service.enviar_mensagem_erro(erro_completo)