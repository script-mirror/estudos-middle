import os
import re
import sys
import pdb
import glob
import json
import time
import base64
import shutil
import hashlib
import datetime
import requests
from zipfile import ZipFile
from tabulate import tabulate

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
# import mplcyberpunk

libsDir = os.path.dirname(os.path.abspath(__file__))
appDir = os.path.dirname(libsDir)
appsDir = os.path.dirname(appDir)
rootDir = os.path.dirname(appsDir)

sys.path.append(rootDir)
from apps.ampere.libs.ee_ampere_consultoria.enum_produto import Produto

max_tentativas = 3
delay_tentativas_seg = 5

cores = {
    'ONS-OFICIAL-NT00752020': '#0066cc',  # Strong blue
    'GFS': '#cc0066',  # Deep pink
    'ETA40': '#009933',  # Forest green
    'ECMWF-ENSEMBLE': '#cc6600',  # Dark orange
    'GEFS': '#6600cc',  # Purple
    'ACOMPH': '#39ff14',  # verde florescente
    'MLT': '#666666',  # Dark gray
    'ONS-OFICIAL-NT00752020-RVEXT-VMEDPONDERADA': '#ff1493',  # Navy blue
    'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER01': '#990033',  # Dark red
    'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER02': '#006633',  # Dark green
    'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER03': '#0099cc',  # Medium blue
    'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER04': '#cc3300',  # Burnt orange
    'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER05': '#660066',  # Deep purple
    'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER06': '#996600',  # Brown
    'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER07': '#cc3333',  # Indian red
    'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER08': '#006666',  # Dark teal
    'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER09': '#990000',  # Dark crimson
    'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER10': '#333399',   # Royal purple
    'EC-45DIAS': '#4169e1',  # Royal Blue
    'EC15-ATUAL-EC45': '#1e90ff',  # Dodger Blue
    'GEFS-ATUAL-EC45': '#9400d3',  # Dark Violet
    'GFS-ATUAL-EC45': '#dc143c',  # Crimson
    'ETA40-ATUAL-EC45': '#228b22',  # Forest Green
}

