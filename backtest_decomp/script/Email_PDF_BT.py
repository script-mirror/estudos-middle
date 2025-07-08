
import os
import sys
from datetime  import datetime,timedelta
import time
import csv
try:
    from accumulative_add_subt_plot import Graficos_Backtest
except:
    #print 'accumulative_add_subt_plot nao se encontra na mesma pasta'
    sys.exit()
try:
    from compara_deck.PDF_utils import PDF_Tabela_Comparador_Prevs, PDF_Tabela_Comparador_UH
except:
    #print 'PDF_Tabela_Comparador_Prevs nao se encontra na mesma pasta'
    from compara_deck.PDF_utils import PDF_Tabela_Comparador_Prevs, PDF_Tabela_Comparador_UH

try:
	from fpdf import FPDF
except:
	#print "instale fpdf"

# EMAIL ####################################$
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage
from email.MIMEBase import MIMEBase
from email import Encoders
import uuid


def BackTest_Out(pathSaida,dictTablePrevs,dictTableUH,listGraphCT,listGraphDP,sem_ref,flag_Manda_EMAIL):
    info, dados = Leitura_Saida(pathSaida)    
#    path_logo ='Logo/edp_header.png'

    path_graficos ,path_tabelas = Graficos_Backtest(dados)

    debug = 1  # manter em ZERO, 1 envia 
    if debug ==1:
	    listMails =['camila.ramos@edpbr.com.br','matheus.salgado@edpbr.com.br', 'gilseu.von@edpbr.com.br']
    else:
	     listMails= ['luisa.ribeiro@edpbr.com.br','cristiane.toma@edpbr.com.br',
			 'ewerton.guarnier@edpbr.com.br','guilherme.henrique@edpbr.com.br','matheus.salgado@edpbr.com.br',
			 'donato.filho@edpbr.com.br','paola.dorado@edpbr.com.br','camila.ramos@edpbr.com.br',"ianca.oliveira@edpbr.com.br",
		         'lisandro.rodriguez@edpbr.com.br','guilherme.ramalho@edpbr.com.br','igor.castro@edpbr.com.br','juliana.passadore@edpbr.com.br',
			 'rodrigo@edpbr.com.br','nataly.lopes@edpbr.com.br','MARCOS.SAVIANO@EDPBR.COM.BR','nayana.scherner@edpbr.com.br']

    time.sleep(4)
    #print("Elaborando o PDF")

    endereco = Monta_PDF(path_graficos,listGraphCT,listGraphDP,path_tabelas,dictTablePrevs,dictTableUH,sem_ref, info)
    #print endereco +" Escrito com sucesso!!!"
    if flag_Manda_EMAIL:
        #print("Preparando para enviar o e-mail")
        dictImages = Leitura_PDF(endereco)
        Manda_EMAIL2(dictImages,endereco,listMails)
    else:
	#print "E-MAIL NAO FOI ENVIADO"
    #print("Fim da execução")
   
def Leitura_PDF(path_pdf):
    listDicts =[]
    imagem = path_pdf.split('/')[-1]
    endereco = path_pdf.strip(imagem)

    img = {	'title': imagem, 'path': endereco+imagem,'cid':str(uuid.uuid4())}
    listDicts.append(img)
	
    return listDicts	

class MyPDF(FPDF):
    #----------------------------------------------------------------------
    def header(self):	
        enderecoLogo ='/datadrive2/Produtos/BackTest/Logo/edp_header.png'
        self.image(enderecoLogo,0,0,210,27)
        # position logo on the right
#        self.cell(w=80)
        now = datetime.today()
        textoA = "BackTest DECOMP"
        #textoA.decode('utf8').encode('ISO-8859-9')
#        textoA = "Indicadores dirios"
        dia = now.day
        mes = int(now.month)
        mes = Nome_Mes(mes)
        ano = now.year
        textoB = str(dia) +" de "+str(mes) + " | " +str(ano)
        textoB.decode('utf8').encode('iso-8859-15')
        self.set_font("Arial", style="B", size=10)
        # page title
        self.cell(180)
        self.set_text_color(251,255,245)
        self.cell(5,0, textoA,200,0,'R' )
        self.set_font("Arial", style="", size=20)
        self.ln(6)
        self.cell(180)
        self.cell(5,2, textoB,200,0,'R' )
        # insert a line break of 20 pixels
        self.ln(20)
    
    def footer(self):
	   # Go to 1.5 cm from bottom
       self.set_y(-15)
       # Select Arial italic 8
       self.set_font('Arial', 'I', 8)
       # Print centered page number
       self.cell(0, 10, 'Pag %s' % self.page_no(), 0, 0, 'R')



