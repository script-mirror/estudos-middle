from functionsProspecAPI import readConfig
from createStudyProspecAPI import run_VE, downloadResultados, runBackTeste
from datetime import datetime
import atualizaearm
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.abspath(os.path.expanduser("~")),'.env'))

PATH_ARQUIVOS = os.getenv('PATH_ARQUIVOS', '/projetos/arquivos')
PATH_PROJETOS = os.getenv('PATH_PROJETOS', '/projetos')
def main(parametros):
    config = readConfig(os.path.join(PATH_PROJETOS, "estudos-middle/api_prospec/config_api/config.csv")) 
    data = datetime.today()

    print(''); print('')
    print ('--------------------------------------------------------------------------------#')
    print('#-API do Prospec Iniciado: ' + str(datetime.now())[:19])

    config.downloadDadger = False
    
    if parametros['apenas_email']:
        print('Iniciando download dos resultados do estudo com id:',int(parametros['id_estudo']))
        return downloadResultados(config, parametros)
    
    elif parametros['back_teste'] == False:

        config.serverName = 'm6i.24xlarge'
        config.studyName  = (config.studyName + '__' + parametros['sensibilidade']).upper()  +'_Dia'
        config.startStudy = parametros['executar_estudo']
        config.waitToFinish = parametros['aguardar_fim'] 
        
        if parametros['rvs'] == 1:
            config.prospecStudyIdToAssociateCuts = config.prospecStudyIdToAssociateCuts1Rv
            config.prospecStudyIdToDuplicate     = config.prospecStudyIdToDuplicate1Rv

        elif parametros['rvs'] == 2:
            config.prospecStudyIdToAssociateCuts = config.prospecStudyIdToAssociateCuts2Rv
            config.prospecStudyIdToDuplicate     = config.prospecStudyIdToDuplicate2Rv
                
        elif parametros['rvs'] == 3:
            config.prospecStudyIdToAssociateCuts = config.prospecStudyIdToAssociateCuts3Rv
            config.prospecStudyIdToDuplicate     = config.prospecStudyIdToDuplicate3Rv

        elif parametros['rvs'] == 4:
            config.prospecStudyIdToAssociateCuts = config.prospecStudyIdToAssociateCuts4Rv
            config.prospecStudyIdToDuplicate     = config.prospecStudyIdToDuplicate4Rv

        elif parametros['rvs'] == 5:
            config.prospecStudyIdToAssociateCuts = config.prospecStudyIdToAssociateCuts5Rv
            config.prospecStudyIdToDuplicate     = config.prospecStudyIdToDuplicate5Rv
        
        elif parametros['rvs'] == 6:
            config.prospecStudyIdToAssociateCuts = config.prospecStudyIdToAssociateCuts6Rv
            config.prospecStudyIdToDuplicate     = config.prospecStudyIdToDuplicate6Rv

        
        elif parametros['rvs'] == 7:
            config.prospecStudyIdToAssociateCuts = config.prospecStudyIdToAssociateCuts7Rv
            config.prospecStudyIdToDuplicate     = config.prospecStudyIdToDuplicate7Rv


        elif parametros['rvs'] == 8:
            config.prospecStudyIdToAssociateCuts = config.prospecStudyIdToAssociateCuts8Rv
            config.prospecStudyIdToDuplicate     = config.prospecStudyIdToDuplicate8Rv

        if parametros['prevs'] == 'PREVS_RAIZEN_ENCAD':
            config.prospecStudyIdToAssociateCuts = config.prospecStudyIdToAssociateCuts7Rv
            config.prospecStudyIdToDuplicate     = config.prospecStudyIdToDuplicate7Rv
            config.pathToAllPrevs      = '/WX2TB/Documentos/fontes/PMO/API_Prospec/GerarDecks/PREVS/EncadRaizen'
            config.pathToPrevs         = '/WX2TB/Documentos/fontes/PMO/API_Prospec/GerarDecks/PREVS/EncadRaizen'
            config.studyName           = parametros['nomeEstudo']
            config.waitToFinish        = parametros['waitToFinish']

        if parametros['prevs'] == 'PREVS_ONS_GRUPOS':
            config.studyName           =  'NW-DC_Agrupados__ONS-' + parametros['nomeEstudo'] 
            config.serverName          = 'm5.24xlarge'
            config.waitToFinish        = parametros['waitToFinish']
        
        if parametros['prevs'] == 'PREVS_PLUVIA_2_RV':
            config.downloadDadger = True  

        if parametros['prevs'] == 'PREVS_PLUVIA_EC_EXT':
            config.waitToFinish        = parametros['waitToFinish']

        if parametros['prevs'] == 'PREVS_PLUVIA_RAIZEN':
            config.prospecStudyIdToAssociateCuts = config.prospecStudyIdToAssociateCuts1Rv
            config.prospecStudyIdToDuplicate     = config.prospecStudyIdToDuplicate1Rv

        config.pathToDownloadCompilado  = '/projetos/estudos-middle/backtest_decomp/input/raizen_prospec/' 

        # Gera o arquivo de EA inicial
        status =  True
        if config.sendVolume: 
            status = atualizaearm.main() 
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
        config.prospecStudyIdToAssociateCuts = config.prospecStudyIdToAssociateCuts1Rv
        config.studyName                     = parametros['deck'][:-4]
        config.pathToFile                    = parametros['path_deck']
        config.nameFileDecomp                = parametros['deck']
        config.waitToFinish                  = parametros['waitToFinish']
        return runBackTeste(config)

if __name__ == '__main__':    
    main()