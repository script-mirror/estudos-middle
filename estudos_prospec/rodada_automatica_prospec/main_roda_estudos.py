import os
import sys
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
import time
import pdb
import random
from dateutil.relativedelta import relativedelta
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.abspath(os.path.expanduser("~")),'.env'))

API_PROSPEC_USERNAME:  str = os.getenv('API_PROSPEC_USERNAME')
API_PROSPEC_PASSWORD:  str = os.getenv('API_PROSPEC_PASSWORD')
PATH_ARQUIVOS:        str = os.getenv('PATH_ARQUIVOS', '/projetos/arquivos')
PATH_PROJETOS:        str = os.getenv('PATH_PROJETOS', '/projetos')
PATH_PREVS_PROSPEC:   str = os.getenv('PATH_PREVS_PROSPEC')
PATH_RESULTS_PROSPEC: str = os.getenv('PATH_RESULTS_PROSPEC')
PATH_PREVS_INTERNO:   str = os.getenv('PATH_PREVS_INTERNO')
USER_EMAIL_MIDDLE:    str = os.getenv('USER_EMAIL_MIDDLE')
USER_EMAIL_FRONT:     str = os.getenv('USER_EMAIL_FRONT')
USER_EMAIL_GILSEU:    str = os.getenv('USER_EMAIL_GILSEU')
USER_EMAIL_CELSO:     str = os.getenv('USER_EMAIL_CELSO')
RUN_GERAR_PRODUTO:    str = os.getenv('RUN_GERAR_PRODUTO')
RUN_GERAR_PRODUTO = ". /WX/WX2TB/Documentos/fontes/PMO/scripts_unificados/env/bin/activate; cd /WX2TB/Documentos/fontes/PMO/scripts_unificados/apps/gerarProdutos; python gerarProdutos.py"

sys.path.append(os.path.join(PATH_PROJETOS, "estudos-middle/api_prospec"))
sys.path.append(os.path.join(PATH_PROJETOS, "estudos-middle/api_pluvia"))


# Importando .py do Pluvia e do Prospec
import run_prospec
import run_pluvia
from functionsProspecAPI import authenticateProspec, getStudiesByTag

from functions import *

EMAIL_CONFIG = {
    'NEXT-RV': {
        'description': 'Rodadas proxima RV',
        'emails': f'["{USER_EMAIL_MIDDLE}", "{USER_EMAIL_FRONT}"]',
        'n_estudos': 1
    },
    'P.CONJ': {
        'description': 'Rodadas P. Conjunto',
        'emails': f'["{USER_EMAIL_MIDDLE}", "{USER_EMAIL_FRONT}"]',
        'n_estudos': 5
    },
    'CENARIOS': {
        'description': 'Rodadas Cenarios Raizen',
        'emails': f'["{USER_EMAIL_MIDDLE}", "{USER_EMAIL_FRONT}"]',
        'n_estudos': 10
    },
    'P.ZERO': {
        'description': 'Rodadas Chuva Zero',
        'emails': f'["{USER_EMAIL_MIDDLE}", "{USER_EMAIL_FRONT}"]',
        'n_estudos': 1
    },
    'P.APR': {
        'description': 'Rodadas P. Conjunto Precipitação Agrupada',
        'emails': f'["{USER_EMAIL_GILSEU}"]',
        'n_estudos': 1
    },
    'NAO-CONSISTIDO': {
        'description': 'Rodadas Não Consistidas',
        'emails': f'["{USER_EMAIL_MIDDLE}", "{USER_EMAIL_FRONT}"]',
        'n_estudos': 1
    },
    'EC-EXT': {
        'description': 'Rodadas EC EXT',
        'emails': f'["{USER_EMAIL_MIDDLE}", "{USER_EMAIL_FRONT}"]',
        'n_estudos': 5
    },
    'ONS-GRUPOS': {
        'description': 'Rodadas ONS Agrupados',
        'emails': f'["{USER_EMAIL_MIDDLE}", "{USER_EMAIL_FRONT}"]',
        'n_estudos': 1
    }
}


