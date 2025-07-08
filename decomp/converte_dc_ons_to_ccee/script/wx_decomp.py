# -*- coding: utf-8 -*-

import os 
import glob
import shutil
import locale
from datetime import date, datetime, timedelta
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

def copia_arquivos(arquivos_copia,path_dropbox, nomesMaiusculos=False):

	for file_path in (glob.glob(arquivos_copia)):
		try:
			f = file_path.split('/')[-1]
			arquivosCaixaBaixa = 'polinjus.dat'
			if nomesMaiusculos and f not in arquivosCaixaBaixa:
				f = f.upper()
			shutil.copy(file_path,path_dropbox + '/' + f)
		except Exception as e:
			print("Nao foi possivel copiar arquivo " + file_path)
			print(e)

def cria_diretorio(path):
	try:
		os.mkdir(path)
	except OSError as error:  
		print(error)

def comenta_dadger(dadgerin,dadgerout,rev,dt_decomp):
	restricoes=["141","143","145","147","272","449","451","453","464","470","471","501","503","505","509",
			"513","515","517","519","521","525","527","529","531","533","535","537","539","541","543","545",
			"547","561","562","564","570","571","604","606","608","654","611","612", "613","614","615"]
		
	dadger_in = open(dadgerin,'r')
	dadger_out = open(dadgerout,'w')
	lin = dadger_in.readlines()
	for i in range(len(lin)):
		if lin[i][:2] == 'TE':
			dadger_out.write("TE  {} - {} - COMENTADO PLD - Rodada Automatica WX\n".format(rev, dt_decomp.strftime('%B/%Y')))
		elif lin[i][:2] in ["RE", "FU", "LU","FT", "FI"]:
			if lin[i][4:7] in restricoes:
				dadger_out.write("&" + lin[i])
			else:
				dadger_out.write(lin[i])			
		else:
			dadger_out.write(lin[i])			

	dadger_in.close()
	dadger_out.close()

def comenta_dadgnl(dadgnlin,dadgnlout):

	fin_dadgnl = open(dadgnlin, 'r')
	fou_dadgnl = open(dadgnlout, 'w')
	lin = fin_dadgnl.readlines()
	flag = 0
	for i in range(len(lin)):
		if 'eletrica' in lin[i][:]:
			print(' linha: ' + str(i+1) + ' Encontrado ' + lin[i])
			flag = 1
			fou_dadgnl.write('& Bloco alterado na conversao WX\n')

		elif 'merito' in lin[i][:]:
			print(' linha: ' + str(i+1) + ' Encontrado ' + lin[i])
			flag = 0
			fou_dadgnl.write('& Bloco nao alterado na conversao WX\n')
		
		if flag == 1 and lin[i][:1] != "&":
			lista_lin=list(lin[i])
			for ii in [0,15,30]:
				lista_lin[23+ii]='0';lista_lin[24+ii]='0';lista_lin[25+ii]='0';
				lista_lin[26+ii]='0';lista_lin[27+ii]='.';lista_lin[28+ii]='0'
				lin[i]= "".join(lista_lin)
		
		fou_dadgnl.write(lin[i])
	fin_dadgnl.close()
	fou_dadgnl.close()


def getNextFriday(data):
    dataReturn = data
    if data.isoweekday() == 7:
        dataReturn = data + timedelta(days= 5)
    elif data.isoweekday() == 6:
        dataReturn = data + timedelta(days= 6)
    else :
        dataReturn = data + timedelta(days= 5 - data.isoweekday())
    return dataReturn

#if __name__ == '__main__':
	