class AmpereAPI:
    def __init__(self, username, password, user_token, uri="https://h.ampereconsultoria.com.br"):
        self.URI = uri
        self.username = username
        self.password = password
        self.user_token = user_token
        self.access_token = None
        self.product_keys = {
            'meteorologia': None,
        } 

    def autenticate(self):

        endpoint = "/automated-login"
        md5_password_hash = hashlib.md5(self.password.encode('utf-8')).hexdigest()

        payload = json.dumps({
            "username": self.username,
            "password": md5_password_hash
        })
        
        headers = {
            'x-user-token': self.user_token,
            'Content-Type': 'application/json',
        }

        url = self.URI + endpoint
        response = requests.request("PUT", url, headers=headers, data=payload)

        resp_data = json.loads(response.text)
        if resp_data.get('code') == 200:
            self.access_token = resp_data['data']['access_token']

        return resp_data

    def get_access_token(self):
        if self.access_token is None:
            resp = self.autenticate()
            if resp.get('code') != 200:
                print(f'Erro ao tentar logar:\n{resp}')
        return self.access_token

    def get_product_permission(self, produto):
        
        if self.access_token is None:
            self.get_access_token()
        
        if self.product_keys.get(produto) is not None:
            return self.product_keys.get(produto)
        else:
            endpoint = f"/admin/contratos/current-user-has-permission/?item={produto}"
            
            headers = {
                'x-access-token': self.access_token,
                'x-user-token': self.user_token,
            }
            
            url = self.URI + endpoint
            response = requests.request("GET", url, headers=headers)
            response_json = json.loads(response.text)
            product_key = response_json['data']['product_key']
            self.product_keys[produto] = product_key
            
        return product_key
    
    def request_with_retry(self, method, url, headers, data, max_tentativas=max_tentativas, delay_tentativas_seg=delay_tentativas_seg):
        for i in range(max_tentativas):
            response = requests.request(method, url, headers=headers, data=data)
            if response.status_code == 200 :
                json_response = json.loads(response.text)
                if 'code' in json_response  and json_response['code'] == 200: 
                    return response
            print(f"Erro na tentativa {i+1} de {max_tentativas}.")
            time.sleep(delay_tentativas_seg)
        return None
                
            
    
    def get_list_last_results_automatico(self):
        
        nome_produto = Produto.FLUX_AUTOMATICO.value 
        product_key = self.get_product_permission(nome_produto)
        
        payload = {}
        endpoint = f"/produtos/previvaz-automatico/verify-last-results-automatico/?product_key={product_key}"

        headers = {
            'x-access-token': self.access_token,
            'x-user-token': self.user_token,
            'Content-Type': 'application/json',
        }
        
        url = self.URI + endpoint
        response = requests.request("POST", url, headers=headers, data=payload)
        
        return json.loads(response.text)

    def get_revisao_fechamento_mes(self, lista_modelos, revisao, submercado="SUDESTE"):
        
        nome_produto = Produto.FLUX_AUTOMATICO.value 
        product_key = self.get_product_permission(nome_produto)
        
        endpoint = f"/produtos/previvaz-ena-diaria/rvx-acompanhamento/?product_key={product_key}"

        # data_previsao = "latest" ou datetime.datetime.now().strftime('%Y%m%d')
        # data_acomph = "latest" ou datetime.datetime.now().strftime('%Y%m%d')
        
        payload = json.dumps({
            "versao": "latest",
            "unidade": "%mlt",
            "data_acomph": "latest",
            "data_previsao": "latest", #2nd_latest
            "ndiasprev": 15,
            "lista_cenarios": lista_modelos,
            "revisao": revisao,
            "lista_simulacoes_antigas": [],
            "subsistema": submercado
        })
        
        headers = {
            'x-access-token': self.access_token,
            'x-user-token': self.user_token,
            'Content-Type': 'application/json',
        }

        url = self.URI + endpoint
        response = self.request_with_retry("POST", url, headers, payload)
        
        return json.loads(response.text)

    def ena_diaria_get_options(self):
        
        nome_produto = Produto.FLUX_AUTOMATICO.value 
        product_key = self.get_product_permission(nome_produto)
        
        endpoint = f"/produtos/previvaz-ena-diaria/get-data/?product_key={product_key}"
        
        headers = {
            'x-access-token': self.access_token,
            'x-user-token': self.user_token,
        }
        
        url = self.URI + endpoint
        response = requests.request("GET", url, headers=headers)

        return json.loads(response.text)
    
    def get_ena_diaria_old(self, data_previsao:datetime, modelo:str, versao:str, subdivisao:str):

        nome_produto = Produto.FLUX_AUTOMATICO.value 
        product_key = self.get_product_permission(nome_produto)
        
        endpoint = f"/produtos/previvaz-ena-diaria/get-cenario/?product_key={product_key}"

        json_data = {
            'data_acomph': 'latest',
            'data_previsao': 'latest',
            'versao': 'latest',
            'lista_cenarios': [
                'ONS-OFICIAL-NT00752020-RVEXT-VMEDPONDERADA',
                'GFS',
                'ETA40',
                'GEFS',
                'ECMWF-ENSEMBLE',
            ],
            'incluir_acomph': True,
            'incluir_mlt': True,
            'lista_simulacoes_antigas': [],
            'subsistema': 'SUDESTE',
        }

        payload = json.dumps({
        "run_time": data_previsao.strftime('%Y-%m-%d'),
        "modelo": modelo,
        "versao": versao,
        "subdivisao": subdivisao
        })
        
        headers = {
            'x-access-token': self.access_token,
            'x-user-token': self.user_token,
        }

        url = self.URI + endpoint
        response = requests.request("POST", url, headers=headers, data=payload)

        return
        
    def get_ena_diaria(self, lista_cenarios:list, subsistema:str, simulacoes_antigas=[]):

        nome_produto = Produto.FLUX_AUTOMATICO.value 
        product_key = self.get_product_permission(nome_produto)
        
        endpoint = f"/produtos/previvaz-ena-diaria/get-data-daily/?product_key={product_key}"

        if subsistema in ['SUDESTE', 'SUL', 'NORDESTE', 'NORTE']:
            json_data = {
                'data_acomph': 'latest',
                'data_previsao': 'latest',
                'versao': 'latest',
                'lista_cenarios': lista_cenarios,
                'incluir_acomph': True,
                'incluir_mlt': True,
                'lista_simulacoes_antigas': simulacoes_antigas,
                'subsistema': subsistema,
            }
        elif bool(re.match(r'^\s*-?\d+', subsistema)):    # condição para a requisição ser de um posto
            posto = subsistema
            json_data = {
                'data_acomph': 'latest',
                'data_previsao': 'latest',
                'versao': 'latest',
                'lista_cenarios': lista_cenarios,
                'incluir_acomph': True,
                'incluir_mlt': True,
                'lista_simulacoes_antigas': simulacoes_antigas,
                'posto': posto,
            }
        else:
            bacia = subsistema
            json_data = {
                'data_acomph': 'latest',
                'data_previsao': 'latest',
                'versao': 'latest',
                'lista_cenarios': lista_cenarios,
                'incluir_acomph': True,
                'incluir_mlt': True,
                'lista_simulacoes_antigas': simulacoes_antigas,
                'bacia': bacia,
            }

        payload = json.dumps(json_data)

        headers = {
            'x-access-token': self.access_token,
            'x-user-token': self.user_token,
        }

        url = self.URI + endpoint
        response = self.request_with_retry("POST", url, headers, payload)

        return json.loads(response.text)
        
    def comparacao(self, model1, data_previsao1, model2, data_previsao2, periodo, runtime1=0, membro1='0', 
                   nivel_atm1='single_level', var1='prec', rmv1=0, 
                    runtime2=0, membro2='0', nivel_atm2='single_level', var2='prec', rmv2=0):
        
        nome_produto = Produto.METEOROLOGIA.value 
        product_key = self.get_product_permission(nome_produto)
        endpoint = f"/produtos/comparador/execute-comparison/?product_key={product_key}"
        
        headers = {
            'x-access-token': self.access_token,
            'x-user-token': self.user_token,
        }
        
        payload_data = {
            'base': {
                'modelo': model2,
                'data_previsao': data_previsao2,
                'runtime': runtime2,
                'membro': membro2,
                'nivel_atm': nivel_atm2,
                'var': var2,
                'rmv': rmv2,
            },
            'confrontante': {
                'modelo': model1,
                'data_previsao': data_previsao1,
                'runtime': runtime1,
                'membro': membro1,
                'nivel_atm': nivel_atm1,
                'var': var1,
                'rmv': rmv1,
            },
            'periodo': periodo,
        }
        payload = json.dumps(payload_data)
        
        url = self.URI + endpoint
        response = self.request_with_retry("POST", url, headers, payload)

        return json.loads(response.text)
    
    def mapas_observados(self, datahora_inicial=None, datahora_final=None, predefinido=None, anom=False, dados_por_estacao=False, regiao='BR', var='prec'):

        nome_produto = Produto.METEOROLOGIA.value 
        product_key = self.get_product_permission(nome_produto)
        endpoint = f"/produtos/dados-observados/execute/?product_key={product_key}"
        
        headers = {
            'x-access-token': self.access_token,
            'x-user-token': self.user_token,
        }
        payload_data = {
            'var': var,
            'regiao': regiao,
            'dados_por_estacao': dados_por_estacao,
            'anom': anom,
        }
        
        if isinstance(datahora_inicial, datetime.datetime):
            datahora_inicial_unix = time.mktime(datahora_inicial.timetuple())
        if isinstance(datahora_final, datetime.datetime):
            datahora_final_unix = time.mktime(datahora_final.timetuple())
            
        if predefinido:
            payload_data['predefinido'] = predefinido
        else:
            payload_data['datahora_inicial'] = datahora_inicial_unix # timestampunix iniciando em 15Z GMT (12Z local)
            payload_data['datahora_final'] = datahora_final_unix
        
        payload = json.dumps(payload_data)
        
        url = self.URI + endpoint
        response = requests.request("POST", url, headers=headers, data=payload)

        return json.loads(response.text)
            
    def imagens_clima(self, data_prev, prazo, index):
        
        nome_produto = Produto.METEOROLOGIA.value 
        product_key = self.get_product_permission(nome_produto)
            
        day = data_prev.day
        month = data_prev.month
        year = data_prev.year
        
        endpoint = f"/produtos/meteorologia/imagens-clima/"
        endpoint += f"?product_key={product_key}&tipo={prazo}&day={day}&"
        endpoint += f"month={month}&year={year}&index={index}"
        
        payload = {}
        headers = {
            'x-access-token': self.access_token,
            'x-user-token': self.user_token,
        }

        url = self.URI + endpoint
        response = requests.request("GET", url, headers=headers, data=payload)

        return json.loads(response.text)

    def get_ena_chuva_zip(self, cenario, data_previsao):
        """
        Dado um cenário, esta função baixa o zip correspondente da Ampere e retorna o caminho para o csv das
        ENAs diárias e a pasta das previsões de precipitação. Se a data_previsao não for 'latest', deve ser
        uma string com a data no formato aaaammdd, a função também aceitará o formato aaaammdd-PSAT.
        """

        nome_produto = Produto.FLUX_AUTOMATICO.value 
        product_key = self.get_product_permission(nome_produto)
        
        endpoint = f"/produtos/previvaz-ena-diaria/get-zip/?product_key={product_key}"

        tipo = 'revisao' if data_previsao != 'latest' else 'diaria'
        data_acomph = f'ACOMPH{data_previsao}' if data_previsao != 'latest' else 'latest'
        data_previsao = data_previsao.replace('-PSAT', '')

        json_data = {
            'data_acomph': data_acomph,
            'data_previsao': data_previsao,
            'versao': 'latest',
            'lista_cenarios': [cenario],
            'subsistema': 'SUDESTE',
            'type': tipo,
        }

        payload = json.dumps(json_data)

        headers = {
            'x-access-token': self.access_token,
            'x-user-token': self.user_token,
        }

        url = self.URI + endpoint
        response = requests.request("POST", url, headers=headers, data=payload)
        
        # Apaga qualquer zip antigo e cria a pasta para o zip novo.
        path_root = os.path.join(appDir, 'arquivos')
        path_to_file = os.path.join(path_root, 'tmp.zip')        
        os.makedirs(path_root, exist_ok=True)
        
        if os.path.exists(path_to_file):
            os.remove(path_to_file)
        
        # Salva o zip.
        content = response.content
        with open(path_to_file, 'wb') as f:
            f.write(content)
            
        folder = unzipAmpere(path_to_file, path_root, remove_zip=True)
        
        # Busca o arquivo de ENA diária.
        files = glob.glob(os.path.join(folder, '*', 'ena_diaria*'))
        file_ena = files[0] if len(files) > 0 else None

        # Busca o pasta com as previsões de precipitação.
        files = glob.glob(os.path.join(folder, '*', 'pmed'))
        folder_chuva = files[0] if len(files) > 0 else None

        return file_ena, folder_chuva
    
