
import os
import re
import sys
import glob
import shutil
import hashlib
import zipfile
import datetime
import pandas as pd
from tabulate import tabulate
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.abspath(os.path.expanduser("~")),'.env'))

homePath =  os.path.expanduser('~')
downloadsPath = os.path.join(homePath, 'Downloads')

appDir = os.path.dirname(os.path.abspath(__file__))
appsDir = os.path.dirname(appDir)
rootDir = os.path.dirname(appsDir)

sys.path.append(os.path.join(appDir, 'libs'))
sys.path.append(rootDir)
from ampere.libs import helper
from ampere.libs.ee_ampere_consultoria.produtos.flux import FluxENADiaria
from ampere.libs.ee_ampere_consultoria.produtos.flux import FluxAutomatico
from ampere.libs.opweek import ElecData

# CREDENCIAIS -----------------------------------------------------------

USERNAME = os.getenv("API_AMPERE_USERNAME")
SENHA = os.getenv("API_AMPERE_PASSWORD")
USER_ACCESS_TOKEN = os.getenv("API_AMPERE_TOKEN")
        
MD5_PASSWORD_HASH = hashlib.md5(SENHA.encode('utf-8')).hexdigest()


def list_ena():
    
    flux = FluxENADiaria(USERNAME, MD5_PASSWORD_HASH, USER_ACCESS_TOKEN)
    lista_estudos = flux.get_simulacoes()
    return sorted(lista_estudos.keys())
    
def get_ena(data:datetime, modelo:str, versao:str, subdivisao:str):
    
    flux = FluxENADiaria(USERNAME, MD5_PASSWORD_HASH, USER_ACCESS_TOKEN)

    runtime = datetime.datetime.strftime(data, "%Y-%m-%d")
    r = flux.get_ena(runtime, modelo, versao, subdivisao)


def list_estudos(acomph:str=None, data_prev:str=None, modelo:str=None):
    
    flux = FluxAutomatico(USERNAME, MD5_PASSWORD_HASH, USER_ACCESS_TOKEN)
    return flux.verify_last_results(acomph, data_prev, modelo)
    
def get_estudos(modelo:str=None, data_prev:str=None, acomph:str=None, nomezip:str=None):

    flux = FluxAutomatico(USERNAME, MD5_PASSWORD_HASH, USER_ACCESS_TOKEN)
    return flux.download(acomph, data_prev, modelo, nomezip)

def unzip_file(zip_path, path_unzip:str=None):
    
    if path_unzip == None:
        path_unzip = os.path.dirname(zip_path)
        
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(path_unzip)
    
    return path_unzip

def mover_prevs(zip_path:str, path_dst:str=None, modeloBase:str=None, considerar_apenas_rvf=False):
    
    if os.path.exists: 
        try: shutil.rmtree(path_dst)
        except: pass
    if os.path.exists (path_dst) == False: os.mkdir (path_dst)
    
    n_prevs = 0 
    zip_dir = unzip_file(zip_path)    
    folder_name = os.path.basename(zip_path).replace('.zip','')
    padrao_glob_vazoes = os.path.join(zip_dir, folder_name, 'VAZOES.DAT')
    
    os.makedirs(path_dst, exist_ok=True)
    
    if os.path.exists(padrao_glob_vazoes):
        caminho_arquivo_destino = os.path.join(path_dst, 'VAZOES.DAT')
        shutil.copy2(padrao_glob_vazoes, caminho_arquivo_destino)
    
    if considerar_apenas_rvf:
        padrao_glob_prevs = os.path.join(zip_dir, folder_name, 'PREVS.*.REVF')
        for arquivo in glob.glob(padrao_glob_prevs):
            nome_arquivo = os.path.basename(arquivo)
            padrao = r'PREVS\.(.*)\.([0-9]{6})\.REVF'
            match = re.match(padrao, nome_arquivo)
            
            if match:
                modelo = match.group(1)
                mesOperativo = match.group(2)
                sem_eletrica = ElecData(datetime.datetime.strptime(mesOperativo,'%Y%M'))
                rv_ref = ElecData(sem_eletrica.primeiroDiaMes)
                while sem_eletrica.mesReferente == rv_ref.mesReferente:
                    rv = rv_ref.atualRevisao
                    if modelo != modeloBase:
                        nome_arquivo = f'{mesOperativo}-PREVS-{modelo}_{fonte}.rv{rv}'
                    else:
                        nome_arquivo = f'{mesOperativo}-PREVS.rv{rv}'
                        
                    caminho_arquivo_destino = os.path.join(path_dst, nome_arquivo)
                    shutil.copy2(arquivo, caminho_arquivo_destino)
                    rv_ref = ElecData(rv_ref.data + datetime.timedelta(days=7))
            
    else:
        padrao_glob_prevs = os.path.join(zip_dir, folder_name, 'PREVS.*.REV[0-9]')
        for arquivo in glob.glob(padrao_glob_prevs):
            nome_arquivo = os.path.basename(arquivo)
            
            padrao = r'PREVS\.(.*)\.([0-9]{6})\.REV([0-9]{1})'
            match = re.match(padrao, nome_arquivo)
        
            if match:
                modelo = match.group(1)
                mesOperativo = match.group(2)
                rv = match.group(3)
                

                nome_arquivo = f'prevs.rv{rv}'

                pathOutput = path_dst  +'/'+ str(int(mesOperativo[-2:]))
                os.makedirs(pathOutput, exist_ok=True)
                n_prevs += 1
                caminho_arquivo_destino = os.path.join(pathOutput, nome_arquivo)
                shutil.copy2(arquivo, caminho_arquivo_destino)

    # Excluir a pasta extraída e o arquivo zip
    shutil.rmtree(os.path.join(zip_dir, folder_name))
    os.remove(zip_path)
    return 'P.CONJ_AMPERE', n_prevs

