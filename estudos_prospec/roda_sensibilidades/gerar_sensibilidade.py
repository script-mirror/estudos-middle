from typing import List, Dict, Any, Tuple
import os
import copy
import pandas as pd
from datetime import datetime, timedelta
import time
import warnings
import shutil
import sys
import zipfile
import logging  # Already present, kept for clarity
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.abspath(os.path.expanduser("~")),'.env'))

API_PROSPEC_USERNAME:   str = os.getenv('API_PROSPEC_USERNAME')
API_PROSPEC_PASSWORD:   str = os.getenv('API_PROSPEC_PASSWORD')
SERVER_DEFLATE_PROSPEC: str = os.getenv('SERVER_DEFLATE_PROSPEC')
SEND_MAIL:              str = os.getenv('RUN_STUDY_PROSPEC')
EMAIL_GILSEU:           str = os.getenv('USER_EMAIL_GILSEU')
PATH_ARQUIVOS:          str = os.getenv('PATH_ARQUIVOS')
PATH_PROJETOS:          str = os.getenv('PATH_PROJETOS')
ABS_PATH:               str = os.path.join(PATH_ARQUIVOS, "prospec/roda_sensibilidades")
ABS_PATH_LOG:           str = os.path.join(ABS_PATH, 'log_sens.log')

global logger
warnings.filterwarnings("ignore")  # Ignore all warnings
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(ABS_PATH_LOG, mode='w'),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)
logger = logging.getLogger(__name__)


from middle.decomp.atualiza_decomp import process_decomp 
from middle.decomp import DecompParams
from middle.decomp.patamar_processor import read_patamar_carga, read_patamar_pq

# Cria diretórios se não existirem
os.makedirs(ABS_PATH, exist_ok=True)

sys.path.append(os.path.join(PATH_PROJETOS, "estudos-middle/"))
sys.path.append(os.path.join(PATH_PROJETOS, "estudos-middle/api_prospec"))
sys.path.append(os.path.join(PATH_PROJETOS, "estudos-middle/estudos_prospec/rodada_automatica_prospec"))

from functionsProspecAPI import *
from main_roda_estudos import run_with_params


def clear_log_file(log_file_path):
    with open(log_file_path, 'w') as f:
        f.truncate(0)
        
def criar_estudo(params: Dict[str, Any]) -> Any:
    logger.info("Creating study with params=%s", params)
    sys.argv = [
        'mainRodadaAutoProspec.py',
        'prevs', 'PREVS_PLUVIA_RAIZEN',
        'rvs', '1',
        'mapas', str(params['mapa']),
        'aguardar_fim', '0',
        'executar_estudo', '0',
        'nome_estudo', str(params['case'])
    ]
    result = run_with_params()
    logger.info("Study created with id=%s", result)
    return result

 
def get_path_dadger(caminho_zip: str) -> Tuple[List[str], List[str]]:
    logger.info("Extracting dadger files from zip=%s", caminho_zip)
    nome_zip: str = os.path.splitext(os.path.basename(caminho_zip))[0]
    diretorio_pai: str = os.path.dirname(caminho_zip)
    diretorio_extracao: str = os.path.join(diretorio_pai, nome_zip)

    if not os.path.exists(diretorio_extracao):
        os.makedirs(diretorio_extracao)
        logger.debug("Created extraction directory: %s", diretorio_extracao)

    with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
        zip_ref.extractall(diretorio_extracao)
        logger.debug("Extracted zip file to %s", diretorio_extracao)

    arquivos_dadger: List[str] = []
    caminho_completo: List[str] = []
    for root, dirs, files in os.walk(diretorio_extracao):
        for arquivo in files:
            if "dadger" in arquivo.lower():
                extensao: str = os.path.splitext(arquivo)[1]
                if not (extensao.startswith('.') and extensao[1:].isdigit() and len(extensao[1:]) == 3):
                    caminho_in: str = os.path.join(root, arquivo)
                    caminho_completo.append(caminho_in)
                    arquivos_dadger.append(arquivo)
                    logger.debug("Found dadger file: %s", caminho_in)
    
    logger.info("Found %s dadger files", len(arquivos_dadger))
    return caminho_completo, arquivos_dadger

# Send email notification after study completion or back
def send_email_notification(id_list: List[Any], email_list: str, subject: str) -> None:
    logger.info("Sending email notification for id_list=%s, subject=%s", id_list, subject)
    cmd = (SEND_MAIL + f" apenas_email 1 id_estudo '{id_list}' list_email '{email_list}' assunto_email '{subject}'")

    try:
        os.system(cmd)
        logger.info("Email notification sent successfully")
    except Exception as e:
        logger.error("Failed to send email notification: %s", e)
        raise


