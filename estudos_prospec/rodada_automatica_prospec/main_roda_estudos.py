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


sys.path.append(os.path.join(PATH_PROJETOS, "estudos-middle/api_prospec"))
sys.path.append(os.path.join(PATH_PROJETOS, "estudos-middle/api_pluvia"))

#from PMO.scripts_unificados.bibliotecas import  wx_dbLib

# Importando .py do Pluvia e do Prospec
import run_prospec
import run_pluvia
from functions import *

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
    parametros['path_config_email'] = create_directory(PATH_PROJETOS, 'estudos-middle/estudos_prospec/rodada_automatica_prospec/input/Config')
    parametros['path_prevs_prel']   = create_directory(PATH_PREVS_INTERNO, f"{parametros.get('data', datetime.now()).strftime('%Y%m%d')}/preliminar")
    parametros['path_prevs_def']    = create_directory(PATH_PREVS_INTERNO, f"{parametros.get('data', datetime.now()).strftime('%Y%m%d')}/teste")
    parametros['path_prevs_encad']  = create_directory(PATH_PREVS_INTERNO, f"{parametros.get('data', datetime.now()).strftime('%Y%m%d')}")
    parametros['path_output_encad'] = create_directory(PATH_PREVS_PROSPEC, 'raizen_encad')
    parametros['path_out']          = create_directory(PATH_PREVS_PROSPEC, 'all')
    parametros['path_output_tok']   = create_directory(PATH_PREVS_PROSPEC, 'TOK')
    parametros['path_result']       = create_directory(PATH_RESULTS_PROSPEC, '')


    # Argumentos necessarios para rodar
    # prevs: xx rvs: x data: 'dd/mm/yyyy'
 
    # prevs
    # --------------------------------------------------------------------------------------------# 
    # PREVS_PLUVIA_EC_EXT -> roda o ec estendido do pluvia 5rvs
    # PREVS_PLUVIA_2_RV   -> roda o P Conjunto do Pluvia
    # PREVS_PLUVIA        -> roda os prevs do pluvia definidos no "mainPluvia_RodadaDiariaProspec"
    # PREVS_RAIZEN        -> roda os prevs da raizen que estiverem na pasta input 
    # PREVS_PLUVIA_RAIZEN -> roda os prevs da raizen e do pluvia
    # PREVS_RAIZEN_ENCAD  -> roda os prevs da raizen que estiverem na pasta input/PrevsRaizenEncad
    # PREVS_TOK           -> roda os prevs da TOK que estiverem na pasta input/TOK/'Data'

    # rvs
    # --------------------------------------------------------------------------------------------# 
    # numero inteiro, roda o estudo de X rv que esta definido no config da api do prospec
    # 1 -> estudo 1 rv
    # 2 -> estudo 2 rv
    # 4 -> estudo 4 rv
    # 5 -> estudo 5 rv

    # preliminar
    # --------------------------------------------------------------------------------------------# 
    # numero inteiro, define se utiliza prevs preliminar ou definitivo 
    # 0 -> definitivo
    # 1 -> preliminar

    #exemplo
    # --------------------------------------------------------------------------------------------# 
    # python mainRodadaAutoProspec.py prevs PREVS_PLUVIA_2_RV rvs 2 data 05/10/2021


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


        #Enviando e-mail
        # --------------------------------------------------------------------------------------------#     
       
        if parametros['prevs'] == 'PREVS_RAIZEN' or parametros['prevs'] == 'PREVS_PLUVIA_RAIZEN' or parametros['prevs'] == 'PREVS_PLUVIA' and parametros['rvs'] != 1:
            parametros['assunto_email']     = 'Rodada Proxima RV'
            parametros['path_config_email'] = parametros['path_config_email'] +'configEmail_1rv.csv'
            parametros['corpo_email']       = "Rodadas proxima revisão"
            parametros['path_name'], parametros['prevs_name'] = get_rodadas_email(parametros,(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')) 

        elif parametros['prevs'] == 'PREVS_PLUVIA_2_RV':            
            parametros['path_config_email'] = parametros['path_config_email'] +'configEmail_Pconj.csv'
            parametros['assunto_email']     = 'Rodada P. Conjunto'
            parametros['corpo_email']       = "Ultimas rodadas utilizando o Prevs P. Conjunto"
            parametros['subir_banco']       = False
            parametros['path_name'], parametros['prevs_name'] = get_rodadas_email(parametros, (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'))
        
        elif parametros['prevs'] == 'PREVS_PLUVIA_APR':                     
            parametros['path_name']     = [parametros['prospec_out'][0]]
            parametros['prevs_name']    = [parametros['sensibilidade']]          
            parametros['assunto_email'] = 'Rodada P. Conjunto Precipitação Agrupada'
            parametros['corpo_email']   = "Rodada utilizando o prevs com a precipitação agrupada"
            parametros['subir_banco']   = False
            parametros['list_email']     = f'["{USER_EMAIL_GILSEU}", "{USER_EMAIL_GILSEU}"]' 
        
        elif parametros['prevs']  == 'PREVS_NAO_CONSISTIDO':  
            parametros['path_name']     = [parametros['prospec_out'][0]]
            parametros['prevs_name']    = [parametros['sensibilidade']]          
            parametros['assunto_email'] = 'Rodada Não Consistido'
            parametros['corpo_email']   = ""
        
        elif parametros['prevs']  == 'PREVS_PLUVIA_USUARIO':
            parametros['path_config_email'] = parametros['path_config_email'] +'configEmail_CenRaizen.csv'                   
            parametros['assunto_email']     = 'Rodada Cenarios Raizen'
            parametros['corpo_email']       = "Ultimas rodadas utilizando os cenarios criados no Pluvia"
            parametros['subir_banco']       = False

            parametros['path_name'], parametros['prevs_name'] = get_rodadas_email(parametros, (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'))
        
        elif parametros['prevs']  == 'PREVS_PLUVIA_PREC_ZERO':
            parametros['path_name']     = [parametros['prospec_out'][0]]
            parametros['prevs_name']    = ['Chuva Zero']          
            parametros['assunto_email'] = 'Rodada Chuva Zero'
            parametros['corpo_email']   = "Rodada Chuva Zero"
            parametros['subir_banco']   = False
            
        if parametros['prevs']  != 'PREVS_ONS_GRUPOS' and parametros['prevs']  != 'PREVS_PLUVIA_EC_EXT':
            print('Envinado e-mail de estudos não PREVS_ONS_GRUPOS')
            send_email(parametros)
            e_date_global = datetime.now() 

            print(''); print(''); print('')
            print ('#-Tempo de Execução: ' + str(e_date_global - s_date_global)[0:7] + ' mm----#')
    
    else:
        # Envio do e-mail
        send_email(parametros)
    return ['sucesso']

    # Função para criar diretórios e retornar o caminho como Path
def create_directory(base_path: str, sub_path: str) -> Path:
        full_path = Path(base_path) / sub_path
        full_path.mkdir(parents=True, exist_ok=True)
        return full_path
    
def send_email(parametros):
    print ("#-Iniciando processo de envio de e-mail------------------------------------#")  
      
    pathName = []
    nomesEstudos = []
    idEstudos = []
    if parametros['path_name'] == '':
        try:
            idEstudos = eval(parametros['id_estudo'])
        except:
            idEstudos = parametros['id_estudo']
        #idEstudos = [*range(15103, 15149, 1)]
        print(parametros['id_estudo'])
        print(idEstudos)
        id_estudos = []
        n_rvs = []
        for id in idEstudos: 
            try:
                parametros['id_estudo'] = int(id)  
                parametros['prospec_out'] = run_prospec.main(parametros)
                pathName.append(str(parametros['path_result']) +'/'+ parametros['prospec_out'][0])
                nomesEstudos.append(parametros['prospec_out'][2])
                n_rvs.append(parametros['prospec_out'][3])
                id_estudos.append(id)
            except:
                print("Não foi possivel baixar o compilado do estudo id: ", id, ", será enviado e-mail sem este estudo!")
        idEstudos = id_estudos
        parametros['path_name'] = pathName
        parametros['n_rvs'] = str(max(n_rvs))
    else:
        for nome in parametros['path_name']:
            pathName.append(str(parametros['path_result']) +'/'+  +  nome)
    parametros['path_name'] = pathName
    if parametros['prevs_name'] == '':
        parametros['prevs_name'] = [nome.split('__')[len(nome.split('__'))-1].split('_Dia')[0] for nome in nomesEstudos]
        #parametros['prevs_name'] = [nome.split('_4Tri_')[len(nome.split('_4Tri_'))-1].split('_Dia')[0] for nome in nomesEstudos]

    #print(parametros['prevs_name'])

    if parametros['assunto_email'] == '':
        parametros['assunto_email'] =  'Resultados estudos id: ' + str(idEstudos) 
        parametros['corpo_email']    = 'Resultados estudos porspec: <br> '

    if parametros['corpo_email'] == '':
        parametros['corpo_email']    = 'Resultados estudos porspec: <br> '


    if parametros['gerar_matriz'] == 1:
        parametros['assunto_email'] =  'Matriz estudos id: ' + str(idEstudos) 

    for i in range(len(idEstudos)):
        parametros['corpo_email']    += 'Id ' + str(idEstudos[i]) + ' com titulo   ->   ' + str(nomesEstudos[i]+ '<br> ')        
    
    parametros['assunto_email'] = parametros['assunto_email'] + ' ' +parametros['n_rvs']+'_Rvs'
    parametros['corpo_email'] = parametros['corpo_email'] +  "<br/>"
    #parametros['enviar_whats '] = 1
    
    print("#Enviando os resultados por email-------------------------------------------#")
    cmd = (RUN_GERAR_PRODUTO + f" produto RESULTADOS_PROSPEC enviar_whats {parametros['enviar_whats']} "
        f"gerarmatriz {parametros['gerar_matriz']} considerarrv {parametros['considerar_rv']} "
        f"fazer_media {parametros['media_rvs']} nomeRodadaOriginal \"{parametros['prevs_name']}\" "
        f"destinatarioEmail \"{parametros['list_email']}\" assuntoEmail \"{parametros['assunto_email']}\" "
        f"corpoEmail \"{parametros['corpo_email']}\" path \"{parametros['path_name']}\";")
    
    print(cmd)  
    os.system(cmd)
    
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
            parametros['sensibilidade'] = 'EC_EXT-membro_'+str(membro)
            if membro =='ENSEMBLE':  parametros['sensibilidade'] = 'EC_EXT-ENSEMBLE' 
            a, parametros['rvs']  = run_pluvia.main(parametros)
            parametros['nomeEstudo'] = 'EC_ext__' + parametros['sensibilidade'] 
            idEstudos.append(run_prospec.main(parametros))
        except:
            pass

    parametros['id_estudo']     = idEstudos
    parametros['apenas_email']  = True    
    parametros['subir_banco']   = True
    parametros['assunto_email'] = 'Rodada EC_EXT Pluvia'
    parametros['corpo_email']   = "Ultimas rodadas utilizando o Prevs do EC EXT do Pluvia"
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
            parametros['sensibilidade'] = str(membro)
            a, parametros['rvs']  = run_pluvia.main(parametros)
            try:
                parametros['nomeEstudo'] = str(membro) +'_Peso('+ str(getPesosGrupos(membro, parametros))+'%)'
            except:
                print('Não foi possivel encontrar os pesos no banco de dados')
                parametros['nomeEstudo'] = str(membro) + ''
            idEstudos.append(run_prospec.main(parametros))
        except:
            pass

    parametros['id_estudo']     = idEstudos
    parametros['apenas_email']  = True    
    parametros['subir_banco']   = True
    parametros['assunto_email'] = 'Rodada Agrupados ONS'
    parametros['corpo_email']   = "Ultimas rodadas utilizando o Prevs do EC EXT Agrupado"
    time.sleep(1200)
    send_email(parametros)       

def get_rodadas_email(parametros, dataInicial):
    configEmail               = pd.read_csv(parametros['path_config_email'], sep = ";")
    df                        = pd.DataFrame({'dataRodada':[parametros['data'].strftime('%Y/%m/%d')],'prevName':[parametros['sensibilidade'] +'_' +parametros['data'].strftime('%d/%m')], 'pathName':[parametros['prospec_out'][0]]})
    configEmail               = configEmail.append(df, ignore_index=True)
    configEmail['dataRodada'] = pd.to_datetime(configEmail['dataRodada'])
    configEmail['dataRodada'] = configEmail['dataRodada'].dt.strftime('%Y-%m-%d')
    configEmail               = configEmail.loc[configEmail['dataRodada'] > dataInicial]
    configEmail               = configEmail.drop_duplicates(subset="pathName")
    configEmail.to_csv(parametros['path_config_email'], mode='w', index=False, header=True, sep = ";")
    prevName = []
    pathName = []
    for index in configEmail.index:
        prevName.append(configEmail.loc[index]['prevName']) 
        pathName.append( configEmail.loc[index]['pathName']) 
    prevName.reverse()
    pathName.reverse()

    return  pathName, prevName
    
def help():
    print('')
    print('    Os seguintes parametros podem ser enviados:')
    #print('')
    print ("    --------------------------------------------------------------------------------------------------------------")
    print('    Parametros para realizar a rodada e enviar o e-mail')
    print('')

    print('    prevs:')
    print('    PREVS_PLUVIA_EC_EXT -> roda os prevs do ec estendido do pluvia 5rvs')
    print('    PREVS_PLUVIA_2_RV   -> roda os prevs do P Conjunto do Pluvia')
    print('    PREVS_PLUVIA        -> roda os prevs do pluvia definidos no "run_pluvia"')
    print('    PREVS_RAIZEN        -> roda os prevs da raizen que estiverem na pasta input') 
    print('    PREVS_PLUVIA_RAIZEN -> roda os prevs da raizen e do pluvia')
    print('    PREVS_RAIZEN_ENCAD  -> roda os prevs da raizen que estiverem na pasta input/PrevsRaizenEncad')
    print('    PREVS_TOK           -> roda os prevs da TOK que estiverem na pasta input/TOK/"Data"')
    print('')
    print('    rvs:')
    print('    1 -> estudo 1 rv')
    print('    2 -> estudo 2 rv')
    print('    4 -> estudo 4 rv')
    print('    5 -> estudo 5 rv')
    print('')
    print('    data:')
    print('    Data dos prevs que deseja rodar, utiliza o formato dd/mm/yyyy. Exemplo:', datetime.now().strftime('%d/%m/%Y'))
    print('    Definido como padrão a data de hoje!')
    print('')
    print('    preliminar:')
    print('    0 -> roda apenas prevs DEFINITIVO')
    print('    1 -> roda os prevs definitivos disponiveis e o restante preliminar')
    print('    Definido por padrão como 1')
    print('')
    print('    Exemplo: python .../mainRodadaAutoProspec.py prevs PREVS_PLUVIA_2_RV rvs 2')
    print('');print('')
    print ("    --------------------------------------------------------------------------------------------------------------")
    print('    Parametros para apenas enviar o e-mail')
    print('')
    print('    apenas_email:')
    print('    1 -> baixa os decks e envia o e-mail (se necessario aguarda o estudo finalizar)')
    print('')
    print('    id_estudo:')
    print('    id dos estudos do prospec o qual quer enviar o email, formato de lista')
    print('    Exemplo: \'["xxxx","yyyy","zzzz"]\'')
    print('')
    print('    list_email:')
    print('    lista de e-mail a ser enviado ()')
    print('    Exemplo: \'["email1@raizen.com","email2@raizen.com","email3@raizen.com"]\'')
    print('')
    print('    considerar_rv:')
    print('    caso queria filtrar apenas uma rv em especifico')
    print('    Exemplo todas as rv0 de um estudo: considerar_rv sem1_s1')
    print('')
    print('    Exemplo: python .../mainRodadaAutoProspec.py apenas_email 1  id_estudo \'["9080","9079"]\' list_email \'["middle@wxe.com.br"]\'')
    print('')
    sys.exit() 


def run_with_params():
    parametros = {}
    # DEFINIÇÃO DOS PARAMETROS PADRÃO
    parametros['enviar_whats']  = 1
    parametros["preliminar"]     = 1
    parametros["data"]           = datetime.now()
    #parametros["data"]           = datetime.strptime('01/06/2025', '%d/%m/%Y')
    parametros['path_prevs']     = ''
    parametros['apenas_email']   = True
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
        print("    Visualize o help e defina os parametros!")  
        help()
        

if __name__ == '__main__':
    """"parametros = {}
    # DEFINIÇÃO DOS PARAMETROS PADRÃO
    parametros['enviar_whats']  = 1
    parametros["preliminar"]     = 1
    parametros["data"]           = datetime.now()
    #parametros["data"]           = datetime.strptime('01/06/2025', '%d/%m/%Y')
    parametros['path_prevs']     = ''
    parametros['apenas_email']   = True
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
    parametros ["id_estudo"]     = "['26562','26569']"""""
 
    #rodar(parametros)
    run_with_params()
