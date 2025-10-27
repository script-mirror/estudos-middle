# -*- coding: utf-8 -*-
import sys
import os
import shutil
import zipfile
import codecs
import logging
import re
import time
import pandas as pd
from pathlib import Path
from datetime import datetime, date, timedelta
from string import ascii_lowercase
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from middle.message import send_whatsapp_message
from middle.utils import Constants, setup_logger, extract_zip, create_directory, SemanaOperativa, get_decks_ccee
from middle.s3 import (
    handle_webhook_file,
    get_latest_webhook_product,
)
consts = Constants()
logger = setup_logger()


def get_latest_deck_ccee(data):
    path_deck = get_decks_ccee(path=consts.PATH_ARQUIVOS_TEMP, deck='dessem', file_name= consts.CCEE_DECK_DESSEM)
    path_deck_unzip = extract_zip(path_deck)
    files = os.listdir(path_deck_unzip)
    decks = [file for file in files if 'Resultado' not in file]
    for days in range(5):
        date_check = (data - timedelta(days=days))
        rv = int(SemanaOperativa(date_check).current_revision)
        deck = [file for file in decks if f'RV{rv}D{str(date_check.day).zfill(2)}' in file]
        if deck:
            latest_deck = max(deck, key=lambda x: os.path.getctime(os.path.join(path_deck_unzip, x)))    
            return extract_zip(os.path.join(path_deck_unzip, latest_deck))
        
def get_latest_deck_ons(data):
    df_payload = pd.DataFrame(get_latest_webhook_product(consts.WEBHOOK_DECK_DESSEM))
    data = data.strftime("%Y-%m-%d")
    payload = df_payload[df_payload['periodicidade'].str.contains(data)]
    if payload.empty:
        raise ValueError(f"No deck found for date {data} in webhook payloads.")
    path_deck = handle_webhook_file(dict(payload.iloc[0]),  consts.PATH_ARQUIVOS_TEMP)
    path_deck_unzip = extract_zip(path_deck)
    return path_deck_unzip

def create_deck_base(path_ons: str, path_ccee: str):
    rv= path_ccee.split('RV')[1][:1]
    files_ccee_to_copy = [f'cortdeco.rv{rv}', 'rmpflx.dat','dessem.arq',f'mapcut.rv{rv}','restseg.dat','rstlpp.dat']
    path_dest = path_ons.replace('ONS', 'ONS-TO-CCEE')
    create_directory(path_dest,'')
    
    for file in os.listdir(path_ons):
        if not file.endswith('.afp') and not file.endswith('.pwf') and not file.startswith('pdo_'):
            shutil.copyfile(os.path.join(path_ons, file), os.path.join(path_dest, file))
    
    for file in os.listdir(path_ccee):
        if file in files_ccee_to_copy:
            shutil.copyfile(os.path.join(path_ccee, file), os.path.join(path_dest, file)) 
    return path_dest


  
def find_file(directory: str, file_find: str) -> str:
    """Find the dadger file in the specified directory."""
    logger.info(f"Searching {file_find} in {directory}")
    for file in os.listdir(directory):
        if file.lower().startswith(file_find.lower()):
            logger.info(f"File found: {file}")
            file_txt = open(os.path.join(directory, file),
            'r', encoding='utf-8', errors='ignore').readlines()
            return file_txt
    logger.error(f"No {file_find} file found in {directory}")
    raise FileNotFoundError(f"No {file_find} file found in {directory}") 

def write_file(directory: str, file_name: str, content: List[str]) -> None:
    """Write content to a file in the specified directory."""
    with open(os.path.join(directory, file_name), 'w', encoding='utf-8') as f:
        f.writelines(content)
    logger.info(f"File {file_name} written successfully in {directory}")



def format_line(parts, line) -> str:
    new_line = parts[0]
    base_parts = line.split()
    space = re.findall(r'\s+', line)
    for i in range(1,len(parts)):
        new_line += parts[i].rjust(len(space[i-1]) + len(base_parts[i]))
    return new_line + space[-1]
 
