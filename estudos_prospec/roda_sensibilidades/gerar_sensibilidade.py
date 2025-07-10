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
sys.path.append("/projetos/raizen-power-trading-estudos-middle/")
sys.path.append("/projetos/raizen-power-trading-estudos-middle/decomp/manipula_decomp")
sys.path.append("/projetos/raizen-power-trading-estudos-middle/api_prospec")
sys.path.append("/projetos/raizen-power-trading-estudos-middle/estudos_prospec/rodada_automatica_prospec")
from atualiza_decomp import process_decomp
from functionsProspecAPI import *
from main_roda_estudos import runWithParams


ABS_PATH = '/projetos/raizen-power-trading-estudos-middle/estudos_prospec/roda_sensibilidades'
ABS_PATH_LOG = os.path.join('/projetos/raizen-power-trading-estudos-middle/decomp/manipula_decomp/output/log', 'logging.log')
warnings.filterwarnings("ignore")  # Ignora todos os warnings
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


def criar_estudo(params):
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
    result = runWithParams()
    logger.info("Study created with id=%s", result)
    return result


def get_path_dadger(caminho_zip):
    logger.info("Extracting dadger files from zip=%s", caminho_zip)
    nome_zip = os.path.splitext(os.path.basename(caminho_zip))[0]
    diretorio_pai = os.path.dirname(caminho_zip)
    diretorio_extracao = os.path.join(diretorio_pai, nome_zip)

    if not os.path.exists(diretorio_extracao):
        os.makedirs(diretorio_extracao)
        logger.debug("Created extraction directory: %s", diretorio_extracao)

    with zipfile.ZipFile(caminho_zip, 'r') as zip_ref:
        zip_ref.extractall(diretorio_extracao)
        logger.debug("Extracted zip file to %s", diretorio_extracao)

    arquivos_dadger = []
    caminho_completo = []
    for root, dirs, files in os.walk(diretorio_extracao):
        for arquivo in files:
            if "dadger" in arquivo.lower():
                extensao = os.path.splitext(arquivo)[1]
                if not (extensao.startswith('.') and extensao[1:].isdigit() and len(extensao[1:]) == 3):
                    caminho_in = os.path.join(root, arquivo)
                    caminho_completo.append(caminho_in)
                    arquivos_dadger.append(arquivo)
                    logger.debug("Found dadger file: %s", caminho_in)
    
    logger.info("Found %s dadger files", len(arquivos_dadger))
    return caminho_completo, arquivos_dadger

#
def send_email_notification(id_list, email_list, subject):
    logger.info("Sending email notification for id_list=%s, subject=%s", id_list, subject)
    cmd = (
        ". /WX2TB/Documentos/fontes/PMO/scripts_unificados/env_activate;"
        "cd /projetos/raizen-power-trading-estudos-middle/estudos_prospec/rodada_automatica_prospec;"
        f"python mainRodadaAutoProspec.py apenas_email 1 id_estudo '{id_list}' "
        f"list_email '{email_list}' assunto_email '{subject}';"
    )
    try:
        os.system(cmd)
        logger.info("Email notification sent successfully")
    except Exception as e:
        logger.error("Failed to send email notification: %s", e)
        raise


def start_study(params):

    logger.info("Starting study execution with id=%s", params['id_estudo'])
    authenticateProspec('gilseu.muhlen@raizen.com', 'cJfCKni1')
    info = getInfoFromStudy(params['id_estudo'])
    logger.debug("Retrieved study info: %s", info)
    
    idNEWAVEJson = {2025: info['NewaveVersionId']}
    idDECOMPJson = {2025: info['DecompVersionId']}
    idDESSEMJson = {2025: info['DessemVersionId']}
    idServer = getIdOfServer('m6i.24xlarge')
    idQueue = getIdOfFirstQueueOfServer('m6i.24xlarge')
    logger.debug("Server ID=%s, Queue ID=%s", idServer, idQueue)

    prospecStudy = sendFileToDeck(params['id_estudo'], str(info['Decks'][0]['Id']), params['output_path'], params['arquivo'])
    logger.info("Sent file to deck: study_id=%s, deck_id=%s, file=%s", params['id_estudo'], info['Decks'][0]['Id'], params['output_path'])
    time.sleep(5)  # Wait for the file to be processed
    sendFileToDeck(params['id_estudo'], str(info['Decks'][0]['Id']), ABS_PATH_LOG, 'logging.log')

    runExecution(params['id_estudo'], idServer, idQueue, idNEWAVEJson, idDECOMPJson, idDESSEMJson, 'm6i.24xlarge', 0, 3, 3, 2)
    logger.info("Study execution started")
    print(" ")
    print(" ")


def clear_dir(path_dir):
    logger.info("Clearing directory: %s", path_dir)
    if os.path.exists(path_dir):
        shutil.rmtree(path_dir)
        logger.debug("Removed directory: %s", path_dir)
    os.makedirs(path_dir)
    logger.debug("Created directory: %s", path_dir)
    return path_dir


def gerar_estudo_prospec(params):

    logger.info("Generating Prospec study with params=%s", params)
    os.chdir(os.getcwd())
    input_dir = clear_dir(os.path.abspath(ABS_PATH + '/input/deck'))
    output_dir = clear_dir(os.path.abspath(ABS_PATH + '/output/decomp'))
    logger.debug("Input dir=%s, Output dir=%s", input_dir, output_dir)

    id_estudo = criar_estudo(params)
    logger.debug("Created study with id=%s", id_estudo)

    authenticateProspec('gilseu.muhlen@raizen.com', 'cJfCKni1')
    downloadDecksOfStudy(id_estudo, input_dir + '/', 'decomp.zip')
    logger.debug("Downloaded decomp.zip to %s", input_dir)

    caminhos, arquivos = get_path_dadger(input_dir + '/decomp.zip')
    logger.debug("Dadger files: %s", arquivos)
    
    params['arquivo'] = arquivos[0]
    params['dadger_path'] = caminhos[0]
    params['output_path'] = os.path.abspath(os.path.join(output_dir, arquivos[0]))
    params['id_estudo'] = id_estudo
    params['pq_load_level'] =   ABS_PATH +  '/input/patamar.dat'
    params['load_level_data'] = ABS_PATH +  '/input/patamar.dat'

    return params


def run_with_parms():
    logger.info("Date=%s", datetime.now())
    params = {}
    argumentos = sys.argv[1]
    print (argumentos)
    print(eval(argumentos))
    params['sensibilidades'] = eval(argumentos)
    logger.debug("Parsed parameters: %s", params['sensibilidades'])
    print(" ")
    print(" ")
    print(" ")
    print(params['sensibilidades'])
  
    # Set default values for parameters  
    params['mapa'] = 'ONS_Pluvia'
    # If 'mapa' is provided in sensitivities, use it
    if 'mapa'in params['sensibilidades']:
        params['mapa'] = params['sensibilidades']['mapa']
        del params['sensibilidades']['mapa']
    
    id_prospec_list = [] 
    # Loop through each sensitivity case 
    for sensitivity, sensitivity_df in params['sensibilidades'].items():
        logger.info("Starting sensitivity analysis with params=%s", params)
        params['case'] = sensitivity
        params = gerar_estudo_prospec(params)

        id_prospec_list.append(params['id_estudo'])

        process_decomp(copy.deepcopy( params), sensitivity_df)    
        start_study(params)

    logger.info("Waiting 10 minutes before sending email")
    time.sleep(600)
    send_email_notification( id_prospec_list,'["gilseu.muhlen@raizen.com"]', "Sensibilidades")


if __name__ == '__main__':
    logger.info("Script execution started")
    run_with_parms()