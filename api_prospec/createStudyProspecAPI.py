import time
from datetime import datetime
import calendar
import sys
from functionsProspecAPI import *

def run_VE(config):
 
    date  = datetime.today()
    time_sleep = 600
    # First step is to authenticate | Primeiro passo é autenticar
    print('Nome do usuário: ', config.username) 

    #print('Senha do usuário: ', config.password)
    authenticateProspec(config.username, config.password)

    # Get number of total requests | Buscar quantidade de requests já usados


    # Get Ids of interest | Buscar Ids de interesse

    idNEWAVE = {2024: getIdOfNEWAVE(config.newaveVersion2023), 2025: getIdOfNEWAVE('30.0.4')}
    idDECOMP = {2024: getIdOfDECOMP(config.decompVersion2023), 2025: getIdOfDECOMP('32.0.1')}
    idDESSEM = {2024: getIdOfDESSEM(config.dessemVersion), 2025: getIdOfDESSEM(config.dessemVersion)}
    idServer = getIdOfServer(config.serverName)
    idQueue  = getIdOfFirstQueueOfServer(config.serverName)

    if config.prospecStudyIdToDuplicate != '':

        # Duplicate Study | Duplicar um estudo
        tags = []  
        tags.append(['Duplicate of Study Id ' + config.prospecStudyIdToDuplicate, 'red', 'white'])
        tags.append([str(date.year)+str(date.month).zfill(2)+'_API', 'white', 'black'])

        prospecStudyId = duplicateStudy(config.prospecStudyIdToDuplicate,
                                        config.studyName + '_'+ str(date.day)+ '/'+ str(date.month) + '-'+ str(date.hour) + ':'+ str(date.minute) + 'h',                                        
                                        'Rodada Automatica',  tags, 2,1,1)
    # Send prevs files to each deck | Enviar arquivo prevs para cada deck
    if config.sendAllPREVStoStudy:
        sendAllPrevsToStudy(prospecStudyId, config.pathToAllPrevs + '/')

    elif config.sendAllPREVStoDeck:
        sendAllPrevsToEachDeck(prospecStudyId, config.pathToPrevs  + '/')

    elif config.sendPREVS:
        sendPrevsToStudy(prospecStudyId, config.pathToPrevs)

    if config.sendVolume:
        prospecStudy        = getInfoFromStudy(prospecStudyId)
        listOfDecks         = prospecStudy['Decks']
        previousStage       = []
        destinationVolumeId = []

        for deck in listOfDecks:
           if deck['Model'] == 'DECOMP':
                destinationVolumeId.append(deck['Id'])

        sendFileToDeck(prospecStudyId, destinationVolumeId[0], config.pathToFileVolume + '/volume_uhe.csv', 'volume_uhe.csv')
    
    if config.sendFileVazoes:
        prospecStudy        = getInfoFromStudy(prospecStudyId)
        listOfDecks         = prospecStudy['Decks']
        previousStage       = []
        destinationVazoesId = []

        for deck in listOfDecks:
           if deck['Model'] == 'DECOMP':
                destinationVazoesId.append(deck['Id'])

        sendVazoesToDeck(prospecStudyId, destinationVazoesId, config.pathToFileVazoes)  

    # Download decks | Download decks
    if config.dowloadDecks:
        downloadDecksOfStudy(prospecStudyId, config.pathToDownloadDecks  + '/', 'CompleteStudy.zip')

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
            if config.serverName == '':
                runExecution(prospecStudyId, idServer,
                         idQueue,idNEWAVE, idDECOMP, idDESSEM, '', 0, config.infeasibilityHandling,
                         config.infeasibilityHandlingSensibility, config.maxRestarts)
            else:
                runExecution(prospecStudyId, idServer,
                         idQueue,idNEWAVE, idDECOMP, idDESSEM, config.serverName, 0, config.infeasibilityHandling,
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
            downloadCompilationOfStudy(prospecStudyId, config.pathToDownloadResults,
                               'Estudo_'+ str(prospecStudyId) + '_compilation.zip')
            print('Compilado baixado com sucesso')
        
        if config.downloadDadger:
            print('Iniciando download do Dadger')
            try:
                prospecStudy = getInfoFromStudy(prospecStudyId)
                listOfDecks = prospecStudy['Decks']
            
                for deck in listOfDecks:
                    if deck['Model'] == 'DECOMP':
                        fileNameDownload = deck['FileName']
                        arrayOfFiles = ['dadger.rv'+str(deck['Revision']), 'dadgnl.rv'+str(deck['Revision']), 'vazoes.rv'+str(deck['Revision'])]
                        try:
                            downloadFileFromDeckV2(deck['Id'],config.pathToDownloadCompilado + 'decomp/', deck['FileName'], deck['FileName'],arrayOfFiles)
                            break
                        except:
                            pass
            
            except Exception as e:
                print(f"Ocorreu um erro inesperado: {e}")
                print('Não foi possivel baixar o dadger')

            try:
                prospecStudy = getInfoFromStudy(prospecStudyId)
                listOfDecks = prospecStudy['Decks']
                fileName = ''
                idDeck  = 0
                for deck in listOfDecks:
                    if deck['Model'] == 'NEWAVE':
                        print(deck)
                        fileName = deck['FileName']
                        idDeck   = deck['Id']
                        downloadDeckOfStudy(prospecStudyId,idDeck, config.pathToDownloadCompilado + 'newave/', fileName)
                        break 

            except Exception as e:
                print(f"Ocorreu um erro inesperado: {e}")
                print('Não foi possivel baixar o NEWAVE')
        
              
        prospecStudy = getInfoFromStudy(prospecStudyId)
        n_decks = 0
        for deck in prospecStudy['Decks']:
            if ((deck['Model'] == 'DECOMP') and (deck['SensibilityInfo'] == 'Original')):
                n_decks +=1

        return ['Estudo_'+ str(prospecStudyId) + '_compilation.zip', studyStatus, n_decks] 
    else: 
        return prospecStudyId


def runBackTeste(config):
 
    date  = datetime.today()

    print('Nome do usuário: ', config.username) 

    authenticateProspec(config.username, config.password)

    idNEWAVE = {2024: getIdOfNEWAVE(config.newaveVersion2023), 2025: getIdOfNEWAVE('30.0.4')}
    idDECOMP = {2024: getIdOfDECOMP(config.decompVersion2023), 2025: getIdOfDECOMP('32.0.1')}
    idDESSEM = {2024: getIdOfDESSEM(config.dessemVersion), 2025: getIdOfDESSEM(config.dessemVersion)}
    idServer = getIdOfServer(config.serverName)
    idQueue  = getIdOfFirstQueueOfServer(config.serverName)

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
            if config.serverName == '':
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
            downloadCompilationOfStudy(prospecStudyId, config.pathToDownloadResults,
                               'Estudo_'+ str(prospecStudyId) + '_compilation.zip')
            time.sleep(10)
            print('Finalizado o  Download do compilado')

        return ['Estudo_'+ str(prospecStudyId) + '_compilation.zip', studyStatus] 
    else:
        return prospecStudyId




def downloadResultados(config, parametros):

    prospecStudyId = int(parametros['id_estudo'])
    # First step is to authenticate | Primeiro passo é autenticar
    authenticateProspec(config.username, config.password)
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
            downloadCompilationOfStudy(prospecStudyId, config.pathToDownloadResults,
                                'Estudo_'+ str(prospecStudyId) + '_compilation.zip')

        if studyStatus == 'Failed' or studyStatus == 'Aborted':        
            print('Prospec não rodou com sucesso, por favor conferir o estudo ',prospecStudyId,' !')
            sys.exit()
        elif studyStatus == 'Finished':
            print('Prospec rodou com sucesso!')  
    else:
        if config.downloadCompilation:
            print('Iniciando Download do compilado')
            downloadCompilationOfStudy(prospecStudyId, config.pathToDownloadResults,
                                'Estudo_'+ str(prospecStudyId) + '_compilation.zip')
            print('Finalizado o  Download do compilado do estudo: ',prospecStudyId)
    prospecStudy = getInfoFromStudy(prospecStudyId)
    n_decks = 0
    for deck in prospecStudy['Decks']:
        if ((deck['Model'] == 'DECOMP') and (deck['SensibilityInfo'] == 'Original')):
            n_decks +=1

    return ['Estudo_'+ str(prospecStudyId) + '_compilation.zip', studyStatus, getInfoFromStudy(prospecStudyId)['Title'], n_decks] 

