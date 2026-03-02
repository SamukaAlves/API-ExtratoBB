from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime, timedelta
import os

from src.Services.WebServices import ConfiguracoesNavegador
from src.Services.HelperServices import ServicosGerais
import shutil

class ExtratosBB():
    def __init__(self, ultima_execucao, pasta_auxiliar=None):
        self.servicosGerais = ServicosGerais()
        self.configuracoesNavegador = ConfiguracoesNavegador(pasta_auxiliar)

        config = self.servicosGerais.abrir_config()
        config_restrito = self.servicosGerais.abrir_config('RESTRITO')
        
        self.config = config['banco_do_brasil']
        self.config_restrito = config_restrito['banco_do_brasil']

        self.driver = self.configuracoesNavegador.driver
        self.driver.get(self.config['site'])
        self.driver.maximize_window()

        ultima_att = self.servicosGerais.pega_d_menos_x_dias(1, data_especifica=ultima_execucao)[0]
        self.dias_atualizar = self.servicosGerais.pega_d_menos_x_dias(0, ultima_att)
        
        # Filtrar apenas datas a partir de janeiro de 2026
        data_corte = datetime(2026, 1, 1)
        self.dias_atualizar = [d for d in self.dias_atualizar if d >= data_corte]
        
        print(f"Dias a atualizar: {len(self.dias_atualizar)} dias")
        if self.dias_atualizar:
            print(f"   De: {self.dias_atualizar[0].strftime('%d/%m/%Y')}")
            print(f"   Até: {self.dias_atualizar[-1].strftime('%d/%m/%Y')}")

    def fazer_login(self,num_chave_j,senha,senha_8_dig):
        chaveJ = WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID,'identificador')))
        chaveJ.clear()
        chaveJ.send_keys(num_chave_j)

        login = self.driver.find_element(By.NAME,'senha')
        login.clear()
        login.send_keys(senha)

        self.driver.find_element(By.ID,'submit').click()            
        
        # Entrar 8 dig
        while True:
            try:
                a=self.driver.find_element(By.CSS_SELECTOR,'#modal-0 > div.modal__content.modal__content--opening > div.modal__data > div > div.div-senha-conta > form > div.row.campo-senha-tela-login > label > input')
                a.send_keys(senha_8_dig)
                break
            except:
                sleep(1)
                
        self.driver.find_element(By.CSS_SELECTOR,'b').click()

    def acessar_relatorios(self):
        while True:
            try:
                self.driver.find_element(By.CSS_SELECTOR,'.titulo-border .col-xs-6').click() # MENU

                self.driver.find_element(By.ID,'19154').click() #Conta Corrente

                element_to_hover =self.driver.find_element(By.CSS_SELECTOR,r'#\31 9165 > span') #Consultas
                actions = ActionChains(self.driver)
                actions.move_to_element(element_to_hover).perform()

                self.driver.find_element(By.CSS_SELECTOR,r'#\31 9192 > span').click() #Extrato de conta corrente
                break
            except:
                sleep(1)
        
        while True:
            try:
                iframe=self.driver.find_element(By.ID,'idIframeAreaTransacional')
                self.driver.switch_to.frame(iframe)
                break
            except:
                sleep(1)

    def selecionar_dia_extratos(self,dia):
        elemento_select=WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.NAME,'tipoConsulta')))
        select= Select(elemento_select)

        select.select_by_visible_text('Período')

        dia_extrato = dia.strftime('%d%m%Y')
        definir_data = self.driver.find_element(By.ID,'dataInicio')
        definir_data.clear()
        definir_data.send_keys(dia_extrato)
        definir_data_fim = self.driver.find_element(By.ID,'dataFim')
        definir_data_fim.clear()
        definir_data_fim.send_keys(dia_extrato)
        self.ano = dia.strftime('%Y')
        self.mes = dia.strftime('%m')
        self.nome_dia_string = dia.strftime('%d_%m_%Y')
    
    def login_fundo(self,conta,senha_8_dig):
        nConta = self.driver.find_element(By.NAME,'numeroContratoOrigem')
        nConta.clear()
        nConta.send_keys(conta)

        passw = self.driver.find_element(By.ID,'senhaConta')
        passw.clear()
        passw.send_keys(senha_8_dig)

        self.driver.find_element(By.ID,'botao.acao.ok').click()
    
    def fazer_download(self,nome_fundo,path_destino,extensao='Excel'):
        #extensao: primeira letra em maiusculo
        extrato_path = os.path.abspath(path_destino)

        element = self.driver.find_element(By.CSS_SELECTOR,'#selectSalvar')
        self.driver.execute_script("arguments[0].click();", element)
        sleep(1)
        while True:
            try:
                self.driver.find_element(By.CSS_SELECTOR,f'#salvar{extensao} > p').click()
                break
            except:
                sleep(1)
        if extensao == 'Excel': 
            extensao = 'xlsx'
        
        self.configuracoesNavegador.move_arquivo_download(
            extrato_path,
            f"Extrato_BB_{nome_fundo}_{self.nome_dia_string}.{extensao.lower()}",
            self.ano,
            self.config_restrito  # Passa a configuração
        )

    def sair_sessao(self):
        # Sair da conta do BB
        self.driver.switch_to.default_content()
        self.driver.find_element(By.CLASS_NAME,'btn-logout').click()
        sleep(1)

    def fecha_navegador(self):
        self.configuracoesNavegador.fecha_navegador()