def start_study(params: Dict[str, Any]) -> None:

    logger.info("Starting study execution with id=%s", params['id_estudo'])
    authenticateProspec(API_PROSPEC_USERNAME, API_PROSPEC_PASSWORD)
    info: Dict[str, Any] = getInfoFromStudy(params['id_estudo'])
    logger.debug("Retrieved study info: %s", info)
    
    idNEWAVEJson: Dict[int, Any] = {2025: info['NewaveVersionId']}
    idDECOMPJson: Dict[int, Any] = {2025: info['DecompVersionId']}
    idDESSEMJson: Dict[int, Any] = {2025: info['DessemVersionId']}
    idServer: Any = getIdOfServer(SERVER_DEFLATE_PROSPEC)
    idQueue: Any = getIdOfFirstQueueOfServer(SERVER_DEFLATE_PROSPEC)
    logger.debug("Server ID=%s, Queue ID=%s", idServer, idQueue)
    pat_dadger = os.path.join(params['output_path'], params['arquivo'])
    
    prospecStudy: Any = sendFileToDeck(params['id_estudo'], str(info['Decks'][0]['Id']), pat_dadger, params['arquivo'])
    logger.info("Sent file to deck: study_id=%s, deck_id=%s, file=%s", params['id_estudo'], info['Decks'][0]['Id'], pat_dadger)
    time.sleep(5)  # Wait for the file to be processed
    sendFileToDeck(params['id_estudo'], str(info['Decks'][0]['Id']), ABS_PATH_LOG, 'log_sens.log')

    runExecution(params['id_estudo'], idServer, idQueue, idNEWAVEJson, idDECOMPJson, idDESSEMJson, SERVER_DEFLATE_PROSPEC, 0, 3, 3, 2)
    logger.info("Study execution started")
    print(" ")
    print(" ")


def clear_dir(path_dir: str) -> str:
    logger.info("Clearing directory: %s", path_dir)
    if os.path.exists(path_dir):
        shutil.rmtree(path_dir)
        logger.debug("Removed directory: %s", path_dir)
    os.makedirs(path_dir)
    logger.debug("Created directory: %s", path_dir)
    return path_dir


def gerar_estudo_prospec(params: Dict[str, Any]) -> Dict[str, Any]:

    logger.info("Generating Prospec study with params=%s", params)
    os.chdir(os.getcwd())
    input_dir: str = clear_dir(os.path.abspath(ABS_PATH + '/input/deck'))
    output_dir: str = clear_dir(os.path.abspath(ABS_PATH + '/output/decomp'))
    logger.debug("Input dir=%s, Output dir=%s", input_dir, output_dir)

    id_estudo: Any = criar_estudo(params)
    logger.debug("Created study with id=%s", id_estudo)

    authenticateProspec(API_PROSPEC_USERNAME, API_PROSPEC_PASSWORD)
    downloadDecksOfStudy(id_estudo, input_dir + '/', 'decomp.zip')
    logger.debug("Downloaded decomp.zip to %s", input_dir)

    caminhos, arquivos = get_path_dadger(input_dir + '/decomp.zip')
    logger.debug("Dadger files: %s", arquivos)
    
    params['arquivo']         = arquivos[0]
    params['dadger_path']     = caminhos[0]
    params['output_path']     = os.path.abspath(output_dir)
    params['id_estudo']       = id_estudo
    params['pq_load_level']   =  read_patamar_pq( ABS_PATH +  '/input/patamar/patamar.dat')
    params['load_level_data'] =  read_patamar_carga( ABS_PATH +  '/input/patamar/patamar.dat')

    return params


def run_with_parms() -> None:
    
    params: Dict[str, Any] = {}
    #argumentos: str = sys.argv[1]
    argumentos = "{'BASE': {'dp': {'carga': {'1': {'1': 0}, 'absoluto': 0}}}, 'CARGA-SE(-100)': {'dp': {'carga': {'1': {'1': -100}, 'absoluto': 0}}}, 'mapa': 'ONS'}"
    params['sensibilidades']: Dict[str, Any] = eval(argumentos)
    print (argumentos)
    print(eval(argumentos))

      # Set default values for parameters  
    params['mapa']: str = 'ONS_Pluvia'
    
    # If 'mapa' is provided in sensitivities, use it
    if 'mapa'in params['sensibilidades']:
        params['mapa'] = params['sensibilidades']['mapa']
        del params['sensibilidades']['mapa']
        
    sensibilidades = params['sensibilidades']
    del params['sensibilidades']
    
    id_prospec_list: List[Any] = [] 
    # Loop through each sensitivity case 
    for sensitivity, sensitivity_df in sensibilidades.items():
        
        clear_log_file(ABS_PATH_LOG)
        
        params['logger']  = logger   
        logger.debug("Parsed parameters: %s", sensitivity_df)
        print(" ")
        print(" ")
        print(" ")
        print(sensibilidades)
        logger.info("Date=%s", datetime.now())        
        logger.info("Starting sensitivity analysis with params=%s", params)
        params['case']: str = sensitivity
        params = gerar_estudo_prospec(params)

        id_prospec_list.append(params['id_estudo'])

        process_decomp(copy.deepcopy( DecompParams(**params)), sensitivity_df)    
        start_study(params)

    logger.info("Waiting 10 minutes before sending email")
    time.sleep(600)
    send_email_notification( id_prospec_list, f'["{EMAIL_GILSEU}"]', "Sensibilidades")

   # "{'BASE': {'dp': {'carga': {'1': {'1': 0}, 'absoluto': 0}}}, 'CARGA-SE(-100)': {'dp': {'carga': {'1': {'1': -100}, 'absoluto': 0}}}, 'mapa': 'ONS'}"
if __name__ == '__main__':
    logger.info("Script execution started")
    run_with_parms()