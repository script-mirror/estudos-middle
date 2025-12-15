import datetime
import os
import sys
import shutil
import requests
import pandas as pd
from update_newave import NewaveUpdater
from update_decomp import DecompUpdater
from middle.message import send_whatsapp_message
from middle.utils import Constants, get_auth_header, setup_logger, criar_logger, create_directory

class DeckUpdater:
    def __init__(self):
        self.consts = Constants()
        self.header = get_auth_header()
        self.base_url_api = self.consts.BASE_URL + '/api/v2/decks/'
        self.logger = setup_logger()
        self.newave = NewaveUpdater()
        self.decomp = DecompUpdater()

    def date_4_du(self, data_atual: datetime) -> bool:
        ano = data_atual.year
        mes = data_atual.month
        data_inicio = datetime.datetime(ano, mes, 1)
        data_fim = datetime.datetime(ano, mes + 1, 1) - pd.Timedelta(days=1)
        dias_uteis = pd.bdate_range(start=data_inicio, end=data_fim)
        if len(dias_uteis) >= 2:
            segundo_dia_util = dias_uteis[1]  # 2º dia útil
            sexto_dia_util = dias_uteis[5]   # 6º dia útil
            return segundo_dia_util.date() <= data_atual.date() <= sexto_dia_util.date()
        return False

    def get_dados_banco(self, produto: str) -> pd.DataFrame:
        res = requests.get(self.base_url_api + produto, headers=self.header)
        if res.status_code != 200:
            self.logger.error(f"Erro {res.status_code} ao buscar carga: {res.text}")
            res.raise_for_status()
        return pd.DataFrame(res.json())

    def get_cvu_banco(self, produto: str, fonte: str = '') -> pd.DataFrame:
        res = requests.get(self.base_url_api + produto, params={'fonte': fonte}, headers=self.header)
        if res.status_code != 200:
            self.logger.error(f"Erro {res.status_code} ao buscar os dados no banco: {res.text}")
            res.raise_for_status()
        return pd.DataFrame(res.json())

    def get_cvu_historico(self, fonte: str = '') -> pd.DataFrame:
        res = requests.get(self.base_url_api + 'historico-cvu', params={'fonte': fonte}, headers=self.header)
        if res.status_code != 200:
            self.logger.error(f"Erro {res.status_code} ao buscar os dados no banco: {res.text}")
            res.raise_for_status()
        df_date = pd.DataFrame(res.json()['data'])
        df_date = df_date.sort_values('data_atualizacao', ascending=False)
        df_date = df_date.drop_duplicates(subset=['tipo_cvu'], keep='first')
        return df_date

    def update_cvu(self, params: dict) -> None:
        tipo_cvu = params['tipo_cvu']
        dt_produto = params['dt_produto']

        if tipo_cvu == 'conjuntural_revisado':
            if self.date_4_du(dt_produto):
                df_data = self.get_cvu_banco('cvu', tipo_cvu)
                df_data = df_data.sort_values('mes_referencia', ascending=False)
                df_data = df_data.drop_duplicates(subset=['cd_usina'], keep='first')
                df_data = df_data.reset_index(drop=True)
                df_data = df_data.sort_values('cd_usina').reset_index(drop=True)
                self.newave.update_cvu_conjuntural(params, df_data)
                self.decomp.update_cvu(params, df_data)
            else:
                send_whatsapp_message(
                    self.consts.WHATSAPP_DECKS,
                    f"Erro na atualização CVU \nTipo: CVU {tipo_cvu} \nData do produto: {dt_produto.strftime('%d/%m/%Y')} \nNão confere com a data padrão de atualização.",'')
                self.logger.info(f"Data do produto {dt_produto.strftime('%d/%m/%Y')} não está entre o 2º e o 6º dia útil do mês.")
                raise ValueError(f"Data do produto {dt_produto.strftime('%d/%m/%Y')} não está entre o 2º e o 6º dia útil do mês.")

        elif tipo_cvu == 'conjuntural':
            if 15 < dt_produto.day < 22:
                df_data = self.get_cvu_banco('cvu', tipo_cvu)
                df_data = df_data.sort_values('mes_referencia', ascending=False)
                df_data = df_data.drop_duplicates(subset=['cd_usina'], keep='first')
                df_data = df_data.reset_index(drop=True)
                df_data = df_data.sort_values('cd_usina').reset_index(drop=True)
                self.newave.update_cvu_conjuntural(params, df_data)
                self.decomp.update_cvu(params, df_data)
            else:
                send_whatsapp_message(
                    self.consts.WHATSAPP_DECKS,
                    f"Erro na atualização CVU \nTipo: CVU {tipo_cvu} \nData do produto: {dt_produto.strftime('%d/%m/%Y')} \nNão confere com a data padrão de atualização.",'')
                self.logger.info(f"Data do produto {dt_produto.strftime('%d/%m/%Y')} não está entre o 16º e o 21º dia do mês.")
                raise ValueError(f"Data do produto {dt_produto.strftime('%d/%m/%Y')} não está entre o 16º e o 21º dia do mês.")

        elif tipo_cvu == 'merchant':
            df_data = self.get_cvu_banco('cvu', tipo_cvu)
            df_data = df_data[df_data['mes_referencia']== max(df_data['mes_referencia'].to_list())]
            df_data = df_data.sort_values('data_fim').reset_index(drop=True)
            df_data = df_data.reset_index(drop=True)
            df_data = df_data.sort_values('cd_usina').reset_index(drop=True)
            df_data['data_inicio'] = pd.to_datetime(df_data['data_inicio'])
            df_data['data_fim'] = pd.to_datetime(df_data['data_fim'])
            df_data = df_data.sort_values('data_fim').reset_index(drop=True)
            self.decomp.update_cvu(params, df_data)
            self.newave.update_cvu_merchant(params, df_data)
            

            df = self.get_cvu_historico()
            df = df[df['tipo_cvu'].str.contains("conjuntural", case=False, na=False)]
            df['data_atualizacao'] = pd.to_datetime(df['data_atualizacao'])
            df = df.sort_values(by='data_atualizacao')

            for tipo in df['tipo_cvu']:
                params['tipo_cvu'] = tipo
                df_data = self.get_cvu_banco('cvu', params['tipo_cvu'])
                df_data = df_data.sort_values('mes_referencia', ascending=False)
                df_data = df_data.drop_duplicates(subset=['cd_usina'], keep='first')
                df_data = df_data.reset_index(drop=True)
                df_data = df_data.sort_values('cd_usina').reset_index(drop=True)
                self.newave.update_cvu_conjuntural(params, df_data)
                self.decomp.update_cvu(params, df_data)

        elif tipo_cvu == 'estrutural':
            if 15 < dt_produto.day < 22:
                df_data = self.get_cvu_banco('cvu', tipo_cvu)
                self.newave.update_cvu_estrutural(params, df_data)
            else:
                send_whatsapp_message(
                    self.consts.WHATSAPP_DECKS,
                    f"Erro na atualização CVU \nTipo: CVU {tipo_cvu} \nData do produto: {dt_produto.strftime('%d/%m/%Y')} \nNão confere com a data padrão de atualização.",'')
                self.logger.info(f"Data do produto {dt_produto.strftime('%d/%m/%Y')} não está entre o 16º e o 21º dia do mês.")
                raise ValueError(f"Data do produto {dt_produto.strftime('%d/%m/%Y')} não está entre o 16º e o 21º dia do mês.")
        else:
            send_whatsapp_message(
                self.consts.WHATSAPP_GILSEU,
                f"Erro na atualização CVU \nTipo: CVU {tipo_cvu} \nData do produto: {dt_produto.strftime('%d/%m/%Y')} \nNão confere com nenhum padrão de cvu.",'')
            self.logger.info(f"Produto {params['produto']} inválido. Use 'conjuntural', 'conjuntural_revisado' ou 'merchant'.")
            raise ValueError(f"Produto {params['produto']} inválido. Use 'conjuntural', 'conjuntural_revisado' ou 'merchant'.")

    def update_eolica(self, params: dict) -> None:
        df_data = self.get_dados_banco('weol')
        self.decomp.update_eolica(params, df_data)
        self.newave.update_eolica(params)

    def update_carga_decomp(self, params: dict) -> None:
        df_data = self.get_dados_banco('carga-decomp')
        self.decomp.update_carga_and_mmgd(params, df_data)
        
    def update_carga_newave(self, params: dict) -> None:
        df_data = self.get_dados_banco('newave/previsoes-cargas')
        self.newave.update_carga(params)     
        df_decomp = self.decomp.carga_nw_to_decomp(params, df_data)
        self.decomp.update_carga_and_mmgd(params, df_decomp, True)

    def update_re(self, params: dict) -> None:
        df_data = self.get_dados_banco('restricoes-eletricas')
        self.decomp.update_re(params, df_data)

    def run_with_params(self, params: dict = None) -> None:
        if params is None:
            params = {
                "produto":    None ,#'CVU',
                'id_estudo':  None, #[27219],
                'dt_produto': None,#datetime.datetime(2025, 8, 18),
                'tipo_cvu':   None,
                'path_download': '',
                'path_out': '',
            }

        BLOCK_FUNCTIONS = {
            'CVU': self.update_cvu,
            'EOLICA': self.update_eolica,
            'CARGA-DECOMP': self.update_carga_decomp,
            'CARGA-NEWAVE': self.update_carga_newave,
            'RE-DECOMP': self.update_re,
            None: lambda params: self.logger.error("Produto não informado ou inválido. Por favor, informe um produto válido.")
        }

        # debug
        params['produto'] = 'CARGA-NEWAVE'
        params['path_download'] = create_directory(self.consts.PATH_RESULTS_PROSPEC, 'update_decks/' + params['produto']) + '/'
        params['path_out'] = create_directory(self.consts.PATH_RESULTS_PROSPEC, 'update_decks/' + params['produto']) + '/'
        params['id_estudo'] = [28632]
        BLOCK_FUNCTIONS[params['produto']](params)
        
        
        params['produto'] = 'CVU'
        params['tipo_cvu'] = 'merchant'
        params['path_download'] = create_directory(self.consts.PATH_RESULTS_PROSPEC, 'update_decks/' + params['produto']) + '/'
        params['path_out'] = create_directory(self.consts.PATH_RESULTS_PROSPEC, 'update_decks/' + params['produto']) + '/'
        params['id_estudo'] = [28632]
        BLOCK_FUNCTIONS[params['produto']](params)
        
               
        if len(sys.argv) >= 3:
            for i in range(1, len(sys.argv), 2):
                argumento = sys.argv[i].lower()
                if argumento == "produto":
                    params[argumento] = sys.argv[i + 1].upper()
                elif argumento == "id_estudo":
                    params[argumento] = eval(sys.argv[i + 1])
                elif argumento == "tipo_cvu":
                    params[argumento] = sys.argv[i + 1]
                elif argumento == "dt_produto":
                    params[argumento] = datetime.datetime.strptime(sys.argv[i + 1], '%d/%m/%Y')
        else:
            self.logger.info(f"Parâmetros recebidos: {params}")
            if 'produto' not in params or not params['produto']:
                print("É obrigatório informar o parâmetro: produto")
                sys.exit(1)

        params['path_download'] = create_directory(self.consts.PATH_RESULTS_PROSPEC, 'update_decks/' + params['produto']) + '/'
        params['path_out']      = create_directory(self.consts.PATH_RESULTS_PROSPEC, 'update_decks/' + params['produto']) + '/'

        print(params)
        BLOCK_FUNCTIONS[params['produto']](params)
        shutil.rmtree(params['path_download'], ignore_errors=True)
        shutil.rmtree(params['path_out'], ignore_errors=True)
        
if __name__ == '__main__':
    logger = criar_logger('logger.log', os.path.join(Constants().PATH_ARQUIVOS, 'logger.log'))
    updater = DeckUpdater()
    updater.run_with_params()