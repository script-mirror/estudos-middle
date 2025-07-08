
# -*- coding: utf-8 -*-
import sys
import os
import shutil
import zipfile
import codecs
import logging
import time
from datetime import datetime, date
from string import ascii_lowercase
from copy import deepcopy
import pandas as pd
from ComparaCT import *
from ComparaDP import *
from ComparaUH import *
sys.path.append('/WX2TB/Documentos/fontes/PMO/API_Prospec/Script/') 
import mainProspecAPI_RodadaAutoDiaria

# Constants
CHECKLIST_BLOCKS = ['UH', 'CT', 'PQ', 'DP', 'MP', 'RE', 'HV', 'HQ', 'VE']
BASE_PATH = '/WX/WX2TB/Documentos/fontes/PMO/backTest_DC/'
PATH_CONFIG = {
    'output_decks': os.path.join(BASE_PATH, 'output/decks'),
    'output_dp': os.path.join(BASE_PATH, f'output/saidaDP_{date.today().strftime("%Y_%m_%d")}.csv'),
    'output_ct': os.path.join(BASE_PATH, f'output/saidaCT_{date.today().strftime("%Y_%m_%d")}.csv'),
    'oficial_decomp': os.path.join(BASE_PATH, 'input/oficial/decomp'),
    'raizen_decomp': os.path.join(BASE_PATH, 'input/raizen/decomp'),
    'raizen_prospec_decomp': os.path.join(BASE_PATH, 'input/raizenProspec/decomp')
}
FILES_TO_COPY = ['caso.dat', 'hidr.dat', 'mlt.dat', 'perdas.dat', 'polinjus.csv', 'indices.csv']
DADGNL_VAZOES = ['dadgnl.rv{}', 'vazoes.rv{}']
LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'

# Configure logging
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger(__name__)

def setup_directories(paths):
    """Create or clear directories as needed."""
    for path in paths:
        try:
            if os.path.exists(path):
                shutil.rmtree(path)
            os.makedirs(path)
            logger.info(f"Directory created: {path}")
        except Exception as e:
            logger.warning(f"Failed to setup directory {path}: {e}")

def convert_deck_ons_to_ccee():
    """Execute script to convert ONS deck to CCEE format."""
    cmd = (
        ". /WX2TB/Documentos/fontes/PMO/scripts_unificados/env_activate;"
        "cd /WX/WX2TB/Documentos/fontes/PMO/converte_dc/script;"
        "python wx_dc_comentadopld.py;"
    )
    try:
        os.system(cmd)
        logger.info("ONS to CCEE conversion completed")
    except Exception as e:
        logger.error(f"ONS to CCEE conversion failed: {e}")
        raise

def find_dadger_file(directory):
    """Find the dadger file in the specified directory."""
    for file in os.listdir(directory):
        if file.lower().startswith('dadger'):
            return file
    raise FileNotFoundError(f"No dadger file found in {directory}")

def extract_zip_folder(zip_path, folder):
    """Extract a zip folder to the specified path."""
    unzip_path = os.path.join(zip_path, folder[:-4])
    if not os.path.exists(unzip_path):
        os.makedirs(unzip_path)
    with zipfile.ZipFile(os.path.join(zip_path, folder), 'r') as zip_ref:
        zip_ref.extractall(unzip_path)
    logger.info(f"Extracted zip: {folder} to {unzip_path}")
    return unzip_path

def copy_files(file_list, src, dst):
    """Copy specified files from source to destination."""
    for file in file_list:
        src_path = os.path.join(src, file)
        dst_path = os.path.join(dst, file)
        if os.path.exists(src_path):
            shutil.copyfile(src_path, dst_path)
            logger.info(f"Copied {file} from {src} to {dst}")
        else:
            logger.warning(f"File {file} not found in {src}")

def convert_file_encoding(src_path, dst_path, src_encoding='ISO-8859-1', dst_encoding='utf-8'):
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

def create_deck(path_oficial, path_output, block):
    """Create a new deck directory for the specified block."""
    deck_path = os.path.join(path_output, f'DC-OFICIAL_{block}-RAIZEN')
    dc_path = os.path.join(deck_path, 'DC')
    os.makedirs(deck_path)
    shutil.copytree(path_oficial, dc_path)
    logger.info(f"Created deck for block {block} at {deck_path}")
    return dc_path

