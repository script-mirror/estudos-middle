import os
import csv
import re
import glob
from datetime import datetime, date, timedelta 
from dateutil.relativedelta import relativedelta
import calendar
import zipfile
from requestsProspecAPI import * 
from middle.utils.file_manipulation import extract_zip


# -----------------------------------------------------------------------------
# Global variables | Variáveis globais
# -----------------------------------------------------------------------------

token = ''

# -----------------------------------------------------------------------------
# Get token | Obter token
# -----------------------------------------------------------------------------


def authenticateProspec(username, password):
    global token
    token = getToken(username, password)

# -----------------------------------------------------------------------------
# Update Password | Atualizar Senha
# -----------------------------------------------------------------------------


def updatePassword(oldPassword, newPassword):
    parameter = ''
    data = {
        "OldPassword": oldPassword,
        "NewPassword": newPassword,
        "ConfirmPassword": newPassword
    }
    postInAPI(token, '/api/Account/ChangePassword', parameter,
              data)

    return 0

# -----------------------------------------------------------------------------
# Get number of total requests | Buscar quantidade de requests já usados
# -----------------------------------------------------------------------------


def getNumberOfRequests():
    numberOfRequests = getInfoFromAPI(token, '/api/Account/Requests')
    return numberOfRequests

# -----------------------------------------------------------------------------
# Get list of NEWAVES | Obter lista de NEWAVES
# -----------------------------------------------------------------------------


def getListOfNEWAVEs():
    return getInfoFromAPI(token, '/api/CepelModels/Newaves')

# -----------------------------------------------------------------------------
# Get list of NEWAVES and choose one | Obter lista de NEWAVES e escolher um
# -----------------------------------------------------------------------------


def getIdOfNEWAVE(version):
    listOfNewave = getListOfNEWAVEs()

    idNewave = ''
    for newave in listOfNewave:
        if newave['Version'] == version:
            idNewave = newave['Id']
            return idNewave

    return 0

# -----------------------------------------------------------------------------
# Get list of DECOMPs | Obter lista de DECOMPs
# -----------------------------------------------------------------------------

def getStudiesByTag(tags):
    return getInfoFromAPI(token, '/api/v2/prospectiveStudies/',  tags)


def getListOfDECOMPs():
    return getInfoFromAPI(token, '/api/CepelModels/Decomps')

# -----------------------------------------------------------------------------
# Get list of NEWAVES and choose one | Obter lista de NEWAVES e escolher um
# -----------------------------------------------------------------------------


def getIdOfDECOMP(version):
    listOfDecomps = getListOfDECOMPs()

    idDecomp = ''
    for decomp in listOfDecomps:
        if decomp['Version'] == version:
            idDecomp = decomp['Id']
            return idDecomp

    return 0

# -----------------------------------------------------------------------------
# Get list of DESSEM | Obter lista de DESSEM
# -----------------------------------------------------------------------------

def getListOfDESSEMs():
    return getInfoFromAPI(token, '/api/CepelModels/Dessems')

# -----------------------------------------------------------------------------
# Get list of DESSEM and choose one | Obter lista de DESSEM e escolher um
# -----------------------------------------------------------------------------

def getIdOfDESSEM(version):
    listOfDessem = getListOfDESSEMs()

    idDessem = ''
    for dessem in listOfDessem:
        if dessem['Version'] == version:
            idDessem = dessem['Id']
            return idDessem

    return 0

# -----------------------------------------------------------------------------
# Get list of GEVAZP | Obter lista de GEVAZP
# -----------------------------------------------------------------------------

def getListOfGEVAZPs():
    return getInfoFromAPI(token, '/api/CepelModels/Gevazps')

# -----------------------------------------------------------------------------
# Get list of GEVAZP and choose one | Obter lista de GEVAZP e escolher um
# -----------------------------------------------------------------------------


def getIdOfGEVAZP(version):
    listOfGevazp = getListOfGEVAZPs()

    idGevazp = ''
    for gevazp in listOfGevazp:
        if gevazp['Version'] == version:
            idGevazp = gevazp['Id']
            return idGevazp

    return 0

# -----------------------------------------------------------------------------
# Get list of Tags | Obter lista de marcadores
# -----------------------------------------------------------------------------

def getListOfTags():
    return getInfoFromAPI(token, '/api/prospectiveStudies/Tags')

# -----------------------------------------------------------------------------
# Get list of Spot Instances Types | Obter lista de tipos de instâncias SPOT
# -----------------------------------------------------------------------------


def getListOfSpotInstancesTypes():
    return getInfoFromAPI(token, '/api/Servers/SpotInstances')

# -----------------------------------------------------------------------------
# Get list of Spot Instances Types    and choose one
# Obter lista de tipos de instâncias SPOT e escolher um
# -----------------------------------------------------------------------------


def getIdOfSpotInstancesType(serverType):
    listOfSpotInstances = getListOfSpotInstancesTypes()

    idSpotInstances = ''
    for spotInstances in listOfSpotInstances:
        if spotInstances['InstanceType'] == serverType:
            idSpotInstances = spotInstances['Id']
            return idSpotInstances

    return 0

# -----------------------------------------------------------------------------
# Get list of servers - this is necessary to add studies in a given queue
# Obter lista de servidores - necessário para adicionar um estudo em uma fila
# -----------------------------------------------------------------------------


def getListOfServers():
    return getInfoFromAPI(token, '/api/Servers')


def getIdOfServer(serverName):
    listOfServers = getListOfServers()

    for server in listOfServers:
        if server['Name'] == serverName:
            idServer = server['Id']
            return idServer

    return 0


