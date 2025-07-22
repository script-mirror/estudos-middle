import time
from datetime import datetime
import calendar
import sys
import os
from functionsProspecAPI import *
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.abspath(os.path.expanduser("~")),'.env'))

API_PROSPEC_USERNAME:   str = os.getenv('API_PROSPEC_USERNAME')
API_PROSPEC_PASSWORD:   str = os.getenv('API_PROSPEC_PASSWORD')
SERVER_DEFLATE_PROSPEC: str = os.getenv('SERVER_DEFLATE_PROSPEC')
PATH_PROJETOS:          str = os.getenv('PATH_PROJETOS')
PATH_PREVS_PROSPEC:     str = os.getenv('PATH_PREVS_PROSPEC')
PATH_RESULTS_PROSPEC:   str = os.getenv('PATH_RESULTS_PROSPEC')
PATH_PREVS_INTERNO:     str = os.getenv('PATH_PREVS_INTERNO')
PATH_ALL_PREVS = PATH_PREVS_PROSPEC + '/all/'
PATH_VOLUME = PATH_PROJETOS + '/estudos-middle/api_prospec/calculo_volume'

def run_VE(config):
 
    date  = datetime.today()
    time_sleep = 600
    # First step is to authenticate | Primeiro passo é autenticar
    print('Nome do usuário: ', API_PROSPEC_USERNAME) 

    #print('Senha do usuário: ', API_PROSPEC_PASSWORD)
    authenticateProspec(API_PROSPEC_USERNAME, API_PROSPEC_PASSWORD)

    # Get number of total requests | Buscar quantidade de requests já usados


    # Get Ids of interest | Buscar Ids de interesse

    idNEWAVE = {2024: getIdOfNEWAVE('30.0.4'), 2025: getIdOfNEWAVE('30.0.4')}
    idDECOMP = {2024: getIdOfDECOMP('32.0.1'), 2025: getIdOfDECOMP('32.0.1')}
    idDESSEM = {2024: getIdOfDESSEM(''), 2025: getIdOfDESSEM('')}
    idServer = getIdOfServer(SERVER_DEFLATE_PROSPEC)
    idQueue  = getIdOfFirstQueueOfServer(SERVER_DEFLATE_PROSPEC)

    if config.prospecStudyIdToDuplicate != '':

        # Duplicate Study | Duplicar um estudo
        tags = []  
        tags.append(['DUP-FROM: ' + config.prospecStudyIdToDuplicate, 'black', 'white'])
        tags.append(['FCF-FROM: ' + str(config.prospecStudyIdToAssociateCuts), 'black', 'white'])
        tags.append(['EAR-FROM: ' + str(config.prospecStudyIdToAssociateVolumes), 'black', 'white'])
        tags.append(['EAR', 'white', 'white'])
        tags.append([config.tag, 'black', 'white'])

        prospecStudyId = duplicateStudy(config.prospecStudyIdToDuplicate,
                                        config.studyName + '_'+ str(date.day)+ '/'+ str(date.month) + '-'+ str(date.hour) + ':'+ str(date.minute) + 'h',                                        
                                        'Rodada Automatica',  tags, 2,1,1)
        
    prospecStudy = getInfoFromStudy(prospecStudyId)
    listOfDecks  = prospecStudy['Decks']
    
    # Send prevs files to each deck | Enviar arquivo prevs para cada deck

    if config.sendAllPREVStoStudy:
        sendAllPrevsToStudy(prospecStudyId, PATH_ALL_PREVS)

    elif config.sendAllPREVStoDeck:
        sendAllPrevsToEachDeck(prospecStudyId, PATH_ALL_PREVS)

    elif config.sendPREVS:
        sendPrevsToStudy(prospecStudyId, PATH_ALL_PREVS)

    if config.sendVolume:
        previousStage       = []
        destinationVolumeId = []

        for deck in listOfDecks:
           if deck['Model'] == 'DECOMP':
                destinationVolumeId.append(deck['Id'])

        sendFileToDeck(prospecStudyId, destinationVolumeId[0], PATH_VOLUME + '/volume_uhe.csv', 'volume_uhe.csv')
    
    # Download decks | Download decks
    if config.dowloadDecks:
        downloadDecksOfStudy(prospecStudyId, PATH_RESULTS_PROSPEC + '/', 'CompleteStudy.zip')

    # Associate Cuts and Volumes/GNL | Reaproveitar Cortes e Volumes/GNL
    if config.associateDecks:
        destinationCortesId   = []
        previousStage         = []
        destinationVolumeId   = []
        destinationCortesIdDC = []

        for deck in listOfDecks:
            if deck['Model'] == 'NEWAVE':
                destinationCortesId.append(deck['Id'])

            elif deck['Model'] == 'DECOMP':
                destinationVolumeId.append(deck['Id'])
                destinationCortesIdDC.append(deck['Id'])
                previousStage.append(False)

                if 'Matriz' in config.studyName:
                    destinationCortesId.append(deck['Id'])
        
        if len(destinationCortesId) == 0 and config.prospecStudyIdToAssociateCuts != '':

            estudo_que_recebe_os_cortes = getInfoFromStudy(prospecStudyId)
            id_do_deck_que_quero_os_cortes = estudo_que_recebe_os_cortes['Decks'][0]['Id']

            cutAssociation_only_decomp(prospecStudyId, [id_do_deck_que_quero_os_cortes], config.prospecStudyIdToAssociateCuts)
            time_sleep = 200
            
        elif len(destinationCortesId) > 0 and config.prospecStudyIdToAssociateCuts != '':
            print('Foi associado os cortes dos seguintes estudos :',config.prospecStudyIdToAssociateCuts)
            cutAssociation(prospecStudyId, destinationCortesId, config.prospecStudyIdToAssociateCuts)

        if len(destinationVolumeId) > 0 and config.prospecStudyIdToAssociateVolumes != '':
            volumeAssociation(prospecStudyId, [destinationVolumeId[0]], previousStage, config.prospecStudyIdToAssociateVolumes)


    # Start Execution | Iniciar execução
    studyStatus = getStatusFromStudy(prospecStudyId)

    if config.startStudy:
        initialStatus = studyStatus
        if studyStatus != 'Executing':
            if SERVER_DEFLATE_PROSPEC == '':
                runExecution(prospecStudyId, idServer,
                         idQueue,idNEWAVE, idDECOMP, idDESSEM, '', 0, config.infeasibilityHandling,
                         config.infeasibilityHandlingSensibility, config.maxRestarts)
            else:
                runExecution(prospecStudyId, idServer,
                         idQueue,idNEWAVE, idDECOMP, idDESSEM, SERVER_DEFLATE_PROSPEC, 0, config.infeasibilityHandling,
                         config.infeasibilityHandlingSensibility, config.maxRestarts)

    # Wait Execution to Finish | Aguardar execução terminar
    if config.waitToFinish:
        time.sleep(90) 
        # Wait to change from the initial status | aguardar mudança de status
        countIterations = 0
        if studyStatus != 'Executing':
            if initialStatus != '':
                checkExecution = 0
                while countIterations < 50:
                    countIterations = countIterations + 1
                    time.sleep(60)    # sleep for 10s | aguardar por 10s
                    studyStatus = getStatusFromStudy(prospecStudyId)
                    print(studyStatus)
                    if (studyStatus != initialStatus):
                        checkExecution = 1
                        break

        # Wait to finish | Aguardar terminar
        tempoEspera = 10
        try: 
            tempoEspera = ((len([ x for x in prospecStudy['Decks'] if x['Model'] == 'NEWAVE'])-len(config.prospecStudyIdToAssociateCuts)) *130) + ((len([ y for y in prospecStudy['Decks'] if y['Model'] == 'DECOMP' and y['SensibilityInfo']=='Original'])) *10)
            if tempoEspera < 0: tempoEspera = 10
        except:
            tempoEspera = 10
        print('Aguardando ', tempoEspera, ' minutos para verificar o status do estudo')
        countIterations = 0
        while countIterations < 90:
            countIterations = countIterations + 1
            if countIterations == 1:
                time.sleep(tempoEspera*60)
            else:            
                time.sleep(time_sleep)    # sleep for 10m | aguardar por 10m
            studyStatus = getStatusFromStudy(prospecStudyId)
            print(studyStatus)
            if studyStatus == 'Finished':
                print('Estudo terminou.')
                break
            elif studyStatus == 'Aborted':
                print('Estudo foi abortado.')
                break
            elif studyStatus == 'Failed':
                print('Estudo parou com falha.')
                break
            elif studyStatus == 'Executing':
                print('Estudo executando...')

            elif studyStatus == 'Ready':
                print('Estudo na fila  fila de execução...')

            # Dowload Compilation | Download da compilação de resultados
        if config.downloadCompilation:
            print('Iniciando Download do compilado')
            downloadCompilationOfStudy(prospecStudyId, PATH_RESULTS_PROSPEC +'/',
                               'Estudo_'+ str(prospecStudyId) + '_compilation.zip')
            print('Compilado baixado com sucesso')
        
        if config.downloadDadger:
            print('Iniciando download do Dadger')
            try:         
                for deck in listOfDecks:
                    if deck['Model'] == 'DECOMP':
                        arrayOfFiles = ['dadger.rv'+str(deck['Revision']), 'dadgnl.rv'+str(deck['Revision']), 'vazoes.rv'+str(deck['Revision'])]
                        try:
                            downloadFileFromDeckV2(deck['Id'],PATH_RESULTS_PROSPEC + '/decomp/', deck['FileName'], deck['FileName'],arrayOfFiles)
                            break
                        except:
                            pass
            
            except Exception as e:
                print(f"Ocorreu um erro inesperado: {e}")
                print('Não foi possivel baixar o dadger')

            try:
                fileName = ''
                idDeck  = 0
                for deck in listOfDecks:
                    if deck['Model'] == 'NEWAVE':
                        print(deck)
                        fileName = deck['FileName']
                        idDeck   = deck['Id']
                        downloadDeckOfStudy(prospecStudyId,idDeck, PATH_RESULTS_PROSPEC + '/newave/', fileName)
                        break 

            except Exception as e:
                print(f"Ocorreu um erro inesperado: {e}")
                print('Não foi possivel baixar o NEWAVE')
        
              
        n_decks = 0
        for deck in prospecStudy['Decks']:
            if ((deck['Model'] == 'DECOMP') and (deck['SensibilityInfo'] == 'Original')):
                n_decks +=1

        return [prospecStudyId, 'Estudo_'+ str(prospecStudyId) + '_compilation.zip', studyStatus, n_decks] 
    else: 
        return [prospecStudyId]