def read_dadger(pathDadger):
    """Read a dadger file and organize its blocks."""
    dictDadger = {}
    blocoAtual = "TE"
    blocoAnterior = "TE"
    dictDadger['TE'] = []
    listOrdemBlocos = []
    listOrdemBlocos.append('TE')
    dictdadger = dict()

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

def Escreve_Dadger(arquivo, dadger):
    """Write a dadger file from its dictionary representation."""
    with open(arquivo, "w") as fh:
        for bloco in dadger['blocos']:
            for linha in dadger['dadger'][bloco]:
                fh.write(linha)
    time.sleep(1)

def alter_dadger(base_dadger, block, external_block_data, output_path, altered_blocks):
    """Alter the dadger file for the specified block."""
    base_dadger['dadger']['TE'] = [
        f"TE  DECOMP OFICIAL - UTILIZANDO O BLOCO RAIZEN: {altered_blocks}\n"
        if line.startswith('TE') else line
        for line in base_dadger['dadger']['TE']
    ]
    base_dadger['dadger'][block] = external_block_data
    Escreve_Dadger(output_path, base_dadger)
    logger.info(f"Altered dadger for block {block} at {output_path}")
    return base_dadger

def zip_decomp_files(deck_path, zip_name):
    """Zip only the files in the DC folder, without including subdirectories."""
    dc_path = os.path.join(deck_path, 'DC')
    zip_path = f"{zip_name}.zip"
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in os.listdir(dc_path):
                file_path = os.path.join(dc_path, file)
                if os.path.isfile(file_path):  # Only include files, not directories
                    zipf.write(file_path, arcname=file)  # Use only the file name in the zip
        logger.info(f"Created zip {zip_path} with files from {dc_path}")
    except Exception as e:
        logger.error(f"Failed to create zip {zip_path}: {e}")
        raise

def execute_prospec(params, deck_path, deck_name):
    """Execute Prospec for the given deck."""
    params['deck'] = f"{deck_name}.zip"
    params['path_deck'] = deck_path + '/'
    try:
        prospec_out = mainProspecAPI_RodadaAutoDiaria.main(params)
        logger.info(f"Prospec executed for deck {deck_name}: {prospec_out}")
        return prospec_out
    except Exception as e:
        logger.error(f"Prospec execution failed for {deck_name}: {e}")
        raise

def send_email_notification(id_list, email_list, subject):
    """Send email notification with Prospec results."""
    cmd = (
        ". /WX2TB/Documentos/fontes/PMO/scripts_unificados/env_activate;"
        "cd /WX/WX2TB/Documentos/fontes/PMO/rodada_automatica_prospec/script;"
        f"python mainRodadaAutoProspec.py apenas_email 1 id_estudo '{id_list}' "
        f"list_email '{email_list}' assunto_email '{subject}';"
    )
    try:
        os.system(cmd)
        logger.info("Email notification sent")
    except Exception as e:
        logger.error(f"Failed to send email notification: {e}")
        raise