def print_options(dict_source:dict, show=True):
    df = pd.DataFrame()
    for dt in dict_source:
        for modelo in dict_source[dt]:
            for versao in dict_source[dt][modelo]:
                nova_linha = {'data_previsao':dt, 'modelo':modelo, 'versao':versao}
                df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
    
    if show:
        print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

    return df    
    
def base64_to_png(file_base64:str, path_png:str):
    path_dir = os.path.dirname(path_png)
    if os.path.exists(path_dir) is False:
        os.makedirs(path_dir)

    file = file_base64.split(',')
    if len(file) == 1:
        file = file[0]
    elif len(file) >= 2:
        file = file[1]
        
    with open(path_png, "wb") as fh:
        fh.write(base64.b64decode(file))
        
    return path_png

def formatar_tabela_fechamento(data, titulo:str, path_png:str):

    # Extrair valores numéricos
    numeric_values = [[f"{item[0]*100:>.1f}%" if item[0] is not None else "" for item in row] for row in data['values']]
    color_values = [[item[1] for item in row] for row in data['values']]

    # Criar DataFrame
    df = pd.DataFrame(numeric_values, 
                    columns=[f'd-{14-i}' for i in range(15)], 
                    index=data['rowLabels'])

    # Configurar figura
    plt.figure(figsize=(15, 3.5))
    plt.axis('off')

    # Criar tabela
    table = plt.table(cellText=df.round(4).values,
                    cellColours=[color_values[i] for i in range(len(data['rowLabels']))],
                    rowLabels=df.index,
                    colLabels=df.columns,
                    loc='center',
                    cellLoc='center')

    # Ajustar estilo da tabela
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.2, 1.5)

    # Salvar como imagem
    plt.title(titulo, pad=20)
    plt.tight_layout()
    plt.savefig(path_png, bbox_inches='tight', dpi=300)

    return
    
