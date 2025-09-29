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
from middle.message import send_whatsapp_message
import main_roda_estudos
from middle.utils import Constants
from middle.utils.file_manipulation import extract_zip
from middle.s3 import (
    handle_webhook_file,
    get_latest_webhook_product,
)
consts = Constants()
# Configure logging
LOG_FORMAT: str = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger: logging.Logger = logging.getLogger(__name__)
PATH_BASE: str = os.path.join(consts.PATH_ARQUIVOS,  'prospec/backtest_decomp')
os.makedirs(consts.PATH_ARQUIVOS, exist_ok=True)
os.makedirs(PATH_BASE, exist_ok=True)
sys.path.append(os.path.join(consts.PATH_PROJETOS, "estudos-middle/api_prospec"))   
import run_prospec
from functionsProspecAPI import getStudiesByTag, authenticateProspec, getInfoFromStudy, downloadFileFromDeckV2

def create_directory(base_path: str, sub_path: str) -> Path:
    logger.info(f"Creating directory at {base_path}/{sub_path}")
    full_path = Path(base_path) / sub_path
    try:
        if os.path.exists(full_path):
            logger.debug(f"Removing existing directory: {full_path}")
            os.remove(full_path)
    except:
        logger.warning(f"Failed to remove file {full_path}")
        pass
    try:
        if os.path.exists(full_path):
            logger.debug(f"Removing existing directory tree: {full_path}")
            shutil.rmtree(full_path)
    except:
        logger.warning(f"Failed to remove directory tree {full_path}")
        pass
    full_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Directory created successfully: {full_path}")
    return full_path.as_posix()

# Constants
PATH_CONFIG: Dict[str, str] = {
    'output_decks':   create_directory(PATH_BASE, 'output/decks'),
    'decomp_ons':     create_directory(consts.PATH_ARQUIVOS, 'decks/decomp/ons'),
    'decomp_interno': create_directory(PATH_BASE, 'input/decomp/interno')
}

FILES_TO_COPY: List[str] = ['caso.dat', 'hidr.dat', 'mlt.dat', 'perdas.dat', 'polinjus.csv', 'indices.csv']
DADGNL_VAZOES: List[str] = ['dadgnl.rv{}', 'vazoes.rv{}']
CHECKLIST_BLOCKS: List[str] = ['UH', 'CT', 'PQ', 'DP', 'MP', 'RE', 'HV', 'HQ', 'VE']

def get_deck_interno(year, month, rv):
    logger.info(f"Fetching internal deck for year={year}, month={month}, revision={rv}")
    authenticateProspec(consts.API_PROSPEC_USERNAME, consts.API_PROSPEC_PASSWORD)
    logger.debug("Authenticated with Prospec API")
    estudos = getStudiesByTag({'page': 1, 'pageSize': 3, 'tags': 'P.CONJ'})
    logger.debug(f"Retrieved {len(estudos['ProspectiveStudies'])} studies with tag P.CONJ")
    for estudo in estudos['ProspectiveStudies']:
        if estudo['Status'] == 'Concluído':
            prospecId = estudo['Id']
            logger.info(f"Processing study ID: {prospecId}")
            prospecStudy = getInfoFromStudy(prospecId)
            listOfDecks = prospecStudy['Decks']
            for deck in listOfDecks:
                if deck['Model'] == 'DECOMP':
                    if deck['Year'] == year and deck['Month'] == month and deck['Revision'] == rv:
                        logger.info(f"Deck found in study {prospecId}: {deck['FileName']}")
                        path = consts.PATH_RESULTS_PROSPEC + '/decomp/' + deck['FileName']
                        arrayOfFiles = ['dadger.rv'+str(deck['Revision']), 'dadgnl.rv'+str(deck['Revision']), 'vazoes.rv'+str(deck['Revision'])]
                        logger.debug(f"Downloading files: {arrayOfFiles}")
                        downloadFileFromDeckV2(deck['Id'], consts.PATH_RESULTS_PROSPEC + '/decomp/', deck['FileName'], deck['FileName'], arrayOfFiles)
                        path_unzip = extract_zip(path)
                        logger.info(f"Extracted zip to {path_unzip}")
                        return path_unzip
    logger.warning(f"No matching deck found for year={year}, month={month}, revision={rv}")
    return None

