import sys
import glob
from requestsPluviaAPI import *
from datetime import datetime, timedelta
from pathlib import Path
import pathlib
import shutil
import zipfile
import time
import os
import pandas as pd
from middle.utils import Constants 
import logging

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

consts = Constants()
 
PATH_PREVS_PLUVIA   = pathlib.Path(os.path.join(consts.PATH_ARQUIVOS,'pluvia'))
PATH_PREVS_PROSPEC  = pathlib.Path(consts.PATH_PREVS_PROSPEC)
os.makedirs(PATH_PREVS_PLUVIA, exist_ok=True)
os.makedirs(PATH_PREVS_PROSPEC, exist_ok=True)

def main(parametros):    
    logger.info('Iniciando API do Pluvia')
    print(''); print('')
    print ('--------------------------------------------------------------------------------#')
    print('#-API do Pluvia Iniciado: ' + str(datetime.now())[:19])

    logger.info('Autenticando no Pluvia')
    authenticatePluvia(consts.API_PLUVIA_USERNAME, consts.API_PLUVIA_PASSWORD)
   
    PATH_FORECAST_DAY =  pathlib.Path(os.path.join(PATH_PREVS_PLUVIA, parametros['prevs'], parametros['data'].strftime('%Y-%m-%d')))    
    logger.info(f'Criando diretório para previsões: {PATH_FORECAST_DAY}')
    os.makedirs(PATH_FORECAST_DAY, exist_ok=True)
    n_tentativas = 0
    aguardar_prevs = True
    
    while n_tentativas <= parametros['n_tentativas']:
        logger.info(f'Iniciando tentativa {n_tentativas + 1} de {parametros["n_tentativas"]}')
        if n_tentativas == parametros['n_tentativas']:
            aguardar_prevs = False
        sucesso, folders = get_prevs(parametros, aguardar_prevs, PATH_FORECAST_DAY)
        if sucesso:
            logger.info('Previsões obtidas com sucesso, movendo arquivos')
            return mover_prevs(folders, parametros['path_out_prevs'])
        else:
            n_tentativas += 1
            print(f'Tentativa {n_tentativas} de {parametros["n_tentativas"]}...')
            logger.warning(f'Tentativa {n_tentativas} falhou, aguardando 10 minutos')
            time.sleep(600)
    logger.error('Número máximo de tentativas atingido. Encerrando o processo.')
    print('Número máximo de tentativas atingido. Encerrando o processo.')
    sys.exit()
    
def get_prevs(parametros, aguardar_prevs, PATH_FORECAST_DAY):
    logger.info('Obtendo previsões via API')
    logger.info(f'Mapas buscados: {parametros["mapas"]}')
    mapas = pd.DataFrame(getInfoFromAPI('/v2/previsoes?dataPrevisao='+parametros['data'].strftime('%d/%m/%Y'))) 
    df_mapas = mapas.loc[mapas['nome'].isin(parametros["mapas"])]
    logger.info(f'Mapas encontrados: {df_mapas["nome"].to_list()}')
    
    if any('ONS_Pluvia' in x for x in df_mapas['nome']):
        logger.info('Removendo mapas ONS_ETAd_1_Pluvia da lista')
        df_mapas = df_mapas[~df_mapas['nome'].str.contains('ONS_ETAd_1_Pluvia', na=False)]
        parametros["mapas"] = [item for item in parametros["mapas"] if "ONS_ETAd_1_Pluvia" not in item]
    
    pathFolders = []
    if not aguardar_prevs:
        logger.info('Modo sem espera ativado')
        print('Mapas request    : ', parametros['mapas'])
        print('Mapas encontrados: ', df_mapas['nome'].to_list())
        for index, row in df_mapas.iterrows():
            logger.info(f'Baixando arquivo para mapa: {row["nome"]}')
            results = pd.DataFrame(row['resultados'])
            getFileFromAPI('/v2/resultados/' + str(results[results['nome']=='Prevs']['id'].iloc[0]), row['nome'] + '.zip', PATH_FORECAST_DAY)
            pathFolders.append(os.path.join(PATH_FORECAST_DAY, row['nome'] + '.zip'))
        logger.info('Download de mapas concluído')
        return True, pathFolders    
                       
    elif len(df_mapas) == len(parametros['mapas']) and aguardar_prevs:
        logger.info('Todos os mapas esperados foram encontrados')
        for index, row in df_mapas.iterrows():
            logger.info(f'Baixando arquivo para mapa: {row["nome"]}')
            results = pd.DataFrame(row['resultados'])
            getFileFromAPI('/v2/resultados/' + str(results[results['nome']=='Prevs']['id'].iloc[0]), row['nome'] + '.zip', PATH_FORECAST_DAY)
            pathFolders.append(os.path.join(PATH_FORECAST_DAY, row['nome'] + '.zip'))
        logger.info('Download de mapas concluído')
        return True, pathFolders   
                 
    else:
        logger.warning('Mapas esperados não encontrados')
        print('Mapas request    : ', parametros['mapas'])
        print('Mapas encontrados: ', df_mapas['nome'].to_list())
        print('Aguardando mapas serem disponibilizados...')
        return False, []

def unzip_file(zip_path, path_unzip:str=None):
    logger.info(f'Descompactando arquivo: {zip_path}')
    if path_unzip == None:
        path_unzip = os.path.dirname(zip_path)
        
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(path_unzip)
    
    logger.info(f'Arquivo descompactado em: {path_unzip}')
    return path_unzip

def mover_prevs(folders:str, path_dst:str):
    logger.info(f'Movendo previsões para: {path_dst}')
    shutil.rmtree(Path(path_dst), ignore_errors=True)
    if os.path.exists: 
        try: 
            os.remove(Path(path_dst))
            logger.info(f'Arquivo removido: {path_dst}')
        except: 
            logger.warning(f'Falha ao remover arquivo: {path_dst}')
            pass                
    os.makedirs(path_dst, exist_ok=True)
    sens = ''
    list_prevs = []
    sens = None
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
                nome_arquivo = f'prevs-{modelo.upper()}.rv{rv}'
            elif sens is None:
                sens = modelo.replace('Preliminar','Prel').replace('_Pluvia','').replace('AgrupadoPrecipitacao','A.Precip')
                sens = sens.replace('PrecZero_60','P.Zero').replace('PrecZero_120','P.Zero').replace('Usuario_','')
            n_prevs += 1
            caminho_arquivo_destino = os.path.join(pathOutput, nome_arquivo)
            logger.info(f'Copiando arquivo {arquivo} para {caminho_arquivo_destino}')
            shutil.copy2(arquivo, caminho_arquivo_destino)
        list_prevs.append(n_prevs)
        logger.info(f'Removendo diretório temporário: {unzip_dir}')
        shutil.rmtree(unzip_dir, ignore_errors=True)
        logger.info(f'Removendo arquivo zip: {zip_path}')
        os.remove(zip_path)
    logger.info('Movimento de previsões concluído')
    return sens, max(list_prevs)

if __name__ == '__main__': 
    logger.info('Script iniciado')
    parametros =  dict()
    main(parametros)
    logger.info('Script finalizado')