def Monta_PDF(list_graficos,listGraphCT,listGraphDP,list_tabelas,dictTablePrevs,dictTableUH,sem_ref, info):
    now = datetime.now()
    strAno_Mes_Dia = str(now.year) + "_" + str(now.month).zfill(2) + "_" + str(now.day).zfill(2)    

    ### Monta página de Inicial#####
    pdf = MyPDF('P','mm','A4')#210 x 297mm
    pdf.add_page()
    # Titulo
    
    pdf.set_font('Arial','B',28)
    header1 = 'RELATORIO DE BACKTEST DECOMP'
    pdf.cell(0,10,header1,0,1,'L')
    #Rodada do deck
    header2 = info[0]
    pdf.set_font('Arial','B',18)
    pdf.cell(0,5,header2,0,1,'L')
    pdf.ln(1)
    #data deck EDP
    header3 = info[1]
    pdf.set_font('Arial','I',14)
    pdf.cell(0,4,header3,0,1,'L')
    pdf.ln(20)
    #Metodologia
    header4 = 'Metodologia:'
    pdf.set_font('Arial','U',14)
    pdf.cell(0,5.5,header4,0,1,'L')
    #Metodologia1
    pdf.set_font('Arial','',14)
    header5 = '-Inicialmente roda-se os Decks da CCEE e da EDP, comparando os desvios de preco.'
    pdf.cell(0,5,header5,0,1,'L')
    #Metodologia2
    header6 = '-Substitui-se continuamente blocos especificos um a um no deck da EDP'
    header6b= '  pelo bloco correspondente do deck oficial CCEE.'
    pdf.cell(0,5.5,header6,0,1,'L')
    pdf.cell(0,5.5,header6b,0,1,'L')
    #Metodologia3
    header7 = '-Em cada substituicao, roda-se o DECOMP e obtem-se um novo preco com o deck '
    header7b = ' alterado.'
    pdf.cell(0,5.5,header7,0,1,'L')
    pdf.cell(0,5,header7b,0,1,'L')
    #Metodologia4
    header8 = '-No final, o deck EDP vai estar semelhante ao deck CCEE.'
    pdf.cell(0,5.5,header8,0,1,'L')
    #Metodologia5
    header9 = '-Conclui-se que os desvios remanescentes sao causados pelos blocos inalterados.'
    pdf.cell(0,5.5,header9,0,1,'L')
    #Metodologia6
    header9 = '-Utiliza-se a mesma funcao de custo futuro para todas as rodadas.'
    pdf.cell(0,5.5,header9,0,1,'L')
    #Metodologia7
    header10 = '-Os precos nao sao limitados pelo maximo e minimo regulatorio.'
    pdf.cell(0,5.5,header10,0,1,'L')

        
    
    ### Monta pagina de graficos #####
    pdf.add_page()
    pdf.set_font('Arial','U',18)
    header10 = 'Variacao de precos ao longo das rodadas de substituicao'
    pdf.cell(0,11,header10,0,1,'L')
    
    # Printa graf 1
    grafico = list_graficos[0]
    x = 10
    y=55
    rt = 110
    pdf.image(grafico,x,y,rt*1.684,rt*1)
    
    # Printa graf 2 (se houver)
    try:
        grafico = list_graficos[1]
        y=140
        pdf.image(grafico,x,y,rt*1.684,rt*1)
    except:
        pass

    # Printa graf 3 (se houver)
    try:
        grafico = list_graficos[2]
        pdf.add_page()
        header10 = 'Variacao de precos ao longo das rodadas de substituicao (Cont.)'
        pdf.cell(0,11,header10,0,1,'L')

        y=55
        pdf.image(grafico,x,y,rt*1.684,rt*1)
    except:
        pass

    # Printa graf 4 (se houver)
    try:
        grafico = list_graficos[3]
        y= 140
        pdf.image(grafico,x,y,rt*1.684,rt*1)
    except:
        pass


    ### Tabelas ####
    pdf.add_page()
    pdf.set_font('Arial','B',18)
    header11 = 'Tabelas de Resultados'
    
    pdf.cell(0,3,header11,0,1,'L')
    listTitulos = ['Resultado Rodadas(R$/MWh)','Desvio de preco entre rodadas (R$/MWh)',
                   'Desvio da rodada em relacao ao absoluto CCEE-EDP(%)']    
    i =0
    pdf.ln(10)
    col_width = 200/len(list_tabelas[0][0])
    ##### TABELAS ###########################3
    for tabela in list_tabelas[:-1]: # Retirar "[:-1]" para inserir de volta a tabela 3!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # Titulo
        pdf.set_font('Arial','U',16)
        titulo = listTitulos[i]
        pdf.cell(0,3,titulo,0,1,'L')

        # Tabela
        pdf.ln(2)
        pdf.set_font('Arial','',10)
        PDF_Table(pdf,tabela,col_width)
        pdf.ln(8)
        i+=1

    ## Comparador
    PDF_Tabela_Comparador_Prevs(pdf,dictTablePrevs,sem_ref)

    PDF_Tabela_Comparador_UH(pdf,dictTableUH)

    #-- Monta pagina de TERMICAS ----------------------------------------#
    pdf.add_page()    
    pdf.set_font('Arial','B',24)
    header1 = 'Comparacao - Bloco de Termicas'
    pdf.cell(0,10,header1,0,1,'L')
    
    # Printa graf SIN
    grafico = listGraphCT[0]
    x = 5
    y=55
    rt = 60
    pdf.image(grafico,x,y,rt*1.618, rt*1)
    
    # Printa graf SE
    grafico = listGraphCT[1]
    x = 5
    y=115
    rt = 60
    pdf.image(grafico,x,y,rt*1.618, rt*1)


    # Printa graf S
    grafico = listGraphCT[2]
    x = 105
    y=115
    rt = 60
    pdf.image(grafico,x,y,rt*1.618, rt*1)

    # Printa graf NE
    grafico = listGraphCT[3]
    x = 5
    y=185
    rt = 60
    pdf.image(grafico,x,y,rt*1.618, rt*1)


    # Printa graf N
    grafico = listGraphCT[4]
    x = 105
    y=185
    rt = 60
    pdf.image(grafico,x,y,rt*1.618, rt*1)


    #-- Monta pagina de CARGA ----------------------------------------#
    pdf.add_page()    
    pdf.set_font('Arial','B',24)
    header1 = 'Comparacao - Bloco de Carga'
    pdf.cell(0,10,header1,0,1,'L')
    
    # Printa graf SIN
    grafico = listGraphDP[0]
    x = 5
    y=55
    rt = 60
    pdf.image(grafico,x,y,rt*1.618, rt*1)
    
    # Printa graf SE
    grafico = listGraphDP[1]
    x = 5
    y=115
    rt = 60
    pdf.image(grafico,x,y,rt*1.618, rt*1)


    # Printa graf S
    grafico = listGraphDP[2]
    x = 105
    y=115
    rt = 60
    pdf.image(grafico,x,y,rt*1.618, rt*1)

    # Printa graf NE
    grafico = listGraphDP[3]
    x = 5
    y=185
    rt = 60
    pdf.image(grafico,x,y,rt*1.618, rt*1)


    # Printa graf N
    grafico = listGraphDP[4]
    x = 105
    y=185
    rt = 60
    pdf.image(grafico,x,y,rt*1.618, rt*1)
    #print "Escrito com sucesso! SAIDA/BackTest_"+strAno_Mes_Dia+".pdf"
    endereco ="/datadrive2/Produtos/BackTest/SAIDA/BackTest_"+strAno_Mes_Dia+".pdf"
    pdf.output(endereco,"F")
    time.sleep(10)
    return endereco