def rodar(parametros):
    """Main function to process and compare decks."""
    # Setup directories
    setup_directories([
        PATH_CONFIG['output_decks'],
        PATH_CONFIG['raizen_decomp']
    ])

    # Convert ONS deck to CCEE
    convert_deck_ons_to_ccee()

    # Find dadger file
    dadger_file = find_dadger_file(PATH_CONFIG['oficial_decomp'])
    rv = dadger_file[-1:]
    logger.info(f"Found dadger file: {dadger_file} with rv: {rv}")

    # Extract Raizen Prospec zip
    for folder in os.listdir(PATH_CONFIG['raizen_prospec_decomp']):
        if '.zip' in folder:
            path_in = extract_zip_folder(PATH_CONFIG['raizen_prospec_decomp'], folder)
            break
    else:
        raise FileNotFoundError("No zip file found in Raizen Prospec decomp directory")

    # Copy necessary files
    copy_files(FILES_TO_COPY + [f'rv{rv}'], PATH_CONFIG['oficial_decomp'], PATH_CONFIG['raizen_decomp'])
    convert_file_encoding(
        os.path.join(path_in, dadger_file),
        os.path.join(PATH_CONFIG['raizen_decomp'], dadger_file)
    )
    copy_files(
        [f.format(rv) for f in DADGNL_VAZOES],
        path_in,
        PATH_CONFIG['raizen_decomp']
    )

    # Clean up extracted folder
    try:
        shutil.rmtree(path_in)
        os.remove(f"{path_in}.zip")
        logger.info(f"Cleaned up extracted folder: {path_in}")
    except Exception as e:
        logger.warning(f"Failed to clean up {path_in}: {e}")

    # Read dadger files
    path_dc_oficial = os.path.join(PATH_CONFIG['oficial_decomp'], dadger_file)
    path_dc_raizen = os.path.join(PATH_CONFIG['raizen_decomp'], dadger_file)
    dadger_oficial = read_dadger(path_dc_oficial)
    dadger_base = read_dadger(path_dc_oficial)
    dadger_raizen = read_dadger(path_dc_raizen)

    # Compare UH
    dict_uh = {'Oficial': dadger_oficial['dadger']['UH'], 'Raizen': dadger_raizen['dadger']['UH']}
    dict_subm = {'Raizen': {'1': 0, '2': 0, '3': 0, '4': 0}, 'CCEE': {'1': 0, '2': 0, '3': 0, '4': 0}}

    # Analyze CT
    Analise_CT(path_dc_raizen, path_dc_oficial, dict_subm, PATH_CONFIG['output_ct'])

    # Setup output decks
    for folder in ['DC-OFICIAL', 'DC-RAIZEN', 'DC-OFICIAL_VAZOES-RAIZEN']:
        folder_path = os.path.join(PATH_CONFIG['output_decks'], folder)
        os.makedirs(folder_path, exist_ok=True)
        shutil.copytree(PATH_CONFIG['oficial_decomp'], os.path.join(folder_path, 'DC'))
        if folder == 'DC-OFICIAL_VAZOES-RAIZEN':
            shutil.copy(
                os.path.join(PATH_CONFIG['raizen_decomp'], f'vazoes.rv{rv}'),
                os.path.join(folder_path, 'DC')
            )
        logger.info(f"Setup output folder: {folder_path}")

    # Process checklist blocks
    for block in CHECKLIST_BLOCKS:
        deck_path = create_deck(
            PATH_CONFIG['oficial_decomp'],
            PATH_CONFIG['output_decks'],
            block
        )
        alter_dadger(
            deepcopy(dadger_base),
            block,
            dadger_raizen['dadger'][block],
            os.path.join(deck_path, dadger_file),
            block
        )

    # Execute Prospec for each deck
    id_prospec_list = []
    for deck in os.listdir(PATH_CONFIG['output_decks']):
        deck_path = os.path.join(PATH_CONFIG['output_decks'], deck)
        zip_decomp_files(deck_path, os.path.join(PATH_CONFIG['output_decks'], deck))
        id_prospec_list.append(execute_prospec(parametros, PATH_CONFIG['output_decks'], deck))

    # Wait and send email
    logger.info("Waiting 10 minutes before sending email")
    time.sleep(600)
    send_email_notification(
        id_prospec_list,
        '["gilseu.muhlen@raizen.com"]',
        "Back Test Decomp"
    )

def run_with_params():
    """Parse command-line arguments and run the main process."""
    params = {
        'preliminar': 1,
        'data': datetime.now(),
        'path_prevs': '',
        'apenas_email': False,
        'assunto_email': '',
        'list_email': '["gilseu.muhlen@raizen.com"]',
        'prevs_name': '',
        'considerar_rv': 'sem',
        'gerar_matriz': 0,
        'path_name': '',
        'subir_banco': False,
        'back_teste': True,
        'rvs': 1,
        'executar_deck': True,
        'waitToFinish': False
    }

    for i in range(1, len(sys.argv), 2):
        arg = sys.argv[i].lower()
        if i + 1 >= len(sys.argv):
            break
        value = sys.argv[i + 1]
        try:
            if arg in ['prevs', 'path_prevs', 'prevs_name', 'assunto_email', 'id_estudo', 'list_email', 'considerar_rv']:
                params[arg] = value
            elif arg in ['rvs', 'preliminar', 'gerar_matriz']:
                params[arg] = int(value)
            elif arg in ['apenas_email', 'back_teste']:
                params[arg] = bool(int(value))
            elif arg == 'data':
                params[arg] = datetime.strptime(value, '%d/%m/%Y')
        except ValueError as e:
            logger.error(f"Invalid value for argument {arg}: {value}. Error: {e}")
            sys.exit(1)

    rodar(params)

if __name__ == '__main__':
    run_with_params()