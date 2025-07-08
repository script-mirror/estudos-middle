# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 17:44:04 2019

@author: 6913
"""
import sys
import os
import csv
import time
import numpy as np
try:
     from RegrasDat import Aplica_RegrasDat_prevs
except:
     print( 'RegrasDat nao esta presente')

try:
     from PDF_utils import PDF_Tabela_Comparador_Prevs
except:
     print ('PDF_utils nao esta presente')


def Compara_vazao(path_cadastro,path_prevsEDP,path_prevsOficial,mes):

     #------------ PARAMETROS ENTRADA ----------------------------------------#
     sem_ref = 'sem'+str(int(path_prevsEDP[-1])+1)
     #------------------------------------------------------------------------#
     print( 'Compara ENA prevs')
     listDatas =['sem1','sem2','sem3','sem4','sem5','sem6']
     dictCadastro,listSubm, listBacia, listRee = Leitura_Cadastro(path_cadastro)
     #prevsEDP
     dictPrevs1 = Leitura_Prevs(path_prevsEDP)
     dictPrevs1 = Aplica_RegrasDat_prevs(dictPrevs1,listDatas,mes)

     #prevsOFICIAL
     dictPrevs2 = Leitura_Prevs(path_prevsOficial)
     dictPrevs2 = Aplica_RegrasDat_prevs(dictPrevs2,listDatas,mes)


     dictENA1 = Prevs_2_ENA(dictPrevs1, dictCadastro,listDatas)
     dictENA2 = Prevs_2_ENA(dictPrevs2, dictCadastro,listDatas)


     dictCompilado1 = Compila_Regiao(dictENA1, dictCadastro,listDatas,listSubm, listBacia, listRee)
     dictCompilado2 = Compila_Regiao(dictENA2, dictCadastro,listDatas,listSubm, listBacia, listRee)

     dictTable = Compara_prevs(dictCompilado1,dictCompilado2,listSubm, listBacia, listRee,listDatas)
     return dictTable,sem_ref
     # OUTPUT
#     strDataHoje = ''
#     Escreve_csv_table(dictTable,path_saida+'\\ComparaCompilado'+strDataHoje+'.csv')
#     Escreve_csv_prevs(dictENA1,dictENA2,path_saida+'\\ComparaPREVS'+strDataHoje+'.csv')

     # REPORT


     #PDF_Tabela_Comparador_Prevs(path_saida_pdf,dictTable,sem_ref)

def DashBoard_ENA(path_SUBM,path_REE,path_BACIA, sem_ref,mes):
     dictSUBM = Leitura_Comparador(path_SUBM)
     dictREE = Leitura_Comparador(path_REE)
     dictBACIA = Leitura_Comparador(path_BACIA)

     # Listando maiores
#     print dictSUBM
     listCSV = []
     #Submercado
     l_Subm =['SE','S','NE','N']
     listSubmErro = []
     setSubm = set()
     for sub in l_Subm:
#     for sub in dictSUBM['deck2 - deck1'].keys():
          mlt = get_MLT(sub,mes)
#          print dictSUBM['deck2 - deck1'][sub][sem_ref]
#          sys.exit()
          pct_erro = int(dictSUBM['deck2 - deck1'][sub][sem_ref])*100/int(mlt)
          if abs(pct_erro) > 2:
               valor1 = dictSUBM['deck2'][sub][sem_ref]
               valor2 = dictSUBM['deck1'][sub][sem_ref]
               delta = dictSUBM['deck2 - deck1'][sub][sem_ref]
               erros = [sub,valor1,valor2,delta,pct_erro]
               listSubmErro.append(erros)
               setSubm.add(sub)

     dictSubm_REE ={'SE':['1','10','12','6','5','7'], #17 bacias
                    'S':['2','11'],
                    'NE':['3'],
                    'N':['4','8','9']}

     listReeErro = []
     setREE = set()
     for sub in l_Subm:
          if sub in setSubm:
               for ree in dictSubm_REE[sub]:
     #     for sub in dictSUBM['deck2 - deck1'].keys():
                    mlt = get_MLT(ree,mes)
                    pct_erro = int(dictREE['deck2 - deck1'][ree][sem_ref])*100/int(mlt)
                    if abs(pct_erro) > 0:
                         valor1 = dictREE['deck2'][ree][sem_ref]
                         valor2 = dictREE['deck1'][ree][sem_ref]
                         delta = dictREE['deck2 - deck1'][ree][sem_ref]
                         erros = [nome, ree, sub,valor1,valor2,delta,pct_erro]
                         listReeErro.append(erros)
                         setREE.add(ree)

#     dictREE_Bacia ={'1':['TOCANTINS (SE)','SAO FRANCISCO (SE)','PARAIBA DO SUL','PARAGUAI','MUCURI','JEQUITINHONHA (SE)','ITABAPOANA','DOCE','ALTO TIETE'],
#                    '2':['URUGUAI','JACUI','ITAJAI-ACU','CAPIVARI'],
#                    '3':['SAO FRANCISCO (NE)','JEQUITINHONHA (NE)','PARNAIBA','PARAGUACU'],
#                    '4':['TOCANTINS (N)'],
#                    '5':['ITAIPU INC'],
#                    '6':['AMAZONAS (SE)'],
#                    '7':['TELES PIRES'],
#                    '8':['BELO MONTE'],
#                    '9':['AMAZONAS (N)'],
#                    '10':['GRANDE','PARANA','PARANAIBA','TIETE'],
#                    '11':['PARANAPANEMA (S)','IGUACU'],
#                    '12':['PARANAPANEMA (SE)']}

     dictREE_Bacia ={'TOCANTINS (SE)':'SE',
                     'SAO FRANCISCO (SE)':'SE',
                     'PARAIBA DO SUL':'SE',
                     'PARAGUAI':'SE',
                     'MUCURI':'SE',
                     'JEQUITINHONHA (SE)':'SE',
                     'ITABAPOANA':'SE',
                     'DOCE':'SE',
                     'ALTO TIETE':'SE',
                    'URUGUAI':'S',
                    'JACUI':'S',
                    'ITAJAI-ACU':'S',
                    'CAPIVARI':'S',
                    'SAO FRANCISCO (NE)':'NE',
                    'JEQUITINHONHA (NE)':'NE',
                    'PARNAIBA':'NE',
                    'PARAGUACU':'NE',
                    'TOCANTINS (N)':'N',
                    'ITAIPU INC':'SE',
                    'AMAZONAS (SE)':'SE',
                    'TELES PIRES':'SE',
                    'BELO MONTE':'N',
                    'AMAZONAS (N)':'N',
                    'GRANDE':'SE',
                    'PARANA':'SE',
                    'PARANAIBA':'SE',
                    'TIETE':'SE',
                    'PARANAPANEMA (S)':'S',
                    'IGUACU':'S',
                    'PARANAPANEMA (SE)':'SE'
                    }

     listBaciaErro = []

     for sub in l_Subm:
          if sub in setSubm:
               for ree in dictSubm_REE[sub]:
                    if ree in setREE:
                         for bacia in dictREE_Bacia[ree]:
               #     for sub in dictSUBM['deck2 - deck1'].keys():
                              pct_erro = int(dictBACIA['deck2 - deck1'][bacia][sem_ref])
                              valor1 = dictBACIA['deck2'][bacia][sem_ref]
                              valor2 = dictBACIA['deck1'][bacia][sem_ref]
                              delta = dictBACIA['deck2 - deck1'][bacia][sem_ref]
                              erros = [ree,bacia,valor1,valor2,delta,pct_erro]
                              listBaciaErro.append(erros)


     return listSubmErro,listReeErro,listBaciaErro,sem_ref


def Compara_prevs(d_1,d_2,l_Subm, l_Bacia, l_Ree,listDatas):

     dictTable ={'deck1':{},'deck2':{},'delta':{}}
     listSems = ['sem1','sem2','sem3','sem4','sem5','sem6']
     # SUBMERCADO
     l_Subm =['SE','S','NE','N']

     # delta
     listTable = []
     listTable.append(['delta'] + listSems)
     for reg in l_Subm:
          listLinha =[reg]
          for data in listDatas:
               valor1 = d_1['subm'][reg][data]
               valor2 = d_2['subm'][reg][data]
               delta = valor2 - valor1
               listLinha.append(delta)
          listTable.append(listLinha)
     dictTable['delta']['subm'] = listTable

     # deck 1
     listTable=[]
     listTable.append(['EDP'] + listSems)
     for reg in l_Subm:
          listLinha =[reg]
          for data in listDatas:
               valor1 = d_1['subm'][reg][data]
               listLinha.append(valor1)
          listTable.append(listLinha)
     dictTable['deck1']['subm'] = listTable

     # deck 2
     listTable=[]
     listTable.append(['OFICIAL'] + listSems)
     for reg in l_Subm:
          listLinha =[reg]
          for data in listDatas:
               valor2 = d_2['subm'][reg][data]
               listLinha.append(valor2)
          listTable.append(listLinha)
     dictTable['deck2']['subm'] = listTable

     # BACIA
     # delta
     listTable = []
     l_Bacia = ['TOCANTINS (SE)',
                     'SAO FRANCISCO (SE)',
                     'PARAIBA DO SUL',
                     'PARAGUAI',
                     'MUCURI',
                     'JEQUITINHONHA (SE)',
                    'ITAIPU INC',
                    'AMAZONAS (SE)',
                    'TELES PIRES',
                     'GRANDE',
                    'PARANA',
                    'PARANAIBA',
                    'TIETE',
                     'PARANAPANEMA (SE)',
                     'ITABAPOANA',
                     'DOCE',
                     'ALTO TIETE',
                    'URUGUAI',
                    'JACUI',
                    'ITAJAI-ACU',
                    'CAPIVARI',
                    'PARANAPANEMA (S)',
                    'IGUACU',
                    'SAO FRANCISCO (NE)',
                    'JEQUITINHONHA (NE)',
                    'PARNAIBA',
                    'PARAGUACU',
                    'TOCANTINS (N)',
                    'BELO MONTE',
                    'AMAZONAS (N)']


#     dictBacia_Subm ={'TOCANTINS (SE)':'SE',
#                     'SAO FRANCISCO (SE)':'SE',
#                     'PARAIBA DO SUL':'SE',
#                     'PARAGUAI':'SE',
#                     'MUCURI':'SE',
#                     'JEQUITINHONHA (SE)':'SE',
#                     'ITABAPOANA':'SE',
#                     'DOCE':'SE',
#                     'ALTO TIETE':'SE',
#                    'URUGUAI':'S',
#                    'JACUI':'S',
#                    'ITAJAI-ACU':'S',
#                    'CAPIVARI':'S',
#                    'SAO FRANCISCO (NE)':'NE',
#                    'JEQUITINHONHA (NE)':'NE',
#                    'PARNAIBA':'NE',
#                    'PARAGUACU':'NE',
#                    'TOCANTINS (N)':'N',
#                    'ITAIPU INC':'SE',
#                    'AMAZONAS (SE)':'SE',
#                    'TELES PIRES':'SE',
#                    'BELO MONTE':'N',
#                    'AMAZONAS (N)':'N',
#                    'GRANDE':'SE',
#                    'PARANA':'SE',
#                    'PARANAIBA':'SE',
#                    'TIETE':'SE',
#                    'PARANAPANEMA (S)':'S',
#                    'IGUACU':'S',
#                    'PARANAPANEMA (SE)':'SE'
#                    }
     listTable.append(['delta'] + listSems)
     for reg in l_Bacia:
          listLinha =[reg]
          for data in listDatas:
               valor1 = d_1['bacia'][reg][data]
               valor2 = d_2['bacia'][reg][data]
               delta = valor2 - valor1
               listLinha.append(delta)
          listTable.append(listLinha)
     dictTable['delta']['bacia'] = listTable

     # deck 1
     listTable =[]
     listTable.append(['deck1'] + listSems)
     for reg in l_Bacia:
          listLinha =[reg]
          for data in listDatas:
               valor1 = d_1['bacia'][reg][data]
               listLinha.append(valor1)
          listTable.append(listLinha)
     dictTable['deck1']['bacia'] = listTable

     # deck 2
     listTable =[]
     listTable.append(['deck2'] + listSems)
     for reg in l_Bacia:
          listLinha =[reg]
          for data in listDatas:
               valor2 = d_2['bacia'][reg][data]
               listLinha.append(valor2)
          listTable.append(listLinha)
     dictTable['deck2']['bacia'] = listTable




     dictSubm_REE ={'SE':['1','10','12','6','5','7'], #17 bacias
                    'S':['2','11'],
                    'NE':['3'],
                    'N':['4','8','9']}

     dictREE_Nome ={'1':'SUDESTE',
                    '10':'PARANA',
                    '12':'PRNPANEMA',
                    '6':'MADEIRA',
                    '5':'ITAIPU',
                    '7':'TPIRES',
                    '2':'SUL',
                    '11':'IGUACU',
                    '3':'NORDESTE',
                    '4':'NORTE',
                    '8':'BMONTE',
                    '9':'MAN-AP'}

     l_Ree = ['1','10','12','6','5','7','2','11','3','4','8','9']
     # REE
     # delta
     listTable = []
     listTable.append(['delta','nome'] + listSems)
     for reg in l_Ree:
          listLinha =[reg,dictREE_Nome[reg]]
          for data in listDatas:
               valor1 = d_1['ree'][reg][data]
               valor2 = d_2['ree'][reg][data]
               delta = valor2 - valor1
               listLinha.append(delta)
          listTable.append(listLinha)
     dictTable['delta']['ree'] = listTable

     # deck 1
     listTable =[]
     listTable.append(['EDP'] + listSems)
     for reg in l_Ree:
          listLinha =[reg]
          for data in listDatas:
               valor1 = d_1['ree'][reg][data]
               listLinha.append(valor1)
          listTable.append(listLinha)
     dictTable['deck1']['ree'] = listTable

     # deck 2
     listTable =[]
     listTable.append(['OFICIAL'] + listSems)
     for reg in l_Ree:
          listLinha =[reg]
          for data in listDatas:
               valor2 = d_2['ree'][reg][data]
               listLinha.append(valor2)
          listTable.append(listLinha)
     dictTable['deck2']['ree'] = listTable

     return dictTable





def Compila_Regiao(dictENA, dictCad, listDatas, l_Subm, l_Bacia, l_Ree):
     dictComparador ={'subm':{},
                      'bacia':{},
                      'ree':{}
                      }

     for data in listDatas:
          # SUBMERCADO
          for reg in l_Subm:
               try:
                    dictComparador['subm'][reg]
               except:
                    dictComparador['subm'][reg] ={}
               soma_diaria = 0
               for posto in dictENA:
                    if dictCad[posto]['subm'] == reg:
                         soma_diaria += dictENA[posto][data]
               dictComparador['subm'][reg][data] = int(soma_diaria)



          # BACIA
          for reg in l_Bacia:
               try:
                    dictComparador['bacia'][reg]
               except:
                    dictComparador['bacia'][reg] ={}
               soma_diaria = 0
               for posto in dictENA:
                    if dictCad[posto]['bacia'] == reg:
                         soma_diaria += dictENA[posto][data]

               dictComparador['bacia'][reg][data] =int(soma_diaria)


          # REE
          for reg in l_Ree:
#               reg = '1'
#               print data
               try:
                    dictComparador['ree'][reg]
               except:
                    dictComparador['ree'][reg] ={}
               soma_diaria = 0
               for posto in sorted(dictENA.keys()):
                    if dictCad[posto]['ree'] == reg:
#                         print posto, dictCad[posto]['nome'], dictENA[posto][data]['RDH'], dictENA[posto][data]['ACOMPH']
                         soma_diaria += dictENA[posto][data]
               dictComparador['ree'][reg][data] =int(soma_diaria)


     return dictComparador

def Leitura_Prevs(endereco):
    try:
        arquivo  = open(endereco, "r")
    except:
        return '0'
    listSems = ['sem1','sem2','sem3','sem4','sem5','sem6']
    dictPrevs ={}
    for linha in arquivo:
        strLinha=linha.split()
#        num = int(strLinha[0])
        cod = str(strLinha[1])
        dictPrevs[cod] = {}
        for i in range(len(listSems)):
             valor = strLinha[2+i]
             sem = listSems[i]
             dictPrevs[cod][sem] = int(valor)
    return dictPrevs

def Prevs_2_ENA(dictPostoDataVaz, dictCadastro,listDatas):
     listPostosProd =dictCadastro.keys()
     listPostos = dictPostoDataVaz.keys()

     dictENA ={}
     for posto in listPostosProd:
          prod = dictCadastro[posto]['prod']
          if posto in listPostos:
               dictENA[posto] = {}
               for data in listDatas:
                    vaz = float(dictPostoDataVaz[posto][data])
                    dictENA[posto][data] = vaz*prod
          else:
               if prod != 0:
                    print( 'posto '+str(posto)+' tem prod mas nao tem vazao!!!')
          if (prod != 0) and (vaz == 0):
               print( 'posto '+str(posto)+' tem prod mas nao tem vazao!!!')


     return dictENA


def Leitura_Cadastro(path):
     file = open(path,'r')
     arquivo = csv.reader(file,delimiter = ';')

     dictCadastro ={}
     listCSV = []
     for linha in arquivo:
          listCSV.append(linha)
     setSubm =set()
     setBacia =set()
     setRee =set()
     setBacia =set()
     for linha in listCSV[1:]:
          cod = linha[0]
          nome = linha[1]
          subm = linha[2]
          bacia = linha[3]
          ree = linha[4]
          try:
               prod = float(linha[5])
          except:
               print( linha[5])
          dictCadastro[cod] ={
                    'nome':nome,
                    'subm':subm,
                    'bacia':bacia,
                    'ree':ree,
                    'prod':prod,
                    }

          setSubm.add(subm.strip())
          setBacia.add(bacia.strip())
          setRee.add(ree.strip())

     return dictCadastro, list(setSubm), list(setBacia), sorted(list(setRee))

def Leitura_Comparador(path):
     listSems = ['sem1','sem2','sem3','sem4','sem5','sem6']

     file = open(path,'r')
     arquivo = csv.reader(file,delimiter = ';')

     listCSV = []

     dictComparador ={}
     for linha in arquivo:
          listCSV.append(linha)

     tipo = ''
     for linha in listCSV:
          if 'sem' in linha[1]:
               tipo = linha[0]
               dictComparador[tipo] ={}
          else:
               reg = linha[0]
               dictComparador[tipo][reg] ={}
               for col in range(1,len(linha)):
                    valor = linha[col]
                    if valor:
                         sem = listSems[col-1]
                         dictComparador[tipo][reg][sem] = valor

     return dictComparador

def Escreve_csv_prevs(dictENA1, dictENA2, path):
     listPostos = dictENA1.keys()
     listPostos = map(int, listPostos)
     listSems = ['sem1','sem2','sem3','sem4','sem5','sem6',]


     out = open(path, 'w')
     # Delta
     out.write('delta;sem1;sem2;sem3;sem4;sem5;sem6;\n')
     for posto in sorted(listPostos):
          out.write('%s;' % str(posto))
          for sem in listSems:
               valor1 = dictENA1[str(posto)][sem]
               valor2 = dictENA2[str(posto)][sem]
               diff = valor2 - valor1
               try:
                    out.write('%s;' % diff)
               except:
                    out.write('%d;'% diff)
          out.write('\n')
          time.sleep(0.0005)

     out.write('deck1;sem1;sem2;sem3;sem4;sem5;sem6;\n')
     for posto in sorted(listPostos):
          out.write('%s;' % str(posto))
          for sem in listSems:
               valor1 = dictENA1[str(posto)][sem]
               try:
                    out.write('%s;' % valor1)
               except:
                    out.write('%d;'% valor1)
          out.write('\n')
          time.sleep(0.0005)

     out.write('deck2;sem1;sem2;sem3;sem4;sem5;sem6;\n')
     for posto in sorted(listPostos):
          out.write('%s;' % str(posto))
          for sem in listSems:
               valor2 = dictENA2[str(posto)][sem]
               try:
                    out.write('%s;' % valor2)
               except:
                    out.write('%d;'% valor2)
          out.write('\n')
          time.sleep(0.0005)
     print( 'Escrito ' + path + '  com sucesso')

     out.close()


def Escreve_csv_table(dictTable,path):
     listDecks = ['delta','deck1','deck2']
     listReg = ['subm','ree','bacia']

     out = open(path, 'w')
     for reg in listReg:
          for deck in listDecks:
               listCSV = dictTable[deck][reg]
               for row in listCSV:
                    for column in row:
                         try:
                              out.write('%s;' % column)
                         except:
                              out.write('%d;'% column)
                    out.write('\n')
          time.sleep(0.0005)

     out.close()
     print( 'Escrito ' + path + '  com sucesso')
     return path

def get_MLT(title,mes_atual):
     path ='C:\\dev\\Comparador_ENA\\MLT.csv'
     file = open(path,'r')
     arquivo = csv.reader(file,delimiter = ';')

     listCSV =[]
     for linha in arquivo:
          listCSV.append(linha)

     dictSubmMesMLT ={}
     listSubm = listCSV[0][1:]

     for i in range(1,len(listSubm)+1):
          subm = listSubm[i-1]
          try:
               dictSubmMesMLT[subm]
          except:
               dictSubmMesMLT[subm] = {}
          for j in range(1,len(listCSV)):

               mes = int(listCSV[j][0])
               dictSubmMesMLT[subm][mes] = int(listCSV[j][i])


     mlt = dictSubmMesMLT[title][mes_atual]

     return mlt
