
import os
import sys
import numpy as np
import matplotlib
import time
import requests
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from copy import copy, deepcopy
def Analise_CT(path_dadgerRaizen,path_dadgerCCEE, dictSubmPLD,pathSaidaCT):

     for deck in dictSubmPLD.keys():
          pld_max = 0.0
          for subm in dictSubmPLD[deck].keys():
               if dictSubmPLD[deck][subm] > pld_max:
                    pld_max = dictSubmPLD[deck][subm]

          dictSubmPLD[deck]['0'] = pld_max     

     dictCTRaizen = Leitura_blocoCT(path_dadgerRaizen)
     dictCTCCEE   = Leitura_blocoCT(path_dadgerCCEE)
     dictCTRaizen = Abate_Inflex(dictCTRaizen)
     dictCTCCEE   = Abate_Inflex(dictCTCCEE)
     listEstagios = ['1']
     listSubm     = ['0','1','2','3','4']
     listFigsCT   = []
     dictTableCT  = {}

     for estag in listEstagios:
          dictTableCT[estag] = {}
          for subm in listSubm:
               tuplePilhaRaizen         = Ordena_CVU(dictCTRaizen,subm,estag)
               tuplePilhaCCEE           = Ordena_CVU(dictCTCCEE,subm,estag)
               dictTableCT[estag][subm] =[tuplePilhaRaizen,tuplePilhaCCEE]
               fig_ct                   = Grafico_Pilha_Termica(tuplePilhaRaizen,tuplePilhaCCEE, subm,dictSubmPLD)
               listFigsCT.append(fig_ct)

     EscreveLogCT(dictTableCT,pathSaidaCT)
     return listFigsCT

def Grafico_Pilha_Termica(tuplePilhaRaizen,tuplePilhaCCEE,subm,pld):
     strRegiao   = get_Regiao(subm)
     nome_figura = 'termica_'+strRegiao+'.png'
     X1 = []; Y1 = []; PLD1 =[]
     X2 = []; Y2 = []; PLD2 =[]

     soma = 0.0
     for pair in tuplePilhaRaizen:
          cvu = pair[0]
          pot = int(pair[1])
          soma+=pot
          Y1.append(cvu)
          X1.append(soma)
          PLD1.append(pld['Raizen'][subm])

     soma = 0.0
     for pair in tuplePilhaCCEE:
          cvu = pair[0]
          pot = int(pair[1])
          soma+=pot
          Y2.append(cvu)
          X2.append(soma)
          PLD2.append(pld['CCEE'][subm])
     
     marker_style1 = dict(color='red', linestyle='-', marker='o',
                    markersize=2, markerfacecoloralt='red',label='Raizen')
     marker_style2 = dict(color='blue', linestyle='-', marker='o',
                    markersize=2, markerfacecoloralt='blue',label='CCEE')
     rt = 60/25.4
     #plt.figure(figsize =(rt*1.618, rt*1))
     plt.figure(figsize =(16,9))
     plt.plot(X1,Y1,'.-',**marker_style1)
     plt.plot(X2,Y2,'.-',**marker_style2)
     plt.plot(X1,PLD1,'--',color = 'red')
     plt.plot(X2,PLD2,'--',color = 'blue')

     # Fonte
     SMALL_SIZE = 8
     MEDIUM_SIZE = 10
     BIGGER_SIZE = 12
     plt.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
     plt.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
     plt.rc('xtick', labelsize=    6     )    # fontsize of the tick labels
     plt.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
     plt.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize

     max_y = np.max([np.max(Y1), np.max(Y2), np.max(PLD1), np.max(PLD2)])  # Maior valor entre todos os dados
     max_y_rounded = int(np.ceil(max_y / 100) * 100)  # Arredonda para o próximo múltiplo de 100
     plt.yticks(np.arange(0, max_y_rounded + 100, 100))

     # Definir marcas do eixo x de 1000 em 1000
     max_x = np.max([np.max(X1), np.max(X2)])  # Maior valor entre X1 e X2
     max_x_rounded = int(np.ceil(max_x / 500) * 500)  # Arredonda para o próximo múltiplo de 1000
     plt.xticks(np.arange(0, max_x_rounded + 500, 500))  # Define marcas de 1000 em 1000

     PLD_ref  = np.max([PLD1[0],PLD2[0]])
     X_ref    = np.max(X1)/10
     Y_offset = np.max(Y1)/10
     if PLD1[0] > PLD2[0]:
          aux_raizen = PLD1[0] +2*Y_offset
          aux_ccee   = PLD1[0] +Y_offset
     else:     
          aux_raizen = PLD2[0] +Y_offset
          aux_ccee   = PLD2[0] +2*Y_offset

     th1 = plt.text(X_ref, aux_raizen, str(PLD1[0]), fontsize=6,color = 'red')
     th2 = plt.text(X_ref, aux_ccee, str(PLD2[0]), fontsize=6,color = 'blue')
     #plt.ylim(0, 700)
     plt.legend(loc ='upper left',frameon=False)
     plt.xlabel('MW')
     plt.ylabel('CVU [R$/MWm]')
     plt.xticks(rotation=90)
     plt.title('Pilha de termica - '+strRegiao,size = 12)
     plt.grid()     
     plt.tight_layout()
     
     path_figura = os.path.abspath('/WX/WX2TB/Documentos/fontes/PMO/backTest_DC//output/figuras/'+nome_figura)
     plt.savefig(path_figura, bbox_inches ='tight')
     return path_figura
	