def PDF_Table(pdf,data,col_width):
    spacing =1.5
    RGB = [[255,255,255],
           [255,51,51],
           [255,76,76],
           [255,102,102],
           [255,127,127]]
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
                pdf.set_font("Arial", style="B", size=10)
            else:
                pdf.set_font("Arial", style="", size=10)
                pdf.set_fill_color(0,0, 0)
                align_r = 'R'
                fill_stat = False
            # Colore primeira coluna
                if f_col ==1:
                    pdf.set_fill_color(RGB[i][0],RGB[i][1],RGB[i][2])
                    align_r = 'C'
                    fill_stat = True
                    pdf.set_font("Arial", style="B", size=10)
                else:
                    pdf.set_fill_color(0,0, 0)
                    pdf.set_font("Arial", style="", size=10)
                    align_r = 'R'
                    fill_stat = False    
            
            f_col = 0
            item = str(value)
            pdf.cell(col_width, row_height*spacing,
                     txt=item,align =align_r, border=1,fill=fill_stat)
        f_row =0
        pdf.ln(row_height*spacing)
        i+=1


def Manda_EMAIL2(listDictImagens,Endereco,listEmails):
	listDictImagens = listDictImagens[:]
	strTituloMsg = 'Relatorio de BackTest DECOMP - BETA!'
	mail_to = listEmails
	strUserEmailFrom ='edp.estudosenergeticos1@gmail.com'
	strUserLogin ='edp.estudosenergeticos1@gmail.com'
	strPass ='edpbr2015'
	
	smtp_host ='smtp.gmail.com'
	smtp_porta_linux = 25
	smtp_porta_windows = 587
	msg = MIMEMultipart()
	msg['From'] = strUserEmailFrom
	msg['To'] = ", ".join(mail_to)
	msg['Subject'] = strTituloMsg
	
	for imgDict in listDictImagens:
		try:
			part = MIMEBase('application',"octet-stream")
			part.set_payload(open(imgDict['path'],"rb").read())
			Encoders.encode_base64(part)
			part.add_header('Content-Disposition','attachment; filename ="%s"' %imgDict['title'])
							#% imgDict['Title']))	
			#msg_image = MIMEText(file(imgDict['path']).read())
		except:
			#print imgDict['title']
			sys.exit()
		time.sleep(3)	
		msg.attach(part)
        	
	strTitulo = 'BackTest DECOMP'
	now = datetime.today()
    
	htm_BodyMsg = Montar_Corpo_da_Mensagem_HTML(strTitulo,now.strftime("%d/%m/%Y %H:%M:%S"))
	part = MIMEText(htm_BodyMsg,'html')
	
	msg.attach(part)

	time.sleep(10)
	if(os.name =='posix'):
		mailServer = smtplib.SMTP(smtp_host, smtp_porta_linux)
	else:
		mailServer = smtplib.SMTP(smtp_host, smtp_porta_windows)
	mailServer.ehlo()
	mailServer.starttls()
	mailServer.ehlo()
	#Login no GMAIL
	mailServer.login(strUserLogin,strPass)
	#Envia msg
	mailServer.sendmail(strUserEmailFrom, mail_to,msg.as_string())
	mailServer.close()

