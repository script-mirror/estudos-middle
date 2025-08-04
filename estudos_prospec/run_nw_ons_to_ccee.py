import datetime as dt
import logging
import os
import shutil
import sys
from collections import defaultdict
from datetime import datetime
import zipfile
import openpyxl
from pathlib import Path
from middle.utils.constants import Constants 
from tqdm import tqdm
from middle.message import send_whatsapp_message
from middle.s3 import (
    handle_webhook_file,
    get_latest_webhook_product,
)
consts = Constants()
sys.path.append(os.path.join(consts.PATH_PROJETOS, "estudos-middle/api_prospec"))
import run_prospec
from functionsProspecAPI import  getStudiesByTag, authenticateProspec, getInfoFromStudy, downloadFileFromDeckV2

# Configure logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def create_directory(base_path: str, sub_path: str) -> Path:
        full_path = Path(base_path) / sub_path
        try: os.remove(full_path) if os.path.exists(full_path) else None
        except: pass
        try: shutil.rmtree(full_path) if os.path.exists(full_path) else None
        except: pass
        full_path.mkdir(parents=True, exist_ok=True)
        return full_path.as_posix()  


def get_deck_interno():
    authenticateProspec(consts.API_PROSPEC_USERNAME, consts.API_PROSPEC_PASSWORD)
    estudos = getStudiesByTag({'page':1, 'pageSize':3, 'tags':'FCF'})
    for estudo in estudos['ProspectiveStudies']:
        if estudo['Status'] == 'Concluído':
            prospecId = estudo['Id']
            prospecStudy = getInfoFromStudy(prospecId)
            listOfDecks  = prospecStudy['Decks']
            for deck in listOfDecks:
                if deck['Model'] == 'NEWAVE':
                    path = consts.PATH_RESULTS_PROSPEC + '/newave/' + deck['FileName']
                    arrayOfFiles = ['dger.dat', 'vazpast.dat', 'vazoes.dat','arquivos.dat', 'confhd.dat']
                    downloadFileFromDeckV2(deck['Id'],consts.PATH_RESULTS_PROSPEC + '/newave/', deck['FileName'], deck['FileName'],arrayOfFiles)
                    return extract_zip_folder(path, path)


def extract_zip_folder(zip_path: str, folder: str) -> str:
    """Extract a zip folder to the specified path."""
    unzip_path: str = os.path.join(zip_path, folder[:-4])
    if not os.path.exists(unzip_path):
        os.makedirs(unzip_path)
    with zipfile.ZipFile(os.path.join(zip_path, folder), 'r') as zip_ref:
        zip_ref.extractall(unzip_path)
    return unzip_path


def gtmin_ccee(src):
    """Read GTMIN data from Excel and return a dictionary mapping usid to month and gtmin_agente."""
    logging.info(f"Loading data from {src}")
    try:
        workbook = openpyxl.load_workbook(src)
        sheet = workbook['GTmin_e_CCEE']
        gtmin = defaultdict(dict)
        for row in tqdm(range(3, len(list(sheet.rows))), desc="Reading Excel rows"):
            try:
                usid = int(sheet.cell(row, 1).value)
                month = sheet.cell(row, 3).value.date()
                gtmin_agente = float(sheet.cell(row, 4).value)
                gtmin[usid][month] = gtmin_agente
            except (TypeError, ValueError) as e:
                logging.warning(f"Skipping row {row} due to error: {e}")
        return dict(gtmin)
    except Exception as e:
        logging.error(f"Failed to read Excel file {src}: {e}")
        raise