def Ordena_CVU(dictCT,regiao,estag):
     listCVU = []
     listPot = []

     for cod in dictCT.keys():
          subm = dictCT[cod]['subm']
          if (subm == regiao) or regiao == '0':
               pot = dictCT[cod][estag]['mw_livre']
               cvu = dictCT[cod][estag]['cvu']
               listPot.append(pot)
               listCVU.append(cvu)
     tuplePilha = sorted(zip(listCVU,listPot))

     tuplePilhaAcum = []
     soma = 0
     for pair in tuplePilha:
          cvu = pair[0]
          pot = pair[1]
          soma+=pot
          tuplePilhaAcum.append((cvu,soma))
     return tuplePilha

def Abate_Inflex(dictCT):

     listCT = deepcopy(list(dictCT.keys()))
     dictCT['Inflex_1'] ={'subm':'1','nome':'INFLEX SE'}
     dictCT['Inflex_2'] ={'subm':'2','nome':'INFLEX S'}
     dictCT['Inflex_3'] ={'subm':'3','nome':'INFLEX NE'}
     dictCT['Inflex_4'] ={'subm':'4','nome':'INFLEX N'}

     for estag in range(1,8):
          for cod in listCT:
               estag_valido = estag
               while str(estag_valido) not in dictCT[cod].keys():
                    estag_valido = estag_valido- 1

               inflex    = dictCT[cod][str(estag_valido)]['inflex']
               disp      = dictCT[cod][str(estag_valido)]['disp']
               cvu       = dictCT[cod][str(estag_valido)]['cvu']
               pot_livre = disp - inflex
               subm      = dictCT[cod]['subm']
               try:
                    dictCT[cod][str(estag)]
                    dictCT['Inflex_'+subm][str(estag)]
               except:
                    dictCT[cod][str(estag)] = {}
                    dictCT['Inflex_'+subm][str(estag)] = {}

               dictCT[cod][str(estag)]['mw_livre'] = round(pot_livre,2)
               dictCT[cod][str(estag)]['cvu'] = round(cvu,2)
               dictCT[cod][str(estag)]['inflex'] = round(inflex,2)
               dictCT[cod][str(estag)]['disp'] = round(disp,2)

               try:    dictCT['Inflex_'+subm][str(estag)]['mw_livre'] += round(inflex,2)
               except: dictCT['Inflex_'+subm][str(estag)]['mw_livre']  = round(inflex,2)
               dictCT['Inflex_'+subm][str(estag)]['cvu'] = 0.0

     return dictCT

