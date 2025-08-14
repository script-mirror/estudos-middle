import os
import sys
import shutil
import glob
import logging
import calendar
import requests
from copy import deepcopy
from typing import List, Dict, Any, Tuple
from middle.message import send_whatsapp_message
from datetime import datetime, timedelta
from pathlib import Path
from dateutil.relativedelta import relativedelta 
import pandas as pd
import pdb
from middle.utils.constants import Constants
from middle.prospec import *
from middle.decomp.atualiza_decomp import process_decomp, retrieve_dadger_metadata, days_per_month
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
    days_per_month(datetime(2025,8,23),datetime(2025,8,30) )
    df_data = get_dados_banco('carga-decomp')
    df_data['semana_operativa'] = pd.to_datetime(df_data['semana_operativa']) - timedelta(days=6)
    path_dadger = download_dadger_update([params['id_estudo'][0]], logger, params['path_download'])
    
    tag_update = f"DP-DC{datetime.strptime(df_data['data_produto'][0], '%Y-%m-%d').strftime('(%d/%m)')}"    
    
    fist_dc = path_dadger[0]
    params_decomp = {
    'arquivo': os.path.basename(fist_dc),   
    'dadger_path': fist_dc,
    'case':'ATUALIZAÇÃO DE CARGA',
    'logger':criar_logger('logging_carga_rv' + fist_dc[-1:]+'.log', os.path.dirname(fist_dc)+'/logging_carga_rv' + fist_dc[-1:]+'.log')}
    
    data_firt_deck = retrieve_dadger_metadata(**params_decomp)['deck_date']
    data_produto = min(pd.to_datetime(df_data['semana_operativa'].unique().tolist()))
           
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
        
        if meta_data['deck_date'] in df_data['semana_operativa'].unique():        
            for stage in meta_data['stages']:
                data = meta_data['deck_date'] + relativedelta(weeks=+stage-1)
                if data in df_data['semana_operativa'].unique():
                    for submercado in SUBMERCADOS.keys():
                        filtered_data = df_data.loc[(df_data['semana_operativa'] == data) & (df_data['submercado'] == submercado)]
                        dict_carga['dp']['valor_p1'][SUBMERCADOS[submercado]][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'pesada'), 'carga_mmgd'].values[0])
                        dict_carga['dp']['valor_p2'][SUBMERCADOS[submercado]][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'media'), 'carga_mmgd'].values[0])
                        dict_carga['dp']['valor_p3'][SUBMERCADOS[submercado]][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'leve'), 'carga_mmgd'].values[0])
                    
                        for mmgd in TYPES_MMGD:
                            dict_carga['pq']['valor_p1'][f'{INDEX_PQ[submercado]}_{mmgd}'][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'pesada'), MAP_MMGD[mmgd]].values[0])
                            dict_carga['pq']['valor_p2'][f'{INDEX_PQ[submercado]}_{mmgd}'][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'media'), MAP_MMGD[mmgd]].values[0])
                            dict_carga['pq']['valor_p3'][f'{INDEX_PQ[submercado]}_{mmgd}'][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'leve'), MAP_MMGD[mmgd]].values[0])

            process_decomp(deepcopy( DecompParams(**params_decomp)), dict_carga) 
        else:
            logger.warning(f"Data do deck {meta_data['deck_date'].strftime('%d/%m/%Y')} não encontrada na base de dados de carga, ignorando atualização para este deck.")
    send_all_dadger_update(params['id_estudo'],params['path_download'],logger, 'logging_carga_rv', tag_update)
  
    
