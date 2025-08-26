import datetime
import os
import sys
import numpy as np
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
import requests
from dateutil.relativedelta import relativedelta
import pandas as pd
from inewave.newave import Clast, Dger, Sistema, Cadic
from middle.utils import Constants, get_auth_header, setup_logger, criar_logger, create_directory, SemanaOperativa
import time

sys.path.append(os.path.join(Constants().PATH_PROJETOS, "estudos-middle/api_prospec"))
from functionsProspecAPI import authenticateProspec, download_newave_update, send_all_newave_update

class NewaveUpdater:
    
    def __init__(self):
        self.consts = Constants()
        self.header = get_auth_header()
        self.base_url_api = self.consts.BASE_URL + '/api/v2/decks/'
        authenticateProspec(self.consts.API_PROSPEC_USERNAME, self.consts.API_PROSPEC_PASSWORD)
        self.logger = setup_logger()

    def get_dados_banco(self, produto: str) -> pd.DataFrame:
        """Fetch data from API endpoint."""
        res = requests.get(self.base_url_api + produto, headers=self.header)
        if res.status_code != 200:
            res.raise_for_status()
        return pd.DataFrame(res.json())

    def calculate_monthly_wind_average(self, df_data, df_pq, MAP_SUBMERCADO):
        """Calculate monthly wind generation averages."""
        dates = pd.date_range(start=pd.to_datetime(min(df_data['inicioSemana'])).replace(day=1),
                            end=pd.to_datetime(max(df_data['inicioSemana'])) + pd.offsets.MonthEnd(0), freq='D')

        df_diaria = pd.DataFrame()
        df_data['inicioSemana'] = pd.to_datetime(df_data['inicioSemana'])
        for date in dates:
            for ss in df_data['submercado'].unique():                                
                data_rv = SemanaOperativa(date)
                data_week = pd.to_datetime(data_rv.week_start)
                filter = ((df_pq['data'] == date.replace(day=1)) & (df_pq['indice_bloco'] == 3) & 
                         (df_pq['codigo_submercado'] == MAP_SUBMERCADO[ss]))
                valor = df_pq[filter]['valor'].values[0]
                
                if data_week in df_data['inicioSemana'].unique():
                    filter = (df_data['submercado'] == ss) & (df_data['inicioSemana'] == data_week)
                    valor = df_data.loc[filter, 'mediaPonderada'].values[0]
                df_diaria = pd.concat([df_diaria, pd.DataFrame([{"data": date, "submercado": ss, "valor": valor}])], 
                                    ignore_index=True)   
                                
        df_diaria['valor'] = df_diaria['valor'].fillna(0)
        df_diaria['mes_ano'] = df_diaria['data'].dt.to_period('M')
        df_diaria = df_diaria.groupby(['mes_ano', 'submercado'])['valor'].mean().round(2).unstack()                        
        return df_diaria

    def update_cvu_conjuntural(self, params: dict, df_data: pd.DataFrame) -> bool:
        """Update CVU for conjuntural type."""
        logging_name = f'logging_cvu_{params["tipo_cvu"]}.log'
        logger = criar_logger(logging_name, os.path.join(params['path_download'], logging_name))
        logger.info(f"Starting update_cvu_conjuntural for tipo_cvu: {params['tipo_cvu']}")

        try:
            file_name = 'clast.dat'
            path_clast = download_newave_update(params['id_estudo'], logger, params['path_download'], file_name)
            tag_update = f"CVU-NW(C){datetime.strptime(df_data['dt_atualizacao'][0], '%Y-%m-%d').strftime('(%d/%m)')}"

            for path in path_clast:
                logger = criar_logger(logging_name, os.path.join(os.path.dirname(path), logging_name))
                logger.info(f"Processing file: {path}")
                try:
                    dger = Dger.read(os.path.join(os.path.dirname(path), 'dger.dat'))
                    clast = Clast.read(path)
                    data_deck = np.datetime64(datetime(dger.ano_inicio_estudo, dger.mes_inicio_estudo, 1))
                    df_usinas = clast.modificacoes
                    df_cvu_old = deepcopy(clast.modificacoes)
                    data_delete = np.datetime64(data_deck + relativedelta(months=1))
                    data_fim = np.datetime64(data_deck + relativedelta(months=2))
                    df_cvu_old = df_cvu_old[df_usinas['data_fim'] <= data_delete]
                    df_usinas = df_usinas[(~(df_usinas['codigo_usina'].isin(df_data['cd_usina'].unique()) &
                                            (df_usinas['data_fim'] <= data_delete)) |
                                          (df_usinas['data_fim'].isna()))]

                    for ute in df_data['cd_usina'].unique():
                        if ute in clast.usinas['codigo_usina'].unique():
                            logger.debug(f"Processing usina: {ute}")
                            
                            if ute in df_usinas['codigo_usina'].unique():
                                df_usinas.loc[df_usinas['codigo_usina'] == ute, 'data_inicio'] = \
                                    df_usinas.loc[df_usinas['codigo_usina'] == ute, 'data_inicio'].replace(data_deck, data_fim)
                                df_usinas.loc[df_usinas['codigo_usina'] == ute, 'data_inicio'] = \
                                    df_usinas.loc[df_usinas['codigo_usina'] == ute, 'data_inicio'].replace(data_delete, data_fim)
                                logger.debug(f"Updated data_inicio for usina {ute} to {data_fim}")

                            new_cvu = round(float(df_data.loc[df_data['cd_usina'] == ute, 'vl_cvu'].values[0]), 2)
                            old_cvu = 0
                            if ute in df_cvu_old['codigo_usina'].unique():
                                old_cvu = round(float(df_cvu_old.loc[df_cvu_old['codigo_usina'] == ute, 'custo'].values[0]), 2)
                                logger.debug(f"Old CVU for usina {ute}: {old_cvu}")

                            new_row = pd.DataFrame([{
                                'codigo_usina': int(ute),
                                'nome_usina': clast.usinas.loc[clast.usinas['codigo_usina'] == ute]['nome_usina'].values[0],
                                'data_inicio': data_deck,
                                'data_fim': data_delete,
                                'custo': new_cvu,
                                'comentario_dif': f"DIF: {str(round(new_cvu - old_cvu,1)).rjust(7)}",
                                'comentario_fonte': f"FONTE: {params['tipo_cvu'].upper()}",
                                'comentario_dt': f"DATA: {datetime.now().strftime('%d-%m %H:%M')}"
                            }])
                            df_usinas = pd.concat([df_usinas, new_row], ignore_index=True)
                            logger.info(f"Created new row for usina {ute} with CVU: current value={old_cvu}, new value={new_cvu}")

                    logger.debug("Sorting and formatting final usinas dataframe")
                    clast.modificacoes = df_usinas.sort_values(by=['codigo_usina', 'data_inicio'], na_position='first')
                    
                    logger.info(f"Writing updated clast to {path}")
                    clast.write(path)

                except Exception as e:
                    logger.error(f"Error processing file {path}: {str(e)}")
                    raise

            logger.info(f"Sending NEWAVE update for study ID: {params['id_estudo']}")
            send_all_newave_update(params['id_estudo'], params['path_download'], file_name, logger, logging_name, tag_update)
            
            logger.info("update_cvu_conjuntural completed successfully")
            return True

        except Exception as e:
            logger.error(f"Fatal error in update_cvu_conjuntural: {str(e)}")
            raise

    def update_cvu_merchant(self, params: dict, df_data: pd.DataFrame) -> bool:
        """Update CVU for merchant type."""
        logging_name = f'logging_cvu_{params["tipo_cvu"]}.log'
        logger = criar_logger(logging_name, os.path.join(params['path_download'], logging_name))
        logger.info(f"Starting update_cvu_merchant for tipo_cvu: {params['tipo_cvu']}")
        
        try:
            file_name = 'clast.dat'
            path_clast = download_newave_update(params['id_estudo'], logger, params['path_download'], file_name)
            tag_update = f"CVU-NW(M){datetime.strptime(df_data['dt_atualizacao'][0], '%Y-%m-%d').strftime('(%d/%m)')}"

            for path in path_clast:
                logger = criar_logger(logging_name, os.path.join(os.path.dirname(path), logging_name))
                logger.info(f"Processing file: {path}")
                try:
                    dger = Dger.read(os.path.join(os.path.dirname(path), 'dger.dat'))
                    clast = Clast.read(path)
                    data_deck = np.datetime64(datetime(dger.ano_inicio_estudo, dger.mes_inicio_estudo, 1))
                    df_usinas = clast.modificacoes
                    df_cvu_old = deepcopy(clast.modificacoes)

                    def check_usina(row, df_data):
                        if row['codigo_usina'] in df_data['cd_usina'].values:
                            condition = (row['data_fim'] > df_data[df_data['cd_usina'] == row['codigo_usina']]['data_fim'] + timedelta(days=31)).values[0]
                            logger.debug(f"Checking usina {row['codigo_usina']}: condition={condition}")
                            return bool(condition)
                        return True

                    df_usinas = df_usinas[df_usinas.apply(lambda row: check_usina(row, df_data), axis=1)]

                    for ute in df_data['cd_usina'].unique():
                        if ute in clast.usinas['codigo_usina'].unique():
                            logger.debug(f"Processing usina: {ute}")
                            
                            new_cvu = round(float(df_data.loc[df_data['cd_usina'] == ute, 'vl_cvu'].values[0]), 2)
                            old_cvu = 0
                            if ute in df_cvu_old['codigo_usina'].unique():
                                old_cvu = round(float(df_cvu_old.loc[df_cvu_old['codigo_usina'] == ute, 'custo'].values[0]), 2)
                                logger.debug(f"Old CVU for usina {ute}: {old_cvu}")

                            data_inicio_row = df_data.loc[df_data['cd_usina'] == ute, 'data_inicio'].values[0]
                            if data_inicio_row < data_deck:
                                logger.debug(f"Adjusting data_inicio for usina {ute} from {data_inicio_row} to {data_deck}")
                                data_inicio_row = data_deck

                            new_row = pd.DataFrame([{
                                'codigo_usina': int(ute),
                                'nome_usina': clast.usinas.loc[clast.usinas['codigo_usina'] == ute]['nome_usina'].values[0],
                                'data_inicio': data_inicio_row,
                                'data_fim': df_data.loc[df_data['cd_usina'] == ute, 'data_fim'].values[0],
                                'custo': new_cvu,
                                'comentario_dif': f"DIF: {str(round(new_cvu - old_cvu,1)).rjust(7)}",
                                'comentario_fonte': f"FONTE: {params['tipo_cvu'].upper()}",
                                'comentario_dt': f"DATA: {datetime.now().strftime('%d-%m %H:%M')}"
                            }])
                            df_usinas = pd.concat([df_usinas, new_row], ignore_index=True)
                            logger.info(f"Creating new row for usina {ute} with CVU: current value={old_cvu}, new value={new_cvu}")

                    logger.debug("Sorting and formatting final usinas dataframe")
                    clast.modificacoes = df_usinas.sort_values(by=['codigo_usina', 'data_inicio'], na_position='first')
                    
                    logger.info(f"Writing updated clast to {path}")
                    clast.write(path)

                except Exception as e:
                    logger.error(f"Error processing file {path}: {str(e)}")
                    raise

            logger.info(f"Sending NEWAVE update for study ID: {params['id_estudo']}")
            send_all_newave_update(params['id_estudo'], params['path_download'], file_name, logger, logging_name, tag_update)
            
            logger.info("update_cvu_merchant completed successfully")
            return True

        except Exception as e:
            logger.error(f"Fatal error in update_cvu_merchant: {str(e)}")
            raise

    def update_cvu_estrutural(self, params: dict, df_data: pd.DataFrame) -> bool:
        """Update CVU for estrutural type."""
        logging_name = f'logging_cvu_{params["tipo_cvu"]}.log'
        logger = criar_logger(logging_name, os.path.join(params['path_download'], logging_name))
        logger.info(f"Starting update_cvu_estrutural for tipo_cvu: {params['tipo_cvu']}")

        try:
            df_data = df_data.sort_values('mes_referencia', ascending=False).reset_index(drop=True)
            tag_update = f"CVU-NW(E){datetime.strptime(df_data['dt_atualizacao'][0], '%Y-%m-%d').strftime('(%d/%m)')}"
            df_data = df_data[df_data['mes_referencia'] == df_data['mes_referencia'][0]].reset_index(drop=True)
            df_data = df_data.sort_values('cd_usina').reset_index(drop=True)
            df_data = df_data.pivot_table(index='cd_usina', columns='ano_horizonte', values='vl_cvu')
            file_name = 'clast.dat'
            path_clast = download_newave_update(params['id_estudo'], logger, params['path_download'], file_name)

            for path in path_clast:
                logger = criar_logger(logging_name, os.path.join(os.path.dirname(path), logging_name))
                logger.info(f"Processing file: {path}")
                
                try:
                    dger = Dger.read(os.path.join(os.path.dirname(path), 'dger.dat'))
                    clast = Clast.read(path)
                    data_deck = np.datetime64(datetime(dger.ano_inicio_estudo, dger.mes_inicio_estudo, 1))
                    df_usinas = clast.usinas

                    MAP_ANOS = {}
                    for ano in range(1, 6):
                        ano_to = (data_deck + relativedelta(years=ano-1)).year
                        if ano_to > max(df_data.keys()):
                            ano_to = max(df_data.keys())
                        MAP_ANOS[ano] = ano_to

                    comentarios = {idx: "  DIF:" for idx in df_data.index}
                    for ute in df_data.index:
                        if ute in df_usinas['codigo_usina'].unique():
                            logger.debug(f"Processing usina: {ute}")
                            for ano in df_usinas[df_usinas['codigo_usina'] == ute]['indice_ano_estudo']:
                                filter = (df_usinas['codigo_usina'] == ute) & (df_usinas['indice_ano_estudo'] == ano)
                                old_value = df_usinas.loc[filter, 'valor'].values[0]
                                new_value = df_data.loc[ute, MAP_ANOS[ano]]
                                diff = round(old_value - new_value, 2)
                                comentarios[ute] = comentarios[ute] + f" {str(diff).rjust(7)}"
                                df_usinas.loc[filter, 'valor'] = new_value
                                logger.info(f"Updated usina {ute}, year {ano}: old={old_value}, new={new_value}, diff={diff}")
                            comentarios[ute] = comentarios[ute] + f"    DATA: {datetime.now().strftime('%d-%m %H:%M')}"
                            df_usinas.loc[df_usinas['codigo_usina'] == ute, 'comentarios'] = comentarios[ute]

                    clast.usinas = df_usinas.sort_values('codigo_usina').reset_index(drop=True)
                    clast.write(path)

                except Exception as e:
                    logger.error(f"Error processing file {path}: {str(e)}")
                    raise

            logger.info(f"Sending NEWAVE update for study ID: {params['id_estudo']}")
            send_all_newave_update(params['id_estudo'], params['path_download'], file_name, logger, logging_name, tag_update)
            
            logger.info("update_cvu_estrutural completed successfully")
            return True

        except Exception as e:
            logger.error(f"Fatal error in update_cvu_estrutural: {str(e)}")
            raise

    def update_eolica(self, params: dict, path_sistema=None) -> bool:
        """Update wind power generation data in sistema.dat with enhanced logging."""
        start_time = time.time()
        send_sistema = False
        MAP_SUBMERCADO = {'SE': 1, 'S': 2, 'NE': 3, 'N': 4}
        logging_name = f'logging_eolica.log'
        logger = criar_logger(logging_name, os.path.join(params['path_download'], logging_name))
        logger.info(f"Starting wind power update for study ID: {params['id_estudo']}")

        try:
            logger.debug("Fetching wind generation data from API")
            df_data = self.get_dados_banco('weol/weighted-average')
            logger.info(f"Retrieved {len(df_data)} wind generation records from API. "
                       f"Submarkets: {df_data['submercado'].unique().tolist()}, "
                       f"Date range: {df_data['inicioSemana'].min()} to {df_data['inicioSemana'].max()}")

            file_name = 'sistema.dat'
            if path_sistema is None:
                logger.debug(f"Downloading {file_name} for study ID: {params['id_estudo']}")
                path_sistema = download_newave_update(params['id_estudo'], logger, params['path_download'], file_name)
                send_sistema = True
                logger.info(f"Downloaded {file_name} to {path_sistema}")
                
            tag_update = f"WEOL-NW{datetime.strptime(df_data['dataProduto'][0], '%Y-%m-%d').strftime('(%d/%m)')}"

            update_count = 0
            for path in path_sistema:
                logger = criar_logger(logging_name, os.path.join(os.path.dirname(path), logging_name))
                logger.info(f"Processing file: {path}")
                try:
                    dger = Dger.read(os.path.join(os.path.dirname(path), 'dger.dat'))
                    sistema = Sistema.read(path)
                    data_deck = datetime(dger.ano_inicio_estudo, dger.mes_inicio_estudo, 1)
                    logger.debug(f"Study start date from dger.dat: {data_deck}")
                    
                    df_pq = sistema.geracao_usinas_nao_simuladas
                    logger.debug(f"Loaded {len(df_pq)} non-simulated generation records from {file_name}")
                    
                    logger.debug("Calculating monthly wind generation averages")
                    df_diaria = self.calculate_monthly_wind_average(df_data, df_pq, MAP_SUBMERCADO)
                    logger.info(f"Generated monthly averages for {len(df_diaria)} months across "
                               f"{len(df_diaria.columns)} submarkets: {list(df_diaria.columns)}")

                    for mes_ano in df_diaria.index:
                        if data_deck.strftime('%Y-%m') == str(mes_ano):
                            logger.info(f"Updating wind generation for deck date: {data_deck.strftime('%Y-%m')}")
                            for ss in df_diaria.keys():
                                filter = ((df_pq['data'] == mes_ano.start_time) & 
                                         (df_pq['indice_bloco'] == 3) & 
                                         (df_pq['codigo_submercado'] == MAP_SUBMERCADO[ss]))
                                if not df_pq[filter].empty:
                                    old_value = df_pq.loc[filter, 'valor'].values[0]
                                    new_value = df_diaria.loc[mes_ano][ss]
                                    df_pq.loc[filter, 'valor'] = new_value
                                    update_count += 1
                                    logger.info(f"Updated submarket: {ss.rjust(2)}, month: {mes_ano}, "
                                                f"old_value:{str(old_value).rjust(8)}, new_value:{str(new_value).rjust(8)}")
                            
                    sistema.geracao_usinas_nao_simuladas = df_pq
                    logger.info(f"Writing updated {file_name} to {path} with {update_count} value updates")
                    sistema.write(path)

                except Exception as e:
                    logger.error(f"Error processing file {path}: {str(e)}. Context: "
                                f"study_id={params['id_estudo']}")
                    raise

            logger.info(f"Sending NEWAVE update for study ID: {params['id_estudo']} with tag: {tag_update}")
            if send_sistema:
                send_all_newave_update(params['id_estudo'], params['path_download'], file_name, logger, logging_name, tag_update)
            
            execution_time = time.time() - start_time
            logger.info(f"Wind power update completed successfully. Total updates: {update_count}, "
                       f"Execution time: {execution_time:.2f} seconds")
            return True

        except Exception as e:
            logger.error(f"Fatal error in wind power update: {str(e)}. "
                        f"Study ID: {params['id_estudo']}, File: {file_name}")
            raise

    def update_carga(self, params: dict, path_sistema=None) -> bool:
        """Update load data in sistema.dat with enhanced logging."""
        
        start_time = time.time()
        send_sistema = False
        MAP_SUBMERCADO = {'SE': 1, 'S': 2, 'NE': 3, 'N': 4}
        MAP_TIPO = {5: 'PCH-MMGD', 6: 'PCT-MMGD', 7: 'EOL-MMGD', 8: 'UFV-MMGD'}
        MAP_MMGD_TOT = {5: 'vl_exp_pch_mmgd', 6: 'vl_exp_pct_mmgd', 7: 'vl_exp_eol_mmgd', 8: 'vl_exp_ufv_mmgd'}
        
        # Initialize logger once at the start
        logging_name = f'logging_carga.log'
        log_path = os.path.join(params['path_download'], logging_name)
        logger = criar_logger(logging_name, log_path)
        logger.info(f"Starting load data update ")

        try:
            df_data = self.get_dados_banco('newave/previsoes-cargas')
            df_data = df_data[df_data['patamar'] == 'media'].reset_index(drop=True)
            df_data['data_referente'] = pd.to_datetime(df_data['data_referente'])
            df_data['data_referente'] = df_data['data_referente'].dt.to_period('M')

            file_name = 'sistema.dat'
            if path_sistema is None:
                logger.debug(f"Downloading {file_name}")
                path_sistema = download_newave_update(params['id_estudo'], logger, params['path_download'], file_name)
                send_sistema = True
                logger.info(f"Downloaded {file_name} to {path_sistema}")
            
            tag_update = f"CARGA-NW{datetime.strptime(df_data['data_produto'][0], '%Y-%m-%d').strftime('(%d/%m)')}"
            logger.debug(f"Generated update tag: {tag_update}")

            for path in path_sistema:
                logger = criar_logger(logging_name, os.path.join(os.path.dirname(path), logging_name))
                logger.info(f"Processing file: {path}")
                try:
                    dger = Dger.read(os.path.join(os.path.dirname(path), 'dger.dat'))
                    sistema = Sistema.read(path)
                    c_adic = Cadic.read(os.path.join(os.path.dirname(path), 'c_adic.dat'))
                    data_deck = datetime(dger.ano_inicio_estudo, dger.mes_inicio_estudo, 1)
                    logger.debug(f"Study start date from dger.dat: {data_deck},  File: {path}")

                    df_pq = sistema.geracao_usinas_nao_simuladas
                    df_carga = sistema.mercado_energia 
                    df_cadic = c_adic.cargas
                    logger.debug(f"Loaded {len(df_pq)} non-simulated generation records, {len(df_carga)} market energy records, "
                                f"{len(df_cadic)} additional load records,  File: {path}")

                    for mes_ano in df_data['data_referente'].unique():
                        for ss in df_data['submercado'].unique():
                            filter_base = ((df_pq['data'] == mes_ano.start_time) & 
                                        (df_pq['codigo_submercado'] == MAP_SUBMERCADO[ss]))
                            filter_data = (df_data['data_referente'] == mes_ano) & (df_data['submercado'] == ss)
                            filter_carga = ((df_carga['data'] == mes_ano.start_time) & 
                                        (df_carga['codigo_submercado'] == MAP_SUBMERCADO[ss]))

                            # Update non-simulated generation (MMGD)
                            for chave, valor in MAP_MMGD_TOT.items():
                                try:
                                    old_value = df_pq.loc[(df_pq['indice_bloco'] == chave) & filter_base, 'valor'].values[0]
                                    new_value = round(df_data.loc[filter_data, valor].values[0], 0)
                                    df_pq.loc[(df_pq['indice_bloco'] == chave) & filter_base, 'valor'] = new_value
                                    logger.info(f"Updated MMGD ,  Submarket: {ss.rjust(2)},  "
                                            f"Source: {MAP_TIPO[chave].rjust(8)},  Month: {mes_ano},  "
                                            f"Old value: {str(old_value).rjust(8)},  New value: {str(new_value).rjust(8)}")
                                except IndexError as e:
                                    logger.error(f"Failed to update MMGD,  Submarket: {ss},  "
                                                f"Source: {MAP_TIPO[chave]},  Month: {mes_ano},  Error: {str(e)}")
                                    raise

                            # Update market energy (LOAD)
                            try:
                                old_value = df_carga.loc[filter_carga, 'valor'].values[0]
                                new_value = round(df_data.loc[filter_data, 'vl_carga'].values[0], 0)
                                df_carga.loc[filter_carga, 'valor'] = new_value
                                logger.info(f"Updated LOAD ,  Submarket: {ss.rjust(2)},  Source: {("CARGA").rjust(8)},  "
                                        f"Month: {mes_ano},  Old value: {str(old_value).rjust(8)},  "
                                        f"New value: {str(new_value).rjust(8)}")
                            except IndexError as e:
                                logger.error(f"Failed to update Load| Submarket: {ss},  Month: {mes_ano},  "
                                            f"Error: {str(e)}")
                                raise

                            # Update additional loads (MMGD)
                            map_mmgd = 'MMGD ' + ss
                            try:
                                filter_cadic = ((df_cadic['data'] == mes_ano.start_time) & 
                                        (df_cadic['codigo_submercado'] == MAP_SUBMERCADO[ss])&
                                        (df_cadic['razao'] == map_mmgd))
                                old_value = df_cadic.loc[filter_cadic, 'valor'].values[0]
                                new_value = round(df_data.loc[filter_data, 'vl_base_total_mmgd'].values[0], 0)
                                df_cadic.loc[filter_cadic, 'valor'] = new_value
                                logger.info(f"Updated CADIC,  Submarket: {ss.rjust(2)},  Source: {map_mmgd.rjust(8)},  "
                                        f"Month: {mes_ano},  Old value: {str(old_value).rjust(8)},  "
                                        f"New value: {str(new_value).rjust(8)}")
                            except IndexError as e:
                                logger.error(f"Failed to update CADIC,  Submarket: {ss},  Source: {map_mmgd},  "
                                            f"Month: {mes_ano},  Error: {str(e)},  File: {path}")
                                raise
                        
                    sistema.geracao_usinas_nao_simuladas = df_pq
                    sistema.mercado_energia = df_carga
                    c_adic.cargas = df_cadic 
                    logger.info(f"Writing updated files,  sistema.dat: {path}")
                    logger.info(f"Writing updated files,  c_adic.dat:  {os.path.join(os.path.dirname(path), 'c_adic.dat')}")

                    sistema.write(path)
                    c_adic.write(os.path.join(os.path.dirname(path), 'c_adic.dat'))
                    logger.info(f"Successfully updated and wrote files,  sistema.dat: {path}")
                    logger.info(f"Successfully updated and wrote files,  c_adic.dat:  {os.path.join(os.path.dirname(path), 'c_adic.dat')}")

                except Exception as e:
                    logger.error(f"Error processing file,  Path: {path},  Error: {str(e)}")
                    raise

            logger.info(f"Sending NEWAVE update,  Tag: {tag_update}")
            if send_sistema:
                send_all_newave_update(params['id_estudo'], params['path_download'], file_name, logger, logging_name, tag_update)
                send_all_newave_update(params['id_estudo'], params['path_download'], 'c_adic.dat', logger, logging_name, tag_update)
                logger.info(f"Sent NEWAVE update,  Files: {file_name}, c_adic.dat ")

            execution_time = time.time() - start_time
            logger.info(f"Load data update completed,  Execution time: {execution_time:.2f} seconds")
            return True

        except Exception as e:
            logger.error(f"Fatal error in load data update,  File: {file_name},  Error: {str(e)}")
            raise

if __name__ == '__main__':
    pass
 