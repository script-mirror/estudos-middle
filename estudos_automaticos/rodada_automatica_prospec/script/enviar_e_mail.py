import os
import sys
from datetime import datetime, timedelta
import pandas as pd
'''
pathOutBase = '/WX2TB/Documentos/fontes/PMO/API_Prospec/DownloadResults/'
limparConfig_1rv = True
pathDadosEmail = '/WX/WX2TB/Documentos/fontes/PMO/rodada_automatica_prospec/input/Config/configEmail_1rv.csv'

configEmail = pd.DataFrame({'prevName':["PCONJ+ECext-ENS0612-80GDE-PB-SF-N",
                                        "PCONJ+ECext-ENS0612-80GDE-PB-SF_Dia",
                                        "PCONJ+ECext-ENS0612-80GDE-PB",
                                        "ECext-ENS0612-100SIN",
                                        "ECext-ENS0612-80SF",
                                        "ECext-ENS0612-80N",
                                        "ECext-ENS0612-80GDE-PB-SF",
                                        "ECext-ENS0612-80GDE-PB-SF-N"], 
                             'pathName':['Estudo_7418_compilation.zip','Estudo_7417_compilation.zip',
                                         'Estudo_7416_compilation.zip','Estudo_7415_compilation.zip',
                                         'Estudo_7414_compilation.zip','Estudo_7413_compilation.zip',
                                         'Estudo_7412_compilation.zip','Estudo_7411_compilation.zip'  ]})

if limparConfig_1rv: configEmail.to_csv(pathDadosEmail, mode='w', index=False, header=True, sep = ";")
else:                configEmail.to_csv(pathDadosEmail, mode='a', index=False, header=False, sep = ";")

configEmail = pd.read_csv(pathDadosEmail, sep = ";")

print(configEmail)
prevName = []
pathName = []
for index in configEmail.index:
    prevName.append(configEmail.loc[index]['prevName']) 
    pathName.append( pathOutBase + configEmail.loc[index]['pathName']) 

print(prevName)
print(pathName)

prevName = ["Original"]
prospec_out = [ "Estudo_8463_Compilacao.zip"]
pathResult = '/WX2TB/Documentos/fontes/PMO/API_Prospec/DownloadResults/'
parametros = {}
parametros['data'] = datetime.now()


dataInicial = (datetime.now() - timedelta(days=2))
print(dataInicial)
pathDadosEmail = '/WX/WX2TB/Documentos/fontes/PMO/rodada_automatica_prospec/input/Config/configEmail_Pconj.csv'

configEmail = pd.read_csv(pathDadosEmail, sep = ";")
df = pd.DataFrame({'dataRodada':[parametros['data'].strftime('%d/%m/%Y')],'prevName':[prevName[0]+'_' +parametros['data'].strftime('%d/%m')], 'pathName':[prospec_out[0]]})
print(df)
configEmail = configEmail.append(df, ignore_index=True)
print(configEmail)
configEmail['dataRodada'] = pd.to_datetime(configEmail['dataRodada'])

configEmail = configEmail.loc[configEmail['dataRodada'] >= dataInicial]
#configEmail.to_csv(pathDadosEmail, mode='w', index=False, header=True, sep = ";")

prevName = []
pathName = []
for index in configEmail.index:
    prevName.append(configEmail.loc[index]['prevName']) 
    pathName.append( pathResult  + configEmail.loc[index]['pathName']) 
'''
prevName = ["ENS"]
pathName = [ "/WX2TB/Documentos/fontes/PMO/API_Prospec/DownloadResults/Estudo_9059_Compilacao.zip"]


#listMail     = '["front@wxe.com.br", "middle@wxe.com.br"]'
listMail     = '["gilseu.muhlen@raizen.com"]'
assuntoEmail =  'Rodada Prevs Pluvia EC-EXT dia 31/01/2021'
corpoEmail   = "Rodada EC-EXT dia 31/01/2021"
print(prevName)
print (pathName)

cmd = ". /WX2TB/Documentos/fontes/PMO/scripts_unificados/env_activate;"
cmd += "cd /WX2TB/Documentos/fontes/PMO/scripts_unificados/apps/gerarProdutos;"
cmd += "python gerarProdutos.py produto RESULTADOS_PROSPEC nomeRodadaOriginal {} destinatarioEmail '{}' assuntoEmail '{}' corpoEmail '{}' path {};".format('"{}"'.format(prevName), str(listMail), str(assuntoEmail), str(corpoEmail),  '"{}"'.format(pathName))
os.system(cmd)
sys.exit()

prevName = ["080-050-080-100"]
pathName = [ "/WX2TB/Documentos/fontes/PMO/API_Prospec/DownloadResults/Estudo_7460_Compilacao.zip"]

#Enviando e-mail
# --------------------------------------------------------------------------------------------# 
listMail     = '["gilseu.muhlen@raizen.com", "celso.trombetta@raizen.com"]'
assuntoEmail =  'Rodada Sensibilidade Norte Janeiro/2022' 
corpoEmail   = 'Rodada Sensibilidade Norte Janeiro/2022' 

print("#Enviando os resultados por email-------------------------------------------#")
cmd = ". /WX2TB/Documentos/fontes/PMO/scripts_unificados/env_activate;"
cmd += "cd /WX2TB/Documentos/fontes/PMO/scripts_unificados/apps/gerarProdutos;"
cmd += "python gerarProdutos.py produto RESULTADOS_PROSPEC nomeRodadaOriginal {} destinatarioEmail '{}' assuntoEmail '{}' corpoEmail '{}' path {};".format('"{}"'.format(prevName), str(listMail), str(assuntoEmail), str(corpoEmail),  '"{}"'.format(pathName))
print (cmd)
os.system(cmd)

#cmd += "python gerarProdutos.py produto RESULTADOS_PROSPEC nomeRodadaOriginal '{}' destinatarioEmail '{}' assuntoEmail '{}' corpoEmail '{}' path {}'{}';".format(prevName[0], str(listMail), str(assuntoEmail), str(corpoEmail), "/WX2TB/Documentos/fontes/PMO/API_Prospec/DownloadResults/", prospec_out[0])


#python gerarProdutos.py produto RESULTADOS_PROSPEC nomeRodadaOriginal "['ecmwf_ens-wx','ecmwf_ens-wx2']" path "['/WX2TB/Documentos/fontes/PMO/API_Prospec/DownloadResults/Estudo_7405_compilation.zip','/WX2TB/Documentos/fontes/PMO/API_Prospec/DownloadResults/Estudo_7407_compilation.zip']" considerarPrevs "[0]" destinatarioEmail "['thiago@wxe.com.br']"
