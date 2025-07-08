# -*- coding: utf-8 -*-

import pdb
from datetime import date
from datetime import datetime, timedelta
import os 
import glob
import shutil
import threading
import subprocess
from time import sleep
import locale
import zipfile
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
import sys
from wx_decomp import *

# Add o diretorio das bibliotecas da WX
sys.path.insert(1, sys.path[0] + "/libs/")
from wx_opweek import ElecData
from wx_opweek import getLastSaturday


path_cv = '/home/wxenergy/Dropbox/WX - Middle/Chuva-vazão'
path_cv = '/home/wxenergy/WX Energy Dropbox/WX - Middle/Chuva-vazão'

gevazp_exe = '/home/wxenergy/Documentos/Programas/Gevazp/gevazp_8_Linux'
base_DC = '/WX4TB/Documentos/fontes/PMO/decomp/entradas/decomp'
saida = '/WX4TB/Documentos/fontes/PMO/decomp/saidas'
path_temp = '/WX4TB/Documentos/fontes/PMO/decomp/temporarios'
temp_DC = path_temp + '/decomp'
temp_gevazp = path_temp + '/gevazp'


path_ve = '/WX4TB/Documentos/fontes/PMO/decomp/entradas/DC_preliminar'
saida = '/WX4TB/Documentos/fontes/PMO/decomp/saidas'

while True:

	data = date.today()
	# data = data - timedelta(days=14)
	# pdb.set_trace()

	datarev = ElecData(getLastSaturday(data) + timedelta(days=7))
	rev = 'RV{}'.format(int(datarev.atualRevisao))
	rzin = 'rv{}'.format(int(datarev.atualRevisao))
	if rev == 'RV0':
		revarq = 'PMO'
	else:
		revarq = 'REV{}'.format(int(datarev.atualRevisao))
	
	dt_decomp = datarev.primeiroDiaMes + timedelta(days=6)
	data = data.strftime('%Y%m%d')
	# arqzip = 'Nao_Consistido_202007_PMO.zip'
	# rev = 'RV0'

	arqzip = 'Nao_Consistido_' + dt_decomp.strftime('%Y%m') + '_' + revarq + '.zip'

	if os.path.exists(path_ve + '/' + arqzip):
		print(arqzip + ' encontrado!')
		cria_diretorio(saida + '/' + data)
		# DADOS para GEVAZP
		diretorio_GEVAZP(temp_gevazp + '/' + data,base_DC + '/DC' + dt_decomp.strftime('%Y%m') + '-' + rev+ '/*',gevazp_exe + '/*', rev)	

		try:
			with zipfile.ZipFile(path_ve + '/' + arqzip, 'r') as zip_ref:
				zip_ref.extractall(temp_gevazp + '/' + data + '/')
			sleep(4)
		except:
			print("Nao foi possivel dezipar arquivo")
		shutil.copy(temp_gevazp + '/' + data + '/Nao_Consistido/Prevs_VE.prv',temp_gevazp + '/' + data + '/PREVS.' + rev)		
		
		# pdb.set_trace()
		# Roda GEVAZP
		thread_run(temp_gevazp + '/' + data +'/', rodagevazp)
		shutil.copy(temp_gevazp + '/' + data + '/VAZOES.' + rev,saida + '/' + data + '/VAZOES_VE.' + rev)
		shutil.copy(temp_gevazp + '/' + data + '/Nao_Consistido/Prevs_VE.prv',saida + '/' + data + '/')
		
		# DECOMP
		diretorio_DC(temp_DC + '/DC' + dt_decomp.strftime('%Y%m') + '-' + rev, base_DC + '/DC' + dt_decomp.strftime('%Y%m') + '-' + rev+ '/*')	
		
		dadger_in = open(base_DC + '/DC' + dt_decomp.strftime('%Y%m') + '-' + rev+ '/DADGER.' + rev,'r')
		dadger_out = open(temp_DC + '/DC' + dt_decomp.strftime('%Y%m') + '-' + rev+ '/DADGER.' + rev,'w')
		lin = dadger_in.readlines()
		for i in range(len(lin)):
			if lin[i][:2] == 'TE':
				dadger_out.write("TE  {} - {} - Nao Consistido - Rodada Automatica WX\n".format(rev, dt_decomp.strftime('%B/%Y')))
			else:
				dadger_out.write(lin[i])			

		dadger_in.close()
		dadger_out.close()

		shutil.copy(temp_gevazp + '/' + data + '/Nao_Consistido/Prevs_VE.prv',temp_DC + '/DC' + dt_decomp.strftime('%Y%m') + '-' + rev + '/PREVS.' + rev)
		shutil.copy(temp_gevazp + '/' + data + '/Nao_Consistido/Prevs_VE.prv',path_ve + '/PREVS.' + rev)
		shutil.copy(temp_gevazp + '/' + data + '/VAZOES.' + rev,temp_DC + '/DC' + dt_decomp.strftime('%Y%m') + '-' + rev)
		
		# RODANDO DECOMP
		thread_run(temp_DC + '/DC' + dt_decomp.strftime('%Y%m') + '-' + rev + '/', rodaDC)
		if os.path.exists(temp_DC + '/DC' + dt_decomp.strftime('%Y%m') + '-' + rev + '/relato.' + rzin):
			print('Rodada NAOCONSISTIDO rev : ' + rev + ' Concluida com sucesso!')
			try:
				os.remove(path_ve + '/' + arqzip)
			except:
				print("Arquivo " + arqzip + " nao encontrado")
			quit()
			
							

	else:
		print('Arquivo ' + arqzip + ' ainda nao disponivel!')
		print('SAINDO')
		quit()
		# print('Vou aguardar uns minutos e tentar novamente')
		# sleep(60*3)
	
	# pdb.set_trace()
