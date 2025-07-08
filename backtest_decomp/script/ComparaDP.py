
import os
import sys
import numpy as np
import time
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def Analise_DP(path_dadgerRaizen,path_dadgerCCEE, mes,pathSaidaDP):
     rv             = path_dadgerRaizen[-1]
     dictDP_Raizen  = Leitura_blocoDP(path_dadgerRaizen)
     dictDP_Oficial = Leitura_blocoDP(path_dadgerCCEE)
     dictGraph      = Compila_ComparadorDP(dictDP_Raizen,dictDP_Oficial)

     # Comparador
     listFigsCT = []     
     nome_mes   = Nome_Mes(mes)
     list_subm  = ['0','1','2','3','4']
     for subm in list_subm:
          strRegiao   =  get_Regiao(subm)
          nome_figura = 'carga_'+strRegiao+'.png'
          Y1          = dictGraph['Raizen'][subm]['MWmed'] 
          Y1          = [Y1[0]]+Y1
          Y2          = dictGraph['CCEE'][subm]['MWmed']
          Y2          = [Y2[0]]+Y2 
          X           = np.linspace(0,len(Y1)-1,num=len(Y1))
          X_ref       = np.linspace(0.5,len(Y1)+0.5-1,num=len(Y1))
          X_label     = []

          for i in range(len(X)-1):
               rv_atual = int(rv)+i
               X_label.append('RV'+str(rv_atual))
          X_label[-1] = nome_mes
          rt = 60/25.4
          fig, ax = plt.subplots(figsize =(rt*1.618, rt*1))

          plt.step(X, np.array(Y1),where = 'pre', label='Raizen',color = 'red')
          plt.plot(X, np.array(Y1), '.',color = 'red')
          plt.step(X,np.array(Y2), where='pre', label='CCEE',color = 'blue')
          plt.plot(X,np.array(Y2), '.',color = 'blue')

          #########
          ax.xaxis.set_major_locator(ticker.MultipleLocator())
          ax.xaxis.set_major_formatter(ticker.NullFormatter())
          ax.xaxis.set_minor_locator(ticker.FixedLocator(X_ref))
          ax.xaxis.set_minor_formatter(ticker.FixedFormatter(X_label))
          for tick in ax.xaxis.get_minor_ticks():
               tick.tick1line.set_markersize(0)
               tick.tick2line.set_markersize(0)
               tick.label1.set_horizontalalignment('center')

          plt.ylabel('Carga MWm')
          top = np.max(Y1+Y2)*1.1
          bottom = np.min(Y1+Y2)*0.8
          TopBottom = top - bottom
          
          for i in range(1,len(X)):
               xi = X_ref[i-1] 
               # Raizen > CCEE        
               if Y1[i] > Y2[i]:
                    # Raizen
                    ax.annotate(str(int(Y1[i])),xy=(xi-0.3,Y1[i]+TopBottom*0.05),color = 'red',fontsize=8)
                    # CCEE
                    ax.annotate(str(int(Y2[i])),xy=(xi-0.3,Y2[i]-TopBottom*0.05),color = 'blue',fontsize=8)
                    Ymax = Y1[i]
               else:
                    # Raizen
                    ax.annotate(str(int(Y1[i])),xy=(xi-0.3,Y1[i]-TopBottom*0.05),color = 'red',fontsize=8)
                    # CCEE
                    Ymax = Y2[i] 
                    ax.annotate(str(int(Y2[i])),xy=(xi-0.3,Y2[i]+TopBottom*0.05),color = 'blue',fontsize=8)

               # Delta
               Ydelta = str(int(Y2[i]-Y1[i]))+' ('+str(round(100*(Y2[i]-Y1[i])/Y2[i],1))+'%)'
               ax.annotate(Ydelta,xy=(xi-0.4,Ymax+TopBottom*0.1),color = 'black',fontsize=6)

          plt.title('Carga - Subsistema  ' +strRegiao,size = 14)
          plt.legend(loc ='lower right',frameon=False)
          ax.set_axisbelow(True)     
          plt.ylim((bottom, top))
          path_figura = os.path.abspath('../output/figuras/'+nome_figura)
          plt.savefig(path_figura, bbox_inches ='tight')         
          listFigsCT.append(path_figura)
     EscreveLogDP(dictGraph,pathSaidaDP)
     return listFigsCT


