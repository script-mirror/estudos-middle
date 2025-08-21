import datetime
import os
import sys
import numpy as np
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from dateutil.relativedelta import relativedelta
import pandas as pd
from inewave.newave import Clast, Dger
from middle.utils import Constants, get_auth_header, setup_logger, criar_logger

sys.path.append(os.path.join(Constants().PATH_PROJETOS, "estudos-middle/api_prospec"))
from functionsProspecAPI import authenticateProspec, download_newave_update, send_all_newave_update

class NewaveUpdater:
    """Class to handle NEWAVE CVU updates for different types (conjuntural, merchant, estrutural)."""
    
    def __init__(self):
        self.consts = Constants()
        self.header = get_auth_header()
        self.base_url_api = self.consts.BASE_URL + '/api/v2/decks/'
        authenticateProspec(self.consts.API_PROSPEC_USERNAME, self.consts.API_PROSPEC_PASSWORD)
        self.logger = setup_logger()

    def update_cvu_conjuntural(self, params: dict, df_data: pd.DataFrame) -> bool:
        """Update CVU for conjuntural type."""
        logging_name = f'logging_cvu_{params["tipo_cvu"]}.log'
        logger = criar_logger(logging_name, os.path.join(params['path_download'], logging_name))
        logger.info(f"Starting update_cvu_conjuntural for tipo_cvu: {params['tipo_cvu']}")

        try:
            file_name = 'clast.dat'
            path_clast = download_newave_update(params['id_estudo'], logger, params['path_download'], file_name)
            tag_update = f"CVU-NW{datetime.strptime(df_data['dt_atualizacao'][0], '%Y-%m-%d').strftime('(%d/%m)')}"

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
                    #df_usinas['comentario_dif'] = df_usinas['comentario_dif'].str.ljust(17)
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
            tag_update = f"CVU-NW{datetime.strptime(df_data['dt_atualizacao'][0], '%Y-%m-%d').strftime('(%d/%m)')}"

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
                    #df_usinas['comentario_dif'] = df_usinas['comentario_dif'].str.ljust(17)
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
            tag_update = f"CVU-NW{datetime.strptime(df_data['dt_atualizacao'][0], '%Y-%m-%d').strftime('(%d/%m)')}"
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

if __name__ == '__main__':
    pass