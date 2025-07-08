# -*- coding: utf-8 -*-

from datetime import date
from datetime import datetime, timedelta
import os 
import shutil
from time import sleep
import locale
import zipfile
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

from wx_decomp import *
from wx_opweek import *




def main():
	pathOut  =  '/WX/WX2TB/Documentos/fontes/PMO/backTest_DC/input/oficial/decomp/'
	pathIn   =  '../input'

	data = date.today()
	datarev = ElecData(getLastSaturday(data) + timedelta(days=7))
	rev = 'RV{}'.format(int(datarev.atualRevisao))

	dt_decomp = datarev.primeiroDiaMes + timedelta(days=6)
	data = data.strftime('%Y%m%d')	
	
	arqzip = 'PMO_deck_preliminar.zip'
	arqdec = 'DEC_ONS_' + dt_decomp.strftime('%m%Y') + '_' + rev + '_VE.zip'

	if os.path.exists(pathIn + '/' + arqzip):
		print(arqzip + ' encontrado!')

		# DECOMP
		shutil.rmtree(pathOut , ignore_errors=True)
		cria_diretorio(pathOut)

		try:
			with zipfile.ZipFile(pathIn + '/' + arqzip, 'r') as zip_ref:
				zip_ref.extractall(pathIn + '/')
			sleep(2)
		except:
			print("Nao foi possivel dezipar arquivo PMO_deck_preliminar")
		try:
			with zipfile.ZipFile(pathIn + '/' + arqdec, 'r') as zip_ref:
				zip_ref.extractall(pathOut)
			sleep(2)
		except:
			print("Nao foi possivel dezipar arquivo DEC_ONS_")

		for arquivo in os.listdir(pathOut):
			if 'dadger' in arquivo.lower():
				dadger = pathOut + arquivo
				dadgercp = pathOut + arquivo + 'cp'

			if 'dadgnl' in arquivo.lower():
				dadgnl = pathOut + arquivo	
				dadgnlcp = pathOut + arquivo + 'cp'

		try:
			shutil.copy(dadgnl,dadgnlcp)
		except:
			print("Nao foi possivel fazer copia DADGNL")

		try:
			shutil.copy(dadger,dadgercp)
		except:
			print("Nao foi possivel fazer copia DADGER")

		# comenta dadger e dadgnl para PLD
		comenta_dadger(dadgercp,dadger,rev,dt_decomp)

		# comenta_dadgnl(dadgnlcp,dadgnl)
		comenta_dadgnl(dadgnlcp,dadgnl)

		try:
			os.remove(dadgercp)
		except:
			print("Arquivo DADGERcp nao encontrado")
		try:
			os.remove(dadgnlcp)
		except:
			print("Arquivo DADGNLcp nao encontrado")

		shutil.make_archive(pathOut, 'zip', pathOut)
		#shutil.copytree(pathOut + '/DC' + dt_decomp.strftime('%Y%m') + '-' + rev, '/WX/WX2TB/Documentos/fontes/PMO/backTest_DC/input/oficial/decomp')
		shutil.rmtree(pathIn)
		cria_diretorio(pathIn)

	else:
		print('Arquivo ' + arqzip + ' ainda nao disponivel!')
		print('SAINDO')
		quit()
		# print('Vou aguardar uns minutos e tentar novamente')
		# sleep(60*3)


main()