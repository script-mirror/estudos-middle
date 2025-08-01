# -*- coding: utf-8 -*-
import sys
import os
import shutil
import zipfile
import codecs
import logging
import time
from pathlib import Path
from datetime import datetime, date, timedelta
from string import ascii_lowercase
from copy import deepcopy
from typing import List, Dict, Any, Optional, Tuple
from middle.utils import SemanaOperativa
from middle.decomp import ons_to_ccee
from middle.message import send_whatsapp_message, send_email_message
import main_roda_estudos
from middle.utils.constants import Constants 
from middle.s3 import (
    handle_webhook_file,
    get_latest_webhook_product,
)
consts = Constants()

PATH_BASE:     str = os.path.join(consts.PATH_ARQUIVOS,  'prospec/backtest_decomp')
os.makedirs(consts.PATH_ARQUIVOS,exist_ok=True)
os.makedirs(PATH_BASE    ,exist_ok=True)
sys.path.append(os.path.join(consts.PATH_PROJETOS, "estudos-middle/api_prospec"))
import run_prospec
from functionsProspecAPI import  getStudiesByTag, authenticateProspec, getInfoFromStudy, downloadFileFromDeckV2

def create_directory(base_path: str, sub_path: str) -> Path:
        full_path = Path(base_path) / sub_path
        try: os.remove(full_path) if os.path.exists(full_path) else None
        except: pass
        try: shutil.rmtree(full_path) if os.path.exists(full_path) else None
        except: pass
        full_path.mkdir(parents=True, exist_ok=True)
        return full_path.as_posix()  

# Constants
PATH_CONFIG: Dict[str, str] = {
    'output_decks':   create_directory(PATH_BASE, 'output/decks'),
    'decomp_ons':     create_directory(consts.PATH_ARQUIVOS, 'decks/decomp/ons'),
    'decomp_interno': create_directory(PATH_BASE, 'input/decomp/interno')
}

FILES_TO_COPY: List[str] = ['caso.dat', 'hidr.dat', 'mlt.dat', 'perdas.dat', 'polinjus.csv', 'indices.csv']
DADGNL_VAZOES: List[str] = ['dadgnl.rv{}', 'vazoes.rv{}']
LOG_FORMAT: str = '%(asctime)s - %(levelname)s - %(message)s'
#CHECKLIST_BLOCKS: List[str] = ['UH', 'CT', 'PQ', 'DP', 'MP', 'RE', 'HV', 'HQ', 'VE']
CHECKLIST_BLOCKS: List[str] = []

# Configure logging
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger: logging.Logger = logging.getLogger(__name__)


def get_deck_interno(year, month, rv):
    authenticateProspec(consts.API_PROSPEC_USERNAME, consts.API_PROSPEC_PASSWORD)
    estudos = getStudiesByTag({'page':1, 'pageSize':3, 'tags':'P.CONJ'})
    for estudo in estudos['ProspectiveStudies']:
        if estudo['Status'] == 'Concluído':
            prospecId = estudo['Id']
            prospecStudy = getInfoFromStudy(prospecId)
            listOfDecks  = prospecStudy['Decks']
            for deck in listOfDecks:
                if deck['Model'] == 'DECOMP':
                    if deck['Year'] == year and deck['Month'] == month and deck['Revision'] == rv: 
                        path = consts.PATH_RESULTS_PROSPEC + '/decomp/' + deck['FileName']
                        arrayOfFiles = ['dadger.rv'+str(deck['Revision']), 'dadgnl.rv'+str(deck['Revision']), 'vazoes.rv'+str(deck['Revision'])]
                        downloadFileFromDeckV2(deck['Id'],consts.PATH_RESULTS_PROSPEC + '/decomp/', deck['FileName'], deck['FileName'],arrayOfFiles)
                        path_unzip = extract_zip_folder(path, path)
                        return path_unzip
     

def setup_directories(paths: List[str]) -> None:
    """Create or clear directories as needed."""
    for path in paths:
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
            os.makedirs(path)
            logger.info(f"Directory created: {path}")
        except Exception as e:
            logger.warning(f"Failed to setup directory {path}: {e}")