def setup_directories(paths: List[str]) -> None:
    """Create or clear directories as needed."""
    logger.info("Setting up directories")
    for path in paths:
        try:
            if os.path.exists(path):
                logger.debug(f"Clearing existing directory: {path}")
                shutil.rmtree(path)
            os.makedirs(path)
            logger.info(f"Directory created: {path}")
        except Exception as e:
            logger.warning(f"Failed to setup directory {path}: {e}")

def convert_deck_ons_to_ccee(input_path: str, output_path: str, arqdec: str, rev: str, data: datetime) -> None:
    """Execute script to convert ONS deck to CCEE format."""
    logger.info(f"Converting ONS deck to CCEE format: {input_path} -> {output_path}")
    try:
        ons_to_ccee(input_path, output_path, arqdec, rev, data)
        logger.info("ONS to CCEE conversion completed")
    except Exception as e:
        logger.error(f"ONS to CCEE conversion failed: {e}")
        raise
    return output_path

def find_dadger_file(directory: str, arquivo: str) -> str:
    """Find the dadger file in the specified directory."""
    logger.info(f"Searching for dadger file starting with {arquivo} in {directory}")
    for file in os.listdir(directory):
        if file.lower().startswith(arquivo.lower()):
            logger.info(f"Dadger file found: {file}")
            return file
    logger.error(f"No dadger file found in {directory}")
    raise FileNotFoundError(f"No dadger file found in {directory}")

def copy_files(file_list: List[str], src: str, dst: str) -> None:
    """Copy specified files from source to destination."""
    logger.info(f"Copying files from {src} to {dst}")
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
    logger.info(f"Converting file encoding: {src_path} to {dst_path}")
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
    logger.info(f"Creating deck for block {block} at {path_output}")
    deck_path: str = os.path.join(path_output, f'{path_decomp}__ONS-TO-CCEE_{block}-RAIZEN')
    dc_path: str = os.path.join(deck_path, path_decomp)
    os.makedirs(deck_path)
    shutil.copytree(path_oficial, dc_path)
    logger.info(f"Created deck for block {block} at {deck_path}")
    return dc_path

def read_dadger(pathDadger: str) -> Dict[str, Any]:
    """Read a dadger file and organize its blocks."""
    logger.info(f"Reading dadger file: {pathDadger}")
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
                if line[:2] in ['VL', 'VU', 'LQ', 'CQ', 'LV', 'CV', 'FU', 'LU', 'FI', 'FE', 'FT', 'HE', 'CM']:
                    pass
                else:
                    blocoAtual = line[:2]
                    if blocoAtual != blocoAnterior:
                        dictDadger[blocoAtual] = []
                        listOrdemBlocos.append(blocoAtual)
                        logger.debug(f"New block detected: {blocoAtual}")
                    else:
                        pass
                blocoAnterior = blocoAtual
            try:
                dictDadger[blocoAtual].append(line)
            except:
                logger.warning(f"Failed to append line to block {blocoAtual}")
                pass
    dictdadger['dadger'] = dictDadger
    dictdadger['blocos'] = listOrdemBlocos
    logger.info(f"Dadger file read successfully: {pathDadger}")
    return dictdadger

def write_dadger(arquivo: str, dadger: Dict[str, Any]) -> None:
    """Write a dadger file from its dictionary representation."""
    logger.info(f"Writing dadger file: {arquivo}")
    with open(arquivo, "w") as fh:
        for bloco in dadger['blocos']:
            for linha in dadger['dadger'][bloco]:
                fh.write(linha)
    time.sleep(1)
    logger.info(f"Dadger file written successfully: {arquivo}")

