import re
import os
import locale
import shutil
import zipfile
import datetime
import base64
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
import shutil
from middle.utils import SemanaOperativa
from middle.utils import HtmlBuilder
from middle.message import send_whatsapp_message, send_email_message
from middle.utils import html_to_image
from middle.utils.constants import Constants 
consts = Constants()
locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')
os.makedirs(consts.PATH_ARQUIVOS, exist_ok=True)

SUBMERCADOS = ['SUDESTE', 'SUL', 'NORDESTE', 'NORTE']

def extract_files(compilado_zipado):
	zip_name_file = os.path.basename(compilado_zipado)
	path = os.path.dirname(compilado_zipado)
	dst_folder = os.path.join(path, zip_name_file.split('.')[0])

	if os.path.exists(dst_folder):
		shutil.rmtree(dst_folder)

	if not os.path.exists(dst_folder):
		os.makedirs(dst_folder)

	with zipfile.ZipFile(compilado_zipado, 'r') as zip_ref:
		zip_ref.extractall(dst_folder)

	return dst_folder


def remove_dir(compilado_zipados):
    
	for compilado_zipado in compilado_zipados:
		zip_name_file = os.path.basename(compilado_zipado)
		path = os.path.dirname(compilado_zipado)
		dst_folder = os.path.join(path, zip_name_file.split('.')[0])

		try:
			shutil.rmtree(dst_folder)
			print('Diretorio deletado com sucesso: ', dst_folder)
		except:
			print('Não foi possivel deletar o diretorio: ', dst_folder)
			pass

		try:
			os.remove(compilado_zipado)
			print('Diretorio deletado com sucesso: ', compilado_zipado)
		except:
			print('Não foi possivel deletar o diretorio: ', compilado_zipado)
			pass


