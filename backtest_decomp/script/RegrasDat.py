# -*- coding: utf-8 -*-
"""
Created on Fri Mar 22 10:38:45 2019

@author: 6913
"""
import sys
import csv
import os
from datetime import date, timedelta
#import xlrd
#import math

def Aplica_RegrasDat(dictPostoData,listDatas):
     for data in listDatas:
          mes = data.month

          dictPostoData = Calcula_artificial(dictPostoData,data,mes)
          dictPostoData = Calcula_REE5(dictPostoData,data)
          dictPostoData = Calcula_RegrasDoAlem(dictPostoData,data)



     return dictPostoData

def Calcula_RegrasDoAlem(dictPostoData,data):
     # 244
     try:
          dictPostoData['244']
     except:
          dictPostoData['244'] ={}
     dictPostoData['244'][data] = dictPostoData['34'][data] + dictPostoData['243'][data]

     # 301 = 118
     try:
          dictPostoData['301']
     except:
          dictPostoData['301'] ={}
     dictPostoData['301'][data] =dictPostoData['118'][data]

     # 104 = 118+119
     try:
          dictPostoData['104']
     except:
          dictPostoData['104'] ={}
     dictPostoData['104'][data] =dictPostoData['118'][data] +dictPostoData['119'][data]

     # 109 = 104+117
     try:
          dictPostoData['109']
     except:
          dictPostoData['109'] ={}
     dictPostoData['109'][data] =dictPostoData['104'][data] -dictPostoData['117'][data]

     # 252 = 259
     try:
          dictPostoData['252']
     except:
          dictPostoData['252'] ={}
     dictPostoData['252'][data] =dictPostoData['259'][data]

     # 175 = 173
     try:
          dictPostoData['175']
     except:
          dictPostoData['175'] ={}
     dictPostoData['175'][data] =dictPostoData['173'][data]

     # 171 = 0
     try:
          dictPostoData['171']
     except:
          dictPostoData['171'] ={}
     dictPostoData['171'][data] = 0

     # 2 = 1
     try:
          dictPostoData['2']
     except:
          dictPostoData['2'] ={}
     dictPostoData['2'][data] = dictPostoData['1'][data]

     # 168 Tempo de viagem, sobradinho incremental (conta inversa)
     try:
          dictPostoData['168']
     except:
          dictPostoData['168'] ={}
     try:# ERRINHO
          dictPostoData['168'][data] = dictPostoData['169'][data] - (dictPostoData['156'][data-timedelta(days=15)] + dictPostoData['158'][data-timedelta(days=15)])
     except:
          print data


     # 160 = 119+104 --- TIRADO DA CARTOLA
     try:
          dictPostoData['160']
     except:
          dictPostoData['160'] ={}
     dictPostoData['160'][data] = dictPostoData['104'][data]-dictPostoData['119'][data]

     # 320 = 301
     try:
          dictPostoData['320']
     except:
          dictPostoData['320'] ={}
     dictPostoData['320'][data] =dictPostoData['301'][data]

     # 203 = 201 + 202
     try:
          dictPostoData['203']
     except:
          dictPostoData['203'] ={}
     dictPostoData['203'][data] =dictPostoData['201'][data] + dictPostoData['202'][data]


     return dictPostoData

def Calcula_REE5(dictPostoData,data):
     # foi alterado no cadastro o posto 166 para representar o ree 5
     #63 246
     #61 34
     #245 jupia
     #61 capivara
     #63 rosana
     # 243 T. irmaos
     # 244 i solteira --- nao tem como
     # 43 T. irmaos ART
     # 62 taquarucu
     # 34 ILHA SOLTEIRA EQUIVALENTE
     # 244 (t) = 034 (t) + 243 (t)
#     Para obter a Energia Natural Afluente (ENA) do Reservatório Equivalente de Energia (REE) de ITAIPU são utilizadas as vazões incrementais (verificadas, estimadas e previstas) dos seguintes reservatórios:
#
#1) JUPIÁ
#2) SÃO DOMINGOS
#3) PORTO PRIMAVERA
#4) TAQUARUÇU
#5) ROSANA
#6) ITAIPU
#
#De forma a facilitar a reprodutibilidade deste cálculo, o somatório destas vazões incrementais é disponibilizado no arquivo PREVS através do posto 166.

     try:
          dictPostoData['166']
     except:
          dictPostoData['166'] ={}
     dictPostoData['166'][data] =dictPostoData['266'][data] -( dictPostoData['61'][data] +dictPostoData['34'][data])


     dictPostoData['66'][data] = dictPostoData['66'][data] - dictPostoData['166'][data]


     return dictPostoData