def convert_deck_ons_to_ccee(input_path: str,output_path: str, arqdec: str, rev: str, data: datetime ) -> None:
    """Execute script to convert ONS deck to CCEE format."""

    try:
        ons_to_ccee(input_path, output_path,  arqdec, rev, data)
        logger.info("ONS to CCEE conversion completed")
    except Exception as e:
        logger.error(f"ONS to CCEE conversion failed: {e}")
        raise
    return output_path


def find_dadger_file(directory: str, arquivo: str) -> str:
    """Find the dadger file in the specified directory."""
    for file in os.listdir(directory):
        if file.lower().startswith(arquivo.lower()):
            return file
    raise FileNotFoundError(f"No dadger file found in {directory}")

def extract_zip_folder(zip_path: str, folder: str) -> str:
    """Extract a zip folder to the specified path."""
    unzip_path: str = os.path.join(zip_path, folder[:-4])
    if not os.path.exists(unzip_path):
        os.makedirs(unzip_path)
    with zipfile.ZipFile(os.path.join(zip_path, folder), 'r') as zip_ref:
        zip_ref.extractall(unzip_path)
    logger.info(f"Extracted zip: {folder} to {unzip_path}")
    return unzip_path

def copy_files(file_list: List[str], src: str, dst: str) -> None:
    """Copy specified files from source to destination."""
    for file in file_list:
        src_path: str = os.path.join(src, file)
        dst_path: str = os.path.join(dst, file)
        if os.path.exists(src_path):
            shutil.copyfile(src_path, dst_path)
            logger.info(f"Copied {file} from {src} to {dst}")
        else:
            logger.warning(f"File {file} not found in {src}")

def convert_file_encoding(src_path: str, dst_path: str, src_encoding: str = 'ISO-8859-1', dst_encoding: str = 'utf-8') -> None:
    """Convert file encoding from source to destination."""
    try:
        with codecs.open(src_path, 'r', encoding=src_encoding) as src_file:
            with codecs.open(dst_path, 'w', encoding=dst_encoding) as dst_file:
                for line in src_file:
                    dst_file.write(line)
        logger.info(f"Converted {src_path} to {dst_path} with encoding {dst_encoding}")
    except Exception as e:
        logger.error(f"Failed to convert file {src_path}: {e}")
        raise

def create_deck(path_oficial: str, path_output: str, block: str, path_decomp: str) -> str:
    """Create a new deck directory for the specified block."""
    deck_path: str = os.path.join(path_output, f'{path_decomp}__ONS-TO-CCEE_{block}-RAIZEN')
    dc_path: str = os.path.join(deck_path, path_decomp)
    os.makedirs(deck_path)
    shutil.copytree(path_oficial, dc_path)
    logger.info(f"Created deck for block {block} at {deck_path}")
    return dc_path

def read_dadger(pathDadger: str) -> Dict[str, Any]:
    """Read a dadger file and organize its blocks."""
    dictDadger: Dict[str, List[str]] = {}
    blocoAtual: str = "TE"
    blocoAnterior: str = "TE"
    dictDadger['TE'] = []
    listOrdemBlocos: List[str] = []
    listOrdemBlocos.append('TE')
    dictdadger: Dict[str, Any] = {}

    with open(pathDadger) as f:
        for line in f:
            if line[0] != '&':
                if line[:2] in  ['VL', 'VU', 'LQ', 'CQ', 'LV', 'CV', 'FU', 'LU', 'FI', 'FE', 'FT', 'HE', 'CM']:
                    pass
                else:
                    blocoAtual = line[:2]
                    if blocoAtual != blocoAnterior:
                        dictDadger[blocoAtual] = []
                        listOrdemBlocos.append(blocoAtual)
                    else:
                        pass
                blocoAnterior = blocoAtual
            try:
                dictDadger[blocoAtual].append(line)
            except:
                pass
    dictdadger['dadger'] = dictDadger
    dictdadger['blocos'] = listOrdemBlocos
    return dictdadger

