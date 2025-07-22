from functionsProspecAPI import  *
from createStudyProspecAPI import *

from datetime import datetime
from atualiza_ear import gera_ear
import os
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.abspath(os.path.expanduser("~")),'.env'))

PATH_ARQUIVOS = os.getenv('PATH_ARQUIVOS', '/projetos/arquivos')
PATH_PROJETOS = os.getenv('PATH_PROJETOS', '/projetos')
API_PROSPEC_USERNAME:   str = os.getenv('API_PROSPEC_USERNAME')
API_PROSPEC_PASSWORD:   str = os.getenv('API_PROSPEC_PASSWORD')

     
def main(parametros):
    config = Config()

    print(''); print('')
    print ('--------------------------------------------------------------------------------#')
    print('#-API do Prospec Iniciado: ' + str(datetime.now())[:19])

    config.downloadDadger = False
    #config.sendVolume = False
    if parametros['apenas_email']:
        print('Iniciando download dos resultados do estudo com id:',int(parametros['id_estudo']))
        return downloadResultados(config, parametros)
    
    elif parametros['back_teste'] == False:

        authenticateProspec(API_PROSPEC_USERNAME, API_PROSPEC_PASSWORD)
        config.prospecStudyIdToDuplicate        =  str(getStudiesByTag({'page':1, 'pageSize':1, 'tags':f"BASE-{parametros['rvs']}-RV"})['ProspectiveStudies'][0]['Id'])
        config.prospecStudyIdToAssociateCuts    = [str(getStudiesByTag({'page':1, 'pageSize':1, 'tags':'FCF'})['ProspectiveStudies'][0]['Id'])]
        config.prospecStudyIdToAssociateVolumes =  get_id_volumes()
        
        config.studyName  = get_study_name(config.prospecStudyIdToDuplicate )
        config.studyName  = (config.studyName + '__' + parametros['sensibilidade']).upper() 
        config.startStudy = parametros['executar_estudo']
        config.waitToFinish = parametros['aguardar_fim']
        config.tag = parametros['tag']
        
        if parametros['prevs'] == 'PREVS_ONS_GRUPOS':
            config.studyName           =  'NW-DC_Agrupados__ONS-' + parametros['nomeEstudo'] 
            config.waitToFinish        = parametros['waitToFinish']
        
        if parametros['prevs'] == 'PREVS_PLUVIA_2_RV':
            config.downloadDadger = True  

        if parametros['prevs'] == 'PREVS_PLUVIA_EC_EXT':
            config.waitToFinish        = parametros['waitToFinish']

        if parametros['prevs'] == 'PREVS_PLUVIA_RAIZEN':
            config.prospecStudyIdToDuplicate  =  str(getStudiesByTag({'page':1, 'pageSize':1, 'tags':'BASE-1-RV'})['ProspectiveStudies'][0]['Id'])

        config.pathToDownloadCompilado  = '/projetos/estudos-middle/backtest_decomp/input/raizen_prospec/' 

        # Gera o arquivo de EA inicial
        status =  True
        if config.sendVolume: 
            status = gera_ear() 
        #   
        #print (vars(config))
        if status:
            print("EARM criado com sucesso!")
            ve_out = run_VE(config)

            print(''); print('')
            print ('#-API do Prospec Terminado em: '  + str(datetime.now())[:19])
            print ('--------------------------------------------------------------------------------#')
            return ve_out
        else:
            print("EARM nao criado!")
            return ['0', 'Failed']

    elif parametros['back_teste']:
        authenticateProspec(API_PROSPEC_USERNAME, API_PROSPEC_PASSWORD)
        config.prospecStudyIdToAssociateCuts    = [str(getStudiesByTag({'page':1, 'pageSize':1, 'tags':'FCF'})['ProspectiveStudies'][0]['Id'])]
        config.studyName                     = parametros['deck'][:-4]
        config.pathToFile                    = parametros['path_deck']
        config.nameFileDecomp                = parametros['deck']
        config.waitToFinish                  = parametros['waitToFinish']
        return runBackTeste(config)

def get_id_volumes():
    
    estudos = getStudiesByTag({'page':1, 'pageSize':30, 'tags':'EAR'})
        
    for estudo in estudos['ProspectiveStudies']:
        if estudo['Status'] == 'Concluído'and len(estudo['Decks']) > 2:
            return str(estudo['Id'])

def get_study_name(id):
    prospecStudy = getInfoFromStudy(id)
        
    for deck in prospecStudy['Decks']:
        if deck['Model']== 'DECOMP':
            return 'DC' + str(deck['Year'])+str(deck['Month']).zfill(2)+'-RV'+str(deck['Revision'])
def get_id_estudos_base():
    list_id = []
    authenticateProspec(API_PROSPEC_USERNAME, API_PROSPEC_PASSWORD)
    for i in range(1, 9):
        list_id.append(getStudiesByTag({'page':1, 'pageSize':1, 'tags':f"BASE-{i}-RV"})['ProspectiveStudies'][0]['Id'])
    return list_id       

        
if __name__ == '__main__':    
    main()