def gerar_resultados(params):    

	html_builder = HtmlBuilder()
	if params['prevs_name'] == None:
		params['prevs_name'] = [''] * len(params['path_name'])

	dir_saida = os.path.join(consts.PATH_ARQUIVOS, 'prospec', 'resultados', 'tmp')
	os.makedirs(dir_saida, exist_ok=True)

	compila_ena = pd.DataFrame()
	compila_ea_inicial = pd.DataFrame()
	compila_cmo_medio = pd.DataFrame()
	compila_preco_medio_nw = pd.DataFrame()
	compila_ena_percentual_mensal = pd.DataFrame()
	compila_ena_mensal = pd.DataFrame()
	compila_gap_mensal = pd.DataFrame()

	num_estudo = []
	contem_nw = True
	for i, compil in enumerate(params['path_name']):
		path_compilado = extract_files(os.path.abspath(compil))
		nome_estudo = os.path.basename(path_compilado)
		print(nome_estudo)
		match = re.match('Estudo_([0-9]{1,})_compilation', nome_estudo)
		numero_estudo = match.group(1)
		num_estudo.append(numero_estudo)

		df = pd.read_csv(os.path.join(path_compilado, 'compila_cmo_medio.csv'), sep=';')
		df['Sensibilidade'] = df['Sensibilidade'].replace({'Original': params['prevs_name'][i]})

		if len(df[df['Deck'].str.contains('NW')]) == 0:
			contem_nw = False

		df.loc[df['Deck'].str.contains('DC'), 'MEN=0-SEM=1'] = 1

		df_mensal = df[df['MEN=0-SEM=1'] == 0].copy()
		df = df[df['MEN=0-SEM=1'] == 1]
		df['Sensibilidade'] = df['Sensibilidade'] + '_id' + numero_estudo

		if params['media_rvs']:
			df['Deck_'] = df['Deck'].str[:-3]
			for deck_, dados in df.groupby('Deck_').mean().iterrows():
				df.loc[df['Deck'] == '{}_s1'.format(deck_), 'SUDESTE'] = dados['SUDESTE']
				df.loc[df['Deck'] == '{}_s1'.format(deck_), 'SUL'] = dados['SUL']
				df.loc[df['Deck'] == '{}_s1'.format(deck_), 'NORDESTE'] = dados['NORDESTE']
				df.loc[df['Deck'] == '{}_s1'.format(deck_), 'NORTE'] = dados['NORTE']

		compila_cmo_medio = pd.concat([compila_cmo_medio, df])

		df_nw = df.copy()
		df_nw['mes_NW'] = df_nw['Deck'].str[2:8]
		df_nw.set_index('mes_NW', inplace=True)

		df_mensal['mes_NW'] = df_mensal['Deck'].str[2:8]
		df_mensal.set_index('mes_NW', inplace=True)
		df_mensal.drop(['Deck', 'Sensibilidade', 'MEN=0-SEM=1'], axis=1, inplace=True)

		df_nw.update(df_mensal)
		compila_preco_medio_nw = pd.concat([compila_preco_medio_nw, df_nw])

		df = pd.read_csv(os.path.join(path_compilado, 'compila_ea_inicial.csv'), sep=';')
		df['Sensibilidade'] = df['Sensibilidade'].replace({'Original': params['prevs_name'][i]})
		df.loc[df['Deck'].str.contains('DC'), 'MEN=0-SEM=1'] = 1

		df = df[df['MEN=0-SEM=1'] == 1]
		df['Sensibilidade'] = df['Sensibilidade'] + '_id' + numero_estudo
		compila_ea_inicial = pd.concat([compila_ea_inicial, df])

		df = pd.read_csv(os.path.join(path_compilado, 'compila_ena.csv'), sep=';')
		df['Sensibilidade'] = df['Sensibilidade'].replace({'Original': params['prevs_name'][i]})
		df.loc[df['Deck'].str.contains('DC'), 'MEN=0-SEM=1'] = 1

		df = df[df['MEN=0-SEM=1'] == 1]
		df['Sensibilidade'] = df['Sensibilidade'] + '_id' + numero_estudo
		compila_ena = pd.concat([compila_ena, df])

		df = pd.read_csv(os.path.join(path_compilado, 'compila_ena_mensal_percentual.csv'), sep=';')
		df['Sensibilidade'] = df['Sensibilidade'].replace({'Original': params['prevs_name'][i]})
		df.loc[df['Deck'].str.contains('DC'), 'MEN=0-SEM=1'] = 1

		df = df[df['MEN=0-SEM=1'] == 1]
		df['Sensibilidade'] = df['Sensibilidade'] + '_id' + numero_estudo
		compila_ena_percentual_mensal = pd.concat([compila_ena_percentual_mensal, df])

		df = pd.read_csv(os.path.join(path_compilado, 'compila_ena_mensal.csv'), sep=';')
		df['Sensibilidade'] = df['Sensibilidade'].replace({'Original': params['prevs_name'][i]})
		df.loc[df['Deck'].str.contains('DC'), 'MEN=0-SEM=1'] = 1

		df = df[df['MEN=0-SEM=1'] == 1]
		df['Sensibilidade'] = df['Sensibilidade'] + '_id' + numero_estudo
		compila_ena_mensal = pd.concat([compila_ena_mensal, df])

		df = pd.read_csv(os.path.join(path_compilado, 'compila_convergencia.csv'), sep=';')
		df['Sensibilidade'] = df['Sensibilidade'].replace({'Original': params['prevs_name'][i]})
		df.loc[df['Deck'].str.contains('DC'), 'MEN=0-SEM=1'] = 1
		df_nw = df[df['Deck'].str.startswith('NW')].set_index('Deck')
		df_dc = df[df['Deck'].str.startswith('DC')].copy()
		df_dc['NW_Group'] = 'NW' + df_dc['Deck'].str[2:8]

		iter_gap_strings = []
		for nw_key, group in df_dc.groupby('NW_Group'):
			if nw_key in df_nw.index:
				nw_row = df_nw.loc[nw_key]
				fixed_part = f"{round(nw_row['GapOuDeltaZinf'], 3)}-{nw_row['NumeroDeIteracoes']}"
				for _, dc_row in group.iterrows():
					dc_gap_value = round(dc_row['GapOuDeltaZinf'], 3)
					iter_gap_string = f"{fixed_part}/{dc_gap_value}-{dc_row['NumeroDeIteracoes']}"
					if dc_gap_value < 0:
						iter_gap_string = f"<span style='color:red;'>{iter_gap_string}</span>"
					iter_gap_strings.append(iter_gap_string)
			else:
				iter_gap_strings.extend([None] * len(group))

		df_dc['iter_gap'] = iter_gap_strings
		df_dc['Sensibilidade'] = df_dc['Sensibilidade'] + '_id' + numero_estudo
		compila_gap_mensal = pd.concat([compila_gap_mensal, df_dc])



	if params['considerar_rv'] != '':
		compila_cmo_medio = compila_cmo_medio[compila_cmo_medio['Deck'].str.contains(params['considerar_rv'])]
		compila_preco_medio_nw = compila_preco_medio_nw[compila_preco_medio_nw['Deck'].str.contains(params['considerar_rv'])]
		compila_ea_inicial = compila_ea_inicial[compila_ea_inicial['Deck'].str.contains(params['considerar_rv'])]
		compila_ena = compila_ena[compila_ena['Deck'].str.contains(params['considerar_rv'])]
		compila_ena_mensal = compila_ena_mensal[compila_ena_mensal['Deck'].str.contains(params['considerar_rv'])]
		compila_ena_percentual_mensal = compila_ena_percentual_mensal[compila_ena_percentual_mensal['Deck'].str.contains(params['considerar_rv'])]
		if params['media_rvs']:
			compila_cmo_medio = compila_cmo_medio[compila_cmo_medio['Deck'].str.contains('s1')]
			compila_preco_medio_nw = compila_preco_medio_nw[compila_preco_medio_nw['Deck'].str.contains('s1')]
			compila_ea_inicial = compila_ea_inicial[compila_ea_inicial['Deck'].str.contains('s1')]
			compila_ena = compila_ena[compila_ena['Deck'].str.contains('s1')]
			compila_ena_mensal = compila_ena_mensal[compila_ena_mensal['Deck'].str.contains('s1')]
			compila_ena_percentual_mensal = compila_ena_percentual_mensal[compila_ena_percentual_mensal['Deck'].str.contains('s1')]

	dicionario_decks = {}
	x_label = []
	for dk in compila_cmo_medio['Deck'].unique():
		mes, sem, encadeamento = re.findall('[0-9]+', dk)
		inicio_mes_eletrico = SemanaOperativa.get_last_saturday(datetime.datetime.strptime(mes, '%Y%m').date())
		dt = SemanaOperativa(inicio_mes_eletrico + datetime.timedelta(days=7 * (int(sem) + int(encadeamento) - 2)))
		dicionario_decks[dk] = dt.date
		label = 'DC_{}-rv{}'.format(dt.date.strftime('%Y%m'), dt.current_revision)
		if label not in x_label:
			x_label.append(label)

	compila_cmo_medio['Deck'] = compila_cmo_medio['Deck'].replace(dicionario_decks)
	compila_preco_medio_nw['Deck'] = compila_preco_medio_nw['Deck'].replace(dicionario_decks)
	compila_ea_inicial['Deck'] = compila_ea_inicial['Deck'].replace(dicionario_decks)
	compila_ena['Deck'] = compila_ena['Deck'].replace(dicionario_decks)
	compila_ena_percentual_mensal['Deck'] = compila_ena_percentual_mensal['Deck'].replace(dicionario_decks)

	def replace_if_contains(value):
		for key, new_value in dicionario_decks.items():
			if value in key:
				return new_value
		return value

	compila_gap_mensal['Deck'] = compila_gap_mensal['Deck'].apply(replace_if_contains)

	cmo = {}
	preco_nw = {}
	ear = {}
	ena = {}
	ena_percent_mensal = {}

	ordem = compila_ena_mensal['Sensibilidade'].unique().tolist()

	path_file_out = os.path.join(dir_saida, 'rodadas.png')
	fig = plt.figure(figsize=(12, 6))

	for sub in SUBMERCADOS:
		cmo[sub] = compila_cmo_medio.pivot(index='Sensibilidade', columns='Deck', values=sub).reindex(ordem)
		preco_nw[sub] = compila_preco_medio_nw.pivot(index='Sensibilidade', columns='Deck', values=sub).reindex(ordem)
		ear[sub] = compila_ea_inicial.pivot(index='Sensibilidade', columns='Deck', values=sub).reindex(ordem)
		ena[sub] = compila_ena.pivot(index='Sensibilidade', columns='Deck', values=sub).reindex(ordem)
		ena_percent_mensal[sub] = compila_ena_percentual_mensal.pivot(index='Sensibilidade', columns='Deck', values=sub).reindex(ordem)

		if sub == 'SUDESTE':
			cmo_aux = []
			sens = []
			for key in cmo[sub].T.keys():
				cmo_aux.append(cmo[sub].T[key].values.tolist())
				sens.append(key)

		cmo[sub] = cmo[sub].applymap(lambda x: "{:.0f}".format(x).replace('.', ','))
		preco_nw[sub] = preco_nw[sub].applymap(lambda x: "{:.0f}".format(x).replace('.', ','))
		ear[sub] = ear[sub].applymap(lambda x: "{:.1f}".format(x).replace(',', '.'))
		ena[sub] = ena[sub].applymap(lambda x: "{:.1f}".format(x / 1000))
		ena_percent_mensal[sub] = ena_percent_mensal[sub].applymap(lambda x: "{:.0f}".format(x).replace('.', ','))

		ena_percent_mensal[sub] = ena_percent_mensal[sub].reindex(columns=cmo[sub].columns)

	compila_gap_mensal = compila_gap_mensal.pivot(index='Sensibilidade', columns='Deck', values='iter_gap').reindex(ordem)

	considerar_prevs = ''
	if considerar_prevs == '':
		dt_rvs = cmo['SUDESTE'].columns
	else:
		dt_rvs = eval('cmo[\'SUDESTE\'].columns' + considerar_prevs)
		if type(dt_rvs) == str:
			dt_rvs = [dt_rvs]
		if type(dt_rvs) == datetime.date:
			dt_rvs = [dt_rvs]

	dts = []
	cmo_resumo = pd.DataFrame()
	preco_nw_resumo = pd.DataFrame()
	ear_resumo = pd.DataFrame()
	enas_resumo = pd.DataFrame()
	enas_mensais_resumo = pd.DataFrame()
	gap_iter_resumo = pd.DataFrame()

	legend_grafico = []
	for dt in dt_rvs:
		dt = SemanaOperativa(dt)
		dts.append(dt)
		dt_rv = datetime.datetime(dt.ref_year, dt.ref_month, 1)
		legend_grafico.append('{} - RV{}'.format(dt_rv.strftime('%b/%y'), int(dt.current_revision)))
		data_rodada_html = '{} - RV{}'.format(dt_rv.strftime('%b/%y'), int(dt.current_revision))

		for sub in SUBMERCADOS:
			if sub == 'SUDESTE':
				ear_resumo[data_rodada_html] = ear[sub][dt.date].astype('str')
				cmo_resumo[data_rodada_html] = cmo[sub][dt.date].astype('str')
				enas_resumo[data_rodada_html] = ena[sub][dt.date].astype('str')
				preco_nw_resumo[data_rodada_html] = preco_nw[sub][dt.date].astype('str')
				enas_mensais_resumo[data_rodada_html] = ena_percent_mensal[sub][dt.date].astype('str')
			else:
				ear_resumo[data_rodada_html] += '-' + ear[sub][dt.date].astype('str')
				cmo_resumo[data_rodada_html] += '-' + cmo[sub][dt.date].astype('str')
				enas_resumo[data_rodada_html] += '-' + ena[sub][dt.date].astype('str')
				preco_nw_resumo[data_rodada_html] += '-' + preco_nw[sub][dt.date].astype('str')
				enas_mensais_resumo[data_rodada_html] += '-' + ena_percent_mensal[sub][dt.date].astype('str')

		try:
			gap_iter_resumo[data_rodada_html] = compila_gap_mensal[dt.date]
		except:
			gap_iter_resumo[data_rodada_html] = '-'

	gap_iter_resumo = gap_iter_resumo.fillna('-')

	titulo_grafico = 'PLD SE ({})'.format(datetime.datetime.now().strftime('%d/%m/%Y'))
	fig = plt.figure(figsize=(12, 6))
	fig.add_axes([0.05, 0.2, 0.75, 0.7])
	for lista in cmo_aux:
		plt.plot(lista)
	plt.gca().set_xticks(np.arange(len(cmo_aux[0])))
	plt.gca().set_xticklabels(legend_grafico)
	plt.gca().legend(sens, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=7)
	plt.title(titulo_grafico)
	plt.xticks(rotation=90)
	plt.ylabel("R$")
	plt.xlabel("RV")
	plt.grid()
	plt.savefig(path_file_out)

	resumo_tabela1 = enas_mensais_resumo + '<br>' + ear_resumo + '<br>' + enas_resumo + '<br>' + gap_iter_resumo + '<br>' + preco_nw_resumo + '<br>' + cmo_resumo
	resumo_tabela1.insert(0, "", ['ENA-Mês(%)<br>EAR(%)<br>ENA-S1(GW)<br>GAP-IT(NW/DC)<br>PLD NW(R$)<br>PLD DC(R$)'] * resumo_tabela1.shape[0])

	if not contem_nw:
		print('ESTUDO SERÁ ENVIADO SEM OS DADOS DO NEWAVE, POIS ALGUM DOS ESTUDOS CONTÉM APENAS DECOMP')
		resumo_tabela1 = enas_mensais_resumo + '<br>' + ear_resumo + '<br>' + enas_resumo + '<br>' + cmo_resumo
		resumo_tabela1.insert(0, "", ['ENA-Mês(%)<br>EAR(%)<br>ENA-S1(GW)<br>PLD DC(R$)'] * resumo_tabela1.shape[0])

	resumo_tabela1 = resumo_tabela1.fillna('-')
	resumo_tabela1 = resumo_tabela1.applymap(lambda x: x.replace('nan-nan-nan-nan', '-') if isinstance(x, str) else x)

	titulo = '[Rodada] - Prospec RV{}'.format(dts[0].current_revision)
	html = "</div>"
	html += "<div class=\"row\" style=\"display: flex;margin-left:-5px;margin-right:-5px;\">"
	html += "<div class=\"column\" style='padding: 5px; text-align: center;' >"
	header_tabela = resumo_tabela1.reset_index().columns.tolist()
	header_tabela_sub = []
	for i_h, h in enumerate(header_tabela):
		if i_h >= 2:
			header_tabela_sub.append(f'{h}<br>SE-S-NE-N')
		else:
			header_tabela_sub.append(h)
	corpo_tabela = resumo_tabela1.reset_index().values.tolist()
 
	dados = {
		'body': corpo_tabela,
		'header': header_tabela_sub,
		'width_colunas': [200, 100] + [120] * (resumo_tabela1.shape[1] - 1),
	}
 
	html += html_builder.gerar_html('resultados_prospec', dados)
	html += "<br/>"
	html += "<br/>"
	html += "<br/>"
	html += "<body>"
	html += "<center>"
	html += "<img src=data:image/png;base64,{image}>"
	html += "{caption}"
	html += "<center>"
	html += "<body>"
	html += "<br/>"
	html += "<br/>"
	html += '<p>Compilado utilizado na geração desse email:<br>{}<p>'.format(params['path_name'])

	with open(path_file_out, 'rb') as image:
		f = image.read()
		image_bytes = bytearray(f)

	image = base64.b64encode(image_bytes).decode('ascii')
	_ = html
	_ = _.format(image=image, caption='')
	html = html.format(image=base64.b64encode(image_bytes).decode('ascii'), caption='')
	html_str = "<div><br>" + html
	soup = BeautifulSoup(html_str, 'lxml')
	tabela = soup.find('table')

	image_binary = html_to_image(str(tabela))
	
	print('Enviando whatsapp')
	send_whatsapp_message(params['list_whats'], params['assunto_email'], image_binary)
	send_email_message(user=consts.EMAIL_RODADAS, destinatario=params['list_email'], mensagem=html, assunto=params['assunto_email'])
 
	remove_dir(params['path_name'])

if __name__ == '__main__':
	
	params = {}
	params['considerar_rv'] = ''
	params['media_rvs'] =  False
	params['prevs_name'] = None
	params['list_whats'] = consts.WHATSAPP_GILSEU
	params['list_email'] = [consts.EMAIL_GILSEU]
	params['assunto_email'] = 'Teste '
	params['path_name'] = ["C:/projetos/arquivos/prospec/resultados/Estudo_26834_compilation.zip"]
	gerar_resultados(params)