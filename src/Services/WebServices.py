from colorama import init,Fore,Back
from time import sleep
import shutil
import json
import os

try:
    from seleniumbase import Driver  # Wrapper de criação de drivers multi-navegador
except ImportError:
    Driver = None  # type: ignore

class ConfiguracoesNavegador():
    def __init__(self, pasta_auxiliar: str | None = None, navegador: str = 'chrome', headless: bool = False):
        init(autoreset=True)
        if Driver is None:
            raise ImportError("Dependência 'seleniumbase' não instalada. Adicione 'seleniumbase' ao requirements.txt e reinstale o ambiente.")

        navegador = (navegador or 'chrome').lower()
        if navegador in ('msedge', 'microsoft-edge', 'edge'):
            navegador = 'edge'
        elif navegador in ('ff', 'firefox'):
            navegador = 'firefox'
        elif navegador in ('chromium',):
            navegador = 'chrome'

        if pasta_auxiliar:
            download_path = os.path.abspath(pasta_auxiliar)
        else:
            download_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        self.download_path = download_path
        if pasta_auxiliar:
            self.apaga_arquivos()

        try:
            self.driver = Driver(
                uc=True,
                browser=navegador,
                headless=headless,
                
            )
        except Exception as e:
            raise RuntimeError(f"Falha ao iniciar driver ({navegador}) via seleniumbase: {e}")

        print(Fore.LIGHTBLUE_EX + f"Driver {navegador} (seleniumbase) pronto.")

    def apaga_arquivos(self):
        for nome_arquivo in os.listdir(self.download_path):
            if nome_arquivo.endswith(".txt"):
                continue
            else:
                caminho_arquivo = os.path.join(self.download_path, nome_arquivo)
                if os.path.isfile(caminho_arquivo):
                    os.remove(caminho_arquivo)
    
    def fecha_navegador(self):
        self.driver.quit()                      
    def move_arquivo_download(self, path_destino: str, nome_arquivo: str, ano_bb='', config_restrito=None):
        while True:
            arquivos = os.listdir(self.download_path)
            arquivo = ''
            for arquivo in arquivos:
                if arquivo.endswith(nome_arquivo.split('.')[-1]):
                    break

            if arquivo.endswith(nome_arquivo.split('.')[-1]):
                break
            sleep(1)

        caminhoArquivo = os.path.join(self.download_path, arquivo)

        if config_restrito:
            # Extrair ano e mês do path_destino (formato: .../Extratos_Bancarios/CARTEIRA/YYYY/MM)
            path_parts = path_destino.replace('\\', '/').split('/')
            ano = path_parts[-2] if len(path_parts) >= 2 else ano_bb
            mes = path_parts[-1] if len(path_parts) >= 1 else '00'
            
            # Usar caminhos do config com estrutura ano/mes
            path_copy_restrito = os.path.join(
                config_restrito.get('enderecos', {}).get('restrito', 'C:\\Users\\samuel.alves\\Funpresp-Jud\\Arquivos - GETES\\_RESTRITO\\Extratos_Diarios'),
                ano,
                mes
            )
            # Tentar extrair o nome do perfil a partir do nome do arquivo (formato esperado: Extrato_BB_<perfil>_DD_MM_YYYY.ext)
            perfil = None
            try:
                if nome_arquivo.startswith('Extrato_BB_'):
                    core = nome_arquivo[len('Extrato_BB_'):]
                    core_no_ext = os.path.splitext(core)[0]
                    # rsplit a partir da direita para isolar a parte do nome do perfil mesmo se contiver underscores
                    parts = core_no_ext.rsplit('_', 3)
                    perfil = parts[0] if parts else None
            except Exception:
                perfil = None

            if perfil:
                path_copy_restrito = os.path.join(path_copy_restrito, perfil)

            os.makedirs(path_copy_restrito, exist_ok=True)
            shutil.copy(caminhoArquivo, os.path.join(path_copy_restrito, nome_arquivo))
            
            path_copy_publico = os.path.join(
                config_restrito.get('enderecos', {}).get('publico', 'C:\\Users\\samuel.alves\\Funpresp-Jud\\Arquivos - GETES\\_PUBLICO\\Extratos_Diarios'),
                ano,
                mes
            )
            if perfil:
                path_copy_publico = os.path.join(path_copy_publico, perfil)

            os.makedirs(path_copy_publico, exist_ok=True)
            shutil.copy(caminhoArquivo, os.path.join(path_copy_publico, nome_arquivo))

        novoCaminhoArq = os.path.join(path_destino, nome_arquivo)
        os.makedirs(path_destino, exist_ok=True)
        shutil.move(caminhoArquivo, novoCaminhoArq)
    
    def modificar_config_senha(self, keys, value):
        file_path = "config/configRestrito.json"
        # Carregando o arquivo json
        with open(file_path, "r",encoding='utf-8') as f:
            data = json.load(f)

        # Modificar o valor
        objeto = data
        for chave in keys[:-1]:
            objeto = objeto[chave]
        objeto[keys[-1]] = value

        # Escrevendo o arquivo json modificado
        with open(file_path, "w",encoding='utf-8') as f:
            json.dump(data, f, indent=4)