def plot_enas(data, titulo, filename, largura=12, altura=6):
    # Definindo as cores para cada curva
    # plt.style.use('cyberpunk')  # Certifique-se de que esse estilo está definido
    plt.figure(figsize=(largura, altura)) 
    for i, (key, values) in enumerate(data.items()):
        match = re.search(r'^(.*?)(?:\(d-(\d+)\))?(?:\(d-(\d+)\))?(?:\(v(\d+)\))?$', key)
        modelo = match.group(1)
        if modelo in cores:
            cor = cores[modelo]
        else:
            cor = 'tomato'
        dates = [datetime.datetime.strptime(item[0], '%d/%m/%Y') for item in values]
        values = [item[1] for item in values]
        
        alpha = 1.0
        linestyle = '-'
        label = modelo
        if match.group(2):
            delay_dia = int(match.group(3))
            alpha = 1.0 - (delay_dia / 8)  # Ajusta o alpha baseado no delay (máximo de 7 dias)
            print(f'{key}: {alpha}')
            # alpha = max(0.2, alpha) # Garante que o alpha não fique menor que 0.2.
            if delay_dia == 1:
                linestyle = '--' 
            elif delay_dia == 2:
                linestyle = '-.'
            else:
                linestyle = ':'
            plt.plot(dates, values, color=cor, alpha=alpha, linestyle=linestyle)
        else:
            plt.plot(dates, values, label=label, color=cor, alpha=alpha, linestyle=linestyle)

    # Configurando o gráfico
    plt.xlabel('Data')
    plt.ylabel('ENA [MWm]')
    plt.title(titulo)
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()
    
    plt.grid(axis='y', alpha=0.3)  # Adiciona grid apenas no eixo Y

    # Exibindo o gráfico
    plt.savefig(filename, format='png')  # Salva como PNG, ajuste o formato conforme necessário
    plt.close()  # Fecha a figura para liberar memória

    return
    