def rodar(parametros):
    
    print (parametros)
    s_date_global = datetime.now() 
    start_date_global = s_date_global.strftime('%d/%m/%Y %H:%M')
    print ("#-Programa Master PLD Semanal Iniciado----------------------#")
    print ('#-Rotina iniciada em: ' + start_date_global + ' mm----------#')
    print ("#-----------------------------------------------------------#")
    print (" ")
    print (" ")

    # Criando os diretórios e armazenando os caminhos como Path no dicionário parametros
    # Configurações de caminhos
    parametros['path_prevs_prel']   = create_directory(PATH_PREVS_INTERNO, f"{parametros.get('data', datetime.now()).strftime('%Y%m%d')}/preliminar")
    parametros['path_prevs_def']    = create_directory(PATH_PREVS_INTERNO, f"{parametros.get('data', datetime.now()).strftime('%Y%m%d')}/teste")
    parametros['path_prevs_encad']  = create_directory(PATH_PREVS_INTERNO, f"{parametros.get('data', datetime.now()).strftime('%Y%m%d')}")
    parametros['path_output_encad'] = create_directory(PATH_PREVS_PROSPEC, 'raizen_encad')
    parametros['path_out']          = create_directory(PATH_PREVS_PROSPEC, 'all')
    parametros['path_output_tok']   = create_directory(PATH_PREVS_PROSPEC, 'TOK')
    parametros['path_result']       = create_directory(PATH_RESULTS_PROSPEC, '')


    #inicia o processo
    if parametros['apenas_email'] == False:

        ### Rodando o Pluvia
        # --------------------------------------------------------------------------------------------# 
        print(parametros['prevs'] )
        if parametros['prevs'] not in ['PREVS_RAIZEN', 'PREVS_PLUVIA_EC_EXT', 'PREVS_RAIZEN_ENCAD', 'PREVS_ONS_GRUPOS', 'PREVS_NAO_CONSISTIDO']:            
            parametros['sensibilidade'], parametros['rvs']  = run_pluvia.main(parametros)
            print('n prevs',parametros['rvs'])

        print(''); print(''); print ('--------------------------------------------------------------------------------#') 

        ### Rodando o Pluvia EC EXT
        # --------------------------------------------------------------------------------------------# 
        if parametros['prevs'] == 'PREVS_PLUVIA_EC_EXT':
            run_ec_ext(parametros)    

        print(''); print(''); print ('--------------------------------------------------------------------------------#') 
       
        ### Rodando o Pluvia EC EXT Agrupados
        # --------------------------------------------------------------------------------------------# 
        if parametros['prevs'] == 'PREVS_ONS_GRUPOS':
            run_grupos(parametros)

        print(''); print(''); print ('--------------------------------------------------------------------------------#')                   
         
        ### Copiando prevs Raizen para o prospec
        # --------------------------------------------------------------------------------------------#
        if parametros['prevs'] == 'PREVS_RAIZEN' or parametros['prevs'] == 'PREVS_PLUVIA_RAIZEN':

            if parametros['prevs'] == 'PREVS_PLUVIA_RAIZEN':
                copy_prevs_to_prospec(parametros, False)
            else:
                parametros['sensibilidade'] = copy_prevs_to_prospec(parametros, True)[0]                   

        ### Copiando prevs Raizen para o prospec ENCADEADO
        # --------------------------------------------------------------------------------------------#
        elif parametros['prevs'] == 'PREVS_RAIZEN_ENCAD':        
            run_prevs_interno(parametros)

        print(''); print(''); print('Copia finalizada')  
        print ('--------------------------------------------------------------------------------#')  
        
        if parametros['nome_estudo'] != '':
            parametros['sensibilidade'] = (parametros['sensibilidade']  + parametros['nome_estudo']).upper()

        print(''); print(''); print('Copia finalizada')  
        print(parametros)

        print ('--------------------------------------------------------------------------------#')  
        # Rodando o prospec
        # --------------------------------------------------------------------------------------------# 
        print("Iniciando a execução do prospec!")  
        parametros['prospec_out'] = run_prospec.main(parametros)  
        parametros['n_rvs'] = str(parametros['prospec_out'][2])  
        if not parametros['aguardar_fim']:
            return  parametros['prospec_out']
        # --------------------------------------------------------------------------------------------#

    send_email(parametros)
    return ['sucesso']

    # Função para criar diretórios e retornar o caminho como Path
def create_directory(base_path: str, sub_path: str) -> Path:
        full_path = Path(base_path) / sub_path
        full_path.mkdir(parents=True, exist_ok=True)
        return full_path.as_posix()

def get_id_email(parametros):
    authenticateProspec(API_PROSPEC_USERNAME, API_PROSPEC_PASSWORD)
    estudos = getStudiesByTag({'page':1, 'pageSize':10, 'tags':parametros['tag']})
    list_id = []   
    for estudo in estudos['ProspectiveStudies']:
        if estudo['Status'] == 'Concluído' and len(list_id) <= EMAIL_CONFIG[parametros['tag']]['n_estudos']:
            list_id.append(str(estudo['Id']))        
    return list_id


