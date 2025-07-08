import zipfile
import os
import pandas as pd 
from datetime import date
import numpy as np
from datetime import date
import csv
import shutil
import openpyxl
import openpyxl as op

def ExtrairPasta(path_src, pastaZip):
    list_arquivos = []
    for arquivo in os.listdir(path_src):
        if not '.zip' in arquivo:
            try: 
                shutil.rmtree(path_src + '/' +arquivo)
            except:
                print('Não foi possivel deletar o diretório: '+ path_src + '/' +arquivo)
                print('Favor deletar manualmente o diretório: '+ path_src + '/' +arquivo)

    for arquivo in [pastaZip]:

        if '.zip' in arquivo:  

            print('Iniciando leitura dos arquivos do estudo: ' + arquivo)
            nome_arq = arquivo[0:len(arquivo)-4]
            list_arquivos.append(nome_arq)
            
            try: os.mkdir(path_src + '/' + nome_arq)
            except: 
                print(nome_arq + ' já existente na pasta ' + path_src)
                pass        
            
            with zipfile.ZipFile(path_src + '/' + arquivo, 'r') as deck_compactado:
                lista_arquivos = deck_compactado.namelist()
                for arquivoInZip in lista_arquivos:
                    if '.csv' in arquivoInZip and not 'DC' in arquivoInZip: 
                        try: deck_compactado.extract(arquivoInZip,path_src + '/' + nome_arq)
                        except: pass
                    
                    if '.zip' in arquivoInZip and not 'NW' in arquivoInZip:
                        try: deck_compactado.extract(arquivoInZip,path_src + '/' + nome_arq)
                        except: pass
                        with zipfile.ZipFile(path_src + '/' + nome_arq + '/' + arquivoInZip, 'r') as deck_decomp:
                            lista_arquivos = deck_decomp.namelist()
                            for arquivoDC in lista_arquivos:
                                if 'dadger.rv' in arquivoDC and not '.0' in arquivoDC:                                    
                                    deck_decomp.extract(arquivoDC ,path_src + '/' + nome_arq)
                                    os.rename( path_src + '/' + nome_arq + '/' + arquivoDC ,
                                                   path_src + '/' + nome_arq + '/' + arquivoInZip[0:len(arquivoInZip)-4] + '_' + arquivoDC)
        
    return [list_arquivos, arquivo]

def readDadosDadger(path_src, data, subsistema):
    geracaoAnde = []
    ghPequenas = []
    for arquivo in os.listdir(path_src):
        if 'dadger' in arquivo:
            if date(int(arquivo[2:6]), int(arquivo[6:8]), 1).strftime("%d_%m_20%y") == data:
                dadger = []
                with open(path_src+ '\\' + arquivo) as file:
                    for linha in file:
                        dadger.append(linha)
                patamar = []
                cargaAnde = []
                ghPq = []
                readRI = True
                readGL = True
                readPQ = True
                for line in dadger:
                    if line[0:2] == "RI" and readRI:
                        readRI = False
                        cargaAnde = [float(line.split()[8]), float(line.split()[13]), float(line.split()[18])]

                    if line[0:2] == "DP" and readGL:
                        readGL = False
                        patamar = [int(float(line[30:39])), int(float(line[50:59])), int(float(line[70:79]))]

                    if line[0:2] == "PQ" and readPQ:
                        if  line.split()[1] == subsistema:
                            readPQ = False
                            ghPq = [float(line[24:29]), float(line[29:34]), float(line[34:39])]

                patamar = [patamar[0]/np.sum(patamar), patamar[1]/np.sum(patamar), patamar[2]/np.sum(patamar)]

                geracaoAnde.append(np.sum(np.array(cargaAnde) * np.array(patamar)))

                ghPequenas.append(np.sum(np.array(ghPq) * np.array(patamar)))
    
    return [round(np.mean(geracaoAnde),2), round(np.mean(ghPequenas),2)]