def update_gtmin(arquivo, data, data_deck):
    """Update EXPT file with CCEE data and insert TEIFT lines."""
    with open(arquivo, 'r') as f1:
        expt = f1.readlines()
    rows = ''
    for i in tqdm(range(2, len(expt)), desc="Processing EXPT lines"):
        ln = expt[i]
        try:
            usid = int(ln[:4])
            first_month, first_year = int(ln[20:22]), int(ln[23:27])
            first_date = dt.date(first_year, first_month, 1)
            if 'GTMIN' in ln:
                inflex_ons = float(ln[12:19])
                logging.debug(f"USID: {usid}, Date: {first_date}, Inflex_ONS: {inflex_ons}")
                if first_date.year < 2030:
                    inflex_ccee = data.get(usid, {}).get(first_date, float('inf'))
                    if inflex_ccee < inflex_ons:
                        ln = ln.replace(ln[12:19], f"{inflex_ccee:.2f}".zfill(7).rjust(7))
        except (ValueError, IndexError) as e:
            logging.error(f"Invalid line format at line {i+1}: {ln.strip()} - {e}")
            continue
        rows += ln
        if i + 1 < len(expt):
            next_ln = expt[i + 1]
            next_usid = int(next_ln[:4])
            if next_usid != usid:
                next_month = (data_deck.replace(day=28) + dt.timedelta(days=4)).replace(day=1)
                extra_line = f"{str(usid).rjust(4)} TEIFT     0.00 {data_deck.month:>2} {data_deck.year} {next_month.month:>2} {next_month.year}\n"
                rows += extra_line
                
    new_expt =  expt[0] + expt[1] + rows
    with open(arquivo, 'w') as f:
        for line in new_expt:
            f.write(line)
  
               
def update_re(file_path):

    with open(file_path, 'r',  encoding='latin1') as f:
        lines = f.readlines()

    with open(file_path, 'w',  encoding='latin1') as f:
        for line in lines:
            parts = line.strip().split(';')
            if len(parts) >= 2 and parts[1].strip() == '10':
                line = '&'+line
            f.write(line)


def update_confhd(confhd_path, internal_path):

    with open(confhd_path, 'r', encoding='latin1') as f1:
        confhd_lines = f1.readlines()

    with open(internal_path, 'r', encoding='latin1') as f2:
        internal_lines = f2.readlines()

    internal_ids = {line.strip().split()[0] for line in internal_lines if line.strip()}

    new_lines = [
        line for line in confhd_lines
        if line.strip() and line.strip().split()[0] not in internal_ids
    ]

    with open(internal_path, 'a', encoding='latin1') as f:
        for line in new_lines:
            f.write(line)

    print(f"{len(new_lines)} line(s) added to '{internal_path}'.")
  
    
def update_confhd(confhd_path, internal_path):
 
    confhd_path = match_file_case_insensitive(confhd_path)
    internal_path = match_file_case_insensitive(internal_path)

    with open(confhd_path, 'r', encoding='latin1') as f:
        confhd_lines = f.readlines()

    with open(internal_path, 'r', encoding='latin1') as f:
        internal_lines = f.readlines()

    internal_ids = {line.strip().split()[0] for line in internal_lines if line.strip()}

    new_lines = [
        line for line in confhd_lines
        if line.strip() and line.strip().split()[0] not in internal_ids
    ]

    with open(internal_path, 'a', encoding='latin1') as f:
        for line in new_lines:
            f.write(line)

    print(f"{len(new_lines)} line(s) added to '{internal_path}'.")


def match_file_case_insensitive(filepath):
  
    directory, target_name = os.path.split(filepath)
    directory = directory or '.'  # handle empty path (current dir)

    for filename in os.listdir(directory):
        if filename.lower() == target_name.lower():
            return os.path.join(directory, filename)
    raise FileNotFoundError(f"File '{target_name}' not found in '{directory}'.")