def Compila_ComparadorDP(dictDP_Raizen,dictDP_Oficial):
     list_subm  = ['1','2','3','4']
     list_estag = dictDP_Raizen.keys()
     dictGraph  = {}

     dictGraph['Raizen']      = {'1':{},'2':{},'3':{},'4':{}}
     dictGraph['Raizen']['1'] = {'pesada':[],'media':[],'leve':[],'MWmed':[]}
     dictGraph['Raizen']['2'] = {'pesada':[],'media':[],'leve':[],'MWmed':[]}
     dictGraph['Raizen']['3'] = {'pesada':[],'media':[],'leve':[],'MWmed':[]}
     dictGraph['Raizen']['4'] = {'pesada':[],'media':[],'leve':[],'MWmed':[]}
     dictGraph['Raizen']['0'] = {'pesada':[],'media':[],'leve':[],'MWmed':[]}
     dictGraph['CCEE']        = {'1':{},'2':{},'3':{},'4':{}}
     dictGraph['CCEE']['1']   = {'pesada':[],'media':[],'leve':[],'MWmed':[]}
     dictGraph['CCEE']['2']   = {'pesada':[],'media':[],'leve':[],'MWmed':[]}
     dictGraph['CCEE']['3']   = {'pesada':[],'media':[],'leve':[],'MWmed':[]}
     dictGraph['CCEE']['4']   = {'pesada':[],'media':[],'leve':[],'MWmed':[]}
     dictGraph['CCEE']['0']   = {'pesada':[],'media':[],'leve':[],'MWmed':[]}
     dictGraph['delta']       = {'1':{},'2':{},'3':{},'4':{}}
     dictGraph['delta']['1']  = {'pesada':[],'media':[],'leve':[],'MWmed':[]}
     dictGraph['delta']['2']  = {'pesada':[],'media':[],'leve':[],'MWmed':[]}
     dictGraph['delta']['3']  = {'pesada':[],'media':[],'leve':[],'MWmed':[]}
     dictGraph['delta']['4']  = {'pesada':[],'media':[],'leve':[],'MWmed':[]}
     dictGraph['delta']['0']  = {'pesada':[],'media':[],'leve':[],'MWmed':[]}

     for estag in list_estag:

          soma_p = 0.0; soma_m   = 0.0
          soma_l = 0.0; soma_med = 0.0
          for subm in list_subm:
               mw_p   = dictDP_Raizen[estag][subm]['mw_p']
               mw_m   = dictDP_Raizen[estag][subm]['mw_m']
               mw_l   = dictDP_Raizen[estag][subm]['mw_l']
               mw_med = dictDP_Raizen[estag][subm]['MWmed']

               dictGraph['Raizen'][subm]['pesada'].append(mw_p)
               dictGraph['Raizen'][subm]['media'].append(mw_m)
               dictGraph['Raizen'][subm]['leve'].append(mw_l)
               dictGraph['Raizen'][subm]['MWmed'].append(mw_med)

               soma_p+=mw_p
               soma_m+=mw_m
               soma_l+=mw_l
               soma_med+=mw_med
          dictGraph['Raizen']['0']['pesada'].append(soma_p)
          dictGraph['Raizen']['0']['media'].append(soma_m)
          dictGraph['Raizen']['0']['leve'].append(soma_l)
          dictGraph['Raizen']['0']['MWmed'].append(soma_med)

     for estag in list_estag:
          soma_p = 0.0; soma_m = 0.0
          soma_l = 0.0; soma_med = 0.0
          for subm in list_subm:
               mw_p = dictDP_Oficial[estag][subm]['mw_p']
               mw_m = dictDP_Oficial[estag][subm]['mw_m']
               mw_l = dictDP_Oficial[estag][subm]['mw_l']
               mw_med = dictDP_Oficial[estag][subm]['MWmed']

               dictGraph['CCEE'][subm]['pesada'].append(mw_p)
               dictGraph['CCEE'][subm]['media'].append(mw_m)
               dictGraph['CCEE'][subm]['leve'].append(mw_l)
               dictGraph['CCEE'][subm]['MWmed'].append(mw_med)

               soma_p+=mw_p
               soma_m+=mw_m
               soma_l+=mw_l
               soma_med+=mw_med
          dictGraph['CCEE']['0']['pesada'].append(soma_p)
          dictGraph['CCEE']['0']['media'].append(soma_m)
          dictGraph['CCEE']['0']['leve'].append(soma_l)
          dictGraph['CCEE']['0']['MWmed'].append(soma_med)

     for estag in list_estag:

          soma_p = 0.0
          soma_m = 0.0
          soma_l = 0.0
          soma_med = 0.0
          for subm in list_subm:
               mw_p = dictDP_Oficial[estag][subm]['mw_p'] - dictDP_Raizen[estag][subm]['mw_p']
               mw_m = dictDP_Oficial[estag][subm]['mw_m'] - dictDP_Raizen[estag][subm]['mw_m']
               mw_l = dictDP_Oficial[estag][subm]['mw_l'] - dictDP_Raizen[estag][subm]['mw_l']
               mw_med = dictDP_Oficial[estag][subm]['MWmed'] - dictDP_Raizen[estag][subm]['MWmed']

               dictGraph['delta'][subm]['pesada'].append(mw_p)
               dictGraph['delta'][subm]['media'].append(mw_m)
               dictGraph['delta'][subm]['leve'].append(mw_l)
               dictGraph['delta'][subm]['MWmed'].append(mw_med)

               soma_p+=mw_p
               soma_m+=mw_m
               soma_l+=mw_l
               soma_med+=mw_med
          dictGraph['delta']['0']['pesada'].append(soma_p)
          dictGraph['delta']['0']['media'].append(soma_m)
          dictGraph['delta']['0']['leve'].append(soma_l)
          dictGraph['delta']['0']['MWmed'].append(soma_med)

     return dictGraph