#def Calcula_artificial(VAZ,data,mes):
#
#     # 176 nao esta no regras
#     try:
#          VAZ['176']
#     except:
#          VAZ['176'] = {}
#     VAZ['176'][data] = VAZ['172'][data]
#
#     try:
#          VAZ['119']
#     except:
#          VAZ['119'] ={}
#     # Trocado 301 por 118
#     if mes ==1:
#          VAZ['119'][data] = VAZ['118'][data]*1.217+0.608
#     if mes ==2:
#          VAZ['119'][data] = VAZ['118'][data]*1.232+0.123
#     if mes ==3:
#          VAZ['119'][data] = VAZ['118'][data]*1.311-2.359
#     if mes ==4:
#          VAZ['119'][data] = VAZ['118'][data]*1.241-0.496
#     if mes ==5:
#          VAZ['119'][data] = VAZ['118'][data]*1.167+0.467
#     if mes ==6:
#          VAZ['119'][data] = VAZ['118'][data]*1.333-0.53
#     if mes ==7:
#          VAZ['119'][data] = VAZ['118'][data]*1.247-0.374
#     if mes ==8:
#          VAZ['119'][data] = VAZ['118'][data]*1.2+0.36
#     if mes ==9:
#          VAZ['119'][data] = VAZ['118'][data]*1.292-1.292
#     if mes ==10:
#          VAZ['119'][data] = VAZ['118'][data]*1.25-0.25
#     if mes ==11:
#          VAZ['119'][data] = VAZ['118'][data]*1.294-1.682
#     if mes ==12:
#          VAZ['119'][data] = VAZ['118'][data]*1.215+0.729
#
#     try:
#          VAZ['116']
#     except:
#          VAZ['116'] ={}
#     VAZ['116'][data] = VAZ['119'][data]-VAZ['118'][data]
#
#     try:
#          VAZ['318']
#     except:
#          VAZ['318'] ={}
#     VAZ['318'][data]  = VAZ['116'][data]+0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])+VAZ['117'][data]+VAZ['118'][data]
#
#
#     try:
#          VAZ['298']
#     except:
#          VAZ['298'] = {}
#     if VAZ['125']<=190:
#        aux = VAZ['125']*119/190
#     else:
#          if VAZ['125']<=209:
#               aux = 119
#          else:
#               if VAZ['125']<=250:
#                    aux = VAZ['125']-90
#               else:
#                    aux = 160
#     VAZ['298'][data] = aux
#
#
#
#
#
#
#
#     try:
#          VAZ['37']
#     except:
#          VAZ['37'] ={}
#     VAZ['37'][data] = VAZ['237'][data]-0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])-VAZ['117'][data]-VAZ['118'][data]
#
#     try:
#          VAZ['38']
#     except:
#          VAZ['38'] ={}
#     VAZ['38'][data] = VAZ['238'][data]-0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])-VAZ['117'][data]-VAZ['118'][data]
#
#     try:
#          VAZ['39']
#     except:
#          VAZ['39'] = {}
#     VAZ['39'][data] = VAZ['239'][data]-0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])-VAZ['117'][data]-VAZ['118'][data]
#
#     try:
#          VAZ['40']
#     except:
#          VAZ['40'] = {}
#     VAZ['40'][data] = VAZ['240'][data]-0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])-VAZ['117'][data]-VAZ['118'][data]
#
#     try:
#          VAZ['42']
#     except:
#          VAZ['42'] ={}
#     VAZ['42'][data] = VAZ['242'][data]-0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])-VAZ['117'][data]-VAZ['118'][data]
#
#     try:
#          VAZ['43']
#     except:
#          VAZ['43'] ={}
#     VAZ['43'][data] = VAZ['243'][data]-0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])-VAZ['117'][data]-VAZ['118'][data]
#
#     try:
#          VAZ['45']
#     except:
#          VAZ['45'] ={}
#     VAZ['45'][data] = VAZ['245'][data]-0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])-VAZ['117'][data]-VAZ['118'][data]
#
#     try:
#          VAZ['46']
#     except:
#          VAZ['46'] = {}
#     VAZ['46'][data] = VAZ['246'][data]-0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])-VAZ['117'][data]-VAZ['118'][data]
#
#     try:
#          VAZ['66']
#     except:
#          VAZ['66'] = {}
#     VAZ['66'][data] = VAZ['266'][data]-0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])-VAZ['117'][data]-VAZ['118'][data]
#
##     '131':{ 'mes':  0,'regra': [MIN(VAZ(316);144)-VAZ(123)]},
#
#     try:
#          VAZ['132']
#     except:
#          VAZ['132'] = {}
#     VAZ['132'][data] = VAZ['202'][data]+min(VAZ['201'][data],25)
#
#     try:
#          VAZ['75']
#     except:
#          VAZ['75'] = {}
#     VAZ['75'][data] = VAZ['76'][data]+min(VAZ['73'][data]-10,173.5)
#
#
#     try:
#          VAZ['317']
#     except:
#          VAZ['317'] = {}
#     VAZ['317'][data] = max(0, VAZ['201'][data]-25)
#     print VAZ['317'][data]
#     sys.exit()
#
#     try:
#          VAZ['315']
#     except:
#          VAZ['315'] = {}
#     VAZ['315'][data] = (VAZ['132'][data])+VAZ['317'][data]+VAZ['298'][data] # alterada
#     print VAZ['315'][data]
#     sys.exit()
#     try:
#          VAZ['316']
#     except:
#          VAZ['316'] =  {}
#     VAZ['316'][data] = max(min(VAZ['315'][data],190),0)
#
#     try:
#          VAZ['131']
#     except:
#          VAZ['131'] =  {}
#     VAZ['131'][data] = min(VAZ['316'][data],144) #-VAZ['123'][data]
#
#     # 303, 132, 201, 202, 316 e 131 possivelmente estao todos cagados
#     try:
#          VAZ['303']
#     except:
#          VAZ['303'] = {}
#     if VAZ['132'][data]<17:
#           aux = VAZ['132'][data]+max(min(VAZ['316'][data]-(VAZ['131'][data]+VAZ['123'][data]) , 34),0)
#     else:
#           aux = 17+max(min(VAZ['316'][data]-(VAZ['131'][data]+VAZ['123'][data]),34),0)
#     VAZ['303'][data] = aux
#
#     try:
#          VAZ['306']
#     except:
#          VAZ['306'] = {}
#     VAZ['306'][data] = VAZ['303'][data]+VAZ['131'][data]
#
#     try:
#          VAZ['304']
#     except:
#          VAZ['304'] = {}
#     VAZ['304'][data] = VAZ['315'][data]-VAZ['316'][data]
#
#
##     '302':{ 'mes':  0,'regra': [   VAZ(288)-VAZ(292)]},
#     try:
#          VAZ['292']
#     except:
#          VAZ['292'] = {}
#     if mes ==1:
#          vaz_ref = 1100
#     if mes ==2:
#          vaz_ref = 1600
#     if mes ==3:
#          vaz_ref = 4000
#     if mes ==4:
#          vaz_ref = 8000
#     if mes ==5:
#          vaz_ref = 4000
#     if mes ==6:
#          vaz_ref = 2000
#     if mes ==7:
#          vaz_ref = 1200
#     if mes ==8:
#          vaz_ref = 900
#     if mes ==9:
#          vaz_ref = 750
#     if mes ==10:
#          vaz_ref = 700
#     if mes ==11:
#          vaz_ref = 800
#     if mes ==12:
#          vaz_ref = 900
#
#     if VAZ['288'][data]<=vaz_ref:
#          aux = 0
#     else:
#           if VAZ['288'][data]<=(vaz_ref+13900):
#               aux = VAZ['288'][data]-vaz_ref
#           else:
#               aux = 13900
#     VAZ['292'][data] = aux
#
#     try:
#          VAZ['302']
#     except:
#          VAZ['302'] ={}
#
#     VAZ['302'][data] = VAZ['288'][data]-VAZ['292'][data]
#
#     try:
#          VAZ['127']
#     except:
#          VAZ['127'] = {}
#     VAZ['127'][data] = VAZ['129'][data]-VAZ['298'][data]-VAZ['201'][data]-VAZ['202'][data]+VAZ['304'][data]  # alterado tambem
#
#
#     try:
#          VAZ['126']
#     except:
#          VAZ['126'] ={}
#     if VAZ['127'][data]<=430:
#          aux = max(0,VAZ['127'][data]-90)
#     else:
#          aux = 340
#     VAZ['126'][data] = aux+VAZ['123'][data]
#
#     try:
#          VAZ['299']
#     except:
#          VAZ['299'] = {}
#     VAZ['299'][data] = VAZ['130'][data]-VAZ['298'][data]-VAZ['201'][data]-VAZ['202'][data]+VAZ['304'][data]+VAZ['123'][data]
#
#
#
#     return VAZ
#
#


