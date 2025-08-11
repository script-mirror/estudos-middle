import os
import sys
import shutil
import glob
import logging
import requests
from copy import deepcopy
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from dateutil.relativedelta import relativedelta 
import pandas as pd
from middle.utils.constants import Constants
from middle.prospec import *
from middle.decomp.atualiza_decomp import process_decomp, retrieve_dadger_metadata 
from middle.decomp import DecompParams
from middle.utils import ( Constants, get_auth_header)
consts = Constants()

sys.path.append(os.path.join(consts.PATH_PROJETOS, "estudos-middle/api_prospec"))
from functionsProspecAPI import authenticateProspec,  download_dadger_update, send_all_dadger_update
authenticateProspec(consts.API_PROSPEC_USERNAME, consts.API_PROSPEC_PASSWORD)

HEADER = get_auth_header()
BASE_URL_API = consts.BASE_URL + '/api/v2/decks/'
SUBMERCADOS  = {'SECO': '1', 'S': '2', 'NE': '3', 'N': '4'}
INDEX_PQ     = {'SECO': 'SECO', 'S': 'SUL', 'NE': 'NE', 'N': 'N'}
MAP_MMGD     = {'PCHgd':'exp_cgh','PCTgd':'exp_ute','EOLgd':'exp_eol','UFVgd':'exp_ufv'}
REGIONS_MMGD = ['SECO', 'SUL', 'NE', 'N']
TYPES_MMGD   = ['PCHgd', 'PCTgd', 'EOLgd', 'UFVgd']
  

def update_carga_and_mmgd(params):     
    
    df_carga = get_dados_banco('carga-decomp')
    df_carga['semana_operativa'] = pd.to_datetime(df_carga['semana_operativa']) - timedelta(days=6)
    path_dadger = download_dadger_update(params['id_estudo'][0], logger, params['path_download'])
    
    tag_update = f"DP-DC{datetime.strptime(df_carga['data_produto'][0], '%Y-%m-%d').strftime('(%d/%m)')}"    
    
    fist_dc = path_dadger[0]
    params_decomp = {
    'arquivo': os.path.basename(fist_dc),   
    'dadger_path': fist_dc,
    'case':'ATUALIZAÇÂO DE CARGA',
    'logger':criar_logger('logging_carga_rv' + fist_dc[-1:]+'.log', os.path.dirname(fist_dc)+'/logging_carga_rv' + fist_dc[-1:]+'.log')}
    
    data_firt_deck = retrieve_dadger_metadata(**params_decomp)['deck_date']
    data_produto = min(pd.to_datetime(df_carga['semana_operativa'].unique().tolist()))
           
    if data_firt_deck == data_produto :
        logger.info('Data do produto coincide com a data do deck, prosseguindo com a atualização')
    else:
        logger.error(f"Data do produto: {data_produto}, Data do deck: {data_firt_deck}")
        raise ValueError('Data do produto não coincide com a data do deck, verifique os dados')
    
    for path in path_dadger:
        print(f'Path do dadger: {path}')
        params_decomp= {
        'arquivo': os.path.basename(path),
        'dadger_path': path,
        'output_path': path,
        'id_estudo': None,
        'case': 'ATUALIZAÇÂO DE CARGA',
        'logger':criar_logger('logger.log', os.path.dirname(path) + '/logger_rv' + path[-1:]+'.log') }
        
        meta_data = retrieve_dadger_metadata(**params_decomp)
        
        params_decomp['output_path'] = os.path.dirname(path)
        dict_carga={'dp':criar_dict_dp(),
                    'pq':criar_dict_mmgd()}
        
        if meta_data['deck_date'] in df_carga['semana_operativa'].unique():        
            for stage in meta_data['stages']:
                data = meta_data['deck_date'] + relativedelta(weeks=+stage-1)
                if data in df_carga['semana_operativa'].unique():
                    for submercado in SUBMERCADOS.keys():
                        filtered_data = df_carga.loc[(df_carga['semana_operativa'] == data) & (df_carga['submercado'] == submercado)]
                        dict_carga['dp']['valor_p1'][SUBMERCADOS[submercado]][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'pesada'), 'carga_mmgd'].values[0])
                        dict_carga['dp']['valor_p2'][SUBMERCADOS[submercado]][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'media'), 'carga_mmgd'].values[0])
                        dict_carga['dp']['valor_p3'][SUBMERCADOS[submercado]][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'leve'), 'carga_mmgd'].values[0])
                    
                        for mmgd in TYPES_MMGD:
                            dict_carga['pq']['valor_p1'][f'{INDEX_PQ[submercado]}_{mmgd}'][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'pesada'), MAP_MMGD[mmgd]].values[0])
                            dict_carga['pq']['valor_p2'][f'{INDEX_PQ[submercado]}_{mmgd}'][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'media'), MAP_MMGD[mmgd]].values[0])
                            dict_carga['pq']['valor_p3'][f'{INDEX_PQ[submercado]}_{mmgd}'][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'leve'), MAP_MMGD[mmgd]].values[0])

            process_decomp(deepcopy( DecompParams(**params_decomp)), dict_carga) 
   
    send_all_dadger_update(params['id_estudo'],params['path_download'],logger, 'logging_carga_rv', tag_update)
    
    return params