def baixar_rodada(modelo:str, data_previsao:datetime, preliminar:bool, psat:bool):
    
    path_download = os.path.join(appDir, 'arquivos')
    os.makedirs(path_download, exist_ok=True)
    data_prev = data_previsao.strftime('%Y%m%d')
    if psat:
        data_prev = f'{data_prev}-PSAT'
        
    data_acomph = data_previsao
    if preliminar:
        data_acomph = data_acomph - datetime.timedelta(days=1)
    data_acomph = f'ACOMPH{data_acomph.strftime("%Y%m%d")}'
    lista_estudos = list_estudos(data_prev=data_prev)

    if lista_estudos:
        df_estudos = pd.DataFrame(lista_estudos)
        filtro_1 = df_estudos['cenario'] == modelo
        filtro_2 = df_estudos['data_acomph']==data_acomph
        estudos_interesse = df_estudos.loc[filtro_1 & filtro_2]
        if estudos_interesse.shape[0] >= 1:
            path_zip = os.path.join(path_download, f'{data_prev}_{data_acomph}_{modelo}.zip')
            if get_estudos(modelo=modelo, data_prev=data_prev, acomph=data_acomph, nomezip=path_zip):
                print(path_zip)
                return path_zip
            else:
                print(f'Nao foi posivel baixar o modelo {data_prev}_{data_acomph}_{modelo}')
                return None
            
    print(f'Nenhum estudo encontrado com os parametros: {data_prev}_{data_acomph}_{modelo}')
    return None

 
def baixar_arquivos_rodada_automatica(data_prev:datetime.date,modelos:list,preliminar:bool,psat:bool):
    ultima_tentativa = datetime.datetime.now().replace(hour=7, minute=45, second=0, microsecond=0)
    while 1:
        _modelos = modelos.copy()
        for modelo in _modelos:
            path_zip = baixar_rodada(modelo, data_prev, preliminar, psat)
            if path_zip:
                destino_prevs = os.path.join(rootDir, 'apps', 'prospec', 'arquivos', 'prevs', data_prev.strftime('%y%m%d'))
                mover_prevs(zip_path=path_zip, path_dst=destino_prevs, modeloBase='ONS-OFICIAL-NT00752020-RVEXT-VMEDPONDERADA', considerar_apenas_rvf=True)
                modelos.remove(modelo)
        if len(modelos) == 0 or datetime.datetime.now() >= ultima_tentativa:
            return 
                
def listar_rodadas_disponiveis(data_previsao:datetime, preliminar:int=False, psat:int=True):
    data_prev = data_previsao.strftime('%Y%m%d')
    if psat:
        data_prev = f'{data_prev}-PSAT'
        
    data_acomph = data_previsao
    if preliminar:
        data_acomph = data_acomph - datetime.timedelta(days=1)
    
    data_acomph = f'ACOMPH{data_acomph.strftime("%Y%m%d")}'
    lista_estudos = list_estudos(acomph=data_acomph, data_prev=data_prev)
    df_lista_estudos = pd.DataFrame(lista_estudos)
    df_lista_estudos['last_update'] = pd.to_datetime(df_lista_estudos['last_update'], unit='s') - pd.Timedelta(hours=3)
    df_lista_estudos = df_lista_estudos.sort_values(by='last_update')
    print(tabulate(df_lista_estudos, headers='keys', tablefmt='grid', showindex=False))
    

if __name__ == '__main__':    
    
    if not len(sys.argv) > 1:
        helper.printHelper()
    
    parametros = {}
    
    for i in range(1, len(sys.argv)):
        argumento = sys.argv[i].lower()
        
        if argumento == 'data':
            parametros[argumento] = datetime.datetime.strptime(sys.argv[i+1], '%d/%m/%Y')
            
        if argumento == 'data_previsao':
            parametros[argumento] = datetime.datetime.strptime(sys.argv[i+1], '%d/%m/%Y')

        elif argumento == "path_zip":
            parametros[argumento] = sys.argv[i+1]
            
        elif argumento == "modelo":
            parametros[argumento] = sys.argv[i+1]
            
        elif argumento == "lista_modelos":
            parametros[argumento] = eval(sys.argv[i+1])

        elif argumento == "pos_acomph":
            parametros[argumento] = bool(int(sys.argv[i+1]))

        elif argumento == "pos_psat":
            parametros[argumento] = bool(int(sys.argv[i+1]))
            
    parametros = helper.parametrosDefault(parametros)
        
    if sys.argv[1] == 'baixar_rodada':
        modelo = parametros['modelo']
        data_previsao = parametros['data_previsao']
        preliminar = not parametros['pos_acomph']
        psat = parametros['pos_psat']
        baixar_rodada(modelo, data_previsao, preliminar,psat)
        
    if sys.argv[1] == 'listar_rodadas_disponiveis':
        data_previsao = parametros['data_previsao']
        preliminar = not parametros['pos_acomph']
        psat = parametros['pos_psat']
        listar_rodadas_disponiveis(data_previsao=data_previsao, preliminar=preliminar, psat=psat)

    if sys.argv[1] == 'baixar_arquivos_rodada_automatica':
        data_prev = parametros['data_previsao']
        modelos = parametros['lista_modelos']
        preliminar = not parametros['pos_acomph']
        psat = parametros['pos_psat']
        baixar_arquivos_rodada_automatica(data_prev,modelos,preliminar,psat)
        
    
        
        
        