def unzipAmpere(path_to_file, path_root, remove_zip=True):
    """
    Função feita especificamente para extrair o zip da Ampere. Este zip tem uma estrutura interna um pouco convoluta, 
    então vale a pena simplificar. Os arquivos extraídos vão para {path_root}/tmp_zip_folder_second.
    """

    folder_first = os.path.join(path_root, 'ampere_tmp_1')
    folder_second = os.path.join(path_root, 'ampere_tmp_2')

    if os.path.exists(folder_first):
        shutil.rmtree(folder_first)
        
    if os.path.exists(folder_second):
        shutil.rmtree(folder_second)
    
    with ZipFile(path_to_file, 'r') as zf:
        zf.extractall(folder_first)
    
    files = glob.glob(os.path.join(folder_first, '*.zip'))
    file = files[0] if len(files) > 0 else None
    
    if file is not None:
        with ZipFile(file, 'r') as zf:
            zf.extractall(folder_second)
            
    # Apaga o zip original.
    if remove_zip:
        os.remove(path_to_file)

    return folder_second

    
if __name__ == '__main__':
    from dotenv import load_dotenv
    
    homePath =  os.path.expanduser('~')
    load_dotenv(os.path.join(homePath,'.env'))
    data_prev = datetime.datetime(2024, 11, 19)
    
    USERNAME = os.getenv("API_AMPERE_USERNAME")
    SENHA = os.getenv("API_AMPERE_PASSWORD")
    USER_ACCESS_TOKEN = os.getenv("API_AMPERE_TOKEN")
    
    api = AmpereAPI(USERNAME, SENHA, USER_ACCESS_TOKEN)
    resultados = api.get_list_last_results_automatico()
    pdb.set_trace()
    
    # mapa = api.mapas_observados(predefinido='hoje')
    # path_png = os.path.abspath(r'C:\hd1\fontes\scripts\apps\ampere\arquivos\relatorio_diario\20241111\obs_hoje.png')
    # pdb.set_trace()
    # base64_to_png(mapa['data']['obs'], path_png)
    # pdb.set_trace()
    # quit()
    
    # lista_modelos = [
    #     "ONS-OFICIAL-NT00752020-RVEXT-VMEDPONDERADA",
    #     "EC-45DIAS",
    #     "EC15-ATUAL-EC45",
    #     "GEFS-ATUAL-EC45",
    #     "GFS-ATUAL-EC45",
    #     "ONS-OFICIAL-ATUAL-EC45",
    #     "ETA40-ATUAL-EC45"
    # ]
    # revisao = "202411.REVF"

    # data_acomph="latest"
    # data_previsao="latest"
    
    # # data_acomph = "20241119"
    # data_previsao = data_prev.strftime('%Y%m%d')
    # fechamento_mensal = api.get_revisao_fechamento_mes(lista_modelos, revisao, data_acomph, data_previsao)
    # titulo=f'Fechamento do dia {data_prev.strftime("%Y%m%d")}'
    # nome_arquivo=f'_fechamento_{datetime.datetime.now().strftime('%Y%m%d%M%S')}.png'
    # path_png=os.path.join(appDir,'arquivos',data_prev.strftime('%Y%m%d'),nome_arquivo)
    # formatar_tabela_fechamento(fechamento_mensal['data'], titulo, path_png='')
    # quit()
    
    
    
    # options_ena_diaria = api.ena_diaria_get_options()
    # print_options({'2024-11-19': options_ena_diaria['data']['cenarios']['2024-11-19']})

    # prazo = "cp"
    # index = "1"
    # imagem_b64 = api.imagens_clima(data_prev, prazo, index)
    # for model in imagem_b64['data']:
    #     for d in imagem_b64['data'][model]:
    #         for var in imagem_b64['data'][model][d]:
    #             path_fig = os.path.join(appDir,'arquivos',data_prev.strftime('%Y%m%d'),f"{model}_D{d}_{var}.png")
    #             base64_to_png(imagem_b64['data'][model][d][var], path_fig)
    #             print(path_fig)
    

    
    # # if resposta_autenticacao['code'] == 200:
    # #     produto = 'prevs-automatico'
    # #     resposta_permicao = api.get_product_permission(produto)
        
    # #     if resposta_permicao['code'] == 200:
    # #         product_key = resposta_permicao['data']['product_key']
            
    # #         lista_modelos = [
    # #             "EC-45DIAS",
    # #             "EC15-ATUAL-EC45",
    # #             "GEFS-ATUAL-EC45",
    # #             "GFS-ATUAL-EC45",
    # #             "ONS-OFICIAL-ATUAL-EC45",
    # #             "ETA40-ATUAL-EC45"
    # #         ]
    # #         revisao = "202411.REVF"

    # #         revisao_fechamento_mes = api.get_revisao_fechamento_mes(product_key, lista_modelos, revisao)
            
    # #         options_ena_diaria = api.ena_diaria_get_options(product_key)
            
    # #         data_prev = datetime.datetime(2024, 11, 18)
    # #         prazo = "cp"
    # #         index = "1"
    # #         imagem = api.imagens_clima(product_key, data_prev, prazo, index)
    
    
    ena_options = api.ena_diaria_get_options()
    data_previsao = datetime.datetime(2024,11,25)
    modelo = '*'
    versao = 'PRE-ACOMPH-PRE-PSAT'
    subdivisao = 'SUB_SUDESTE'
    
    ena = api.get_ena_diaria(data_previsao, modelo, versao, subdivisao)
    
    