def update_eolica(params):     
    
    df_data = get_dados_banco('weol')
    df_data['semana_operativa'] = pd.to_datetime(df_data['inicioSemana'])
    path_dadger = download_dadger_update(params['id_estudo'], logger, params['path_download'])    
    tag_update  = f"WEOL-DC{datetime.strptime(df_data['dataProduto'][0], '%Y-%m-%d').strftime('(%d/%m)')}"    
    
    for path in path_dadger:
        print(f'Path do dadger: {path}')
        params_decomp= {
        'arquivo': os.path.basename(path),
        'dadger_path': path,
        'output_path': path,
        'id_estudo': None,
        'case': 'ATUALIZAÇÂO WEOL',
        'logger':criar_logger('logging_weol_rv.log', os.path.dirname(path) + '/logging_weol_rv' + path[-1:]+'.log') }
        
        meta_data = retrieve_dadger_metadata(**params_decomp)        
        params_decomp['output_path'] = os.path.dirname(path)
        dict_carga={'pq':criar_dict_weol()}
        
        if meta_data['deck_date'] in df_data['semana_operativa'].unique():
            df_month = df_data.loc[df_data['mesEletrico'] == (meta_data['deck_date'] + timedelta(days=6)).month]        
            for stage in meta_data['stages']:
                data = meta_data['deck_date'] + relativedelta(weeks=+stage-1)
                if data in df_month['semana_operativa'].unique():
                    for submercado in SUBMERCADOS.keys():
                        if submercado in df_month['submercado'].unique():
                            filtered_data = df_month.loc[(df_data['semana_operativa'] == data) & (df_month['submercado'] == submercado)]                                              
                            dict_carga['pq']['valor_p1'][f'{INDEX_PQ[submercado]}_EOL'][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'pesado'), 'valor'].values[0])
                            dict_carga['pq']['valor_p2'][f'{INDEX_PQ[submercado]}_EOL'][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'medio'), 'valor'].values[0])
                            dict_carga['pq']['valor_p3'][f'{INDEX_PQ[submercado]}_EOL'][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'leve'), 'valor'].values[0])

            process_decomp(deepcopy( DecompParams(**params_decomp)), dict_carga) 
        else:
            logger.warning(f"Data do deck {meta_data['deck_date'].strftime('%d/%m/%Y')} não encontrada na base de dados WEOL, ignorando atualização para este deck.")
    send_all_dadger_update(params['id_estudo'],params['path_download'],logger, 'logging_weol_rv', tag_update)
  
    