def getIdOfFirstQueueOfServer(serverName):

    listOfServers = getListOfServers()

    for server in listOfServers:
        if server['Name'] == serverName:
            listOfQueues = server['Queues']
            firsQueue = listOfQueues[0]
            return firsQueue['Id']

    return 0

# -----------------------------------------------------------------------------
# Create one study | Criar um estudo
# -----------------------------------------------------------------------------


def createStudy(title, description, idDecomp, idNewave):
    parameter = ''

    data = {
        "Title": title,
        "Description": description,
        "DecompVersionId": int(idDecomp),
        "NewaveVersionId": int(idNewave),
    }

    print("Creating study with the following configuration:")
    print(data)

    prospecStudyId = postInAPI(token, '/api/prospectiveStudies', parameter,
                               data)
    return prospecStudyId

# -----------------------------------------------------------------------------
# Get info from a specific study | Obter informações de um estudo específico
# -----------------------------------------------------------------------------


def getInfoFromStudy(idStudy):
    prospecStudy = getInfoFromAPI(token, '/api/prospectiveStudies/'
                                  + str(idStudy))
    return prospecStudy

# -----------------------------------------------------------------------------
# Get status from a specific study | Obter o status de um estudo específico
# -----------------------------------------------------------------------------


def getStatusFromStudy(idStudy):
    prospecStudy = getInfoFromAPI(token, '/api/prospectiveStudies/'
                                  + str(idStudy))
    return prospecStudy['Status']

# -----------------------------------------------------------------------------
# Send files to a study | Enviar arquivos para um estudo
# -----------------------------------------------------------------------------


def sendFileToStudy(idStudy, pathToFile, fileName):
    prospecStudy = sendFileToAPI(token, '/api/prospectiveStudies/'
                                 + str(idStudy) + '/UploadFiles',
                                 pathToFile, fileName)
    return prospecStudy

# -----------------------------------------------------------------------------
# Send files to a deck of a study | Enviar arquivos para um deck de um estudo
# -----------------------------------------------------------------------------


def sendFileToDeck(idStudy, idDeck, pathToFile, fileName):
    prospecStudy = sendFileToAPI(token, '/api/prospectiveStudies/'
                                 + str(idStudy) + '/UploadFiles?deckId='
                                 + str(idDeck), pathToFile, fileName)
    return prospecStudy



def sendVazoesToDeck(idStudy, listOfDecks, pathToFile):
    for deck in listOfDecks:
        for file in os.listdir(pathToFile):
            prospecStudy = sendFileToAPI(token, '/api/prospectiveStudies/'
                                 + str(idStudy) + '/UploadFiles?deckId='
                                 + str(deck), pathToFile+ '/'+ file , file)
    return prospecStudy

def downloadFileFromDeckV2(idDeck, pathToDownload, fileNameDownload, fileName, fileNames):
    os.makedirs(pathToDownload,exist_ok=True)
    filesToGet = fileNames
    response = getFileFromS3viaAPIV2(token, '/api/v2/prospectiveStudies/DownloadResultFiles/' + str(idDeck), filesToGet, fileName, pathToDownload)




# -----------------------------------------------------------------------------
# Generate decks to a prospective study
# Gerar decks para um estudo prospectivo
# -----------------------------------------------------------------------------
def generateDessemStudyDecks(idStudy, initialYear, initialMonth, initialDay, duration, firstDessemFile):
    parameter = ''
    data = {
        "InitialYear": initialYear,
        "InitialMonth": initialMonth,
        "InitialDay": initialDay,
        "Duration": duration,
        "DessemFileName": firstDessemFile,
    }
    print("Gerando decks com as seguintes configuracoes para o estudo: ",
          str(idStudy))
    print(data)
    postInAPI(token, '/api/prospectiveStudies/' + str(idStudy) + '/GenerateDessem',
              parameter, data)
    

def generateStudyDecks(idStudy, initialYear, initialMonth, duration, month,
                       year, multipleStages, multipleRevision, firstNewaveFile,
                       otherNewaveFiles, decompFile, spreadsheetFile, tags):

    listOfDeckConfiguration = []
    listOfTags = []

    i = 0
    for deck in month:
        deckConfiguration = {}
        deckConfiguration['Year'] = year[i]
        deckConfiguration['Month'] = month[i]
        deckConfiguration['MultipleStages'] = multipleStages[i]
        deckConfiguration['MultipleRevisions'] = multipleRevision[i]
        if (i > 0):
            if (otherNewaveFiles[i] != ''):
                deckConfiguration['NewaveUploaded'] = otherNewaveFiles[i]
        listOfDeckConfiguration.append(deckConfiguration)
        i = i + 1

    for tag in tags:
        tagsConfiguration = {}
        tagsConfiguration['Text'] = tag
        listOfTags.append(tagsConfiguration)

    parameter = ''
    data = {
        "InitialYear": initialYear,
        "InitialMonth": initialMonth,
        "Duration": duration,
        "DeckCreationConfigurations": listOfDeckConfiguration,
        "Tags": listOfTags,
        "InitialFiles": {
            "NewaveFileName": firstNewaveFile,
            "DecompFileName": decompFile,
            "SpreadsheetFileName": spreadsheetFile
        }
    }

    print("Gerando decks com as seguintes configuracoes para o estudo: ",
          str(idStudy))
    print(data)

    postInAPI(token, '/api/prospectiveStudies/' + str(idStudy) + '/Generate',
              parameter, data)

# -----------------------------------------------------------------------------
# Generate next revision
# Gerar próxima revisão
# -----------------------------------------------------------------------------