def alter_dadger(base_dadger: Dict[str, Any], block: str, external_block_data: List[str], output_path: str) -> Dict[str, Any]:
    """Alter the dadger file for the specified block."""
    logger.info(f"Altering dadger file for block {block} at {output_path}")
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
    logger.info(f"Zipping files from {deck_path}/{path_decomp} to {zip_name}.zip")
    dc_path: str = os.path.join(deck_path, path_decomp)
    zip_path: str = f"{zip_name}.zip"
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in os.listdir(dc_path):
                file_path: str = os.path.join(dc_path, file)
                if os.path.isfile(file_path):
                    zipf.write(file_path, arcname=file)
                    logger.debug(f"Added file to zip: {file}")
        logger.info(f"Created zip {zip_path} with files from {dc_path}")
    except Exception as e:
        logger.error(f"Failed to create zip {zip_path}: {e}")
        raise

def execute_prospec(params: Dict[str, Any], deck_path: str, deck_name: str) -> Any:
    """Execute Prospec for the given deck."""
    logger.info(f"Executing Prospec for deck {deck_name} at {deck_path}")
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

def get_latest_deck(arqdec):
    logger.info(f"Fetching latest deck: {arqdec}")
    payload = get_latest_webhook_product(consts.WEBHOOK_DECK_DECOMP_PRELIMINAR)[0]
    logger.debug("Retrieved latest webhook product")
    path_deck_decomp = handle_webhook_file(payload, PATH_CONFIG['decomp_ons'])
    logger.debug(f"Handled webhook file, path: {path_deck_decomp}")
    deck_encontrado = extract_zip(path_deck_decomp)
    if arqdec in os.listdir(deck_encontrado):
        logger.info(f"Deck {arqdec} found in {deck_encontrado}")
        return path_deck_decomp
    else:
        logger.error(f"Deck {arqdec} not found in {deck_encontrado}")
        logger.error(f"Available decks: {os.listdir(deck_encontrado)}")
        raise FileNotFoundError(f"Deck {arqdec} not found in {deck_encontrado}")