# (Pdb) ena_options['data']['cenarios'].keys()
# dict_keys(['2024-11-07', '2024-11-10', '2024-10-22', '2024-11-01', '2024-11-23', '2024-10-16', '2024-11-21', '2024-11-02', '2024-10-27', '2024-11-03', '2024-10-13', '2024-10-17', '2024-11-05', '2024-10-21', '2024-10-19', '2024-10-26', '2024-10-28', '2024-10-20', '2024-11-06', '2024-10-15', '2024-11-25', '2024-11-14', '2024-10-14', '2024-11-22', '2024-11-09', '2024-11-17', '2024-11-11', '2024-11-19', '2024-11-12', '2024-10-24', '2024-10-30', '2024-10-12', '2024-11-04', '2024-10-31', '2024-11-08', '2024-11-24', '2024-10-25', '2024-10-18', '2024-10-29', '2024-10-23', '2024-11-20', '2024-11-18', '2024-11-15', '2024-11-13', '2024-11-16', '1900-01-01'])
# (Pdb) ena_options['data']['cenarios']['2024-11-25'].keys()
# dict_keys(['ACOMPH', 'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER05', 'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER01', 'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER10', 'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER04', 'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER08', 'AMPERE-ATUAL-EC45-PREV-20241124-RMV', 'GFS-ATUAL-GEFS35-PREV-20241124-RMV', 'ONS-OFICIAL-ATUAL-EC45-PREV-20241124-RMV', 'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER02', 'GEFS-ATUAL-GEFS35-PREV-20241124-RMV', 'GEM-ATUAL-EC45-PREV-20241124-RMV', 'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER06', 'EC15-ATUAL-EC45-PREV-20241124-RMV', 'ONS-OFICIAL-NT00752020-RVEXT-VMEDPONDERADA', 'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER03', 'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER09', 'GEFS-ATUAL-EC45-PREV-20241124-RMV', 'ONS-OFICIAL-NT00752020-RVEXT-CLUSTER07', 'ZERO'])
# (Pdb) ena_options['data']['cenarios']['2024-11-25']['ZERO'].keys()
# dict_keys(['PRE-ACOMPH-PRE-PSAT'])
# (Pdb) ena_options['data']['cenarios']['2024-11-25']['ZERO']['PRE-ACOMPH-PRE-PSAT''].keys()
# *** SyntaxError: unterminated string literal (detected at line 1)
# (Pdb) ena_options['data']['cenarios']['2024-11-25']['ZERO']['PRE-ACOMPH-PRE-PSAT']
# ['SUB_SUDESTE', 'SUB_SUL', 'SUB_NORDESTE', 'SUB_NORTE', 'REE_BMONTE', 'REE_IGUACU', 'REE_ITAIPU', 'REE_MADEIRA', 'REE_MAN-AP', 'REE_NORDESTE', 'REE_NORTE', 'REE_PARANA', 'REE_PRNPANEMA', 'REE_SUDESTE', 'REE_SUL', 'REE_TPIRES']
# (Pdb) ena_options['data']['cenarios']['2024-11-25']['ZERO']['PRE-ACOMPH-PRE-PSAT']
        

