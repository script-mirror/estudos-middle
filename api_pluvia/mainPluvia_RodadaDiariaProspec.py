#API
from functionsPluviaAPI import *
from requestsPluviaAPI import authenticatePluvia
from datetime import datetime, timedelta
import pathlib
import zipfile
import copy
import re
import sys
import time
import os
import pdb
import pandas as pd
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.abspath(os.path.expanduser("~")),'.env'))

usuario_pluvia = os.getenv('usuario_pluvia')
senha_pluvia = os.getenv('senha_pluvia')


def main(parametros):    

    
    print(''); print('')
    print ('--------------------------------------------------------------------------------#')
    print('#-API do Pluvia Iniciado: ' + str(datetime.now())[:19])
    print('Usuário: gilseu.wx')

    path = pathlib.Path(os.getcwd())

    folders = run(usuario_pluvia, senha_pluvia, path, parametros)
    time.sleep(20)
    listPrevs = copiaPrevsProspec(path, folders, parametros)
    
    print(''); print('')
    print ('#-API do Pluvia Terminado em: '  +  str(datetime.now())[:19])
    print ('--------------------------------------------------------------------------------#')

    return listPrevs


# -----------------------------------------------------------------------------
# Casos a serem executados
# -----------------------------------------------------------------------------
def run(username,password, path, parametros):

    # -----------------------------------------------------------------------------
    # Criação                
    # -----------------------------------------------------------------------------
    authenticatePluvia(username, password)
    data_atual = datetime.now()
    data                     = parametros['data']
    #data                     = datetime.strptime('26/08/2024', '%d/%m/%Y')
    forecastDate             = data.strftime('%d/%m/%Y')
    precipitationDataSources = parametros['mapas']
    forecastModels           = ['SMAP']
    bias                     = '' 
    preliminary              = 'Definitiva' 
    years                    = [data.year]
    members                  = parametros['membros']
    pathResult               = path.joinpath('/WX2TB/Documentos/fontes/PMO/API_Pluvia/Resultados')
    #pathResult               = path.joinpath('')
    pathForecastDay          = pathResult.joinpath(data.strftime('%Y-%m-%d'))    
    nTentarivas              = 10
    pathFolders              = []
    cenario                  = parametros['cenario']
    modes                    = []
    # pdb.set_trace()

    if parametros["preliminar"] == 1:
        parametros["preliminar"] = 'Preliminar'
        preliminary = 'Preliminar'

    if parametros["preliminar"] == 0:
        parametros["preliminar"] = 'Definitiva'
        preliminary = 'Definitiva'


    if parametros['prevs'] == 'PREVS_PLUVIA_PREC_ZERO':
        precipitationDataSources = ['Prec. Zero']
        members                  = ['NULO']

    if parametros['prevs'] == 'PREVS_PLUVIA_USUARIO':
        precipitationDataSources = ['Usuário']
        members                  = ['NULO']
        preliminary = 'Preliminar'
        
    if parametros['prevs'] == 'PREVS_PLUVIA_EC_EXT':
        nTentarivas = 12
        precipitationDataSources = ['ECMWF_ENS_EXT', 'ONS']
        members = ['ENSEMBLE', 'NULO']
        for valor in range(100):
            precipitationDataSources.append('ECMWF_ENS_EXT')
            members.append(str(valor).zfill(2))        

    if parametros['prevs'] == 'PREVS_PLUVIA_EC_EXT':
        nTentarivas = 12
        precipitationDataSources = ['ECMWF_ENS_EXT']
        if parametros['member'] != 'ENSEMBLE':
            members = [parametros['member']]

    
    if parametros['prevs'] == 'PREVS_PLUVIA_GEFS_EXT':
        nTentarivas = 12
        precipitationDataSources = ['GEFS_EXT']
        if parametros['member'] != 'ENSEMBLE':
            members = [parametros['member']]


    if parametros['prevs'] == 'PREVS_ONS_GRUPOS':
        nTentarivas = 25
        countIterations = 0
        precipitationDataSources = ['ONS_Pluvia'] 
        members = [parametros['member']]

 
    if parametros['prevs'] == 'PREVS_PLUVIA_2_RV':
        nTentarivas = 15
        if parametros['preliminar'] == 'Preliminar':
            #precipitationDataSources = ['ONS_ETAd_1_Pluvia']
            precipitationDataSources = ['ONS_Pluvia']   
        else:
            precipitationDataSources = ['ONS']
            
        if data.weekday() == 6 or data.weekday() == 5:
            parametros['preliminar'] = 'Preliminar'
            precipitationDataSources = ['ONS_Pluvia'] 


        members = ['NULO']
        nTentarivas = 15


    if parametros['prevs'] == 'PREVS_PLUVIA_APR':
        nTentarivas = 25
        precipitationDataSources = ['ONS_Pluvia']  
        members = ['AgrupadoPrecipitacao']
        parametros["preliminar"] = 'Preliminar'
        preliminary = 'Preliminar'

    print('')
    parametros["preliminar"] = 'Preliminar'
    
    print('')
    print('Parametros: ',parametros) 
    print('')

    if not pathResult.exists():
        try:
            pathlib.Path.mkdir(pathResult)
        except:
            print(pathResult)
            print('Falha em criar pasta de resultados')
            time.sleep(5)
            try:
                pathlib.Path.mkdir(pathResult)
            except:
                print('Nova falha em criar pasta de resultados')
                return(5)

    if not pathForecastDay.exists():
            try:
                pathlib.Path.mkdir(pathForecastDay)
            except:
                print('Falha em criar a pasta para salvar as previsões do dia')
                time.sleep(1)
                try:
                    pathlib.Path.mkdir(pathForecastDay)
                except:
                    print('Falha em criar a pasta para salvar as previsões do dia')
                    return(1)

    countIterations = 0

    print(precipitationDataSources)
    while len(precipitationDataSources) > 0 and countIterations < nTentarivas:

        precipitationAux = []
        authenticatePluvia(username, password)

        for i in range(len(precipitationDataSources)): 

            member = [members[i]]
            precipitationDataSource = precipitationDataSources[i]
            idPrecipitationDataSource = []
            idForecast = []  
            idPrecipitationDataSource.append(getIdOfPrecipitationDataSource(precipitationDataSource))

            for forecastModel in forecastModels:    
                idForecast.append(getIdOfForecastModel(forecastModel))
            idModo = []
            for mode in modes:    
                idModo.append(getIdOfModes(mode))

            forecasts_in = getForecasts(forecastDate, idPrecipitationDataSource, idForecast, bias, preliminary, idModo, years, member)
            forecast = []

            if parametros['prevs'] == 'PREVS_PLUVIA_USUARIO':
                for forecast_aux in forecasts_in:
                    #try:
                    if int(forecast_aux['nome'].split('__')[1])==cenario:
                        print((forecast_aux['nome']))
                        forecast = [forecast_aux]
                    #except:
                       #pass
                forecasts_in = forecast 
            else:

                forecast = forecasts_in 
            
            if len(forecast) == 0 and parametros['preliminar'] == 'Preliminar' and parametros['prevs'] != 'PREVS_PLUVIA_USUARIO' :   
                preliminary = 'Preliminar'                 
                idModo = []
                for mode in modes:    
                    idModo.append(getIdOfModes(mode))

                forecast = getForecasts(forecastDate, idPrecipitationDataSource, idForecast, bias, preliminary, idModo, years, member)

            if len(forecast) > 0:
                if 'Prevs' not in str(forecast[0]['resultados']):
                    forecast = []

            if len(forecast) > 0:
                time.sleep(10)

                for dado in forecasts_in[0]['resultados']:
                    if dado['nome'] == 'Prevs':
                        downloadForecast(dado['id'], pathForecastDay, forecast[0]['nome'] + '-' + forecast[0]['membro'] + '-Prevs.zip')
                        pathFolders.append(forecast[0]['nome'] + '-' + forecast[0]['membro'] + '-Prevs.zip')
                    
                        if preliminary == 'Preliminar':
                            print('Download mapa', precipitationDataSource, 'preliminar membro ' + forecast[0]['membro']+ ' com sucesso em: ' + str(datetime.now())[:19])
                        else:
                            print('Download mapa', precipitationDataSource, 'definitivo membro ' + forecast[0]['membro']+ ' com sucesso em: ' + str(datetime.now())[:19])
            else:
                precipitationAux.append(precipitationDataSource)

        precipitationDataSources = copy.deepcopy(precipitationAux) 

        countIterations = countIterations + 1
        if len(precipitationDataSources) > 0 and countIterations < nTentarivas:
            try:
                print('Aguardando disponibilização dos prevs: ', precipitationDataSource, members, preliminary, str(datetime.now())[:19])
            except:
                pass
            if countIterations == 1: 
                time.sleep(600)
            else:    
                time.sleep(600)
            del idPrecipitationDataSource
            del forecast
            del member
            del precipitationDataSource
            del precipitationAux
            

    return pathFolders