def Leitura_blocoCT(pathDadger):
     dictCT ={}
     with open(pathDadger) as f:
        for line in f:
            if (line[0] != '&') and(line[0] != '\n') :
                 bloco = line[:2]
                 if bloco =='CT':
                      listParam = line.split()
                      cod    = listParam[1].strip()
                      subm   = listParam[2].strip()
                      nome   = line[14:25].strip()
                      estag  = line[24:26].strip()
                      inflex = []; disp = []; cvu = []

                      inflex.append(float(line[29:34].strip()))
                      disp.append(float(line[34:39].strip()))
                      cvu.append(float(line[39:49].strip()))
                      inflex.append(float(line[49:54].strip()))
                      disp.append(float(line[54:59].strip()))
                      cvu.append(float(line[59:69].strip()))
                      inflex.append(float(line[69:74].strip()))
                      disp.append(float(line[74:79].strip()))
                      cvu.append(float(line[79:89].strip()))

                      try:
                           dictCT[cod]
                      except:
                           dictCT[cod] = {}
                      dictCT[cod]['subm'] = subm
                      dictCT[cod]['nome'] = nome
                      dictCT[cod][estag] ={}
                      dictCT[cod][estag]['inflex'] = np.average(inflex)
                      dictCT[cod][estag]['disp'] = np.average(disp)
                      dictCT[cod][estag]['cvu'] = np.average(cvu)
     return dictCT


def EscreveLogCT(dictTableCT, path):
     faixa = 10 # MW em MW considerado na analise
     dictTable = ComparaSerieCT(dictTableCT,faixa)     
     listSubm  = ['0','1','2','3','4']
     listEstag = ['1']
     listDeck  = ['delta','CCEE','Raizen']     
     out       = open(path, 'w')
     
     for deck in listDeck:
          for estag in listEstag:
               for subm in listSubm:                    
                    if subm =='1': nome = 'SE'
                    if subm =='2': nome = 'S'
                    if subm =='3': nome = 'NE'
                    if subm =='4': nome = 'N'
                    if subm =='0': nome = 'SIN'
                   
                    listCVU_POT = dictTable[estag][subm][deck]
                    for cvu,pot in listCVU_POT:
                         out.write('%s;' % deck)
                         out.write('%s;' % estag)
                         out.write('%s;' % nome) 
                         out.write('%s;' % cvu)
                         out.write('%s;' % pot)
                         out.write('\n') 
               time.sleep(0.0005)

     out.close()
     print( 'Escrito ' + path + '  com sucesso')
     return path


def ComparaSerieCT(dictTableCT,faixa):

     listSubm  = ['0','1','2','3','4']     
     dictTable = {}
     listEstag = ['1']
     for estag in listEstag:
          dictTable[estag] = {}
          
          for subm in listSubm:
               dictTable[estag][subm] ={}
               tupleCTRaizen = dictTableCT[estag][subm][0]
               tupleCTCCEE = dictTableCT[estag][subm][1]
               i = 0
               # Raizen
               listRaizen = []
               soma = 0.0
               for pair in tupleCTRaizen:
                    cvu = pair[0]
                    pot = int(pair[1])
                    soma+=pot
                    listRaizen.append([cvu,soma])

               maxCVU = cvu
               # CCEE
               listCCEE = []
               soma = 0.0
               for pair in tupleCTCCEE:
                    cvu = pair[0]
                    pot = pair[1]
                    soma+=pot
                    listCCEE.append((cvu,soma))
               
               maxCVU = np.max([cvu, maxCVU])
               
               listRaizen_faixa = []
               listCCEE_faixa = []
               listDelta_faixa = []
               for cvu in range(0,int(maxCVU) ,faixa):                    
                    for i in range(len(listRaizen)):
                         if  cvu <= listRaizen[i][0]:
                              potRaizen =  listRaizen[i][1]
                              listRaizen_faixa.append((cvu,potRaizen))
                              break
         
                    for i in range(len(listCCEE)):
                         if  cvu <= listCCEE[i][0]:
                              potCCEE =  listCCEE[i][1]
                              listCCEE_faixa.append((cvu,potCCEE))
                              break
                    
                    listDelta_faixa.append((cvu,potCCEE - potRaizen))
               
               dictTable[estag][subm]['Raizen'] = listRaizen_faixa
               dictTable[estag][subm]['CCEE']   = listCCEE_faixa
               dictTable[estag][subm]['delta']  = listDelta_faixa     
     return dictTable

def get_Regiao(subm):
     if   subm == '1': strRegiao = 'Sudeste'
     elif subm == '2': strRegiao = 'Sul'
     elif subm == '3': strRegiao = 'Nordeste'
     elif subm == '4': strRegiao = 'Norte'
     elif subm == '0': strRegiao = 'SIN'
     return strRegiao