def send_email(parametros):
    print ("#-Iniciando processo de envio de e-mail------------------------------------#")  
    
    parametros['apenas_email'] = True  
    
    pathName = []
    nomesEstudos = []
    idEstudos = []
    
    if parametros['tag'] is not None:
        if EMAIL_CONFIG[parametros['tag']]['n_estudos'] == 1:
             parametros['id_estudo'] = [parametros['prospec_out'][0]]
        else:
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

        if parametros['prevs_name'] == '':
            parametros['prevs_name'] = [nome.split('__')[len(nome.split('__'))-1].split('-hr-')[0] for nome in nomesEstudos]

        if parametros['assunto_email'] == '':
            parametros['assunto_email'] = EMAIL_CONFIG[parametros['tag']]['description']
            parametros['corpo_email']   = EMAIL_CONFIG[parametros['tag']]['description']
            parametros['list_email']    = EMAIL_CONFIG[parametros['tag']]['emails']

        for i in range(len(idEstudos)):
            parametros['corpo_email']    += 'Id ' + str(idEstudos[i]) + ' com titulo   ->   ' + str(nomesEstudos[i]+ '<br> ')        
        
        parametros['assunto_email'] = parametros['assunto_email'] + ' ' +parametros['n_rvs']+'_Rvs'
        parametros['corpo_email'] = parametros['corpo_email'] +  "<br/>"
        #parametros['enviar_whats '] = 1
        
        print("#Enviando os resultados por email-------------------------------------------#")
        cmd = (RUN_GERAR_PRODUTO + f" produto RESULTADOS_PROSPEC enviar_whats {parametros['enviar_whats']} "
            f"gerarmatriz {parametros['gerar_matriz']} considerarrv {parametros['considerar_rv']} "
            f"fazer_media {parametros['media_rvs']} nomeRodadaOriginal \"{parametros['prevs_name']}\" "
            f"destinatarioEmail \'{parametros['list_email']}\' assuntoEmail \'{parametros['assunto_email']}\' "
            f"corpoEmail \"{parametros['corpo_email']}\" path \"{parametros['path_name']}\";")
        
        print(cmd)  
        os.system(cmd)
    else:
        print('Não foi possivel enviar o e-mail, pois não foi informado o id do estudo!')
        print('Favor informar o id do estudo no parametro "id_estudo"')
        print('Exemplo: \'["xxxx","yyyy","zzzz"]\'')
        
    
def run_prevs_interno(parametros ):
    print('Copiando prevs interno para o a pasta do prospec') 
    parametros['waitToFinish'] = False 
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
    
    parametros['waitToFinish'] = False 
    idEstudos = []
    print(parametros['n_Membros'])
    if parametros['n_Membros'] > 0:
        listMembers = random.sample(range(0, 100), parametros['n_Membros'])
        #listMembers = list(range(0, 100))
    else:
        listMembers = parametros['percentis_ec']
    listMembers.append('ENSEMBLE')
    print('Rodando os seguintes membros: ',listMembers)
    
    for membro in listMembers:
        try: 
            parametros['member']  =  str(membro).zfill(2)
            parametros['sensibilidade'] = 'EC_EXT-M:_'+str(membro)
            if membro =='ENSEMBLE':  parametros['sensibilidade'] = 'EC_EXT-ENS' 
            a, parametros['rvs']  = run_pluvia.main(parametros)
            idEstudos.append(run_prospec.main(parametros))
        except:
            pass

    parametros['id_estudo']     = idEstudos
    parametros['apenas_email']  = True    

    time.sleep(1200)
    send_email(parametros) 


def getPesosGrupos(grupo, parametros):

    dtRef = (parametros['data'] - relativedelta(days=1))
    dtRef = datetime(dtRef.year,dtRef.month,dtRef.day)    
    #dict_pesos = wx_dbLib.get_pesos_agrupados_ec(dtRef)
    dict_pesos = {}
    return round(dict_pesos['grupo_'+str(int(grupo[-2:]))]*100)

def run_grupos(parametros):
    
    parametros['waitToFinish'] = False 
    idEstudos = []
    print('grupos rodar',parametros['agrupados'])
    listMembers = parametros['agrupados']    
        
    for membro in listMembers:
       # getPesosGrupos(membro, parametros)
        try: 
            parametros['member']  =  str(membro)
            parametros['sensibilidade'] = str(membro).zfill(2)
            a, parametros['rvs']  = run_pluvia.main(parametros)
            idEstudos.append(run_prospec.main(parametros))
        except:
            pass

    parametros['id_estudo']     = idEstudos
    parametros['apenas_email']  = True    

    time.sleep(1200)
    send_email(parametros)       

  