def adjust_tm(entdados):
    for line in entdados:
        parts= line.split()
        if parts[0] == 'TM':
            parts[5] = '0'
            yield format_line(parts, line)
        else:
            yield line
    return entdados

def map_entdados_ccee(file):
    re_map = []
    ce_map = []
    barra = {'CI':{} ,'CE':{}}
    for line in file:
        parts = line.split()
        if parts[0] == 'RE':
            re_map.append(parts[1])
        if parts[0] == 'CE':
            ce_map.append(parts[1])
            barra['CE'][parts[1]] = parts[3]
        if parts[0] == 'CI':
            ce_map.append(parts[1])
            barra['CI'][parts[1]] = parts[3]
    return {'RE': re_map, 'CE': ce_map, 'CI': ce_map, 'BARRA': barra}


def adjust_di(entdados: str):
    res = ['RE','LU','FI','FH','FE','FT','FC','FR']
    comented_lu = []
    for line in entdados:
        parts = line.split()
        if parts[0] in res:
            if int(parts[1]) >800:
                if parts[0] == 'LU':
                    if  parts[1] not in comented_lu:
                        comented_lu.append(parts[1])
                        parts[2] = 'I'.rjust(len(parts[2]))
                else:
                    parts[2] = 'I'.rjust(len(parts[2]))
                yield format_line(parts, line)
            else:
                yield line
        else:
            yield line
    return entdados


def coment_entdados(entdados: str, map_ccee: dict) -> str:
    entdados_ccee = []
    reg_coments = ['RD']
    res = ['RE','LU','FI','FH','FE','FT','FC','FR']
    
    for line in entdados:
        coment = ''
        parts = line.split()
        if parts[0] in reg_coments:
            coment = '&'
        elif parts[0] in res:
            if parts[1] not in map_ccee['RE']:
                coment = '&'
        elif parts[0] == 'CI':
            if parts[1] not in map_ccee['CI']:
                coment = '&'
        elif parts[0] == 'CE':
            if parts[1] not in map_ccee['CE']:
                coment = '&'
        entdados_ccee.append(coment+line)
    return entdados_ccee
    
def adjust_barras(entdados: str, map_ccee: dict):
    for line in entdados:
        parts = line.split()
        if parts[0] in ['CI','CE']:
            if parts[1] in map_ccee[parts[0]]:
                parts[3] = map_ccee[parts[0]][parts[1]]
                yield format_line(parts, line)
            else:
                yield line
        else: 
            yield line
    return entdados
def read_load_pdo(path:str)-> pd.DataFrame:
    pdo_file = find_file(path, 'pdo_sist.dat')
    with open(pdo_file, 'r', encoding='utf-8') as f:
        pdo_file = f.readlines()
    data = []
    load = False
    for line in pdo_file:
        parts = line.split(';')
        if parts[0].lower() == 'iper':
            load = True
            continue
        if load and line[0] != '-':
            data.append({
                'PERIODO': parts[0],
                'SUB': parts[2],
                'CARGA': parts[4]
            })
    df_pdo = pd.DataFrame(data)
    return df_pdo

def main() -> None:
    data = datetime.now()
    path_ccee = get_latest_deck_ccee(data)
    path_ons  = get_latest_deck_ons(data)
    path_ons_to_ccee = create_deck_base(path_ons, path_ccee)
    
    entdados = adjust_tm(find_file(path_ons_to_ccee, 'entdados.dat'))
    entdados = adjust_di(entdados)
    map_ccee = map_entdados_ccee(find_file(path_ccee, 'entdados.dat'))
    entdados = coment_entdados(entdados, map_ccee)
    entdados = adjust_barras(entdados, map_ccee['BARRA'])
    write_file(path_ons_to_ccee, 'entdados.dat', entdados)

            
    shutil.rmtree(os.path.dirname(path_ccee), ignore_errors=True)
    shutil.rmtree(path_ons, ignore_errors=True)
    pass

if __name__ == '__main__':
    logger.info("Script execution started")
    main()
    logger.info("Script execution completed")