def update_cvu(params):     
    
    if params['tipo_cvu'] == 'conjuntural_revisado':
        if date_4_du(params['dt_produto']):
            df_data = get_cvu_banco('cvu', 'conjuntural_revisado')
            df_data = df_data.sort_values('mes_referencia', ascending=False)
            df_data = df_data.drop_duplicates(subset=['cd_usina'], keep='first')
            df_data = df_data.reset_index(drop=True)
            df_data = df_data.sort_values('cd_usina').reset_index(drop=True)
        else:
            send_whatsapp_message(consts.WHATSAPP_GILSEU,f"Erro na atualização CVU \nTipo: CVU {params['tipo_cvu']} \nData do produto: {params['dt_produto'].strftime('%d/%m/%Y')} \nNão confere com a data padrão de atualização.",'')
            logger.info(f"Data do produto {params['dt_produto'].strftime('%d/%m/%Y')} não está entre o 2º e o 6º dia útil do mês.")
            raise ValueError(f"Data do produto {params['dt_produto'].strftime('%d/%m/%Y')} não está entre o 2º e o 6º dia útil do mês.")
        
    elif params['tipo_cvu'] == 'conjuntural':
        if params['dt_produto'].day > 15 and params['dt_produto'].day < 22:
            df_data = get_cvu_banco('cvu', 'conjuntural')
            df_data = df_data.sort_values('mes_referencia', ascending=False)
            df_data = df_data.drop_duplicates(subset=['cd_usina'], keep='first')
            df_data = df_data.reset_index(drop=True)
            df_data = df_data.sort_values('cd_usina').reset_index(drop=True)  
        else:
            send_whatsapp_message(consts.WHATSAPP_GILSEU,f"Erro na atualização CVU \nTipo: CVU {params['tipo_cvu']} \nData do produto: {params['dt_produto'].strftime('%d/%m/%Y')} \nNão confere com a data padrão de atualização.",'')
            logger.info(f"Data do produto {params['dt_produto'].strftime('%d/%m/%Y')} não está entre o 16º e o 21º dia do mês.")
            raise ValueError(f"Data do produto {params['dt_produto'].strftime('%d/%m/%Y')} não está entre o 16º e o 21º dia do mês.")
        
    elif params['tipo_cvu'] == 'merchant':
        df_data = get_cvu_banco('cvu', 'merchant')
        df_data = df_data.sort_values('mes_referencia', ascending=False)
        df_data = df_data.drop_duplicates(subset=['cd_usina'], keep='first')
        df_data = df_data.reset_index(drop=True)
        df_data = df_data.sort_values('cd_usina').reset_index(drop=True) 
    else:
        send_whatsapp_message(consts.WHATSAPP_GILSEU,f"Erro na atualização CVU \nTipo: CVU {params['tipo_cvu']} \nData do produto: {params['dt_produto'].strftime('%d/%m/%Y')} \nNão confere com  nenhum padão de cvu.",'')
        logger.info(f"Produto {params['produto']} inválido. Use 'conjuntural', 'conjuntural_revisado' ou 'merchant'.")
        raise ValueError(f"Produto {params['produto']} inválido. Use 'conjuntural', 'conjuntural_revisado' ou 'merchant'.")
             
    logging_name  = f'logging_cvu_{params["tipo_cvu"]}_rv'
    path_dadger   = download_dadger_update(params['id_estudo'], logger, params['path_download'])    
    tag_update    = f"CVU-DC{datetime.strptime(df_data['dt_atualizacao'][0], '%Y-%m-%d').strftime('(%d/%m)')}"       
    
    for path in path_dadger:
        print(f'Path do dadger: {path}')
        params_decomp= {
        'arquivo': os.path.basename(path),
        'dadger_path': path,
        'output_path': path,
        'id_estudo': None,
        'case': 'ATUALIZAÇÃO CVU '+ params['tipo_cvu'].upper(),
        'logger':criar_logger(f"{logging_name}.log", os.path.dirname(path) + '/' +f"{logging_name}{path[-1:]}.log") }
        
        meta_data = retrieve_dadger_metadata(**params_decomp)        
        params_decomp['output_path'] = os.path.dirname(path)
        
        dict_data = {'ct': {'cvu': {}}} 
        for ute in meta_data['power_plants']:
            if ute in df_data['cd_usina'].unique():
                dict_data['ct']['cvu'][f'{ute}'] = {}
        
        for stage in meta_data['stages']:
            data = meta_data['deck_date'] + relativedelta(weeks=+stage-1)+ timedelta(days=6)
            for ute in meta_data['power_plants']:
                if ute in df_data['cd_usina'].unique():
                    if params['tipo_cvu'] == 'merchant':
                        data_inicio = df_data[df_data['cd_usina']==ute]['data_inicio'].values[0]
                        data_inicio = datetime(int(data_inicio.split('-')[0]), int(data_inicio.split('-')[1]), int(data_inicio.split('-')[2]), 0, 0)
                        data_fim = df_data[df_data['cd_usina']==ute]['data_fim'].values[0]
                        data_fim = datetime(int(data_fim.split('-')[0]), int(data_fim.split('-')[1]), int(data_fim.split('-')[2]), 0, 0)
                        if data >= data_inicio and data <= data_fim:
                            dict_data['ct']['cvu'][f'{ute}'][f'{stage}'] = float(df_data.loc[(df_data['cd_usina']==ute),'vl_cvu'].values[0])                       
                    else:               
                        dict_data['ct']['cvu'][f'{ute}'][f'{stage}'] = float(df_data.loc[(df_data['cd_usina']==ute),'vl_cvu'].values[0])

        process_decomp(deepcopy( DecompParams(**params_decomp)), dict_data) 
   
    send_all_dadger_update(params['id_estudo'],params['path_download'],logger, logging_name, tag_update)
    

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


