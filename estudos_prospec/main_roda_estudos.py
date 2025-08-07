import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import time
from copy import deepcopy
from dateutil.relativedelta import relativedelta 
from processa_resultados import gerar_resultados
from config_default import PARAMETROS, EMAIL_CONFIG
from functions import *
import pandas as pd
from middle.utils.constants import Constants 

consts = Constants()

sys.path.append(os.path.join(consts.PATH_PROJETOS, "estudos-middle/api_prospec"))
sys.path.append(os.path.join(consts.PATH_PROJETOS, "estudos-middle/api_pluvia"))
sys.path.append(os.path.join(consts.PATH_PROJETOS, "estudos-middle/api_ampere"))

# Importando .py do Pluvia e do Prospec
import run_prospec
import run_pluvia
from functionsProspecAPI import authenticateProspec, getStudiesByTag
from ampere.ampere import get_last_pconj
parametros = deepcopy(PARAMETROS)
PATH_PREVS_AMPERE   = os.path.join(consts.PATH_ARQUIVOS,'ampere')

def rodar(parametros):
    
    print (parametros)
    s_date_global = datetime.now() 
    start_date_global = s_date_global.strftime('%d/%m/%Y %H:%M')
    print ("#-Programa Master PLD Semanal Iniciado----------------------#")
    print ('#-Rotina iniciada em: ' + start_date_global + ' mm----------#')
    print ("#-----------------------------------------------------------#")
    print (" ")
    print (" ")

    parametros['path_result']  = create_directory(consts.PATH_RESULTS_PROSPEC, '')
 
    if parametros['apenas_email'] == False:

        parametros["mapas"]          = EMAIL_CONFIG[parametros["prevs"]]['rodada'][parametros["rodada"]]
        parametros["tag"]            = parametros["prevs"]
        parametros["aguardar_fim"]   = EMAIL_CONFIG[parametros["prevs"]]["aguardar_fim"]
        parametros['path_out_prevs'] = create_directory(consts.PATH_PREVS_PROSPEC, EMAIL_CONFIG[parametros["prevs"]]["path_prevs"])
        
        parametros = BLOCK_FUNCTIONS[parametros['prevs']](parametros)
        
        if parametros['nome_estudo'] != None:
            parametros['sensibilidade'] = (parametros['sensibilidade']  + parametros['nome_estudo']).upper()

        print(parametros)

        # Rodando o prospec
        # --------------------------------------------------------------------------------------------# 
        print("Iniciando a execução do prospec!")
        parametros['rvs'] = min(parametros['rvs'], 8) 
        parametros['prospec_out'] = run_prospec.main(parametros)  
        if not parametros['aguardar_fim']:
            return  parametros['prospec_out']
        # --------------------------------------------------------------------------------------------#
        time.sleep(600)
    send_email(parametros)
    return ['sucesso']


def send_email(parametros):
    print ("#-Iniciando processo de envio de e-mail------------------------------------#")  
    
    parametros['apenas_email'] = True  
    
    pathName = []
    nomesEstudos = []
    idEstudos = []
    #print(parametros['tag'])
    if parametros['tag'] is not None and parametros['id_estudo'] is None:
        parametros['id_estudo'] = get_id_email(parametros)   
    
    if parametros['id_estudo'] is not None: 
        try:
            idEstudos = eval(parametros['id_estudo'])
        except:
            idEstudos = parametros['id_estudo']
            
        id_estudos = []
        n_rvs = []
        for id in idEstudos: 
            try:
                parametros['id_estudo'] = int(id)  
                parametros['prospec_out'] = run_prospec.main(parametros)
                pathName.append(Path(str(parametros['path_result']) +'/'+ parametros['prospec_out'][0]).as_posix())
                nomesEstudos.append(parametros['prospec_out'][2])
                n_rvs.append(parametros['prospec_out'][3])
                id_estudos.append(id)
            except:
                print("Não foi possivel baixar o compilado do estudo id: ", id, ", será enviado e-mail sem este estudo!")
        idEstudos = id_estudos
        parametros['path_name'] = pathName
        parametros['n_rvs'] = str(max(n_rvs))

        if parametros['prevs_name'] == None:
            parametros['prevs_name'] = [nome.split('__')[len(nome.split('__'))-1].split('-hr-')[0] for nome in nomesEstudos]

        if parametros['assunto_email'] == None and parametros['tag'] in EMAIL_CONFIG.keys():
            parametros['assunto_email'] = EMAIL_CONFIG[parametros['tag']]['description']
            parametros['corpo_email']   = EMAIL_CONFIG[parametros['tag']]['description']
            parametros['list_email']    = EMAIL_CONFIG[parametros['tag']]['emails']
            parametros['list_whats']    = EMAIL_CONFIG[parametros['tag']]['whats']
        else:
            parametros['assunto_email'] = 'Estudos: '+ str(idEstudos)
            parametros['corpo_email'] = 'Estudos: '
            
        for i in range(len(idEstudos)):
            parametros['corpo_email']    += 'Id ' + str(idEstudos[i]) + ' com titulo   ->   ' + str(nomesEstudos[i]+ '<br> ')        
        
        parametros['assunto_email'] = parametros['assunto_email'] + ' ' +parametros['n_rvs']+'_Rvs'
        parametros['corpo_email'] = parametros['corpo_email'] +  "<br/>"
            
        print("#Enviando os resultados por email-------------------------------------------#")
        gerar_resultados(parametros)
    else:
        print('Não foi possivel enviar o e-mail, pois não foi informado o id do estudo!')
        print('Favor informar o id do estudo no parametro "id_estudo"')
        print('Exemplo: \'["xxxx","yyyy","zzzz"]\'')
        