def update_eolica(params):

    return params

def update_re(params):

    return params


def criar_dict_dp():
    periods = [f'valor_p{i}' for i in range(1, 4)]  # Creates ['valor_p1', 'valor_p2', 'valor_p3']
    inner_keys = [str(i) for i in range(1, 5)]  # Creates ['1', '2', '3', '4']
    data = {'dp': {}}
    for period in periods:
        data['dp'][period] = {}
        for key in inner_keys:
            data['dp'][period][key] = {}
    return data['dp']

def criar_dict_mmgd():
    periods = [f'valor_p{i}' for i in range(1, 4)]
    data = {'pq': {}}
    for period in periods:
        data['pq'][period] = {}
        for region in REGIONS_MMGD:
            for type_ in TYPES_MMGD:
                key = f'{region}_{type_}'
                data['pq'][period][key] = {}
    return data ['pq']


def get_dados_banco(produto: str) -> dict:
    res = requests.get(BASE_URL_API + produto,
        headers=HEADER
    )
    if res.status_code != 200:
        logger.error(f"Erro {res.status_code} ao buscar carga: {res.text}")
        res.raise_for_status()
    return pd.DataFrame(res.json())


def create_directory(base_path: str, sub_path: str) -> Path:
    full_path = Path(base_path) / sub_path
    shutil.rmtree(full_path, ignore_errors=True)
    if os.path.exists: 
        try: 
            os.remove(full_path)
        except: 
            pass    
    full_path = Path(base_path) / sub_path
    full_path.mkdir(parents=True, exist_ok=True)
    return full_path.as_posix()


def criar_logger(nome_logger, caminho_arquivo): 
    nivel=logging.INFO
    console=True
    diretorio = os.path.dirname(caminho_arquivo) or '.'
    os.makedirs(diretorio, exist_ok=True)
    logger = logging.getLogger(nome_logger)
    logger.setLevel(nivel)
    logger.handlers.clear()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler = logging.FileHandler(caminho_arquivo, mode='a')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    if console:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
    # Impede propagação para o logger raiz
    logger.propagate = False
    return logger


BLOCK_FUNCTIONS = {
    'CARGA-DECOMP':  update_carga_and_mmgd,
    'EOLICA-DECOMP': update_eolica,
} 


def run_with_params():
        
    params =  {
        "produto": 'CARGA-DECOMP',
        'id_estudo': None,
        'path_download': create_directory(consts.PATH_RESULTS_PROSPEC,'update_carga') +'/',
        'path_out': create_directory(consts.PATH_RESULTS_PROSPEC,'update_carga')        
    }
       
    if len(sys.argv) > 3:
	
        for i in range(1, len(sys.argv)):
            argumento = sys.argv[i].lower()

            if   argumento ==   "produto": params[argumento] = sys.argv[i+1].upper()            
            elif argumento == "id_estudo": params[argumento] = eval(sys.argv[i+1])
    else:
        logger.info(f"Parâmetros recebidos: {params}")
        print("É obrigatorio informar o parametro: produto")
        sys.exit(1)
    print(params)
    BLOCK_FUNCTIONS[params['produto']](params)
          
 
if __name__ == '__main__':
    logger = criar_logger('logger.log', os.path.join(consts.PATH_ARQUIVOS, 'logger.log'))
    run_with_params()