def criar_dict_weol():
    periods = [f'valor_p{i}' for i in range(1, 4)]
    data = {'pq': {}}
    for period in periods:
        data['pq'][period] = {}
        for region in ['SUL','NE','N']:
            for type_ in ['EOL']:
                key = f'{region}_{type_}'
                data['pq'][period][key] = {}
    return data ['pq']

def get_dados_banco(produto: str, date ='') -> dict:
    res = requests.get(BASE_URL_API + produto,
        headers=HEADER
    )
    if res.status_code != 200:
        logger.error(f"Erro {res.status_code} ao buscar carga: {res.text}")
        res.raise_for_status()
    return pd.DataFrame(res.json())


def get_cvu_banco(produto: str, fonte ='') -> dict:
    res = requests.get(BASE_URL_API + produto,
        params={ 'fonte': fonte},
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


def date_4_du(data_atual):
    ano = data_atual.year
    mes = data_atual.month
    data_inicio = datetime(ano, mes, 1)
    data_fim = datetime(ano, mes + 1, 1) - pd.Timedelta(days=1)
    dias_uteis = pd.bdate_range(start=data_inicio, end=data_fim)
    if len(dias_uteis) >= 6:
        segundo_dia_util = dias_uteis[1]  # 2º dia útil
        sexto_dia_util = dias_uteis[5]   # 6º dia útil        
        return segundo_dia_util.date() <= data_atual.date() <= sexto_dia_util.date()
    return False


BLOCK_FUNCTIONS = {
    'CARGA-DECOMP':  update_carga_and_mmgd,
    'EOLICA-DECOMP': update_eolica,
    'CVU-DECOMP': update_cvu,
    'RE-DECOMP': update_re,   
    None: lambda params: logger.error("Produto não informado ou inválido. Por favor, informe um produto válido.")
} 


def get_ids_estudos() -> list:
    consts.BASE_URL + '/estudos-middle/api/prospec/base-studies'
    res = requests.get(consts.BASE_URL + '/estudos-middle/api/prospec/base-studies',
        headers=HEADER
    )
    res.raise_for_status()
    return res.json()


def run_with_params():
        
    params =  {
        "produto": None, # CARGA-DECOMP, EOLICA-DECOMP, CVU-DECOMP, RE-DECOMP
        'id_estudo': None,
        'dt_produto': None, #datetime.now().replace(second=0, microsecond=0),
        'tipo_cvu': None,
        'path_download': create_directory(consts.PATH_RESULTS_PROSPEC,'update_decks') +'/',
        'path_out': create_directory(consts.PATH_RESULTS_PROSPEC,'update_decks') +'/',       
    }
    #BLOCK_FUNCTIONS[params['produto']](params) 
    if len(sys.argv) >= 3:
        for i in range(1, len(sys.argv)):
            argumento = sys.argv[i].lower()
            if   argumento ==   "produto": params[argumento]  = sys.argv[i+1].upper()            
            elif argumento == "id_estudo": params[argumento]  = eval(sys.argv[i+1])
            elif argumento == "tipo_cvu":  params[argumento]  = sys.argv[i+1]
            elif argumento == "dt_produto": params[argumento] =  datetime.strptime(sys.argv[i+1], '%d/%m/%Y')
    else:
        logger.info(f"Parâmetros recebidos: {params}")
        print("É obrigatorio informar o parametro: produto")
        sys.exit(1)
    if params['id_estudo'] is None:
        params['id_estudo'] = get_ids_estudos()
    print(params)
    BLOCK_FUNCTIONS[params['produto']](params)
        
 
if __name__ == '__main__':
    logger = criar_logger('logger.log', os.path.join(consts.PATH_ARQUIVOS, 'logger.log'))
    run_with_params()