def run_prevs_ampere(parametros):
    parametros['tag'] = 'P.CONJ'  
    path_zip = create_directory(consts.PATH_ARQUIVOS,'ampere')
    parametros['sensibilidade'], parametros['rvs'] = get_last_pconj(parametros['data'],path_zip, parametros['path_out_prevs'])          
    print('n prevs',parametros['rvs'])
    return parametros

 
def run_prevs_pluvia(parametros):
    parametros['sensibilidade'], parametros['rvs']  = run_pluvia.main(parametros)
    print('n prevs',parametros['rvs'])
    return parametros


def run_1rv_pluvia(parametros):
    parametros['sensibilidade'], parametros['rvs']  = run_pluvia.main(parametros)
    parametros['rvs'] = 1
    print('n prevs',parametros['rvs'])
    return parametros


def run_nao_consistido(parametros):
    parametros['rvs'] = 1
    return parametros


def run_prevs_interno(parametros ):
    print('Copiando prevs interno para o a pasta do prospec') 
    parametros['aguardar_fim'] = False 
    idEstudos = []
  
    for file in os.listdir(parametros['path_prevs_encad']):
        parametros['path_prevs']    = file 
        try:      
            prevName = copy_all_internal_prevs(parametros, True )
            #print(prevName)
            if len(prevName) > 0:            
                prevName = prevName[0].split('.')[0][6:len(prevName[0].split('.')[0])-7]                
                parametros['sensibilidade'] = prevName
                parametros['nomeEstudo'] = 'DC_Encad__' + prevName + '_Dia'
                idEstudos.append(run_prospec.main(parametros))
        except:
            print('Erro ao executar o estudo: ', prevName)

    parametros['id_estudo']     = idEstudos
    parametros['apenas_email']  = True    
    parametros['subir_banco']   = True

    time.sleep(1200)
    send_email(parametros)


def run_ec_ext(parametros):
    
    list_mapas = deepcopy(parametros['mapas'])
    for maps in list_mapas:
        parametros['mapas'] = [maps]
        parametros['sensibilidade'], parametros['rvs']  = run_pluvia.main(parametros)
        run_prospec.main(parametros)

    #time.sleep(1200)
    send_email(parametros) 


def run_grupos(parametros):
    
    list_mapas = deepcopy(parametros['mapas'])
    for maps in list_mapas:
        parametros['mapas'] = [maps]
        parametros['sensibilidade'], parametros['rvs']  = run_pluvia.main(parametros)
        run_prospec.main(parametros)
    time.sleep(1200)
    send_email(parametros)       


def getPesosGrupos(grupo, parametros):

    dtRef = (parametros['data'] - relativedelta(days=1))
    dtRef = datetime(dtRef.year,dtRef.month,dtRef.day)    
    #dict_pesos = wx_dbLib.get_pesos_agrupados_ec(dtRef)
    dict_pesos = {}
    return round(dict_pesos['grupo_'+str(int(grupo[-2:]))]*100)


def create_directory(base_path: str, sub_path: str) -> Path:
        full_path = Path(base_path) / sub_path
        full_path.mkdir(parents=True, exist_ok=True)
        return full_path.as_posix()