def generateNextRev(idStudy, newaveFile, decompFile, spreadsheetFile, tags):

    listOfTags = []

    for tag in tags:
        tagsConfiguration = {}
        tagsConfiguration['Text'] = tag
        listOfTags.append(tagsConfiguration)

    parameter = ''
    data = {
        "InitialFiles": {
            "NewaveFileName": newaveFile,
            "DecompFileName": decompFile,
            "SpreadsheetFileName": spreadsheetFile
        },
        "Tags": listOfTags
    }

    print("Gerando a próxima revisão para o estudo: ",
          str(idStudy))
    print(data)

    patchInAPI(token, '/api/prospectiveStudies/' + str(idStudy) + '/NextRev',
              parameter, data)

# -----------------------------------------------------------------------------
# Generate study with complete decks | Gerando estudo com decks completos
# -----------------------------------------------------------------------------

def completeStudyDecks(idStudy, fileName, tags):

    listOfTags = []

    for tag in tags:
        tagsConfiguration = {}
        tagsConfiguration['Text'] = tag
        listOfTags.append(tagsConfiguration)

    parameter = ''
    data = {
        "Tags": listOfTags,
        "FileName": fileName
    }

    print("Usando a seguinte configuracao para o estudo: ", str(idStudy))
    print(data)

    postInAPI(token, '/api/prospectiveStudies/' + str(idStudy) + '/Complete',
              parameter, data)




def onlyDeckStudyDecks(idStudy, fileName, tags):

    listOfTags = []

    for tag in tags:
        tagsConfiguration = {}
        tagsConfiguration['Text'] = tag
        listOfTags.append(tagsConfiguration)

    parameter = ''
    data = {
        "Tags": listOfTags,
        "FileName": fileName
    }

    print("Usando a seguinte configuracao para o estudo: ", str(idStudy))
    print(data)

    postInAPI(token, '/api/prospectiveStudies/' + str(idStudy) + '/UploadFiles',
              parameter, data)



# -----------------------------------------------------------------------------
# Duplicate a study | Duplicar um estudo
# -----------------------------------------------------------------------------


def duplicateStudy(idStudy, title, description, tags, vazoesDat, vazoesRvx, prevsCondition):
    # VazoesDatCondition(integer)
    # 0 - padrão, não faz nenhuma mudança no decks.
    # 1 - exclui todos os vazoes.dat de todos os decks DECOMP do estudo.
    # 2 - exclui os vazoes.dat do segundo deck DECOMP em diante.

    # VazoesRvxCondition(integer)
    # 0 - Modo padrão
    # 1 - exclui todos os vazoes.rvX de todos os decks DECOMP do estudo.
    # 2 - exclui os vazoes.rvX do segundo deck DECOMP em diante.

    # PrevsCondition(integer)
    # 0 - Modo padrão
    # 1 - exclui todos os prevs, inclusive sensibilidade, de todos os decks DECOMP do estudo.
    # 2 - exclui somente os prevs sensibilidade do primeiro deck DECOMP e dos demais decks exclui todos os prevs, inclusive sensibilidade

    listOfTags = []

    for tag in tags:
        tagsConfiguration = {}
        tagsConfiguration['Text'] = tag[0]
        tagsConfiguration['TextColor'] = tag[1]
        tagsConfiguration['BackgroundColor'] = tag[2]
        listOfTags.append(tagsConfiguration)

    parameter = ''
    data = {
        "Title": title,
        "Description": description,
        "Tags": listOfTags,
        "VazoesDatCondition": vazoesDat,
        "VazoesRvxCondition": vazoesRvx,
        "PrevsCondition": prevsCondition
    }

    print("Usando a seguinte configuracao para o estudo: ", str(idStudy))
    print(data)

    prospecStudyId = postInAPI(token, '/api/prospectiveStudies/'
                               + str(idStudy) + '/Duplicate', parameter, data)
    return prospecStudyId

# -----------------------------------------------------------------------------
# Adding tags to a study | Adicionar tags em um estudos
# -----------------------------------------------------------------------------

def addTags(idStudy, data):

    parameter = ''

    print("Adicionando tags ao estudo: ", str(idStudy))
    print(data)

    patchInAPI(token, '/api/prospectiveStudies/' + str(idStudy) + '/AddTags',
              parameter, data)

# -----------------------------------------------------------------------------
# Removing tags to a study | Remover tags em um estudos
# -----------------------------------------------------------------------------

def removeTags(idStudy, tags):

    listOfTags = []

    for tag in tags:
        tagsConfiguration = {}
        tagsConfiguration['Text'] = tag
        listOfTags.append(tagsConfiguration)

    parameter = ''
    
    data = listOfTags

    print("Removendo tags do estudo: ", str(idStudy))
    print(data)

    patchInAPI(token, '/api/prospectiveStudies/' + str(idStudy) + '/RemoveTags',
              parameter, data)


# -----------------------------------------------------------------------------
# Send prevs file to each deck | Enviar o arquivo prevs para cada deck
# -----------------------------------------------------------------------------

def sendPrevsToStudy(idStudy, pathToPrevs):

    prospecStudy = getInfoFromStudy(idStudy)
    listOfDecks = prospecStudy['Decks']
    listOfFiles = []
    listOfPaths = []
    listOfDecksIds = []

    for deck in listOfDecks:

        if ((deck['Model'] == 'DECOMP') and (deck['SensibilityInfo'] == 'Original')):

            mes = deck['Month']
            revision = ".rv" + str(deck['Revision'])

            pathToFile = pathToPrevs + '/' + str(mes) + '/'

            print('Arquivo em ' + pathToFile)
            for file in os.listdir(pathToFile):
                if file.lower().startswith('prevs'):
                    if file.lower().endswith(revision):
                        prospecStudy = sendFileToDeck(idStudy,
                                                      str(deck['Id']),
                                                      (pathToFile + file),
                                                      file)