def runBackTeste(config):
 
    date  = datetime.today()

    print('Nome do usuário: ', API_PROSPEC_USERNAME) 

    authenticateProspec(API_PROSPEC_USERNAME, API_PROSPEC_PASSWORD)

    idNEWAVE = {2024: getIdOfNEWAVE('30.0.4'), 2025: getIdOfNEWAVE('30.0.4')}
    idDECOMP = {2024: getIdOfDECOMP('32.0.1'), 2025: getIdOfDECOMP('32.0.1')}
    idDESSEM = {2024: getIdOfDESSEM(''), 2025: getIdOfDESSEM('')}
    idServer = getIdOfServer(SERVER_DEFLATE_PROSPEC)
    idQueue  = getIdOfFirstQueueOfServer(SERVER_DEFLATE_PROSPEC)

    prospecStudyId = createStudy(config.studyName,
                                    'Back Test',
                                    idDECOMP[int(date.year)],
                                    idNEWAVE[int(date.year)])

    sendFileToStudy(prospecStudyId,
                    (config.pathToFile + config.nameFileDecomp),
                    config.nameFileDecomp)

    tags = []
    tags.append('API')
    tags.append('BackTestDC')
    anoMes = config.nameFileDecomp[2:8]
    
    generateStudyDecks(prospecStudyId, int(anoMes[:4]), int(anoMes[-2:]), 1, [int(anoMes[-2:])],
            [int(anoMes[:4])], [False], [False], '',
            '',config.nameFileDecomp,'', tags)

    # Associate Cuts and Volumes/GNL | Reaproveitar Cortes e Volumes/GNL
    if config.associateDecks:
        prospecStudy          = getInfoFromStudy(prospecStudyId)
        listOfDecks           = prospecStudy['Decks']
        destinationCortesId   = []
        previousStage         = []
        destinationVolumeId   = []
        destinationCortesIdDC = []

        for deck in listOfDecks:
            if deck['Model'] == 'NEWAVE':
                destinationCortesId.append(deck['Id'])

            elif deck['Model'] == 'DECOMP':
                destinationVolumeId.append(deck['Id'])
                destinationCortesIdDC.append(deck['Id'])
                previousStage.append(False)

                if 'Matriz' in config.studyName:
                    destinationCortesId.append(deck['Id'])
        
        if len(destinationCortesId) == 0:
            destinationCortesId = [destinationCortesIdDC[0]]
            
        if len(destinationCortesId) > 0 and config.prospecStudyIdToAssociateCuts != '':
            cutAssociation(prospecStudyId, destinationCortesId, config.prospecStudyIdToAssociateCuts)



    # Start Execution | Iniciar execução
    studyStatus = getStatusFromStudy(prospecStudyId)

    if config.startStudy:
        initialStatus = studyStatus
        if studyStatus != 'Executing':
            if SERVER_DEFLATE_PROSPEC == '':
                runExecution(prospecStudyId, idServer,
                         idQueue,idNEWAVE, idDECOMP, idDESSEM, '', 0, 1,
                         2, 2)
            else:
                runExecution(prospecStudyId, idServer,
                         idQueue,idNEWAVE, idDECOMP, idDESSEM, 'c6i.32xlarge', 0, 1,
                         2, 2)

    # Wait Execution to Finish | Aguardar execução terminar
    if config.waitToFinish:
        time.sleep(90) 
        # Wait to change from the initial status | aguardar mudança de status
        countIterations = 0
        if studyStatus != 'Executing':
            if initialStatus != '':
                checkExecution = 0
                while countIterations < 10:
                    countIterations = countIterations + 1
                    time.sleep(30)    # sleep for 10s | aguardar por 10s
                    studyStatus = getStatusFromStudy(prospecStudyId)
                    print(studyStatus)
                    if (studyStatus != initialStatus):
                        checkExecution = 1
                        break

        # Wait to finish | Aguardar terminar
        countIterations = 0
        while countIterations < 60:
            countIterations = countIterations + 1
            if countIterations == 1:
                time.sleep(600)
            else:            
                time.sleep(180)    #
            studyStatus = getStatusFromStudy(prospecStudyId)
            print(studyStatus)
            if studyStatus == 'Finished':
                print('Estudo terminou.')
                break
            elif studyStatus == 'Aborted':
                print('Estudo foi abortado.')
                break
            elif studyStatus == 'Failed':
                print('Estudo parou com falha.')
                break
            elif studyStatus == 'Executing':
                print('Estudo executando...')
            # Dowload Compilation | Download da compilação de resultados
        if config.downloadCompilation:
            print('Iniciando Download do compilado')
            downloadCompilationOfStudy(prospecStudyId, PATH_RESULTS_PROSPEC + '/',
                               'Estudo_'+ str(prospecStudyId) + '_compilation.zip')
            time.sleep(10)
            print('Finalizado o  Download do compilado')

        return ['Estudo_'+ str(prospecStudyId) + '_compilation.zip', studyStatus] 
    else:
        return prospecStudyId