def get_id_email(parametros):
    authenticateProspec(consts.API_PROSPEC_USERNAME, consts.API_PROSPEC_PASSWORD)
    n_estudos=30
    if parametros['tag'] in EMAIL_CONFIG.keys():
        n_estudos = EMAIL_CONFIG[parametros['tag']]['n_estudos']
    
    estudos = getStudiesByTag({'page':1, 'pageSize':n_estudos+3, 'tags':parametros['tag']})
    list_id = []   
    for estudo in estudos['ProspectiveStudies']:
        if estudo['Status'] == 'Concluído' and len(list_id) < n_estudos:
            list_id.append(str(estudo['Id']))
    if len(list_id) == 0:
        print( 'Não foi encontrado nenhum estudo com a tag: ', parametros['tag'])
    return list_id


def run_with_params():
    parametros = deepcopy(PARAMETROS)    
    if len(sys.argv) > 3:
	
        for i in range(1, len(sys.argv)):
            argumento = sys.argv[i].lower()

            if   argumento ==        "prevs": parametros[argumento] = sys.argv[i+1].upper()            
            elif argumento ==          "rvs": parametros[argumento] = int(sys.argv[i+1])            
            elif argumento ==       "rodada": parametros[argumento] = sys.argv[i+1]          
            elif argumento ==   "path_prevs": parametros[argumento] = sys.argv[i+1]            
            elif argumento == "apenas_email": parametros[argumento] = bool(int(sys.argv[i+1]))            
            elif argumento =="assunto_email": parametros[argumento] = sys.argv[i+1] 
            elif argumento ==  "nome_estudo": parametros[argumento] = str("_"+sys.argv[i+1])            
            elif argumento ==    "id_estudo": parametros[argumento] = sys.argv[i+1]
            elif argumento ==   "list_email": parametros[argumento] = sys.argv[i+1]
            elif argumento =="considerar_rv": parametros[argumento] = sys.argv[i+1]
            elif argumento == "gerar_matriz": parametros[argumento] = int(sys.argv[i+1])
            elif argumento ==      "cenario": parametros[argumento] = int(sys.argv[i+1])
            elif argumento ==  "subir_banco": parametros[argumento] = bool(int(sys.argv[i+1]))    
            elif argumento == "aguardar_fim": parametros[argumento] = bool(int(sys.argv[i+1]))  
            elif argumento ==    "media_rvs": parametros[argumento] = int(sys.argv[i+1])
            elif argumento ==        "mapas": parametros[argumento] = [sys.argv[i+1]]
            elif argumento ==  "nome_estudo": parametros[argumento] = sys.argv[i+1]
            elif argumento =="sensibilidade": parametros[argumento] = sys.argv[i+1]
            elif argumento =="executar_estudo": parametros[argumento] = bool(int(sys.argv[i+1]))
            elif argumento =="tag": parametros[argumento] = sys.argv[i+1]

            elif argumento == "data":
                try:
                    parametros[argumento] = datetime.strptime(sys.argv[i+1], '%d/%m/%Y')
                except:
                    print("Data no formato errado {}, utiliza o formato 'dd/mm/yyyy'".format())
                    quit()
        print(" ")
        return rodar(parametros)
        
    else:
        print('    ')
        print('    ')
        print("    Não foram encontrados os argumentos necessarios!")  


BLOCK_FUNCTIONS = {
    'NEXT-RV': run_1rv_pluvia,
    'P.CONJ': run_prevs_pluvia,
    'CENARIOS': run_prevs_pluvia,
    'UPDATE': run_prevs_pluvia,
    'P.ZERO': run_prevs_pluvia,
    'P.APR': run_prevs_pluvia,
    'NAO-CONSISTIDO': run_nao_consistido,
    'ONS-GRUPOS': run_grupos,
    'EC-EXT': run_ec_ext,
    'SENS': run_1rv_pluvia,
    'RZ': run_prevs_interno,
    'AMPERE': run_prevs_ampere
} 

if __name__ == '__main__':
    """PARAMETROS =  {
        "rodada": 'Definitiva',
        "data": datetime.now() -timedelta(days=1),
        "apenas_email": False,
        "assunto_email": None,
        "corpo_email": None,
        "considerar_rv": 'sem',
        "gerar_matriz": False,
        "path_name": None,
        "back_teste": False,
        "aguardar_fim": True,
        "executar_estudo": True,
        "media_rvs": False,
        "n_membros": 0,
        "percentis_ec": [],
        "nome_estudo": None,
        "sensibilidade": None,
        "tag": 'P.APR',
        "id_estudo": None,
        "prevs":'P.CONJ',
        "cenario":10,
        "prevs_name": None,
        "n_tentativas": 10
    }
 
    #parametros['apenas_email'] =  True
    #parametros['tag'] = '2025-Q4_03/08'
    #parametros['aguardar_fim'] = False
    rodar(PARAMETROS)
    #rodar(PARAMETROS)"""   
    run_with_params()