def readDadosMultiPrevs(path_src, dados, list_arq, list_sub, list_sens, PldMin, PLdMax):
    for se in list_sens:
        for pasta in list_arq:  
            pathDado = path_src +'/' + pasta
               
            #LEITURA DA EARM               
            readCsvProspec(dados,se, list_sub, list_sens, pathDado, 'compila_ea_inicial.csv' , 'earm', PldMin,PLdMax, False )

            # LEITURA DA ENA
            readCsvProspec(dados,se, list_sub, list_sens, pathDado, 'compila_ena_percentual_mlt.csv' , 'ena', PldMin,PLdMax, False )
            
            # LEITURA DA ENA MÊS
            #readCsvProspec(dados,se, list_sub, list_sens, pathDado, 'compila_ena_mensal_percentual.csv' , 'enaMes', PldMin,PLdMax, False )

            # LEITURA DA CMO 
            readCsvProspec(dados,se, list_sub, list_sens, pathDado, 'compila_pld.csv' , 'pld', PldMin,PLdMax, False ) 
                        
            #LEITURA DA GH    
            readCsvProspec(dados,se, list_sub, list_sens, pathDado, 'compila_gh.csv' , 'gh', PldMin,PLdMax, False ) 

            #LEITURA DA GT    
            readCsvProspec(dados,se, list_sub, list_sens, pathDado, 'compila_gt.csv' , 'gt', PldMin,PLdMax, False ) 

def readCsvProspec(dados, se, list_sub,list_sens, pathDado, arquivo, tipoDado, PldMin,PLdMax, readAnde ):
    dados_arq = pd.read_csv(pathDado + '/' + arquivo,  sep = ';', header =0)
    for ind, sub in enumerate(list_sub):
        if arquivo == 'compila_pld.csv':
            sub = sub + '_Medio'
            print(arquivo, sub)
        print(list_sub)
        for i in range (len(dados_arq[sub])):
            if se == dados_arq['Sensibilidade'][i]:
                if 'DC' in dados_arq['Deck'][i]:
                    rv = 'RV' + str(int(dados_arq['Deck'][i][len(dados_arq['Deck'][i])-4])-1)
                    data = date(int(dados_arq['Deck'][i][2:6]), int(dados_arq['Deck'][i][6:8]), 1).strftime("%d_%m_20%y")
                    
                    #print(data, sub)
                    #print(dados)
                    setDict(data, dados, list_sub[ind], se, list_sens, rv)
                    
                    if tipoDado == 'pld':
                        dados[list_sub[ind]][se][data][rv][tipoDado] = min(max(round(dados_arq[sub][i],1),PldMin),PLdMax)      
               
                    else:
                        dados[sub][se][data][rv][tipoDado] = round(dados_arq[sub][i],1) 

                    if readAnde:
                        dados[sub][se][data][rv]['ande'] =  readDadosDadger(pathDado, data, sub)[0]    


def setDict(data, dados, sub, se,list_sens, rv):
    if not data in dados[sub][se]: 
        for sens in list_sens:                   
            dados[sub][sens][data] = dict()
    for sens in list_sens:
        if not rv in dados[sub][sens][data]:
            dados[sub][sens][data][rv] = dict()
            dados[sub][sens][data][rv]['earm'] = 'NULL'
            dados[sub][sens][data][rv]['ena'] = 'NULL'
            dados[sub][sens][data][rv]['pld'] = 'NULL'
            dados[sub][sens][data][rv]['enaMes'] = 'NULL'
            dados[sub][sens][data][rv]['ande'] = 'NULL'
            dados[sub][sens][data][rv]['gh'] = '0'
            dados[sub][sens][data][rv]['gt'] = '0'


def createDict(list_sens, list_sub):
    dadosDict = dict()
    for sub in list_sub:
        dadosDict[sub] = dict()
        for sens in list_sens:
           dadosDict[sub][sens] = dict()
    return dadosDict  