def Aplica_RegrasDat_prevs(dictPostoData,listDatas,mes):

     for data in listDatas:

          dictPostoData = Calcula_artificial_prevs(dictPostoData,data,mes)
          dictPostoData = Calcula_RegrasDoAlem(dictPostoData,data)
          dictPostoData = Calcula_REE5(dictPostoData,data)



     return dictPostoData


def Calcula_artificial_prevs(VAZ,data,mes):
     # 176 nao esta no regras
     try:
          VAZ['176']
     except:
          VAZ['176'] = {}
     VAZ['176'][data] = VAZ['172'][data]

     try:
          VAZ['119']
     except:
          VAZ['119'] ={}

     # Trocado 301 por 118
     if mes ==1:
          VAZ['119'][data] = VAZ['118'][data]*1.217+0.608
     if mes ==2:
          VAZ['119'][data] = VAZ['118'][data]*1.232+0.123
     if mes ==3:
          VAZ['119'][data] = VAZ['118'][data]*1.311-2.359
     if mes ==4:
          VAZ['119'][data] = VAZ['118'][data]*1.241-0.496
     if mes ==5:
          VAZ['119'][data] = VAZ['118'][data]*1.167+0.467
     if mes ==6:
          VAZ['119'][data] = VAZ['118'][data]*1.333-0.53
     if mes ==7:
          VAZ['119'][data] = VAZ['118'][data]*1.247-0.374
     if mes ==8:
          VAZ['119'][data] = VAZ['118'][data]*1.2+0.36
     if mes ==9:
          VAZ['119'][data] = VAZ['118'][data]*1.292-1.292
     if mes ==10:
          VAZ['119'][data] = VAZ['118'][data]*1.25-0.25
     if mes ==11:
          VAZ['119'][data] = VAZ['118'][data]*1.294-1.682
     if mes ==12:
          VAZ['119'][data] = VAZ['118'][data]*1.215+0.729

     try:
          VAZ['116']
     except:
          VAZ['116'] ={}
     VAZ['116'][data] = VAZ['119'][data]-VAZ['118'][data]

     try:
          VAZ['318']
     except:
          VAZ['318'] ={}
     VAZ['318'][data]  = VAZ['116'][data]+0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])+VAZ['117'][data]+VAZ['118'][data]


     try:
          VAZ['298']
     except:
          VAZ['298'] = {}
     if VAZ['125'][data]<=190:
        aux = VAZ['125'][data]*119/190
     else:
          if VAZ['125'][data]<=209:
               aux = 119
          else:
               if VAZ['125'][data]<=250:
                    aux = VAZ['125'][data]-90
               else:
                    aux = 160
     VAZ['298'][data] = aux

     try:
          VAZ['37']
     except:
          VAZ['37'] ={}
     VAZ['37'][data] = VAZ['237'][data]-0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])-VAZ['117'][data]-VAZ['118'][data]

     try:
          VAZ['38']
     except:
          VAZ['38'] ={}
     VAZ['38'][data] = VAZ['238'][data]-0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])-VAZ['117'][data]-VAZ['118'][data]

     try:
          VAZ['39']
     except:
          VAZ['39'] = {}
     VAZ['39'][data] = VAZ['239'][data]-0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])-VAZ['117'][data]-VAZ['118'][data]

     try:
          VAZ['40']
     except:
          VAZ['40'] = {}
     VAZ['40'][data] = VAZ['240'][data]-0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])-VAZ['117'][data]-VAZ['118'][data]

     try:
          VAZ['42']
     except:
          VAZ['42'] ={}
     VAZ['42'][data] = VAZ['242'][data]-0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])-VAZ['117'][data]-VAZ['118'][data]

     try:
          VAZ['43']
     except:
          VAZ['43'] ={}
     VAZ['43'][data] = VAZ['243'][data]-0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])-VAZ['117'][data]-VAZ['118'][data]

     try:
          VAZ['45']
     except:
          VAZ['45'] ={}
     VAZ['45'][data] = VAZ['245'][data]-0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])-VAZ['117'][data]-VAZ['118'][data]

     try:
          VAZ['46']
     except:
          VAZ['46'] = {}
     VAZ['46'][data] = VAZ['246'][data]-0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])-VAZ['117'][data]-VAZ['118'][data]

     try:
          VAZ['66']
     except:
          VAZ['66'] = {}
     VAZ['66'][data] = VAZ['266'][data]-0.1*(VAZ['161'][data]-VAZ['117'][data]-VAZ['118'][data])-VAZ['117'][data]-VAZ['118'][data]

