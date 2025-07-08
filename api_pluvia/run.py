#API
import time
from functionsPluviaAPI import *
from requestsPluviaAPI import authenticatePluvia
import datetime
import pathlib
import os 
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.abspath(os.path.expanduser("~")),'.env'))

usuario_pluvia = os.getenv('usuario_pluvia')
senha_pluvia = os.getenv('senha_pluvia')

# -----------------------------------------------------------------------------
# Casos a serem executados
# -----------------------------------------------------------------------------
def run_test():
    print('*********************************************')
    print('Execução iniciada em: ' + str(datetime.datetime.now())[:19])
    print('Usuário: ' + username)
    # -----------------------------------------------------------------------------
    # Criação                
    # -----------------------------------------------------------------------------
    authenticatePluvia(username, password)

    forecastDate = '11/04/2023' #formato dd/MM/yyyy
    
    "Possible Values: VNA, Prevs, Dadvaz, PMedia, ENA, ENAPREVS, STR"
    list_of_files = ['Prevs']
    
    "Possible values: MERGE,ETA,GEFS,CFS,Usuário,Prec. Zero,ECMWF_ENS,ECMWF_ENS_EXT,ONS,ONS_Pluvia,ONS_ETAd_1_Pluvia,GEFS_EXT"
    precipitationDataSources = ['ONS']
    
    forecastModels = ['SMAP'] # IA / SMAP                   (vazio baixa todos)
    bias = '' # Original / ComRemocaoVies             (vazio baixa todos)Gilseu
    preliminary = '' # Preliminar / Definitiva        (vazio baixa todos)
    members = [] # ENSEMBLE / 01 / 02 / P50 / P90 etc (vazio baixa todos)
    
    years = [2023] #Lista de Anos Int (vazio baixa todos) - variável obrigatória e exclusiva para o mapa MERGE
    modes = [] #Diário / Mensal (vazio baixa todos) - variável exclusiva para o mapa MERGE
    
    pathResult = path.joinpath('Resultados')

    pathForecastDay = pathResult.joinpath(forecastDate[6:] + '-' + forecastDate[3:5] + '-' + forecastDate[:2])
    
    if not pathResult.exists():
        try:
            pathlib.Path.mkdir(pathResult)
        except:
            print('Falha em criar pasta de resultados')
            time.sleep(1)
            try:
                pathlib.Path.mkdir(pathResult)
            except:
                print('Nova falha em criar pasta de resultados')
                return(1)

    idPrecipitationDataSource = []
    idForecast = []
    idModo = []
    
    for precipitationDataSource in precipitationDataSources:    
        idPrecipitationDataSource.append(getIdOfPrecipitationDataSource(precipitationDataSource))

    for forecastModel in forecastModels:    
        idForecast.append(getIdOfForecastModel(forecastModel))
    
    for mode in modes:    
        idModo.append(getIdOfModes(mode))
    
    forecasts = getForecasts(forecastDate, idPrecipitationDataSource, idForecast, bias, preliminary, idModo, years, members)
    
    for forecast in forecasts:
        
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
        
        list_of_tuples = [(d['nome'], d['id']) for d in forecast['resultados']]
        
        for tup in list_of_tuples:
            
            if not tup[0] in list_of_files:
                continue
            
            downloadForecast(tup[1], pathForecastDay, forecast['nome'] + [' - ' + forecast['membro'] if forecast['membro'] != '' else ''][0] + ' - ' + tup[0] + '.zip')
            
    print('Ok')
            
if __name__ == "__main__":
    
    path = pathlib.Path(__file__).parent.resolve()

    username = usuario_pluvia
    password = senha_pluvia

    statusRun = run_test()
    
    if not statusRun:
        print('*********************************************')
        print('Execução finalizada')
    else:
        print('*********************************************')
        print('Falha na execução')