def run_with_params():
    parametros = {}
    # DEFINIÇÃO DOS PARAMETROS PADRÃO
    parametros['enviar_whats']  = 1
    parametros["preliminar"]     = 1
    parametros["data"]           = datetime.now()
    #parametros["data"]           = datetime.strptime('01/06/2025', '%d/%m/%Y')
    parametros['path_prevs']     = ''
    parametros['apenas_email']   = False
    parametros['assunto_email']  = ''
    parametros['corpo_email']    = ''
    parametros['list_email']     = f'["{USER_EMAIL_MIDDLE}", "{USER_EMAIL_FRONT}"]'
    #parametros['list_email']     = f'["{USER_EMAIL_GILSEU}"]'
    parametros['prevs_name']     = ''
    parametros['considerar_rv']  = 'sem'
    parametros['gerar_matriz']   = 0
    parametros['path_name']      = ''
    parametros['subir_banco']    = False
    parametros['back_teste']     = False
    parametros['aguardar_fim']   = True
    parametros['executar_estudo']= True
    parametros['mapas']          = ['GEFS','ONS_Pluvia', 'ONS_ETAd_1_Pluvia','ECMWF_ENS','ECMWF_ENS','GEFS' ]
    #parametros['mapas']          = ['ONS_Pluvia']
    parametros['membros']        = ['ENSEMBLE','NULO','NULO','ENSEMBLE','00','00'] 
    parametros['cenario']        = 1 
    parametros['media_rvs']      = 0 
    parametros['n_Membros']      = 0
    #parametros['n_Membros']      = 50
    parametros['percentis_ec']   = []
    #parametros['percentis_ec']   = ['24','77','71','37','05','02','43','78','72','93']
    parametros['agrupados']      = ['Grupo01','Grupo02','Grupo03','Grupo04','Grupo05','Grupo06','Grupo07','Grupo08','Grupo09','Grupo10']
    parametros['nome_estudo']    = ''
    parametros['rvs']            = 1
    parametros['sensibilidade']  = 'NAO-INFORMADA'
    parametros ["tag"]     = None
    if len(sys.argv) > 3:
	
        for i in range(1, len(sys.argv)):
            argumento = sys.argv[i].lower()

            if   argumento ==        "prevs": parametros[argumento] = sys.argv[i+1].upper()            
            elif argumento ==          "rvs": parametros[argumento] = int(sys.argv[i+1])            
            elif argumento ==   "preliminar": parametros[argumento] = int(sys.argv[i+1])            
            elif argumento ==   "path_prevs": parametros[argumento] = sys.argv[i+1]            
            elif argumento == "apenas_email": parametros[argumento] = bool(int(sys.argv[i+1]))            
            elif argumento ==   "prevs_name": parametros[argumento] = sys.argv[i+1]            
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


if __name__ == '__main__':
    """ parametros = {}
    # DEFINIÇÃO DOS PARAMETROS PADRÃO
    parametros['enviar_whats']  = 1
    parametros["preliminar"]     = 1
    parametros["data"]           = datetime.now()
    #parametros["data"]           = datetime.strptime('01/06/2025', '%d/%m/%Y')
    parametros['path_prevs']     = ''
    parametros['apenas_email']   = False
    parametros['assunto_email']  = ''
    parametros['corpo_email']    = ''
    parametros['list_email']     = f'["{USER_EMAIL_MIDDLE}", "{USER_EMAIL_FRONT}"]'
    parametros['list_email']     = f'["{USER_EMAIL_GILSEU}"]'
    parametros['prevs_name']     = ''
    parametros['considerar_rv']  = 'sem'
    parametros['gerar_matriz']   = 0
    parametros['path_name']      = ''
    parametros['subir_banco']    = False
    parametros['back_teste']     = False
    parametros['aguardar_fim']   = True
    parametros['executar_estudo']= True
    parametros['mapas']          = ['GEFS','ONS_Pluvia', 'ONS_ETAd_1_Pluvia','ECMWF_ENS','ECMWF_ENS','GEFS' ]
    parametros['mapas']          = ['ONS']
    parametros['membros']        = ['ENSEMBLE','NULO','NULO','ENSEMBLE','00','00'] 
    parametros['cenario']        = 1 
    parametros['media_rvs']      = 0 
    parametros['n_Membros']      = 0
    parametros['prevs']          = 'PREVS_PLUVIA'
    parametros['percentis_ec']   = []
    #parametros['percentis_ec']   = ['24','77','71','37','05','02','43','78','72','93']
    parametros['agrupados']      = ['Grupo01','Grupo02','Grupo03','Grupo04','Grupo05','Grupo06','Grupo07','Grupo08','Grupo09','Grupo10']
    parametros['nome_estudo']    = ''
    parametros['rvs']            = 1
    parametros['sensibilidade']  = 'NAO-INFORMADA'
    parametros ["id_estudo"]     = "['26562','26569']"
    parametros ["tag"]     = 'P.CONJ"""
    
    #rodar(parametros)
    run_with_params()
