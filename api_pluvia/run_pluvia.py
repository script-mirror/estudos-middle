import sys
import glob
from requestsPluviaAPI import *
from datetime import datetime, timedelta
import pathlib
import shutil
import zipfile
import time
import os
import pandas as pd
from middle.utils.constants import Constants 
consts = Constants()
 
PATH_PREVS_PLUVIA   = pathlib.Path(os.path.join(consts.PATH_ARQUIVOS,'pluvia'))
PATH_PREVS_PROSPEC  = pathlib.Path(consts.PATH_PREVS_PROSPEC)
os.makedirs(PATH_PREVS_PLUVIA, exist_ok=True)
os.makedirs(PATH_PREVS_PROSPEC, exist_ok=True)

def main(parametros):    

    print(''); print('')
    print ('--------------------------------------------------------------------------------#')
    print('#-API do Pluvia Iniciado: ' + str(datetime.now())[:19])

    authenticatePluvia(consts.API_PLUVIA_USERNAME, consts.API_PLUVIA_PASSWORD)
   
    PATH_FORECAST_DAY =  pathlib.Path(os.path.join(PATH_PREVS_PLUVIA, parametros['prevs'], parametros['data'].strftime('%Y-%m-%d')))    
    os.makedirs(PATH_FORECAST_DAY, exist_ok=True)
    n_tentativas = 0
    aguardar_prevs = True
    
    while n_tentativas <= parametros['n_tentativas']:
        if n_tentativas == parametros['n_tentativas']:
            aguardar_prevs = False
        sucesso, folders = get_prevs(parametros, aguardar_prevs, PATH_FORECAST_DAY)
        if sucesso:
            return mover_prevs(folders, parametros['path_out_prevs'])
        else:
            n_tentativas += 1
            print(f'Tentativa {n_tentativas} de {parametros["n_tentativas"]}...')
            time.sleep(600)
    print('Número máximo de tentativas atingido. Encerrando o processo.')
    sys.exit()
    
def get_prevs(parametros, aguardar_prevs, PATH_FORECAST_DAY):
    mapas    = pd.DataFrame(getInfoFromAPI('/v2/previsoes?dataPrevisao='+parametros['data'].strftime('%d/%m/%Y'))) 
    df_mapas = mapas.loc[mapas['nome'].isin(parametros["mapas"])]
    
    if any('ONS_ETAd_1_Pluvia' in x for x in df_mapas['nome']) and any('ONS_Pluvia' in x for x in df_mapas['nome']):
        df_mapas = df_mapas[~df_mapas['nome'].str.contains('ONS_ETAd_1_Pluvia', na=False)]
        parametros["mapas"] = [item for item in parametros["mapas"] if "ONS_ETAd_1_Pluvia" not in item]
    
    pathFolders = []
    if not aguardar_prevs:
        print('Mapas request    : ', parametros['mapas'])
        print('Mapas encontrados: ', df_mapas['nome'].to_list())
        for index, row in df_mapas.iterrows():
            results = pd.DataFrame(row['resultados'])
            getFileFromAPI('/v2/resultados/' + str(results[results['nome']=='Prevs']['id'].iloc[0]), row['nome'] + '.zip', PATH_FORECAST_DAY)
            pathFolders.append(os.path.join(PATH_FORECAST_DAY, row['nome'] + '.zip'))
        return True, pathFolders    
                       
    elif len(df_mapas) == len(parametros['mapas']) and aguardar_prevs:
        print('Mapas encontrados: ', df_mapas['nome'].to_list())
        for index, row in df_mapas.iterrows():
            results = pd.DataFrame(row['resultados'])
            getFileFromAPI('/v2/resultados/' + str(results[results['nome']=='Prevs']['id'].iloc[0]), row['nome'] + '.zip', PATH_FORECAST_DAY)
            #downloadForecast(int(results[results['nome']=='Prevs']['id'].iloc[0]), PATH_FORECAST_DAY, row['nome'] + '.zip')
            pathFolders.append(os.path.join(PATH_FORECAST_DAY, row['nome'] + '.zip'))
        return True, pathFolders   
                 
    else:
        print('Mapas request    : ', parametros['mapas'])
        print('Mapas encontrados: ', df_mapas['nome'].to_list())
        print('Aguardando mapas serem disponibilizados...')
        return False, []


def unzip_file(zip_path, path_unzip:str=None):
    
    if path_unzip == None:
        path_unzip = os.path.dirname(zip_path)
        
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(path_unzip)
    
    return path_unzip

def mover_prevs(folders:str, path_dst:str=None):
    
    shutil.rmtree(path_dst, ignore_errors=True)
    if os.path.exists: 
        try: os.remove(path_dst)
        except: pass                
    os.makedirs(path_dst, exist_ok=True)
    sens = ''
    list_prevs = []
    for zip_path in folders:       
        n_prevs = 0 
        unzip_dir = unzip_file(zip_path,zip_path.replace('.zip',''))    
        modelo = os.path.basename(unzip_dir).replace('-SMAP','')        
        padrao_glob_prevs = os.path.join(unzip_dir, '*prevs-*.rv[0-5]')      
        for arquivo in glob.glob(padrao_glob_prevs):
            prevs = os.path.basename(arquivo)
            mesOperativo = prevs.split('-')[0]
            rv = prevs[-1:]           
            nome_arquivo = f'prevs.rv{rv}'
            pathOutput = path_dst  +'/'+ str(int(mesOperativo[-2:]))
            os.makedirs(pathOutput, exist_ok=True)
            if nome_arquivo in os.listdir(pathOutput):
                nome_arquivo = f'prevs-{modelo}_pluvia.rv{rv}'
            else:
                sens = modelo.replace('Preliminar','Prel').replace('_Pluvia','').replace('AgrupadoPrecipitacao','A.Precip')
                sens = sens.replace('PrecZero_60','P.Zero').replace('PrecZero_120','P.Zero').replace('Usuario_','')
            n_prevs += 1
            caminho_arquivo_destino = os.path.join(pathOutput, nome_arquivo)
            shutil.copy2(arquivo, caminho_arquivo_destino)
        list_prevs.append(n_prevs)
        shutil.rmtree(unzip_dir, ignore_errors=True)
        os.remove(zip_path)
    return sens, max(list_prevs)


if __name__ == '__main__': 
    parametros =  dict()
    parametros['prevs'] = 'PREVS_PLUVIA_2_RV'
    parametros['data'] = datetime.strptime('11/04/2023', '%d/%m/%Y')
    parametros['cenario'] = ''
    parametros['mapas'] = 'ONS'
    parametros['membros'] = ['NULO']
    parametros['preliminar']  = 1
    main(parametros)