# -----------------------------------------------------------------------------
# Send all prevs files to a deck | Enviar todos os arquivos prevs de um deck
# -----------------------------------------------------------------------------


def sendAllPrevsToEachDeck(idStudy, pathToPrevs):

    prospecStudy = getInfoFromStudy(idStudy)
    listOfDecks = prospecStudy['Decks']

    for deck in listOfDecks:

        if ((deck['Model'] == 'DECOMP') and (deck['SensibilityInfo'] == 'Original')):

            listOfFiles = {}
            mes = deck['Month']
            revision = ".rv" + str(deck['Revision'])
            print(idStudy, revision)
            pathToFile = pathToPrevs +'/' + str(mes) + '/'

            print('Arquivos em ' + pathToFile)
            print(os.listdir(pathToFile))
            for file in os.listdir(pathToFile):
                if file.lower().startswith('prevs'):
                    if file.lower().endswith(revision):
                        listOfFiles[file] = [file, open((pathToFile + file), 'rb'),
                                             'multipart/form-data', {'Expires': '0'}]
            print(listOfFiles)
            sendFiles(token, '/api/prospectiveStudies/' + str(idStudy)
                      + '/UploadFiles?deckId=' + str(deck['Id']), listOfFiles)

# -----------------------------------------------------------------------------
# Send all prevs files to a study | Enviar todos os arquivos prevs de um estudo
# -----------------------------------------------------------------------------


def sendAllPrevsToStudy(idStudy, pathToAllPrevs):

    listOfPrevs = {}

    for file in os.listdir(pathToAllPrevs):
        if 'prevs' in file.lower():
            listOfPrevs[file] = [file, open((pathToAllPrevs + file), 'rb'),
                                 'multipart/form-data', {'Expires': '0'}]

    sendFiles(token, '/api/prospectiveStudies/' + str(idStudy)
              + '/UploadMultiplePrevs', listOfPrevs)

# -----------------------------------------------------------------------------
# Run a study | Executar um estudo
# -----------------------------------------------------------------------------


def runExecution(idStudy, idServer, idQueue, idNEWAVEJson, idDECOMPJson, idDESSEMJson, spotInstanceType, executionMode,
                 infeasibilityHandling,infeasibilityHandlingSensibility, maxRestarts, spotBreakdownOption=2):
    #Cria uma solicitação para inciar um estudo.
    #Atenção para as opções das propriedades abaixo.
    #ExecutionMode(integer)
    #0 - Modo padrão
    #1 - Consitência
    #2 - Padrão + consistência

    #InfeasibilityHandling(integer)
    #0 - Parar estudo
    #1 - Tratar inviabilidades
    #2 - Ignorar inviabilidades
    #3 - Tratar + Ignorar inviabilidades

    #InfeasibilityHandlingSensibility(integer)
    #0 - Parar estudo
    #1 - Tratar inviabilidades
    #2 - Ignorar inviabilidades
    #3 - Tratar + Ignorar inviabilidades

    parameter = ''
    ServerPurchaseOption = 1
    if idServer == 0:
        if spotInstanceType == '':
            prospecStudy = getInfoFromStudy(idStudy)
            listOfDecks = prospecStudy['Decks']
            containsNEWAVE = False
            for deck in listOfDecks:
                if deck['Model'] == 'NEWAVE':
                    containsNEWAVE = True
                    break

            if containsNEWAVE:
                data = {
                    "EphemeralInstanceType": 'c5.18xlarge',
                    "ServerPurchaseOption": ServerPurchaseOption,
                    "ExecutionMode": executionMode,
                    "InfeasibilityHandling": infeasibilityHandling,
                    "InfeasibilityHandlingSensibility": infeasibilityHandlingSensibility,
                    "MaxTreatmentRestarts": maxRestarts,
                    "SpotBreakdownOption": spotBreakdownOption,
                    "MaxTreatmentRestartsSensibility": 1
                }
            else:
                data = {
                    "EphemeralInstanceType": 'm5.4xlarge',
                    "ServerPurchaseOption": ServerPurchaseOption,
                    "ExecutionMode": executionMode,
                    "InfeasibilityHandling": infeasibilityHandling,
                    "InfeasibilityHandlingSensibility": infeasibilityHandlingSensibility,
                    "MaxTreatmentRestarts": maxRestarts,
                    "SpotBreakdownOption": spotBreakdownOption,
                    "MaxTreatmentRestartsSensibility": 1
                }

        else:
            data = {
                "EphemeralInstanceType": spotInstanceType,
                "ServerPurchaseOption": ServerPurchaseOption,
                "ExecutionMode": executionMode,
                "InfeasibilityHandling": infeasibilityHandling,
                "InfeasibilityHandlingSensibility": infeasibilityHandlingSensibility,
                "MaxTreatmentRestarts": maxRestarts,
                "SpotBreakdownOption": spotBreakdownOption,
                "MaxTreatmentRestartsSensibility": 1
            }
    elif idQueue == 0:
        data = {
            "ServerId": int(idServer),
            "ExecutionMode": executionMode,
            "InfeasibilityHandling": infeasibilityHandling,
            "InfeasibilityHandlingSensibility": infeasibilityHandlingSensibility,
            "MaxTreatmentRestarts": maxRestarts,
            "SpotBreakdownOption": spotBreakdownOption,
            "ServerPurchaseOption": ServerPurchaseOption,
            "MaxTreatmentRestartsSensibility": 1
        }
    else:
        data = {
            "ServerId": int(idServer),
            "QueueId": int(idQueue),
            "ExecutionMode": executionMode,
            "InfeasibilityHandling": infeasibilityHandling,
            "InfeasibilityHandlingSensibility": infeasibilityHandlingSensibility,
            "MaxTreatmentRestarts": maxRestarts,
            "SpotBreakdownOption": spotBreakdownOption,
            "ServerPurchaseOption": ServerPurchaseOption,
            "MaxTreatmentRestartsSensibility": 1
        }
        
    deckModel = []
    prospecStudy = getInfoFromStudy(idStudy)
    listOfDecks = prospecStudy['Decks']
    for deck in listOfDecks:
         if deck['Model'] == 'NEWAVE':
           deckModel.append({"DeckId": deck["Id"], "NewaveVersionId": idNEWAVEJson[deck["Year"]]})

         elif deck['Model'] == 'DECOMP' and deck['SensibilityInfo'] == 'Original':
           deckModel.append({"DeckId": deck["Id"], "DecompVersionId": idDECOMPJson[deck["Year"]] })

         elif deck['Model'] == 'DESSEM' and idDESSEMJson["idDessem"] != 0:
           deckModel.append({"DeckId": deck["Id"], "DessemVersionId": idDESSEMJson[deck["Year"]]})

    if (deckModel.count != 0):
        data["DecksRunModel"] = deckModel

    print("A seguinte configuracao sera usada para iniciar a execucao o estudo: ", str(idStudy))
    print(data)

    response = postInAPI(token, '/api/prospectiveStudies/' + str(idStudy)
                         + '/Run', parameter, data)

    # print(response)