def copiaPrevsProspec(path, folders, parametros ):
    data = parametros['data']
    
    listPrevs = [] 
    pathOutput      = '/WX2TB/Documentos/fontes/PMO/API_Prospec/GerarDecks/PREVS/Pld1Click/ALL/'
    pathResult      = path.joinpath('/WX/WX2TB/Documentos/fontes/PMO/API_Pluvia/Resultados')
    #pathOutput      = 'C:/Dev/API_Prospec/GerarDecks/PREVS/Pld1Click/ALL/'
    pathForecastDay = pathResult.joinpath(data.strftime('20%y-%m-%d'))


    for pasta in os.listdir(pathOutput):
        pathOutput2 = pathOutput + '/' + pasta
        for arquivos in os.listdir(pathOutput2): 
            try: os.remove(pathOutput2 + '/' + arquivos) 
            except: (print('Não foi possivel excluir o aqruivo: ' + pathOutput2 + '/' + arquivos))
        try: os.rmdir(pathOutput2)
        except: (print('Não foi possivel excluir a pasta: ' + pathOutput2))

    for mes in range(int(data.month),int(data.month + 3)):
        if mes < 13:
            pathOutput2 = pathOutput + str(mes)
        else:
            pathOutput2 = pathOutput + str(mes-12)

        if os.path.exists (pathOutput2) == False: os.mkdir (pathOutput2)
        for arquivos in os.listdir(pathOutput2): 
            try: os.remove(pathOutput2 + '/' + arquivos) 
            except: (print('Não foi possivel excluir o aqruivo: ' + pathOutput2 + '/' + arquivos))

    for folder in folders:
        try:
            ExtractFolder(pathForecastDay, pathForecastDay, folder)
            
            pathInput = os.path.join(pathForecastDay ,folder[0:len(folder)-4])
            listaPrevs = os.listdir(pathInput)
            #print(listaPrevs)
            #del listaPrevs[0]
            #print(listaPrevs)

            listaAux = [file for file in listaPrevs if not file.lower().endswith('.rv6')]
            #print(listaAux)
            #sys.exit()
            mumeroRvs = len(listaAux)
            for files in os.listdir(pathInput):
                prevsVE = False
                rv = files[-4:]
                nomePrevs = files.split('-')[3]
                if 'AGRUPADOPRECIPITACAO' in files:
                    nomePrevs = nomePrevs + '-AGRUPADOPRECIPITACAO'

                if len(files.split('-')[4]) == 2:
                    nomePrevs = nomePrevs + '-' + files.split('-')[4]
                    
                if 'PRELIMINAR' in files:
                    nomePrevs = nomePrevs + '-PREL'

                mes = str(int((files[4:6])))
                print(nomePrevs)

                if 'usuario' in files.lower():
                    nomePrevs = files.split('__')[len(files.split('__'))-1][:-12]

                if  parametros['prevs'] == 'PREVS_PLUVIA_EC_EXT': nomePrevs = files[18:-21]
                if 'ONS' in files and parametros['prevs'] == 'PREVS_PLUVIA_EC_EXT': prevsVE = True
                    

                if os.path.exists (os.path.join(pathOutput + mes ,'prevs' + rv)) == False or prevsVE == True:
                    os.rename(os.path.join(pathInput ,files) , os.path.join(pathOutput + mes ,'prevs' + rv))

                    if 'PLUVIA' in nomePrevs.upper():
                        listPrevs.append(nomePrevs.upper())
                    else:
                        listPrevs.append(nomePrevs.upper() +  '_PLUVIA')

                    print(files + ' impresso em ' + os.path.join(pathOutput + mes, 'prevs' +  rv))

                else:
                    os.rename(os.path.join(pathInput ,files) , os.path.join(pathOutput + mes ,'prevs-' + nomePrevs +'_pluvia' +  rv))
                    print(files + ' impresso em ' + os.path.join(pathOutput + mes, 'prevs-' + nomePrevs +'_pluvia' +  rv))
        except:
            pass



    if len(listPrevs) == 0:
        print('Pluvia não encontrou nenhum mapa, por favor conferir processo!')
        if parametros['prevs'] != 'PREVS_PLUVIA_RAIZEN' and parametros['prevs'] != 'PREVS_PLUVIA_2_RV':
            sys.exit()
    
    return listPrevs[0],mumeroRvs

def ExtractFolder(pathIn, pathOut, arquivo):
 
    nome_arq = arquivo[0:len(arquivo)-4]
    
    if os.path.exists (os.path.join(pathOut ,nome_arq)) == False: os.mkdir (os.path.join(pathOut ,nome_arq))
   
    with zipfile.ZipFile(os.path.join(pathOut ,arquivo), 'r') as pastaCompactada:
        for arquivoInZip in pastaCompactada.namelist():
            pastaCompactada.extract(arquivoInZip, os.path.join(pathOut ,nome_arq))

if __name__ == '__main__': 
    parametros =  dict()
    parametros['prevs'] = 'PREVS_PLUVIA_2_RV'
    parametros['data'] = datetime.strptime('11/04/2023', '%d/%m/%Y')
    parametros['cenario'] = ''
    parametros['mapas'] = 'ONS'
    parametros['membros'] = ['NULO']
    parametros['preliminar']  = 1
    main(parametros)