def get_deck_newave(path):
    preliminar  = True
    payload     = get_latest_webhook_product(consts.WEBHOOK_DECK_NEWAVE_PRELIMINAR)[0] 
    payload_def = get_latest_webhook_product(consts.WEBHOOK_DECK_NEWAVE_DEFINITIVO)[0] 
    
    if datetime.fromisoformat(payload_def['createdAt'].replace('Z', '+00:00')) > datetime.fromisoformat(payload['createdAt'].replace('Z', '+00:00')):
        preliminar=False
        payload = payload_def 
            
    path_deck_nw  = handle_webhook_file(payload, path)
    path_deck_nw  = extract_zip_folder(path_deck_nw, path_deck_nw)
    parts             = os.listdir(path_deck_nw)[0].split('.')[0].split('_')
    print('DECK ENCONTRADO: ', os.listdir(path_deck_nw)[0])
    data_deck         = dt.date(int(parts[2]), int(parts[3]), 1)  
    path_deck_nw  = path_deck_nw +'/' +os.listdir(path_deck_nw)[0]
    path_deck_nw  = extract_zip_folder(path_deck_nw, path_deck_nw)
    return path_deck_nw, data_deck, preliminar
 
 
def get_gtmin(path_in):
    payload  = get_latest_webhook_product(consts.WEBHOOK_NOTAS_TECNICAS)
    for arquivo in payload:
        path  = handle_webhook_file(arquivo, path_in)
        path = extract_zip_folder(path, path)
        for file in os.listdir(path):
            if file.lower().startswith('gtmin_ccee'):
                return path, file


def get_expt_name(path):
    for file in os.listdir(path):
        if file.lower().startswith('expt'):
            return path + '/'+ file 


def zip_files(deck_path: str,  path_out: str) -> None:
    """Zip only the files in the DC folder, without including subdirectories."""
    
    with zipfile.ZipFile(path_out, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in os.listdir(deck_path):
            file_path: str = os.path.join(deck_path, file)
            if os.path.isfile(file_path):
                zipf.write(file_path, arcname=file)

def execute_prospec(deck_path: str, deck_name: str):
    params = {}
    params['deck'] = f"{deck_name}.zip"
    params['path_deck'] = deck_path + '/'
    params['tag'] = 'FCF'
    params['aguardar_fim'] = False
    params['apenas_email'] = False
    params['back_teste'] = True
    run_prospec.main(params)
             
def main():
    
    PATH_BASE = create_directory(consts.PATH_ARQUIVOS, 'decks/newave/ons') 
            
    path_deck_nw, data_deck, preliminar = get_deck_newave(PATH_BASE)                   
    path_gtmin, gtmin_file = get_gtmin(PATH_BASE)
    path_expt = get_expt_name(path_deck_nw)
    deck_name =  'NW' + data_deck.strftime('%Y%m')+'_ONS-TO-CCEE.zip'
    
    if preliminar:
        deck_name =  'NW' + data_deck.strftime('%Y%m')+'_ONS-TO-CCEE_PRELIMINAR.zip'
        PATH_NW_INTERNO = get_deck_interno()
        shutil.copy(PATH_NW_INTERNO + '/dger.dat',     path_deck_nw + '/dger.dat')
        shutil.copy(PATH_NW_INTERNO + '/vazoes.dat',   path_deck_nw + '/vazoes.dat')
        shutil.copy(PATH_NW_INTERNO + '/vazpast.dat',  path_deck_nw + '/vazpast.dat')
        shutil.copy(PATH_NW_INTERNO + '/arquivos.dat', path_deck_nw + '/arquivos.dat')
        update_confhd(path_deck_nw + "/confhd.dat", PATH_NW_INTERNO + "/confhd.dat")
        shutil.copy(PATH_NW_INTERNO + '/confhd.dat', path_deck_nw + '/confhd.dat')
        
    update_re(path_deck_nw + "/restricao-eletrica.csv")    
    update_gtmin(path_expt, gtmin_ccee(path_gtmin +'/'+ gtmin_file), data_deck)
    zip_files(path_deck_nw,  PATH_BASE+'/'+deck_name)
    send_whatsapp_message(consts.WHATSAPP_GILSEU,'Deck Newave ONS to CCEE com GTMIN: ' + gtmin_file,  PATH_BASE+'/'+deck_name)
    execute_prospec(PATH_BASE, deck_name.split('.')[0]) 
    
if __name__ == "__main__":
    main()