# -----------------------------------------------------------------------------
# Abort execution | Abortar execução
# -----------------------------------------------------------------------------


def abortExecution(idStudy):
    parameter = ''
    data = ''

    response = postInAPI(token, '/api/prospectiveStudies/' + str(idStudy)
                         + '/Stop', parameter, data)
    print(response)

# -----------------------------------------------------------------------------
# Download study | Download de um estudo
# -----------------------------------------------------------------------------
def downloadDeckOfStudy(idStudy,idDeck, pathToDownload, fileName):
    os.makedirs(pathToDownload ,exist_ok=True)
    response = getFileFromAPI(token, '/api/prospectiveStudies/' + str(idStudy)
                              + '/DeckDownload?deckId='+str(idDeck), fileName, pathToDownload)
    print(response)
"""
def downloadDecksOfStudy(idStudy, pathToDownload, fileName):
    if os.path.exists (pathToDownload) == False: os.mkdir (pathToDownload)
    response = getFileFromAPI(token, '/api/prospectiveStudies/' + str(idStudy)
                              + '/DeckDownload', fileName, pathToDownload)
"""
# -----------------------------------------------------------------------------
# Download File From Deck Results | Download de um arquivo de um resultado do deck
# ----------------------------------------------------------------------------- 

def downloadFileFromDeck(idDeck, pathToDownload, fileNameDownload, fileNames):
    if os.path.exists (pathToDownload) == False: os.mkdir (pathToDownload)
    filesToGet = 'fileNames=' + '&fileNames='.join(fileNames)
    response = getFileFromS3viaAPI(token, '/api/prospectiveStudies/DownloadResultFiles/' + str(idDeck) 
                                + '?' + filesToGet, fileNameDownload, pathToDownload)

# -----------------------------------------------------------------------------
# Download compilation | Download da compilação
# -----------------------------------------------------------------------------


def downloadCompilationOfStudy(idStudy, pathToDownload, fileName):
    if os.path.exists (pathToDownload) == False: os.mkdir (pathToDownload)
    response = getCompilationFromAPI(token, '/api/prospectiveStudies/'
                                     + str(idStudy) + '/CompilationDownload',
                                     fileName, pathToDownload)
# -----------------------------------------------------------------------------
# Download File From Results NWLISTOP | Download de um arquivo de um resultado NWLISTOP
# -----------------------------------------------------------------------------

def downloadResultFileNWLISTOP(idDeck , pathToDownload ,fileNameDownload, fileNames):
    filesToGet = 'fileNames=' + '&fileNames='.join(fileNames)
    response = getFileFromS3viaAPI(token, '/api/prospectiveStudies/DownloadResultNWLISTOP/' + str(idDeck) 
                                   + '?' + filesToGet, fileNameDownload, pathToDownload)

# -----------------------------------------------------------------------------
# Download Results NWLISTOP | Download de um arquivo de um resultado NWISTOP
# -----------------------------------------------------------------------------

def downloadResultNWLISTOP(idDeck , pathToDownload ,fileNameDownload):
    response = getFileFromS3viaAPI(token, '/api/prospectiveStudies/DownloadResultNWLISTOP/' + str(idDeck) ,
                                  fileNameDownload, pathToDownload)

# -----------------------------------------------------------------------------
# Download File From Results NEWDESP | Download de um arquivo de um resultado NEWDESP
# -----------------------------------------------------------------------------

def downloadResultFileNEWDESP(idDeck , pathToDownload ,fileNameDownload, fileNames):
    filesToGet = 'fileNames=' + '&fileNames='.join(fileNames)
    response = getFileFromS3viaAPI(token, '/api/prospectiveStudies/DownloadResultNEWDESP/' + str(idDeck) 
                                + '?' + filesToGet, fileNameDownload, pathToDownload)

# -----------------------------------------------------------------------------
# Download Results NEWDESP | Download de um arquivo de um resultado NEWDESP
# -----------------------------------------------------------------------------

def downloadResultNEWDESP(idDeck , pathToDownload ,fileNameDownload):
    response = getFileFromS3viaAPI(token, '/api/prospectiveStudies/DownloadResultNEWDESP/' + str(idDeck) ,
                                  fileNameDownload, pathToDownload)

# -----------------------------------------------------------------------------
# Associate cuts | Reaproveitar (associar) cortes
# -----------------------------------------------------------------------------