def write_dadger(arquivo: str, dadger: Dict[str, Any]) -> None:
    """Write a dadger file from its dictionary representation."""
    with open(arquivo, "w") as fh:
        for bloco in dadger['blocos']:
            for linha in dadger['dadger'][bloco]:
                fh.write(linha)
    time.sleep(1)

def alter_dadger(base_dadger: Dict[str, Any], block: str, external_block_data: List[str], output_path: str) -> Dict[str, Any]:
    """Alter the dadger file for the specified block."""
    base_dadger['dadger']['TE'] = [
        f"TE  DECOMP OFICIAL - UTILIZANDO O BLOCO RAIZEN: {block}\n"
        if line.startswith('TE') else line
        for line in base_dadger['dadger']['TE']
    ]
    base_dadger['dadger'][block] = external_block_data
    write_dadger(output_path, base_dadger)
    logger.info(f"Altered dadger for block {block} at {output_path}")
    return base_dadger

def zip_decomp_files(deck_path: str, zip_name: str, path_decomp: str) -> None:
    """Zip only the files in the DC folder, without including subdirectories."""
    dc_path: str = os.path.join(deck_path, path_decomp)
    zip_path: str = f"{zip_name}.zip"
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in os.listdir(dc_path):
                file_path: str = os.path.join(dc_path, file)
                if os.path.isfile(file_path):
                    zipf.write(file_path, arcname=file)
        logger.info(f"Created zip {zip_path} with files from {dc_path}")
    except Exception as e:
        logger.error(f"Failed to create zip {zip_path}: {e}")
        raise

def execute_prospec(params: Dict[str, Any], deck_path: str, deck_name: str) -> Any:
    """Execute Prospec for the given deck."""
    params['deck'] = f"{deck_name}.zip"
    params['path_deck'] = deck_path + '/'
    params['tag'] = 'DECOMP'
    params['aguardar_fim'] = False
    params['apenas_email'] = False
    params['back_teste'] = True

    try:
        prospec_out: Any = run_prospec.main(params)
        logger.info(f"Prospec executed for deck {deck_name}: {prospec_out}")
        return prospec_out
    except Exception as e:
        logger.error(f"Prospec execution failed for {deck_name}: {e}")
        raise