#     '131':{ 'mes':  0,'regra': [MIN(VAZ(316);144)-VAZ(123)]},

     try:
          VAZ['132']
     except:
          VAZ['132'] = {}
     VAZ['132'][data] = VAZ['202'][data]+min(VAZ['201'][data],25)

     try:
          VAZ['75']
     except:
          VAZ['75'] = {}
     VAZ['75'][data] = VAZ['76'][data]+min(VAZ['73'][data]-10,173.5)


     try:
          VAZ['317']
     except:
          VAZ['317'] = {}
     VAZ['317'][data] = max(0, VAZ['201'][data]-25)


     try:
          VAZ['315']
     except:
          VAZ['315'] = {}
     VAZ['315'][data] = (VAZ['203'][data]-VAZ['201'][data])+VAZ['317'][data]+VAZ['298'][data] # alterada

     try:
          VAZ['316']
     except:
          VAZ['316'] =  {}
     VAZ['316'][data] = max(min(VAZ['315'][data],190),0)



     try:
          VAZ['131']
     except:
          VAZ['131'] =  {}
     VAZ['131'][data] = min(VAZ['316'][data],144)

     # 303, 132, 201, 202, 316 e 131 possivelmente estao todos cagados
     try:
          VAZ['303']
     except:
          VAZ['303'] = {}
     if VAZ['132'][data]<17:
           aux = VAZ['132'][data]+max(min(VAZ['316'][data]-(VAZ['131'][data]+VAZ['123'][data]) , 34),0)
     else:
           aux = 17+max(min(VAZ['316'][data]-(VAZ['131'][data]+VAZ['123'][data]),34),0)
     VAZ['303'][data] = aux

     try:
          VAZ['306']
     except:
          VAZ['306'] = {}
     VAZ['306'][data] = VAZ['303'][data]+VAZ['131'][data]

     try:
          VAZ['304']
     except:
          VAZ['304'] = {}
     VAZ['304'][data] = VAZ['315'][data]-VAZ['316'][data]