def Leitura_blocoDP(pathDadger):
     dictDP ={}
     with open(pathDadger) as f:
        for line in f:
            if (line[0] != '&') and(line[0] != '\n') :
                 bloco = line[:2]
                 if bloco =='DP':
                      listParam =line.split()
                      estag = listParam[1].strip()
                      subm = listParam[2].strip()

                      # PESADA
                      try:    mw_p = float(line[20:30].strip())
                      except: mw_p = 0
                      h_p =  float(line[30:40].strip())

                      # MEDIA
                      try:    mw_m = float(line[40:50].strip())
                      except: mw_p = 0
                      h_m =  float(line[50:60].strip())

                      # LEVE
                      try:    mw_l = float(line[60:70].strip())
                      except: mw_p = 0
                      h_l =  float(line[70:80].strip())

                      #Compilando
                      try:    dictDP[estag]
                      except: dictDP[estag] = {}

                      dictDP[estag][subm]         = {}
                      dictDP[estag][subm]['mw_p'] = mw_p
                      dictDP[estag][subm]['h_p']  = h_p
                      dictDP[estag][subm]['mw_m'] = mw_m
                      dictDP[estag][subm]['h_m']  = h_m
                      dictDP[estag][subm]['mw_l'] = mw_l
                      dictDP[estag][subm]['h_l']  = h_l

                      tot_h  = h_p + h_m + h_l
                      tot_mw = mw_p*h_p + mw_m*h_m + mw_l*h_l
                      MWmed  = tot_mw/tot_h
                      dictDP[estag][subm]['MWmed'] = round(MWmed,0)

     return dictDP


def EscreveLogDP(dictDP,path):

     listSubm = ['0','1','2','3','4']
     listDeck = ['delta','CCEE','Raizen']     
     out      = open(path, 'w')
     
     for deck in listDeck:
          for subm in listSubm:
                    listDP = dictDP[deck][subm]['MWmed']                    

                    if subm =='1': nome = 'SE'
                    if subm =='2': nome = 'S'
                    if subm =='3': nome = 'NE'
                    if subm =='4': nome = 'N'
                    if subm =='0': nome = 'SIN'
                   
                    out.write('%s;' % deck)
                    out.write('%s;' % nome)
                    
                    for carga in listDP:
                         out.write('%s;' % carga)
                    out.write('\n') 
                    time.sleep(0.0005)
     out.close()
     return path


def Nome_Mes(grafico):
    if grafico == 1: nome = 'Janeiro'
    if grafico == 2: nome = 'Fevereiro'
    if grafico == 3: nome = 'Marco'
    if grafico == 4: nome = 'Abril'
    if grafico == 5: nome = 'Maio'
    if grafico == 6: nome = 'Junho'
    if grafico == 7: nome = 'Julho'
    if grafico == 8: nome = 'Agosto'
    if grafico == 9: nome = 'Setembro'
    if grafico == 10:nome = 'Outubro'
    if grafico == 11:nome = 'Novembro'
    if grafico == 12:nome = 'Dezembro'
    try:    return nome
    except: return ' '

def get_Regiao(subm):
     if subm == '1': strRegiao = 'Sudeste'
     if subm == '2': strRegiao = 'Sul'
     if subm == '3': strRegiao = 'Nordeste'
     if subm == '4': strRegiao = 'Norte'
     if subm == '0': strRegiao = 'SIN'
     return strRegiao
