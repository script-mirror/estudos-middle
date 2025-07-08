# -*- coding: utf-8 -*-
"""
Created on Sat Dec 22 17:37:19 2018

@author: 6913
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import numpy as np
import math
import matplotlib.transforms
import csv
import time
def Graficos_Backtest(dados):
    
    # mudanca de ordem - sugerida pelo Ewerton G.
    dados = dados[1:]+[dados[0]]

    listSubmercado = ['SUDESTE','SUL','NORDESTE','NORTE']
    #Guarda tags
    labels =[]
    for i in range(len(dados)):
        lb = Label_Bloco(dados[i][0])
        labels.append(lb)
    
    
    k = 0
    dictSubmValores ={}
    listTituloGraph =[]
    for submercado in listSubmercado:
        
        listValores = []
        for i in range(len(dados)):
            titulo = submercado
            listValores.append(dados[i][k+1])
        
        dictSubmValores[titulo] = listValores
        k+=1
    listSubmAux = listSubmercado[:]
    

    # PLOTA GRAFICOS
    for key1 in listSubmercado:
        try:
            listSubmAux.remove(key1)
        
            strKeys =key1
            for key2 in listSubmAux[:]:
                if dictSubmValores[key1] == dictSubmValores[key2]:
                    listSubmAux.remove(key2)
                    strKeys = strKeys+' - '+key2
            listValores = dictSubmValores[key1]
            Plota_accum_add_sub(strKeys,labels,listValores)
    
            listTituloGraph.append(strKeys+'.png')
            
            if len(listSubmAux) ==0:
                break
        except:
            pass

    
    # Ajusta dados para printar tabela
    
    coluna1 =['Rodada','SE','S','NE','N']
    
    data = dados
    data =np.array(data).T
    data_aux =[]
    # Transformando em float
    for j in range(len(data)):
        linha_aux =[]
        for i in range(len(data[0])):
            try:
                linha_aux.append(round(float(data[j][i]),2))
            except:
                linha_aux.append(data[j][i])
        data_aux.append([coluna1[j]]+linha_aux)
    

    #############################
    #Tabela 1 - Resultados rodadas
    #############################
    data = data_aux
    table1 = data_aux
        
    
    #############################
    #Tabela 2 - Diferenca entre rodadas
    #############################
    data_var =[]
    linha1 = [data[0][0]] +['EDP-CCEE']+data[0][2:-1]+['Outros']
    for i in range(len(data)-1):
        listVar =[]
        var = data[i+1][1] -data[i+1][-1] # Diferenca EDP-CCEE
        listVar.append(round(var,2))
        for j in range(len(data[0])-2):

            var = data[i+1][j+1] -data[i+1][j+2]
            listVar.append(round(var,2))
        
        # Blocos nao trocados
#        var = data[i+1][1] - data[i+1][-1]
 #       listVar.append(round(var,2))
        #
        data_var.append([coluna1[i+1]]+listVar)
        
    data_var = [linha1] +data_var
    
    table2 = data_var
    
    #############################
    ##Tabela 3 - Percentual de diferenca
    #############################
    linha1 = [data[0][0]] +['ErroRef']+data[0][3:]+['Outros']
    data_var_per =[]
    for i in range(len(data)-1):
        listVar =[]
        varRef = data[i+1][1] -data[i+1][0+2]
        if varRef ==0:
	   varRef = 1000
        listVar.append(round(varRef,2))
        for j in range(1,len(data[0])-2):
            var = 100*round((data[i+1][j+1] -data[i+1][j+2])/varRef,3)    
            if var > 1000:
                var = '>+1000'
            elif var < -1000:
                var = '<-1000'
            else:
                var =str(var)+'%'
                
            listVar.append(var)
        # Blocos nao trocados
        var = str(100*round((data[i+1][1] -data[i+1][-1])/varRef,3))+'%'
        listVar.append(var)
        data_var_per.append([coluna1[i+1]]+listVar)
    
    data_var_per = [linha1] +data_var_per
    table3 = data_var_per
    
#    Printa_tabela(table1)
#    Printa_tabela(table2)
#    print table3
#    sys.exit()
    listTables = [table1,table2,table3]

    time.sleep(5)
    return listTituloGraph ,listTables


def Plota_accum_add_sub(titulo,labels,data):
    
    size = len(data)
    rt = 110/25.4
    fig, ax = plt.subplots(figsize=(rt*1.684,rt*1))
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)    
    ind = np.arange(size)    # the x locations for the groups
    width = 0.7    # the width of the bars: can also be len(x) sequence
    ps,list_Label_Pos = Acc_add_sub_data(data)

    p1 = ax.bar(ind, ps[0], width,color ='white',zorder=0,align='center',linewidth=0) # nulo
    p2 = ax.bar(ind, ps[1], width, color = 'red', #diminuicao
                 bottom=ps[0],align='center')
    p3 = ax.bar(ind, ps[2], width,color = 'blue', #aumento
                 bottom=ps[0],align='center')
    
    # Titulos, labels
    plt.grid(axis='y',zorder=1)
    plt.title(titulo,fontweight='bold')
    plt.ylabel('R$/MWh')
    plt.xticks(ind, labels)

    # hiding tick top and right
    plt.tick_params(
    axis='x',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    top=False)         # ticks along the top edge are off

    plt.tick_params(
    axis='y',          # changes apply to the x-axis
    which='both',      # both major and minor ticks are affected
    right=False)      # ticks along the bottom edge are off
    
    font_tick =10
    for tick in ax.get_xticklabels():#labesl do eixo X
		tick.set_rotation(30)
		tick.set_fontsize(font_tick) 
    gradientbars(p2,'Reds','+')
    gradientbars(p3,'Blues','-')
    
    # limites y_max e y_min
    y_max = math.ceil(float(np.max(data))/10.0)*10
    y_min = math.floor(float(np.min(data))/10.0)*10
    
    y_max = y_max+10
    y_min = y_min -10
    if y_min < 0:
	y_min =0
    plt.ylim(y_min,y_max)

    plt.plot(ind,data,marker="_",ms = 150/size, mew =2.2,lw=1.0,
                          linestyle =':',color='black', zorder = 10)

    # deltas, tamanho dos gaps
    corr_label =0.5
    delta = np.arange(y_min, y_max,5)
    n_deltas = len(delta)
    if n_deltas > 50:
        delta = np.arange(y_min, y_max,25)
        corr_label =2.4
    elif n_deltas > 39 :
        delta = np.arange(y_min, y_max,20)
        corr_label =1.5
    elif n_deltas > 26 :
        delta = np.arange(y_min, y_max,15)
        corr_label =1.5
    elif n_deltas > 13:
         delta = np.arange(y_min, y_max,10)
         corr_label =1
        
    trend_data =data
    # Labels oscilantes nas barras
    if len(trend_data) > 10:
	f_size = 10
    else:
        f_size = 12

    for i, txt in enumerate(trend_data):
        alg = list_Label_Pos[i]
        if alg =='top':
            corr = 6*corr_label
        else:
            corr = -6.5*corr_label

        ax.annotate(txt, (i, corr+trend_data[i]),ha='center',va=alg,fontsize =f_size)
    
    plt.yticks(delta)
    ax.set_axisbelow(True)    
    plt.tight_layout()
    plt.savefig(titulo, bbox_inches ='tight')
    
def gradientbars(bars,name,order):
    if order == '-':
        org = 'lower'
    else:
        org = 'upper'
        
    grad = np.atleast_2d(np.linspace(0,1,256)).T
    ax = bars[0].axes
    lim = ax.get_xlim()+ax.get_ylim()
    for bar in bars:
        bar.set_zorder(1)
        bar.set_facecolor("none")
        x,y = bar.get_xy()
        w, h = bar.get_width(), bar.get_height()
#        ax.imshow(grad, aspect='auto', cmap=plt.get_cmap(name))
        ax.imshow(grad, extent=[x,x+w,y,y+h], aspect="auto", cmap=plt.get_cmap(name),
                  origin = org,zorder=1)
        
    ax.axis(lim)

# Devolve tres listas com as bars de cor: branca, vermelha(-),azul(+)
def Acc_add_sub_data(data):
    list_Label_Pos =[]
    listNull =[]
    listNeg =[]
    listPos =[]
    ref = data[0]
    
    # primeiro valor
    listNull.append(data[0])
    listNeg.append(0)
    listPos.append(0)
    list_Label_Pos.append('top')
    # Demais valores, colocando o valor inicial no final
    for value in data[1:]:
        ref2 = value
        if ref > ref2:  #Diminuicao
            listPos.append(0)   #some
            listNull.append(ref2)   #Novo valor 
            listNeg.append(ref-ref2)   # delta decrescido do valor anterior
            list_Label_Pos.append('bottom')
        elif ref < ref2:  #Aumento
            listNeg.append(0)   # some
            listNull.append(ref)   #valor anterior 
            listPos.append(ref2-ref)   #delta acrescido do valor anterior
            list_Label_Pos.append('top')
        elif ref==ref2:
            listNeg.append(0)   # some
            listPos.append(0)   # some
            listNull.append(ref2) #novo valor
            list_Label_Pos.append('top')
        ref = value
    return [listNull,listNeg,listPos],list_Label_Pos

def Label_Bloco(sigla):
    if sigla =='UH':
        label = 'Armazen.'
    elif sigla =='DP':
        label = 'Carga'
    elif sigla =='CT':
        label = 'Termicas.'
    elif sigla =='MP':
        label = 'Manut. H.'
    elif sigla =='MT':
        label = 'Manut. T.'
    elif sigla =='PQ':
        label = 'Pequenas.'
    elif sigla =='RE':
        label = 'Restr.Ele.'
    elif sigla =='AC':
        label = 'Modific.'
    elif sigla =='HV':
        label = 'Restr.Vol.'
    elif sigla =='HQ':
        label = 'Restr.Vaz.'

    else:
        label = sigla
    return label

def Plota_Tabela(titulo,rows,columns,data):
    fig, axs =plt.subplots(2,1)
    plt.figure(num=None, figsize=(16, 2), dpi=100, facecolor='w', edgecolor='k')
    axx = plt.subplot(111, frame_on=False) 
    axx.xaxis.set_visible(False) 
    axx.yaxis.set_visible(False) 
    
    n_rows = len(data[0])

    # Get some pastel shades for the colors
    colors = plt.cm.BuPu(np.linspace(0, 0.5, n_rows))
    
    cell_text = data
#    axs[0].axis('tight')
#    axs[0].axis('off')
    plt.grid('off')

    colors = colors[::-1]
#    sys.exit()
    # Add a table at the bottom of the axes
    
    the_table = plt.table(cellText=cell_text,
                          rowLabels=rows,
                          rowColours=colors,
                          colLabels=columns,
                          colWidths=[0.065 for x in columns],
                          loc='center')
    the_table.set_fontsize(11)    
    # Adjust layout to make room for the table:
        #prepare for saving:
    # draw canvas once
    #plt.gcf().canvas.draw()
    # get bounding box of table
    #points = the_table.get_window_extent(plt.gcf()._cachedRenderer).get_points()
    # add 10 pixel spacing
    #points[0,:] -= 10; points[1,:] += 10
    # get new bounding box in inches
    #nbbox = matplotlib.transforms.Bbox.from_extents(points/plt.gcf().dpi)
    # save and clip by new bounding box
#    plt.subplots_adjust(left=0.2, bottom=0.06)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.01, hspace=0.01)
    plt.savefig(titulo, bbox_inches ='tight')
    
    
def Nome_Mes(grafico):
    if grafico == 1:
        nome = 'Janeiro'
    if grafico == 2:
        nome = 'Fevereiro'
    if grafico == 3:
        nome = 'Marco'
    if grafico == 4:
        nome = 'Abril'
    if grafico == 5:
        nome = 'Maio'
    if grafico == 6:
        nome = 'Junho'
    if grafico == 7:
        nome = 'Julho'
    if grafico == 8:
        nome = 'Agosto'
    if grafico == 9:
        nome = 'Setembro'
    if grafico == 10:
        nome = 'Outubro'
    if grafico == 11:
        nome = 'Novembro'
    if grafico == 12:
        nome = 'Dezembro'
    try:
        return nome
    except:
        return ' '
    
    

if __name__ == '__main__':
    main()