#     '302':{ 'mes':  0,'regra': [   VAZ(288)-VAZ(292)]},
     try:
          VAZ['292']
     except:
          VAZ['292'] = {}
     if mes ==1:
          vaz_ref = 1100
     if mes ==2:
          vaz_ref = 1600
     if mes ==3:
          vaz_ref = 4000
     if mes ==4:
          vaz_ref = 8000
     if mes ==5:
          vaz_ref = 4000
     if mes ==6:
          vaz_ref = 2000
     if mes ==7:
          vaz_ref = 1200
     if mes ==8:
          vaz_ref = 900
     if mes ==9:
          vaz_ref = 750
     if mes ==10:
          vaz_ref = 700
     if mes ==11:
          vaz_ref = 800
     if mes ==12:
          vaz_ref = 900

     if VAZ['288'][data]<=vaz_ref:
          aux = 0
     else:
           if VAZ['288'][data]<=(vaz_ref+13900):
               aux = VAZ['288'][data]-vaz_ref
           else:
               aux = 13900
     VAZ['292'][data] = aux

     try:
          VAZ['302']
     except:
          VAZ['302'] ={}

     VAZ['302'][data] = VAZ['288'][data]-VAZ['292'][data]

     try:
          VAZ['127']
     except:
          VAZ['127'] = {}
     VAZ['127'][data] = VAZ['129'][data]-VAZ['298'][data]-VAZ['203'][data]+VAZ['304'][data]  # alterado tambem


     try:
          VAZ['126']
     except:
          VAZ['126'] ={}
     if VAZ['127'][data]<=430:
          aux = max(0,VAZ['127'][data]-90)
     else:
          aux = 340
     VAZ['126'][data] = aux #?? +VAZ['123'][data]


     try:
          VAZ['299']
     except:
          VAZ['299'] = {}
     VAZ['299'][data] = VAZ['130'][data]-VAZ['298'][data]-VAZ['201'][data]-VAZ['202'][data]+VAZ['304'][data]#+VAZ['123'][data]
#     print VAZ['127'][data]
#     sys.exit()
     # 166
     try:
          VAZ['166']
     except:
          VAZ['166'] = {}
     VAZ['166'][data] = VAZ['266'][data] -( VAZ['61'][data] +VAZ['34'][data])

     return VAZ