def main() -> None:
    parametros = {}
    """Main function to process and compare decks."""
    setup_directories([PATH_CONFIG['output_decks'], PATH_CONFIG['decomp_interno']])
    
    data             = datetime.today() + timedelta(days=7)
    data_rv          = SemanaOperativa(data)
    rev              = 'RV{}'.format(int(data_rv.current_revision))
    path_in          = get_deck_interno(data.year, data.month, int(data_rv.current_revision))
    payload          = get_latest_webhook_product(consts.WEBHOOK_DECK_DECOMP_PRELIMINAR)[0]       
    path_deck_decomp = handle_webhook_file(payload, PATH_CONFIG['decomp_ons'])
    deck_decomp      = 'DC' + data_rv.date.strftime('%Y%m') + '-' + rev
    output_path      = path_deck_decomp[:-4] + '/' + deck_decomp 
    arqdec           = 'DEC_ONS_' + data_rv.date.strftime('%m%Y') + '_' + rev + '_VE.zip'
    PATH_CONFIG['decomp_ons'] = convert_deck_ons_to_ccee( path_deck_decomp, output_path, arqdec, rev, data)
    
    # Find dadger file
    dadger_file: str = find_dadger_file(PATH_CONFIG['decomp_ons'], 'dadger.'+ rev)
    rv: str = dadger_file[-1:]

    # Copy necessary files
    copy_files(FILES_TO_COPY + [f'rv{rv}'], PATH_CONFIG['decomp_ons'], PATH_CONFIG['decomp_interno'])
    convert_file_encoding( os.path.join(path_in, dadger_file), os.path.join(PATH_CONFIG['decomp_interno'], dadger_file))    
    copy_files([f.format(rv) for f in DADGNL_VAZOES], path_in, PATH_CONFIG['decomp_interno'])
    
    # Read dadger files
    path_dc_oficial: str = os.path.join(PATH_CONFIG['decomp_ons'], dadger_file)
    path_dc_raizen: str = os.path.join(PATH_CONFIG['decomp_interno'], dadger_file)
    dadger_oficial: Dict[str, Any] = read_dadger(path_dc_oficial)
    dadger_raizen: Dict[str, Any] = read_dadger(path_dc_raizen)

  
    # Setup output decks
    for folder in [deck_decomp + '__ONS-TO-CCEE', deck_decomp + '__RAIZEN', deck_decomp + '__ONS-TO-CCEE_VAZOES-RAIZEN']:
        folder_path: str = os.path.join(PATH_CONFIG['output_decks'], folder)
        os.makedirs(folder_path, exist_ok=True)
        if folder == deck_decomp + '__RAIZEN':
            shutil.copytree(PATH_CONFIG['decomp_interno'], os.path.join(folder_path, deck_decomp))
        elif folder == deck_decomp + '__ONS-TO-CCEE':
            shutil.copytree(PATH_CONFIG['decomp_ons'], os.path.join(folder_path, deck_decomp))
        elif folder == deck_decomp + '__ONS-TO-CCEE_VAZOES-RAIZEN':
            shutil.copytree(PATH_CONFIG['decomp_ons'], os.path.join(folder_path, deck_decomp))
            shutil.copy(
                os.path.join(PATH_CONFIG['decomp_interno'], f'vazoes.rv{rv}'),
                os.path.join(folder_path, deck_decomp) )

        logger.info(f"Setup output folder: {folder_path}")

    # Process checklist blocks
    for block in CHECKLIST_BLOCKS:
        deck_path: str = create_deck(PATH_CONFIG['decomp_ons'], PATH_CONFIG['output_decks'], block, deck_decomp)        
        alter_dadger( 
            deepcopy(dadger_oficial), 
            block,  
            dadger_raizen['dadger'][block],
            os.path.join(deck_path, dadger_file)
            )

    # Execute Prospec for each deck
    id_prospec_list: List[Any] = []
    for deck in os.listdir(PATH_CONFIG['output_decks']):
        deck_path: str = os.path.join(PATH_CONFIG['output_decks'], deck)
        zip_decomp_files(deck_path, os.path.join(PATH_CONFIG['output_decks'], deck), deck_decomp)
        id_prospec_list.append(execute_prospec(parametros, PATH_CONFIG['output_decks'], deck))
        try:
            if deck.split('__')[1] == 'ONS-TO-CCEE':
                id_oficial = [id_prospec_list[-1]]
                send_whatsapp_message(consts.WHATSAPP_GILSEU,'Deck Decomp ONS to CCEE', os.path.join(PATH_CONFIG['output_decks'], deck+'.zip'))
        except: pass

    # Wait and send email
    parametros['apenas_email']  = True
    parametros['aguardar_fim']  = True
    parametros['prevs_name']    = None
    parametros['assunto_email'] = None
    parametros['media_rvs']     = False
    parametros['considerar_rv'] = ''
    parametros['id_estudo']     = id_oficial
    parametros['assunto_email'] = 'Decomp ONS to CCEE'
    parametros['corpo_email']   = 'Decomp ONS to CCEE'
    parametros['list_email']    = [consts.EMAIL_MIDDLE, consts.EMAIL_FRONT]
    parametros['list_whats']    = [consts.WHATSAPP_PMO]
    parametros['path_result']   = create_directory(consts.PATH_RESULTS_PROSPEC, '')
    time.sleep(600)
    main_roda_estudos.send_email(parametros)
    
    parametros['prevs_name']    = None
    parametros['assunto_email'] = None
    parametros['id_estudo']     = id_prospec_list
    main_roda_estudos.send_email(parametros)
 
   
if __name__ == '__main__':
    
    main()