# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 18:36:11 2019

@author: 6913
"""
import os
import sys
import numpy as np
from datetime  import datetime,timedelta
import time
try:
	from fpdf import FPDF
except:
	print ("instale fpdf")

#class MyPDF(FPDF):
#    #----------------------------------------------------------------------
#   def header(self):
#        enderecoLogo ='C:\dev\Guilherme\Repositorio Desenvolvedor\Comparador_ENAs\Logo\edp_header.png'
#        self.image(enderecoLogo,0,0,210,27)
#        # position logo on the right
#        self.cell(w=80)
#        now = datetime.today()
#        textoA = "Comparador ENA"
#        #textoA.decode('utf8').encode('ISO-8859-9')
#        textoA = "Indicadores dirios"
#        dia = now.day
#        mes = int(now.month)
#        mes = Nome_Mes(mes)
#        ano = now.year
#        textoB = str(dia) +" de "+str(mes) + " | " +str(ano)
#        textoB.decode('utf8').encode('iso-8859-15')
#        self.set_font("Arial", style="B", size=10)
#        # page title
#        self.cell(180)
#        self.set_text_color(251,255,245)
#        self.cell(5,0, textoA,200,0,'R' )
#        self.set_font("Arial", style="", size=20)
#        self.ln(6)
#        self.cell(180)
#        self.cell(5,2, textoB,200,0,'R' )
#        # insert a line break of 20 pixels
#        self.ln(20)

#    def footer(self):#
#	   # Go to 1.5 cm from bottom
#       self.set_y(-15)
#       # Select Arial italic 8
#       self.set_font('Arial', 'I', 8)
#       # Print centered page number
#       self.cell(0, 10, 'Pag %s' % self.page_no(), 0, 0, 'R')




def PDF_Comparador_ENA(path,list_path_graficos):

    ### Monta pagina do Comparador#####
    pdf.add_page()
    # Titulo

    pdf.set_font('Arial','B',28)
    header1 = 'COMPARADOR DE ENAs'
    pdf.cell(0,10,header1,0,1,'L')
    #Rodada do deck
    header2 = strData
    pdf.set_font('Arial','B',18)
    pdf.cell(0,5,header2,0,1,'L')
    pdf.ln(1)

    ### Monta página de graficos de SUBMERCADOS #####
    GrafSubm = list_path_graficos[0]
    x_size = 220
    y_size = round(x_size/4)
    for i in range(len(GrafSubm)/2):
        graf1 = GrafSubm[i*2]
        graf2 = GrafSubm[i*2+1]

        pdf.add_page()
        pdf.set_font('Arial','U',18)
        header10 = 'SUBMERCADOS'
        pdf.cell(0,11,header10,0,1,'L')

        pdf.image(graf1,-15,55,x_size,y_size)
        pdf.image(graf2,-15,140,x_size,y_size)

    GrafREE = list_path_graficos[1]
    for i in range(len(GrafREE)/2):
        graf1 = GrafREE[i*2]
        graf2 = GrafREE[i*2+1]

        pdf.add_page()
        pdf.set_font('Arial','U',18)
        header10 = 'RESERVATORIOS EQUIVALENTES DE ENERGIA '
        pdf.cell(0,11,header10,0,1,'L')

        pdf.image(graf1,-15,55,x_size,y_size)
        pdf.image(graf2,-15,140,x_size,y_size)


def PDF_Tabela_Comparador_Prevs(pdf, dictTable, sem_ref):

    pdf.add_page()
    #Titulo
    pdf.set_font('Arial','B',28)
    header1 = 'COMPARADOR DE ENAS - SUBM'
    pdf.cell(0,10,header1,0,1,'L')
    ### Tabelas ####
    pdf.ln(3)

    # Tabela Submercados
    # DELTA
    pdf.set_font('Arial','U',16)
    pdf.cell(0,3,'ENA (deck OFICIAL - deck EDP)',0,1,'L')
    pdf.ln(2)
    pdf.set_font('Arial','',12)
    # DECK1
    PDF_Table_Comparador_SUBM(pdf,dictTable['delta']['subm'],sem_ref,1)
    pdf.ln(6)
    pdf.set_font('Arial','U',16)

    pdf.cell(0,3,'ENA (deck EDP)',0,1,'L')
    pdf.ln(2)
    pdf.set_font('Arial','',12)
    # DECK2
    PDF_Table_Comparador_SUBM(pdf,dictTable['deck1']['subm'],sem_ref,0)
    pdf.ln(6)
    pdf.set_font('Arial','U',16)

    pdf.cell(0,3,'ENA (deck OFICIAL)',0,1,'L')
    pdf.ln(2)
    pdf.set_font('Arial','',12)

    PDF_Table_Comparador_SUBM(pdf,dictTable['deck2']['subm'],sem_ref,0)
    pdf.ln(6)


    pdf.add_page()

#    print dictTable['delta']['ree']
#    sys.exit()
    # Tabela REE
    pdf.set_font('Arial','B',28)
    header2 = 'Reservatorio Equivalente de Energia'
    pdf.cell(0,10,header2,0,1,'L')
    ### Tabelas ####
    pdf.ln(2)
    pdf.set_font('Arial','U',16)
    pdf.cell(0,3,'ENA (deck OFICIAL - deck EDP)',0,1,'L')

    pdf.ln(2)
    PDF_Table_Comparador_REE(pdf,dictTable['delta']['ree'],sem_ref)
#
#
#
#    pdf.ln(2)
#
#    # Tabela Bacias
    pdf.add_page()
    pdf.set_font('Arial','B',28)
    header2 = 'ENA Bacias'
    pdf.cell(0,10,header2,0,1,'L')
    ### Tabelas ####
    pdf.ln(2)
    pdf.set_font('Arial','U',16)
    pdf.cell(0,3,'ENA (deck OFICIAL - deck EDP)',0,1,'L')

    pdf.ln(2)
    PDF_Table_Comparador_Bacia(pdf,dictTable['delta']['bacia'],sem_ref)


#    print( 'Escrito '+ path_pdf + '  com sucesso')
#    pdf.output(path_pdf,"F")

def PDF_Table_Comparador_SUBM(pdf,data,sem_ref,flag_cond):
    spacing =1.5
    col_width = 20
#    RGB = [[139,0,0],# Titulo
#           [255,0,0], # SE darkred
#           [178,34,34], # S firebrick
#           [205,92,92], # NE indianred
#           [250,128,114], # N salmon
#           ]
    RGB = [[0,0,170],# Titulo
           [55,41,255], # SE
           [40,80,255], # S
           [91,41,255], # NE
           [41,151,255], # N
           ]

    row_height = pdf.font_size
    align_r = 'C'
    n_row = len(data)
    n_col = len(data[0])
    for row in range(n_row):
        for col in range(n_col):
            value =  data[row][col]
            # Colore primeira linha
            if row == 0:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(0,0,255)
                fill_stat = True
                pdf.set_font("Arial", style="B", size=12)
            else:
                pdf.set_text_color(0,0,0)
                pdf.set_font("Arial", style="", size=12)
                pdf.set_fill_color(0,0, 0)
                fill_stat = False
            # Colore primeira coluna
                if col ==0:
                    pdf.set_fill_color(RGB[row][0],RGB[row][1],RGB[row][2])
                    fill_stat = True
                    pdf.set_font("Arial", style="B", size=12)
                else:
                    if col == int(sem_ref[-1]):
                         pdf.set_fill_color(41,223,255)
                         pdf.set_font("Arial", style="B", size=12)
                         fill_stat = True
                    else:
                         pdf.set_fill_color(0,0, 0)
                         fill_stat = False
                    if flag_cond ==1:
                         if value > 1000:
                              pdf.set_text_color(255,0,0)
                         elif value < -1000:
                              pdf.set_text_color(0,0,255)

            item = str(value)
            pdf.cell(col_width, row_height*spacing,
                     txt=item,align =align_r, border=1,fill=fill_stat)

        pdf.ln(row_height*spacing)
    pdf.set_text_color(0,0,0)


def PDF_Table_Comparador_REE(pdf,data,sem_ref):
    dictSubm_REE ={'1':'SE',
                   '10':'SE',
                   '12':'SE',
                   '6':'SE',
                   '5':'SE',
                   '7':'SE',
                   '2':'S',
                   '11':'S',
                   '3':'NE',
                   '4':'N',
                   '8':'N',
                   '9':'N'}
#              'SE':['1','10','12','6','5','7'], #17 bacias
#                    'S':['2','11'],
#                    'NE':['3'],
#                    'N':['4','8','9']}

    spacing =1.5
    col_width = 20

    RGB = [[0,0,170],# Titulo
           [55,41,255], # SE
           [40,80,255], # S
           [91,41,255], # NE
           [41,151,255], # N
           ]

    row_height = pdf.font_size
    align_r = 'C'
    n_row = len(data)
    n_col = len(data[0])
    for row in range(n_row):
        ree = data[row][0]
        for col in range(n_col):
            col_width = 20
            if (row == 0) and (col == 0):
                 value = 'REE'
            else:
                 value =  data[row][col]
            # Colore primeira linha
            if row == 0:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(0,0,255)
                fill_stat = True
                pdf.set_font("Arial", style="B", size=12)
            else:
                pdf.set_text_color(0,0,0)
                pdf.set_font("Arial", style="", size=12)
                pdf.set_fill_color(0,0, 0)
                fill_stat = False
            # Colore primeira coluna
                if col ==0 or col ==1:
#                    print i
                    subm = dictSubm_REE[ree]
                    if subm =='SE':
                         i = 1
                    if subm =='S':
                         i = 2
                    if subm =='NE':
                         i = 3
                    if subm =='N':
                         i = 4
                    pdf.set_fill_color(RGB[i][0],RGB[i][1],RGB[i][2])
                    fill_stat = True
                    pdf.set_font("Arial", style="B", size=12)
                else:
                    if col == int(sem_ref[-1])+1:
                         pdf.set_fill_color(41,223,255)
                         pdf.set_font("Arial", style="B", size=12)
                         fill_stat = True
                    else:
                         pdf.set_fill_color(0,0, 0)
                         fill_stat = False
                    if value > 1000:
                         pdf.set_text_color(255,0,0)
                    elif value < -1000:
                         pdf.set_text_color(0,0,255)
                    else:
                         pdf.set_text_color(0,0,0)
            item = str(value)
            if col ==1:
                 if row == 0:
                      pdf.set_text_color(255,255,255)
                 else:
                      pdf.set_text_color(0,0,0)
                 col_width = 40



            pdf.cell(col_width, row_height*spacing,
                     txt=item,align =align_r, border=1,fill=fill_stat)

        pdf.ln(row_height*spacing)
    pdf.set_text_color(0,0,0)

def PDF_Table_Comparador_Bacia(pdf,data,sem_ref):
    dictBacia_Subm ={'TOCANTINS (SE)':'SE',
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

    spacing =1.5
    col_width = 20

    RGB = [[0,0,170],# Titulo
           [55,41,255], # SE
           [40,80,255], # S
           [91,41,255], # NE
           [41,151,255], # N
           ]

    row_height = pdf.font_size
    align_r = 'C'
    n_row = len(data)
    n_col = len(data[0])
    for row in range(n_row):

        reg = data[row][0]
        for col in range(n_col):
            if (row == 0) and (col == 0):
                 value = 'Bacia'
            else:
                 value =  data[row][col]
            # Colore primeira linha
            if row == 0:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(0,0,255)
                fill_stat = True
                pdf.set_font("Arial", style="B", size=12)
            else:
                pdf.set_text_color(0,0,0)
                pdf.set_font("Arial", style="", size=12)
                pdf.set_fill_color(0,0, 0)
                fill_stat = False
            # Colore primeira coluna
                if col ==0:
#                    print i
                    subm = dictBacia_Subm[reg]
                    if subm =='SE':
                         i = 1
                    if subm =='S':
                         i = 2
                    if subm =='NE':
                         i = 3
                    if subm =='N':
                         i = 4
                    pdf.set_fill_color(RGB[i][0],RGB[i][1],RGB[i][2])
                    fill_stat = True
                    pdf.set_font("Arial", style="B", size=12)
                else:

                    if col == int(sem_ref[-1]):
                         pdf.set_fill_color(41,223,255)
                         pdf.set_font("Arial", style="B", size=12)
                         fill_stat = True
                    else:
                         pdf.set_fill_color(0,0, 0)
                         fill_stat = False
                    if value > 1000:
                         pdf.set_text_color(255,0,0)
                    elif value < -1000:
                         pdf.set_text_color(0,0,255)
                    else:
                         pdf.set_text_color(0,0,0)

            item = str(value)
            if col == 0:
                 col_width = 60
            else:
                 col_width = 20
            pdf.cell(col_width, row_height*spacing,
                     txt=item,align =align_r, border=1,fill=fill_stat)

        pdf.ln(row_height*spacing)
    pdf.set_text_color(0,0,0)



def PDF_Table(pdf,data,col_width):
    spacing =1.5

    RGB = [[255,255,255],
           [255,51,51],
           [255,76,76],
           [255,102,102],
           [255,127,127],
           [255,152,152],
           [255,177,177]]
    row_height = pdf.font_size
    i=0
    f_row = 1
    for row in data:
        f_col = 1
        for value in row:
            # Colore primeira linha
            if f_row == 1:
                pdf.set_fill_color(255,25,25)
                align_r = 'C'
                fill_stat = True
                pdf.set_font("Arial", style="B", size=12)
            else:
                pdf.set_font("Arial", style="", size=12)
                pdf.set_fill_color(0,0, 0)
                align_r = 'C'
                fill_stat = False
            # Colore primeira coluna
                if f_col ==1:
                    pdf.set_fill_color(RGB[i][0],RGB[i][1],RGB[i][2])
                    align_r = 'C'
                    fill_stat = True
                    pdf.set_font("Arial", style="B", size=12)
                else:
                    pdf.set_fill_color(0,0, 0)
                    if value == row[-1]:
                         pdf.set_font("Arial", style="B", size=12)
                    else:
                         pdf.set_font("Arial", style="", size=12)
                    align_r = 'C'
                    fill_stat = False



            f_col = 0
            item = str(value)
            pdf.cell(col_width, row_height*spacing,
                     txt=item,align =align_r, border=1,fill=fill_stat)
        f_row =0
        pdf.ln(row_height*spacing)
        i+=1

def PDF_Tabela_Comparador_UH(pdf,dictTable):

    pdf.add_page()
    #Titulo
    pdf.set_font('Arial','B',28)
    header1 = 'COMPARADOR DE RESERVATORIO'
    pdf.cell(0,10,header1,0,1,'L')
    pdf.ln(3)

    ### Tabelas ####
    pdf.set_font('Arial','U',18)

    # Tabela Submercados
    header1 = 'Submercado'
    pdf.cell(0,10,header1,0,1,'L')
    pdf.ln(1)

    PDF_Table_Comparador_UH_SUBM(pdf,dictTable['subm'])
    pdf.ln(6)


    # Tabela REE
    pdf.set_font('Arial','U',18)
    header2 = 'Reservatorio Equivalente de Energia'
    pdf.cell(0,10,header2,0,1,'L')
    ### Tabelas ####
    pdf.ln(1)

    PDF_Table_Comparador_UH_REE(pdf,dictTable['ree'])


def PDF_Table_Comparador_UH_SUBM(pdf,data):
    spacing =1.5
    col_width = 20

    RGB = [[0,0,170],# Titulo
           [55,41,255], # SE
           [40,80,255], # S
           [91,41,255], # NE
           [41,151,255], # N
           ]

    row_height = pdf.font_size
    align_r = 'C'
    n_row = len(data)
    n_col = len(data[0])
    for row in range(n_row):
        for col in range(n_col):
            value =  data[row][col]
            # Colore primeira linha
            if row == 0:
 
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(0,0,255)
                fill_stat = True
                pdf.set_font("Arial", style="B", size=12)
            else:
                pdf.set_text_color(0,0,0)
                pdf.set_font("Arial", style="", size=12)
                pdf.set_fill_color(0,0, 0)
                fill_stat = False
            # Colore primeira coluna
                if col ==0:
                    pdf.set_fill_color(RGB[row][0],RGB[row][1],RGB[row][2])
                    fill_stat = True
                    pdf.set_font("Arial", style="B", size=12)
                else:
                    pdf.set_fill_color(0,0, 0)
                    fill_stat = False
            if col == 0:
                 col_width = 20 
            else:
                 col_width = 40
            item = str(value)
            pdf.cell(col_width, row_height*spacing,
                     txt=item,align =align_r, border=1,fill=fill_stat)

        pdf.ln(row_height*spacing)
    pdf.set_text_color(0,0,0)

def PDF_Table_Comparador_UH_REE(pdf,data):
    dictSubm_REE ={'1':'SE',
                   '10':'SE',
                   '12':'SE',
                   '6':'SE',
                   '5':'SE',
                   '7':'SE',
                   '2':'S',
                   '11':'S',
                   '3':'NE',
                   '4':'N',
                   '8':'N',
                   '9':'N'}
#              'SE':['1','10','12','6','5','7'], #17 bacias
#                    'S':['2','11'],
#                    'NE':['3'],
#                    'N':['4','8','9']}

    spacing =1.5
    col_width = 40

    RGB = [[0,0,170],# Titulo
           [55,41,255], # SE
           [40,80,255], # S
           [91,41,255], # NE
           [41,151,255], # N
           ]

    row_height = pdf.font_size
    align_r = 'C'
    n_row = len(data)
    n_col = len(data[0])
    for row in range(n_row):
        ree = data[row][0].split()[0]
        for col in range(n_col):
            col_width = 40
            if (row == 0) and (col == 0):
                 value = 'REE'
            else:
                 value =  data[row][col]
            # Colore primeira linha
            if row == 0:
                pdf.set_text_color(255,255,255)
                pdf.set_fill_color(0,0,255)
                fill_stat = True
                pdf.set_font("Arial", style="B", size=12)
            else:
                pdf.set_text_color(0,0,0)
                pdf.set_font("Arial", style="", size=12)
                pdf.set_fill_color(0,0, 0)
                fill_stat = False
            # Colore primeira coluna
                if col ==0:
#                    print i
                    subm = dictSubm_REE[ree]
                    if subm =='SE':
                         i = 1
                    if subm =='S':
                         i = 2
                    if subm =='NE':
                         i = 3
                    if subm =='N':
                         i = 4
                    pdf.set_fill_color(RGB[i][0],RGB[i][1],RGB[i][2])
                    fill_stat = True
                    pdf.set_font("Arial", style="B", size=12)
                else:
                    pdf.set_fill_color(0,0, 0)
                    fill_stat = False

                    pdf.set_text_color(0,0,0)
            item = str(value)
            if col ==0:
                 if row == 0:
                      pdf.set_text_color(255,255,255)
                 else:
                      pdf.set_text_color(0,0,0)
                 col_width = 40



            pdf.cell(col_width, row_height*spacing,
                     txt=item,align =align_r, border=1,fill=fill_stat)

        pdf.ln(row_height*spacing)
    pdf.set_text_color(0,0,0)


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