def Montar_Corpo_da_Mensagem_HTML(strTitulo,strDataRodada):

	## MONTANDO O CORPO DA MENSAGEM:
    htm_BodyMsg = ''
	##Corpo da Mensagem
    htm_BodyMsg = """
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
      <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">

      <head>
        <title>[TITULO_MSG]</title>
      </head>
	
      <body>
      <br/>
      <h4>Rodado no Servidor Linux BRAZRPPENEPRD </h4>
      <h5>Data e Hor&aacute;rio do envio:  [DT_RODADA]</h5>
	  
      <br>
     
  
      
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Email est&aacute; programado para ser enviado automaticamente <br>
      &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;pela Ger&ecirc;ncia de Estudos Energ&eacute;ticos da EDP.

    
     </body>
	 </br>
	  </html>"""

    htm_BodyMsg = htm_BodyMsg.replace('[TITULO_MSG]',strTitulo)
    htm_BodyMsg = htm_BodyMsg.replace('[DT_RODADA]',strDataRodada)
    
    return htm_BodyMsg
def Leitura_Saida(pathSaida):
    try:
        file = open(pathSaida,'r')
        info_dados = csv.reader(file,delimiter = ';')
    except:
        #print 'nao foi encontrado arquivo de saida: ' +pathSaida
        sys.exit()
    listDados =[]
    for linha in info_dados:
        listLinha =[]
        for coluna in linha:
            try:
                listLinha.append(float(coluna))
            except:
		if len(coluna)>1:
                    listLinha.append(coluna)
        listDados.append(listLinha)
    
    rv = listDados[0][0]
    mes = listDados[0][1]
    dataEDP = listDados[0][2]
    
    # info1
    rv = int(rv)
    strMes = Nome_Mes(int(mes))
    strInfo1 = 'RV'+str(rv)+' de '+strMes
        
    # info2
    strInfo2 ='Data do Deck EDP: '+dataEDP
    info = [strInfo1,strInfo2]
    dados = listDados[1:]
    
    return info,dados


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