def writeCsv(dados,nomeEstudo, path_src):

    with open(path_src , 'a', newline = '') as csvfile:        
        dataWriter = csv.writer(csvfile, delimiter = ';', quoting = csv.QUOTE_MINIMAL)           

        today = date.today()  
        
        for data in dados['NORDESTE']['Original']:
            for rv in dados['NORDESTE']['Original'][data]:
                line = ['edp', today.strftime('%Y-%m-%d'), data[6:10], data[3:5], rv,
                dados['SUDESTE' ]['Original'][data][rv]['pld'],
                dados['SUL'     ]['Original'][data][rv]['pld'],
                dados['NORDESTE']['Original'][data][rv]['pld'],
                dados['NORTE'   ]['Original'][data][rv]['pld'], 
                dados['SUDESTE' ]['Original'][data][rv]['earm'],
                dados['SUL'     ]['Original'][data][rv]['earm'],
                dados['NORDESTE']['Original'][data][rv]['earm'],
                dados['NORTE'   ]['Original'][data][rv]['earm'], 
                dados['SUDESTE' ]['Original'][data][rv]['ena'],
                dados['SUL'     ]['Original'][data][rv]['ena'],
                dados['NORDESTE']['Original'][data][rv]['ena'],
                dados['NORTE'   ]['Original'][data][rv]['ena'],
                dados['SUDESTE' ]['Original'][data][rv]['enaMes'],
                dados['SUL'     ]['Original'][data][rv]['enaMes'],
                dados['NORDESTE']['Original'][data][rv]['enaMes'],
                dados['NORTE'   ]['Original'][data][rv]['enaMes'],  
                dados['SUDESTE' ]['seco'][data][rv]['pld'],
                dados['SUL'     ]['seco'][data][rv]['pld'],
                dados['NORDESTE']['seco'][data][rv]['pld'],
                dados['NORTE'   ]['seco'][data][rv]['pld'], 
                dados['SUDESTE' ]['seco'][data][rv]['earm'],
                dados['SUL'     ]['seco'][data][rv]['earm'],
                dados['NORDESTE']['seco'][data][rv]['earm'],
                dados['NORTE'   ]['seco'][data][rv]['earm'], 
                dados['SUDESTE' ]['seco'][data][rv]['ena'],
                dados['SUL'     ]['seco'][data][rv]['ena'],
                dados['NORDESTE']['seco'][data][rv]['ena'],
                dados['NORTE'   ]['seco'][data][rv]['ena'],
                dados['SUDESTE' ]['seco'][data][rv]['enaMes'],
                dados['SUL'     ]['seco'][data][rv]['enaMes'],
                dados['NORDESTE']['seco'][data][rv]['enaMes'],
                dados['NORTE'   ]['seco'][data][rv]['enaMes'],  
                dados['SUDESTE' ]['moia'][data][rv]['pld'],
                dados['SUL'     ]['moia'][data][rv]['pld'],
                dados['NORDESTE']['moia'][data][rv]['pld'],
                dados['NORTE'   ]['moia'][data][rv]['pld'], 
                dados['SUDESTE' ]['moia'][data][rv]['earm'],
                dados['SUL'     ]['moia'][data][rv]['earm'],
                dados['NORDESTE']['moia'][data][rv]['earm'],
                dados['NORTE'   ]['moia'][data][rv]['earm'], 
                dados['SUDESTE' ]['moia'][data][rv]['ena'],
                dados['SUL'     ]['moia'][data][rv]['ena'],
                dados['NORDESTE']['moia'][data][rv]['ena'],
                dados['NORTE'   ]['moia'][data][rv]['ena'],
                dados['SUDESTE' ]['moia'][data][rv]['enaMes'],
                dados['SUL'     ]['moia'][data][rv]['enaMes'],
                dados['NORDESTE']['moia'][data][rv]['enaMes'],
                dados['NORTE'   ]['moia'][data][rv]['enaMes'],
                int(dados['SUDESTE']['Original'][data][rv]['gh']+
                dados['SUL'     ]['Original'][data][rv]['gh']+
                dados['NORDESTE']['Original'][data][rv]['gh']+
                dados['NORTE'   ]['Original'][data][rv]['gh']),
                int(dados['SUDESTE']['Original'][data][rv]['gt']+
                dados['SUL'     ]['Original'][data][rv]['gt']+
                dados['NORDESTE']['Original'][data][rv]['gt']+
                dados['NORTE'   ]['Original'][data][rv]['gt']), 
                dados['SUDESTE' ]['Original'][data][rv]['ande'], 
                'Estudo utilizado: ' + nomeEstudo ]
                dataWriter.writerow(line)


def main(prospecStudyId):

    path_src = '/datadrive2/Produtos/API_Prospec/DownloadResults'

    list_arq, nomeEstudo = ExtrairPasta(path_src, 'compilation.zip')
    list_sub = ['SUDESTE', 'SUL', 'NORDESTE','NORTE']
    dados_arq = pd.read_csv(path_src +'/' + list_arq[0] + '/compila_pld.csv',sep = ';', header =0)
    PldMin = dados_arq['PLD_Min'][0]
    PLdMax = dados_arq['PLD_Max'][0]
    list_sens = ['moia', 'Original', 'seco']
    del dados_arq
     
    dados = createDict(list_sens, list_sub)
    readDadosMultiPrevs(path_src, dados, list_arq, list_sub, list_sens, PldMin, PLdMax)

    writeCsv(dados, str(prospecStudyId) + '_'+ nomeEstudo, '/datadrive2/Produtos/relatorio_precos/baseProspec.csv')

    print('Leitura Finalizada')

if __name__ == '__main__':
    prospecStudyId = 0
    main(prospecStudyId)
