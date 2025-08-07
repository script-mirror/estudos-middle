from functionsProspecAPI import  *
from createStudyProspecAPI import *
from datetime import datetime
from atualiza_ear import gera_ear
from datetime import datetime
from middle.utils.constants import Constants 
consts = Constants()
     
def main(parametros):
    config = Config()

    print(''); print('')
    print ('--------------------------------------------------------------------------------#')
    print('#-API do Prospec Iniciado: ' + str(datetime.now())[:19])

    config.downloadDadger = False
    config.maxRestarts    = 2      
    #config.sendVolume = False
    
    if parametros['apenas_email']:
        print('Iniciando download dos resultados do estudo com id:',int(parametros['id_estudo']))
        return downloadResultados(parametros)
    
    elif parametros['back_teste'] == False:

        authenticateProspec(consts.API_PROSPEC_USERNAME, consts.API_PROSPEC_PASSWORD)
        config.prospecStudyIdToDuplicate        =  str(getStudiesByTag({'page':1, 'pageSize':1, 'tags':f"BASE-{parametros['rvs']}-RV"})['ProspectiveStudies'][0]['Id'])
        config.prospecStudyIdToAssociateCuts    = [str(getStudiesByTag({'page':1, 'pageSize':1, 'tags':'FCF'})['ProspectiveStudies'][0]['Id'])]
        config.prospecStudyIdToAssociateVolumes = get_id_volumes()      
        config.studyName                        = (get_study_name(config.prospecStudyIdToDuplicate ) + '__' + parametros['sensibilidade']).upper() 
        config.startStudy                       = parametros['executar_estudo']
        config.waitToFinish                     = parametros['aguardar_fim']
        config.tag                              = parametros['tag']
        config.pathToAllPrevs                   =  parametros['path_out_prevs'] 
        config.pathToDownloadCompilado          = '/projetos/estudos-middle/backtest_decomp/input/raizen_prospec/' 

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
        authenticateProspec(consts.API_PROSPEC_USERNAME, consts.API_PROSPEC_PASSWORD)
        config.prospecStudyIdToAssociateCuts    = [str(getStudiesByTag({'page':1, 'pageSize':1, 'tags':'FCF'})['ProspectiveStudies'][0]['Id'])]
        config.studyName                     = parametros['deck'][:-4]
        config.pathToFile                    = parametros['path_deck']
        config.nameFileDecomp                = parametros['deck']
        config.waitToFinish                  = parametros['aguardar_fim']
        config.tag                           = parametros['tag']
        return runBackTeste(config)

def get_id_volumes():
    
    estudos = getStudiesByTag({'page':1, 'pageSize':30, 'tags':'EAR'})
        
    for estudo in estudos['ProspectiveStudies']:
        if estudo['Status'] == 'Concluído'and len(estudo['Decks']) > 2:
            num_decks=0
            for deck in estudo['Decks']:
                if deck['SensibilityInfo'] == 'Original' and deck['Model'] == 'DECOMP':
                    num_decks+=1
                if num_decks > 2:
                    return str(estudo['Id'])

def get_study_name(id):
    prospecStudy = getInfoFromStudy(id)
        
    for deck in prospecStudy['Decks']:
        if deck['Model']== 'DECOMP':
            return 'DC' + str(deck['Year'])+str(deck['Month']).zfill(2)+'-RV'+str(deck['Revision'])
def get_id_estudos_base():
    list_id = []
    authenticateProspec(consts.API_PROSPEC_USERNAME, consts.API_PROSPEC_PASSWORD)
    for i in range(1, 9):
        list_id.append(getStudiesByTag({'page':1, 'pageSize':1, 'tags':f"BASE-{i}-RV"})['ProspectiveStudies'][0]['Id'])
    return list_id       
        
if __name__ == '__main__':    
    main()