def cutAssociation_only_decomp(idStudy, destinationIds, sourceStudyId):
    listOfAssociation = []
    idx = 0
    for deck in destinationIds:
        associationConfiguration = {}
        associationConfiguration['DestinationDeckId'] = deck
        associationConfiguration['SourceStudyId'] = sourceStudyId[idx]
        #associationConfiguration['Mes'] = mes[idx]
        #associationConfiguration['Ano'] = ano[idx]
        idx += 1
        listOfAssociation.append(associationConfiguration)

    parameter = ''
    data = {
    "cortesAssociation": listOfAssociation,
    }

    print("Usando a seguinte configuracao do estudo: ", str(idStudy))
    print(data)

    postInAPI(token, '/api/prospectiveStudies/' + str(idStudy)
    + '/Associate', parameter, data)

    

def cutAssociation(idStudy, destinationIds, sourceStudyId):
    listOfAssociation = []

    for i in range(len(sourceStudyId)):
        associationConfiguration = {}
        associationConfiguration['DestinationDeckId'] = destinationIds[i]
        associationConfiguration['SourceStudyId'] = sourceStudyId[i]
        listOfAssociation.append(associationConfiguration)

    parameter = ''
    data = {
        "cortesAssociation": listOfAssociation,
    }

    print("Usando a seguinte configuracao do estudo: ", str(idStudy))
    print(data)

    postInAPI(token, '/api/prospectiveStudies/' + str(idStudy)
              + '/Associate', parameter, data)

# -----------------------------------------------------------------------------
# Associate Volume and GNL | Reaproveitamento (associação) de volumes e GNL
# -----------------------------------------------------------------------------


def volumeAssociation(idStudy, destinationIds, previsouStage, sourceStudyId):
    listOfAssociation = []

    i = 0
    for deck in destinationIds:
        associationConfiguration = {}
        associationConfiguration['DestinationDeckId'] = deck
        associationConfiguration['SourceStudyId'] = sourceStudyId
        if (len(previsouStage) > i):
            associationConfiguration['PreviousStage'] = previsouStage[i]
        listOfAssociation.append(associationConfiguration)
        i = i + 1

    parameter = ''
    data = {
        "volumeAssociation": listOfAssociation,
    }

    print("Usando a seguinte configuracao do estudo: ", str(idStudy))
    print(data)

    postInAPI(token, '/api/prospectiveStudies/' + str(idStudy)
              + '/Associate', parameter, data)
'''
config = {}
config['id_duplicate'] ={}
config['id_associate_cuts'] ={}
config['send_volume'] = False
config['download_nwlistop'] = False
config['download_dadger'] = False
config['start_study'] = True
config['path_to_file'] = ''
config['path_to_download_results'] = ''
config['path_to_download_nwlistop'] = ''
config['path_to_download_decks'] = ''
config['path_to_prevs'] = ''
config['path_to_all_prevs'] = ''
config['newave_version'] = ''
config['decomp_version'] = ''
config['dessem_version'] = ''
config['server_name'] = ''
config['username'] = ''
config['password'] = ''
config['study_name'] = ''
config['type_study'] = ''
config['name_file_dessem'] = ''
config['name_file_decomp'] = ''
config['name_file_newave'] = ''
config['infeasibility_handling_sensibility'] = 2
config['max_restarts'] = 1 
config['infeasibility_handling'] = 3
config['id_associate_volumes'] = ''
'''