def downloadResultados(config, parametros):

    prospecStudyId = int(parametros['id_estudo'])
    # First step is to authenticate | Primeiro passo é autenticar
    authenticateProspec(API_PROSPEC_USERNAME, API_PROSPEC_PASSWORD)
    #time.sleep(60)
    studyStatus = getStatusFromStudy(prospecStudyId)
    #print(parametros['aguardar_fim'])
    #print(studyStatus)
    if parametros['aguardar_fim']:
        if studyStatus != 'Finished':
            time.sleep(60)
            print(studyStatus)
        
        # Wait to finish | Aguardar terminar
        if studyStatus == 'Executing' or studyStatus == 'Finished' or studyStatus == 'NotReady':
            countIterations = 0
            while countIterations < 60:
                countIterations = countIterations + 1
                if countIterations > 1:
                    time.sleep(600)    # sleep for 10m | aguardar por 10m
                studyStatus = getStatusFromStudy(prospecStudyId)
                print(studyStatus)
                if studyStatus == 'Finished':
                    print('Estudo terminou.')
                    break
                elif studyStatus == 'Aborted':
                    print('Estudo foi abortado.')
                    break
                elif studyStatus == 'Failed':
                    print('Estudo parou com falha.')
                    break
                elif studyStatus == 'Executing':
                    print('Estudo executando...')
        
        # Dowload Compilation | Download da compilação de resultados
        if config.downloadCompilation:
            print('Iniciando Download do compilado')
            downloadCompilationOfStudy(prospecStudyId, PATH_RESULTS_PROSPEC +'/',
                                'Estudo_'+ str(prospecStudyId) + '_compilation.zip')

        if studyStatus == 'Failed' or studyStatus == 'Aborted':        
            print('Prospec não rodou com sucesso, por favor conferir o estudo ',prospecStudyId,' !')
            sys.exit()
        elif studyStatus == 'Finished':
            print('Prospec rodou com sucesso!')  
    else:
        if config.downloadCompilation:
            print('Iniciando Download do compilado')
            downloadCompilationOfStudy(prospecStudyId, PATH_RESULTS_PROSPEC +'/',
                                'Estudo_'+ str(prospecStudyId) + '_compilation.zip')
            print('Finalizado o  Download do compilado do estudo: ',prospecStudyId)
    prospecStudy = getInfoFromStudy(prospecStudyId)
    n_decks = 0
    for deck in prospecStudy['Decks']:
        if ((deck['Model'] == 'DECOMP') and (deck['SensibilityInfo'] == 'Original')):
            n_decks +=1

    return ['Estudo_'+ str(prospecStudyId) + '_compilation.zip', studyStatus, getInfoFromStudy(prospecStudyId)['Title'], n_decks] 