def main() -> None:
    logger.info("Starting main execution")
    parametros = {}
    setup_directories([PATH_CONFIG['output_decks'], PATH_CONFIG['decomp_interno']])
    data = datetime.today() + timedelta(days=7)
    logger.info(f"Using date: {data}")
    data_rv = SemanaOperativa(data)
    rev = 'RV{}'.format(int(data_rv.current_revision))
    logger.info(f"Revision: {rev}")
    deck_decomp = 'DC' + data_rv.date.strftime('%Y%m') + '-' + rev
    logger.info(f"Deck decomp: {deck_decomp}")
    arqdec = 'DEC_ONS_' + data_rv.date.strftime('%m%Y') + '_' + rev + '_VE.zip'
    logger.info(f"Fetching deck: {arqdec}")
    path_deck_decomp = get_latest_deck(arqdec)
    output_path = path_deck_decomp[:-4] + '/' + deck_decomp
    path_in = get_deck_interno(data.year, data.month, int(data_rv.current_revision))
    logger.info(f"Internal deck path: {path_in}")
    PATH_CONFIG['decomp_ons'] = convert_deck_ons_to_ccee(path_deck_decomp, output_path, arqdec, rev, data)
    
    # Find dadger file
    logger.info("Finding dadger file")
    dadger_file: str = find_dadger_file(PATH_CONFIG['decomp_ons'], 'dadger.' + rev)
    rv: str = dadger_file[-1:]
    logger.info(f"Dadger file: {dadger_file}, revision: {rv}")

    # Copy necessary files
    logger.info("Copying necessary files")
    copy_files(FILES_TO_COPY + [f'rv{rv}'], PATH_CONFIG['decomp_ons'], PATH_CONFIG['decomp_interno'])
    convert_file_encoding(os.path.join(path_in, dadger_file), os.path.join(PATH_CONFIG['decomp_interno'], dadger_file))
    copy_files([f.format(rv) for f in DADGNL_VAZOES], path_in, PATH_CONFIG['decomp_interno'])
    
    # Read dadger files
    logger.info("Reading dadger files")
    path_dc_oficial: str = os.path.join(PATH_CONFIG['decomp_ons'], dadger_file)
    path_dc_raizen: str = os.path.join(PATH_CONFIG['decomp_interno'], dadger_file)
    dadger_oficial: Dict[str, Any] = read_dadger(path_dc_oficial)
    dadger_raizen: Dict[str, Any] = read_dadger(path_dc_raizen)

    # Setup output decks
    logger.info("Setting up output decks")
    for folder in [deck_decomp + '__ONS-TO-CCEE', deck_decomp + '__RAIZEN', deck_decomp + '__ONS-TO-CCEE_VAZOES-RAIZEN']:
        folder_path: str = os.path.join(PATH_CONFIG['output_decks'], folder)
        os.makedirs(folder_path, exist_ok=True)
        if folder == deck_decomp + '__RAIZEN':
            shutil.copytree(PATH_CONFIG['decomp_interno'], os.path.join(folder_path, deck_decomp))
            logger.info(f"Copied decomp_interno to {folder_path}")
        elif folder == deck_decomp + '__ONS-TO-CCEE':
            shutil.copytree(PATH_CONFIG['decomp_ons'], os.path.join(folder_path, deck_decomp))
            logger.info(f"Copied decomp_ons to {folder_path}")
        elif folder == deck_decomp + '__ONS-TO-CCEE_VAZOES-RAIZEN':
            shutil.copytree(PATH_CONFIG['decomp_ons'], os.path.join(folder_path, deck_decomp))
            shutil.copy(
                os.path.join(PATH_CONFIG['decomp_interno'], f'vazoes.rv{rv}'),
                os.path.join(folder_path, deck_decomp)
            )
            logger.info(f"Copied vazoes.rv{rv} to {folder_path}")
        logger.info(f"Setup output folder: {folder_path}")

    # Process checklist blocks
    logger.info("Processing checklist blocks")
    for block in CHECKLIST_BLOCKS:
        logger.info(f"Processing block: {block}")
        deck_path: str = create_deck(PATH_CONFIG['decomp_ons'], PATH_CONFIG['output_decks'], block, deck_decomp)
        alter_dadger(
            deepcopy(dadger_oficial),
            block,
            dadger_raizen['dadger'][block],
            os.path.join(deck_path, dadger_file)
        )

    # Execute Prospec for each deck
    logger.info("Executing Prospec for decks")
    id_prospec_list: List[Any] = []
    for deck in os.listdir(PATH_CONFIG['output_decks']):
        deck_path: str = os.path.join(PATH_CONFIG['output_decks'], deck)
        logger.info(f"Zipping deck: {deck}")
        zip_decomp_files(deck_path, os.path.join(PATH_CONFIG['output_decks'], deck), deck_decomp)
        id_prospec_list.append(execute_prospec(parametros, PATH_CONFIG['output_decks'], deck))
        try:
            if deck.split('__')[1] == 'ONS-TO-CCEE':
                id_oficial = [id_prospec_list[-1]]
                logger.info(f"Sending WhatsApp message for deck {deck}")
                send_whatsapp_message(consts.WHATSAPP_GILSEU, 'Deck Decomp ONS to CCEE', os.path.join(PATH_CONFIG['output_decks'], deck + '.zip'))
        except:
            logger.warning(f"Failed to send WhatsApp message for deck {deck}")

    # Wait and send email
    logger.info("Preparing to send email")
    parametros['apenas_email']  = True
    parametros['aguardar_fim']  = True
    parametros['prevs_name']    = None
    parametros['assunto_email'] = None
    parametros['media_rvs']     = False
    parametros['considerar_rv'] = '_s1'
    parametros['id_estudo']     = id_oficial
    parametros['list_email']    = [consts.EMAIL_MIDDLE, consts.EMAIL_FRONT]
    parametros['list_whats']    = [consts.WHATSAPP_PMO]
    parametros['path_result']   = create_directory(consts.PATH_RESULTS_PROSPEC, '')
    logger.info("Sleeping for 600 seconds before sending email")
    time.sleep(600)
    logger.info("Sending email for Decomp ONS to CCEE")
    main_roda_estudos.send_email(parametros)
    
    parametros['prevs_name']    = None
    parametros['assunto_email'] = None
    parametros['id_estudo']     = id_prospec_list
    logger.info("Sending email for all Prospec studies")
    main_roda_estudos.send_email(parametros)

if __name__ == '__main__':
    logger.info("Script execution started")
    main()
    logger.info("Script execution completed")