# Configurações do estudo 
class Config(object):
    def __init__(self):
        self.setup()
        
    def setup(self):
        self.sendPREVS              = False
        self.sendAllPREVStoDeck     = True
        self.sendAllPREVStoStudy    = False
        self.waitToFinish           = True
        self.dowloadDecks           = False
        self.createWithGeneration   = False
        self.abortStudy             = False
        self.downloadCompilation    = True
        self.downloadResultFile     = False
        self.associateDecks         = True
        self.sendFileToStudy        = False
        self.sendVolume             = True
        self.sendDadvaz             = False
        self.sendFileVazoes         = False
        self.downloadNWLISTOP       = False
        self.downloadDadger         = False
        self.startStudy             = True
        self.durationStudy          = 0
        self.dayInitialStudy        = 0
        self.monthInitialStudy      = 0
        self.yearInitialStudy       = 0
        self.pathToFile             = ''
        self.pathToFileDadvaz       = ''
        self.pathToDownloadResults  = ''
        self.pathToDownloadNWLISTOP = ''
        self.pathToDownloadDecks    = ''
        self.pathToPrevs            = ''
        self.pathToAllPrevs         = ''
        self.pathToFilDadavaz       = ''
        self.pathToFileVazoes       = ''
        self.newaveVersion          = ''
        self.decompVersion          = ''
        self.dessemVersion          = ''
        self.serverName             = ''
        self.username               = ''
        self.password               = ''
        self.studyName              = ''
        self.studyName2Rv           = ''
        self.typeStudy              = ''
        self.nameFileDessem         = ''
        self.nameFileDecomp         = ''
        self.nameFileNewave         = ''
        self.tag                    = None
        self.infeasibilityHandlingSensibility = 3
        self.maxRestarts                      = 3
        self.infeasibilityHandling            = 3
        self.prospecStudyIdToDuplicate        = ''
        self.prospecStudyIdToDuplicate2Rv     = ''
        self.prospecStudyIdToDuplicat42Rv     = ''
        self.prospecStudyIdToAssociateCuts    = []
        self.prospecStudyIdToAssociateCuts2Rv = []
        self.prospecStudyIdToAssociateCuts4Rv = []
        self.prospecStudyIdToAssociateVolumes = ''

    def setAttConfig(self, argv ):
        for i in range (len(argv)): 
            key = argv[i][0]
            key = re.sub(r"\s+", "", key, flags=re.UNICODE)
            
            if key == 'sendPREVS'           or key == 'sendAllPREVStoDeck'   or \
               key == 'sendAllPREVStoStudy' or key == 'waitToFinish'         or \
               key == 'dowloadDecks'        or key == 'createWithGeneration' or \
               key == 'abortStudy'          or key == 'downloadCompilation'  or \
               key == 'downloadResultFile'  or key == 'associateDecks'       or \
               key == 'downloadResultFile'  or key == 'sendFileToStudy'      or \
               key == 'sendVolume'          or key == 'sendFileVazoes'       or\
               key == 'sendDadvaz'          or key == 'downloadNWLISTOP': 
                self.__dict__[key] = bool(int(argv[i][1]))

            elif key == 'durationStudy':
                self.__dict__[key] = int(argv[i][1])            
                
            elif key == 'pathToFile'       or key == 'pathToDownloadDecks' or \
                 key == 'pathToAllPrevs'   or key =='pathToFileVolume'     or\
                 key == 'pathToFileVazoes' or key == 'pathToFileDadvaz'    or\
                 key == 'pathToPrevs'      or key =='pathToDownloadResults':
                self.__dict__[key] = '/projetos/estudos-middle/api_prospec/' + str(re.sub(r"\s+", "", argv[i][1], flags=re.UNICODE))  

            elif key == 'pathToDownloadNWLISTOP':
                self.__dict__[key] =  str(re.sub(r"\s+", "", argv[i][1], flags=re.UNICODE))  

            elif key == 'prospecStudyIdToAssociateCuts' or key == 'nameFileNewave' or\
                 key == 'nameFileDecomp' or key == 'prospecStudyIdToAssociateCuts2Rv'or\
                 key == 'prospecStudyIdToAssociateCuts1Rv' or key == 'prospecStudyIdToAssociateCuts5Rv'or key == 'prospecStudyIdToAssociateCuts4Rv'or key == 'prospecStudyIdToAssociateCuts3Rv'or\
                 key == 'prospecStudyIdToAssociateCuts7Rv' or key == 'prospecStudyIdToAssociateCuts8Rv' or key == 'prospecStudyIdToAssociateCuts6Rv':
                list_value = []
                del argv[i][0]
                for value in argv[i]: 
                    value_str = str(re.sub(r"\s+", "", value, flags=re.UNICODE))
                    if value_str != '':
                        list_value.append(value_str)
                self.__dict__[key] =  list_value

            elif key == 'studyName' or key == 'studyName2Rv':
                 self.__dict__[key] = argv[i][1]

            else:
                self.__dict__[key] = str(re.sub(r"\s+", "", argv[i][1], flags=re.UNICODE))        



# leitura das configurações
def readConfig(a_file): 
    
    csvfile = open(a_file ,'r')
    data  = csv.reader(csvfile, delimiter=';')        
    argv = []    

    config = Config()

    for line in data:
        if line != '':
            argv.append(line[0:len(line)])

    config.setAttConfig(argv)
    
    return config


def ExtractFolder(pathIn, pathOut, arquivo):
 
    nome_arq = arquivo[0:len(arquivo)-4]
    
    if os.path.exists (pathOut + '/' + nome_arq) == False: os.mkdir (pathOut + '/' + nome_arq)
   
    with zipfile.ZipFile(pathIn + '/' + arquivo, 'r') as pastaCompactada:
        for arquivoInZip in pastaCompactada.namelist():
            pastaCompactada.extract(arquivoInZip, pathOut + '/' + nome_arq)
            
            
def atualizaConfigAutomatizadoDessem(config):
    data = datetime.now() - timedelta(hours=3)

    duracaoEstudo  =  5 - data.weekday() 
    if data.weekday() == 6 or data.weekday() == 7: duracaoEstudo  = data.weekday() - 7 + 6

    config.nameFileDessem =  getFolderName(data)               

    config.dayInitialStudy   = int(data.day)
    config.monthInitialStudy = int(data.month)
    config.yearInitialStudy  = int(data.year)
    config.durationStudy     = int(duracaoEstudo)
    data = datetime.now() - timedelta(hours=3) + timedelta(days=1)
    config.studyName         = 'Dessem_' + data.strftime('20%y-%m-%d')



def getFolderName(data):   
    
    semanaMes = week_of_month(data)
    ultimoDiaMes = calendar.monthrange(data.year, data.month)[1]
    diaSemanaFimMes =  (date(data.year, data.month, ultimoDiaMes)).weekday()
    semanaFimMes = week_of_month(date(data.year, data.month, ultimoDiaMes))
    if diaSemanaFimMes == 5 or diaSemanaFimMes == 6:
        semanaFimMes  = semanaFimMes + 1

    if semanaMes == semanaFimMes and diaSemanaFimMes != 4:
        data = data + relativedelta(months=1) 
        semanaMes = 1

    return 'DS_CCEE_' + str(data.month).zfill(2) + str(data.year).zfill(4) + '_SEMREDE_RV' + str(semanaMes-1) + 'D' + str(data.day).zfill(2) + '.zip'


def week_of_month(a_date_value):
    if a_date_value.month == 1:
        return (a_date_value.isocalendar()[1] + 1)
    else:
        if date(a_date_value.year, a_date_value.month, 1).weekday() == 5:
            return (a_date_value.isocalendar()[1] - a_date_value.replace(day=1).isocalendar()[1] + 1)-1
        else:
            return (a_date_value.isocalendar()[1] - a_date_value.replace(day=1).isocalendar()[1] + 1)


def download_dadger_update(prospecStudyId, logger, pathToDownload):
    logger.info(f"Iniciando download do estudo para o caminho: {pathToDownload}")
    try:
        
        if prospecStudyId is None:
            logger.info("Nenhum ID de estudo fornecido, buscando o estudo BASE-8-RV")
            # Busca o estudo BASE-8-RV
            prospecStudyId = getStudiesByTag({'page': 1, 'pageSize': 1, 'tags': f"BASE-{8}-RV"})['ProspectiveStudies'][0]['Id']
        else:
            prospecStudyId = prospecStudyId[0]
        logger.debug(f"ID do estudo encontrado: {prospecStudyId}")
        
        os.makedirs(pathToDownload, exist_ok=True)
        logger.info(f"Diretório criado ou já existente: {pathToDownload}")
        
        prospecStudy = getInfoFromStudy(prospecStudyId)
        logger.debug(f"Informações do estudo obtidas: {prospecStudy}")
        
        listOfDecks = prospecStudy['Decks']
        logger.info(f"{len(listOfDecks)} decks encontrados no estudo")
        
        list_paths = []
        for deck in listOfDecks:
            if deck['Model'] == 'DECOMP':
                logger.info(f"Processando deck DECOMP: {deck['FileName']} (ID: {deck['Id']})")
                path = pathToDownload + deck['FileName']
                logger.debug(f"Baixando arquivo para: {path}")
                
                getFileFromAPI(token, f"/api/prospectiveStudies/{prospecStudyId}/DeckDownload?deckId={deck['Id']}", deck['FileName'], pathToDownload)
                logger.info(f"Arquivo baixado: {deck['FileName']}")
                
                path_unzip = extract_zip(path)
                logger.debug(f"Arquivo descompactado em: {path_unzip}")
                
                dadger_file = glob.glob(os.path.join(path_unzip, f"dadger.rv{deck['Revision']}"))
                if dadger_file:
                    list_paths.append(dadger_file[0])
                    logger.info(f"Arquivo dadger encontrado e adicionado à lista: {dadger_file[0]}")
                else:
                    logger.warning(f"Nenhum arquivo dadger.rv{deck['Revision']} encontrado em {path_unzip}")
        
        logger.info(f"Download concluído. Total de arquivos dadger encontrados: {len(list_paths)}")
        return list_paths
    
    except Exception as e:
        logger.error(f"Erro durante o download do estudo: {str(e)}", exc_info=True)
        raise

def send_all_dadger_update(id_estudos,path_dadger, logger, logger_send, tag_update):
    logger.info(f"Iniciando envio de atualizações para o caminho: {path_dadger}")
    try:
        if id_estudos is None:
            id_estudos = []
            for rvs in range(1, 9):
                logger.info(" ")
                logger.info("----------------------------------------------------------")
                logger.info(f"Processando estudo de {rvs} rvs")
                id_estudos.append(getStudiesByTag({'page': 1, 'pageSize': 1, 'tags': f"BASE-{rvs}-RV"})['ProspectiveStudies'][0]['Id'])
                logger.debug(f"ID do estudo encontrado para RV{rvs}: {idStudy}")
        logger.info(f"IDs dos estudos encontrados: {id_estudos}")
        for idStudy in id_estudos:
            prospecStudy = getInfoFromStudy(idStudy)
                        
            listOfDecks = prospecStudy['Decks']
            
            logger.info(f"{len(listOfDecks)} decks encontrados para o estudo {idStudy}")
            
            for deck in listOfDecks:
                if (deck['Model'] == 'DECOMP') and (deck['SensibilityInfo'] == 'Original'):
                    pathToFile = path_dadger + '/' + deck['FileName'].split('.')[0] + '/'
                    
                    for file in os.listdir(pathToFile):
                        if file.lower() == (f"dadger.rv{deck['Revision']}") or file.lower() == (f"{logger_send}{deck['Revision']}.log"):
                            sendFileToDeck(idStudy, str(deck['Id']), (pathToFile + file), file)
                            logger.info(f"Arquivo enviado com sucesso: {file} para o estudo {idStudy}, deck {deck['FileName'].split('.')[0]} ")
                        else:
                            logger.debug(f"Arquivo ignorado (não corresponde ao padrão): {file}")
            update_tags(prospecStudy, tag_update, logger)
        logger.info("Envio de todas as atualizações concluído")
    
    except Exception as e:
        logger.error(f"Erro durante o envio de atualizações: {str(e)}", exc_info=True)
        raise

def update_tags(prospecStudy, tag_update, logger):
    logger.info(f"Iniciando update_tags para prospecStudy ID {prospecStudy['Id']} com tag_update: {tag_update}")
    
    tags_list = []
    for tag in prospecStudy['Tags']:
        if tag_update.split('(')[0] not in tag['Text']:
            tags_list.append({'Text': tag['Text'], 'TextColor': tag['TextColor'],'BackgroundColor': tag['BackgroundColor']})
            logger.info(f"Tag mantida: {tag['Text']}")
    
    tags_list.append({'Text':f"{tag_update} {datetime.now().strftime('%d/%m %H:%M')}" ,  'TextColor': '#FFF',  'BackgroundColor': '#44F'})    
    logger.info(f"Tag adicionada: {tag_update}")
    
    logger.info(f"Removendo tags antigas para prospecStudy ID {prospecStudy['Id']}")
    patchInAPI(token, '/api/prospectiveStudies/' + str(prospecStudy['Id']) + '/RemoveTags',  '', prospecStudy['Tags'])
    
    logger.info(f"Adicionando novas tags para prospecStudy ID {prospecStudy['Id']}: {tags_list}")
    patchInAPI(token, '/api/prospectiveStudies/' + str(prospecStudy['Id']) + '/AddTags',  '', tags_list)