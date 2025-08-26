import os
import sys
from copy import deepcopy
from middle.message import send_whatsapp_message
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pandas as pd
from middle.utils import Constants, get_auth_header, criar_logger, SemanaOperativa
from middle.decomp.atualiza_decomp import process_decomp, retrieve_dadger_metadata, days_per_month
from middle.decomp import DecompParams

class DecompUpdater:
    
    def __init__(self):
        self.consts = Constants()
        sys.path.append(os.path.join(self.consts.PATH_PROJETOS, "estudos-middle/api_prospec"))
        from functionsProspecAPI import authenticateProspec, download_dadger_update, send_all_dadger_update
        authenticateProspec(self.consts.API_PROSPEC_USERNAME, self.consts.API_PROSPEC_PASSWORD)
        self.HEADER = get_auth_header()
        self.BASE_URL_API = self.consts.BASE_URL + '/api/v2/decks/'
        self.SUBMERCADOS = {'SECO': '1', 'S': '2', 'NE': '3', 'N': '4'}
        self.INDEX_PQ = {'SECO': 'SECO', 'S': 'SUL', 'NE': 'NE', 'N': 'N'}
        self.MAP_MMGD = {'PCHgd': 'exp_cgh', 'PCTgd': 'exp_ute', 'EOLgd': 'exp_eol', 'UFVgd': 'exp_ufv'}
        self.REGIONS_MMGD = ['SECO', 'SUL', 'NE', 'N']
        self.TYPES_MMGD = ['PCHgd', 'PCTgd', 'EOLgd', 'UFVgd']
        self.download_dadger_update = download_dadger_update
        self.send_all_dadger_update = send_all_dadger_update

    def update_carga_and_mmgd(self, params, df_data):
        logging_name = f'logging_carga.log'
        logger = criar_logger(logging_name, os.path.join(params['path_download'], logging_name))
        df_data['semana_operativa'] = pd.to_datetime(df_data['semana_operativa'])
        path_dadger = self.download_dadger_update(params['id_estudo'], logger, params['path_download'])
        tag_update = f"DP-DC{datetime.strptime(df_data['data_produto'][0], '%Y-%m-%d').strftime('(%d/%m)')}"
        first_dc = path_dadger[0]
        params_decomp = {
            'arquivo': os.path.basename(first_dc),
            'dadger_path': first_dc,
            'case': 'ATUALIZAÇÃO DE CARGA',
            'logger': criar_logger('logging_carga_rv' + first_dc[-1:] + '.log', os.path.dirname(first_dc) + '/logging_carga_rv' + first_dc[-1:] + '.log')
        }

        data_first_deck = retrieve_dadger_metadata(**params_decomp)['deck_date']
        data_produto = min(pd.to_datetime(df_data['semana_operativa'].unique().tolist()))

        if data_first_deck == data_produto:
            logger.info('Data do produto coincide com a data do deck, prosseguindo com a atualização')
        else:
            send_whatsapp_message(self.consts.WHATSAPP_DECKS, f"Erro na atualização de Carga \nData do produto: {data_produto} não confere com a data do deck: {data_first_deck}", '')
            logger.error(f"Data do produto: {data_produto} não confere com a data do deck: {data_first_deck}")
            raise ValueError('Data do produto não coincide com a data do deck, verifique os dados')

        for path in path_dadger:
            print(f'Path do dadger: {path}')
            params_decomp = {
                'arquivo': os.path.basename(path),
                'dadger_path': path,
                'output_path': path,
                'id_estudo': None,
                'case': 'ATUALIZAÇÃO DE CARGA',
                'logger': criar_logger('logger.log', os.path.dirname(path) + '/logger_rv' + path[-1:] + '.log')
            }

            meta_data = retrieve_dadger_metadata(**params_decomp)
            params_decomp['output_path'] = os.path.dirname(path)
            dict_carga = {'dp': self.criar_dict_dp(), 'pq': self.criar_dict_mmgd()}

            if meta_data['deck_date'] in df_data['semana_operativa'].unique():
                for stage in meta_data['stages']:
                    data = meta_data['deck_date'] + relativedelta(weeks=+stage-1)
                    if data in df_data['semana_operativa'].unique().to_pydatetime():
                        for submercado in self.SUBMERCADOS.keys():
                            filtered_data = df_data.loc[(df_data['semana_operativa'] == data) & (df_data['submercado'] == submercado)]
                            dict_carga['dp']['valor_p1'][self.SUBMERCADOS[submercado]][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'pesada'), 'carga_mmgd'].values[0])
                            dict_carga['dp']['valor_p2'][self.SUBMERCADOS[submercado]][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'media'), 'carga_mmgd'].values[0])
                            dict_carga['dp']['valor_p3'][self.SUBMERCADOS[submercado]][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'leve'), 'carga_mmgd'].values[0])

                            for mmgd in self.TYPES_MMGD:
                                dict_carga['pq']['valor_p1'][f'{self.INDEX_PQ[submercado]}_{mmgd}'][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'pesada'), self.MAP_MMGD[mmgd]].values[0])
                                dict_carga['pq']['valor_p2'][f'{self.INDEX_PQ[submercado]}_{mmgd}'][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'media'), self.MAP_MMGD[mmgd]].values[0])
                                dict_carga['pq']['valor_p3'][f'{self.INDEX_PQ[submercado]}_{mmgd}'][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'leve'), self.MAP_MMGD[mmgd]].values[0])

                process_decomp(deepcopy(DecompParams(**params_decomp)), dict_carga)
            else:
                logger.warning(f"Data do deck {meta_data['deck_date'].strftime('%d/%m/%Y')} não encontrada na base de dados de carga, ignorando atualização para este deck.")
        self.send_all_dadger_update(params['id_estudo'], params['path_download'], logger, 'logging_carga_rv', tag_update)

    def update_eolica(self, params, df_data):
        logging_name = f'logging_eolica.log'
        logger = criar_logger(logging_name, os.path.join(params['path_download'], logging_name))
        df_data['semana_operativa'] = pd.to_datetime(df_data['inicioSemana'])
        path_dadger = self.download_dadger_update(params['id_estudo'], logger, params['path_download'])
        tag_update = f"WEOL-DC{datetime.strptime(df_data['dataProduto'][0], '%Y-%m-%d').strftime('(%d/%m)')}"

        for path in path_dadger:
            print(f'Path do dadger: {path}')
            params_decomp = {
                'arquivo': os.path.basename(path),
                'dadger_path': path,
                'output_path': path,
                'id_estudo': None,
                'case': 'ATUALIZAÇÃO WEOL',
                'logger': criar_logger('logging_weol_rv.log', os.path.dirname(path) + '/logging_weol_rv' + path[-1:] + '.log')
            }

            meta_data = retrieve_dadger_metadata(**params_decomp)
            params_decomp['output_path'] = os.path.dirname(path)
            dict_carga = {'pq': self.criar_dict_weol()}

            if meta_data['deck_date'] in df_data['semana_operativa'].unique():
                df_month = df_data.loc[df_data['mesEletrico'] == (meta_data['deck_date'] + timedelta(days=6)).month]
                for stage in meta_data['stages']:
                    data = meta_data['deck_date'] + relativedelta(weeks=+stage-1)
                    if data in df_month['semana_operativa'].unique():
                        for submercado in self.SUBMERCADOS.keys():
                            if submercado in df_month['submercado'].unique():
                                filtered_data = df_month.loc[(df_data['semana_operativa'] == data) & (df_month['submercado'] == submercado)]
                                dict_carga['pq']['valor_p1'][f'{self.INDEX_PQ[submercado]}_EOL'][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'pesado'), 'valor'].values[0])
                                dict_carga['pq']['valor_p2'][f'{self.INDEX_PQ[submercado]}_EOL'][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'medio'), 'valor'].values[0])
                                dict_carga['pq']['valor_p3'][f'{self.INDEX_PQ[submercado]}_EOL'][str(stage)] = round(filtered_data.loc[(filtered_data['patamar'] == 'leve'), 'valor'].values[0])

                process_decomp(deepcopy(DecompParams(**params_decomp)), dict_carga)
            else:
                logger.warning(f"Data do deck {meta_data['deck_date'].strftime('%d/%m/%Y')} não encontrada na base de dados WEOL, ignorando atualização para este deck.")
        self.send_all_dadger_update(params['id_estudo'], params['path_download'], logger, 'logging_weol_rv', tag_update)

    def update_cvu(self, params, df_data):
        logging_name = f'logging_cvu_{params["tipo_cvu"]}_rv'
        logger = criar_logger(logging_name, os.path.join(params['path_download'], logging_name))
        path_dadger = self.download_dadger_update(params['id_estudo'], logger, params['path_download'])
        tag_update = f"CVU-DC{datetime.strptime(df_data['dt_atualizacao'][0], '%Y-%m-%d').strftime('(%d/%m)')}"

        for path in path_dadger:
            print(f'Path do dadger: {path}')
            params_decomp = {
                'arquivo': os.path.basename(path),
                'dadger_path': path,
                'output_path': path,
                'id_estudo': None,
                'case': 'ATUALIZAÇÃO CVU ' + params['tipo_cvu'].upper(),
                'logger': criar_logger(f"{logging_name}.log", os.path.dirname(path) + '/' + f"{logging_name}{path[-1:]}.log")
            }

            meta_data = retrieve_dadger_metadata(**params_decomp)
            params_decomp['output_path'] = os.path.dirname(path)
            dict_data = {'ct': {'cvu': {}}}
            for ute in meta_data['power_plants']:
                if ute in df_data['cd_usina'].unique():
                    dict_data['ct']['cvu'][f'{ute}'] = {}

            for stage in meta_data['stages']:
                data = meta_data['deck_date'] + relativedelta(weeks=+stage-1) + timedelta(days=6)
                for ute in meta_data['power_plants']:
                    if ute in df_data['cd_usina'].unique():
                        if params['tipo_cvu'] == 'merchant':
                            data_inicio = df_data[df_data['cd_usina'] == ute]['data_inicio'].values[0]
                            data_inicio = datetime.fromisoformat(str(data_inicio).replace('T', ' '))
                            data_fim = df_data[df_data['cd_usina'] == ute]['data_fim'].values[0]
                            data_fim = datetime.fromisoformat(str(data_fim).replace('T', ' '))
                            if data >= data_inicio and data <= data_fim:
                                dict_data['ct']['cvu'][f'{ute}'][f'{stage}'] = float(df_data.loc[(df_data['cd_usina'] == ute), 'vl_cvu'].values[0])
                        else:
                            dict_data['ct']['cvu'][f'{ute}'][f'{stage}'] = float(df_data.loc[(df_data['cd_usina'] == ute), 'vl_cvu'].values[0])

            process_decomp(deepcopy(DecompParams(**params_decomp)), dict_data)
        self.send_all_dadger_update(params['id_estudo'], params['path_download'], logger, logging_name, tag_update)

    def update_re(self, params, df_data):
        logging_name = f'logging_re_rv'
        logger = criar_logger(logging_name, os.path.join(params['path_download'], logging_name))
        path_dadger = self.download_dadger_update(params['id_estudo'], logger, params['path_download'])
        tag_update = f"RE-DC{datetime.strptime(df_data['data_produto'][0], '%Y-%m-%d').strftime('(%d/%m)')}"
        logging_name = f'logging_re_rv'

        for path in path_dadger:
            print(f'Path do dadger: {path}')
            params_decomp = {
                'arquivo': os.path.basename(path),
                'dadger_path': path,
                'output_path': path,
                'id_estudo': None,
                'case': 'ATUALIZAÇÃO REs',
                'logger': criar_logger(f"{logging_name}.log", os.path.dirname(path) + '/' + f"{logging_name}{path[-1:]}.log")
            }

            meta_data = retrieve_dadger_metadata(**params_decomp)
            params_decomp['output_path'] = os.path.dirname(path)
            dict_data = {'re': {'vmax_p1': {}, 'vmax_p2': {}, 'vmax_p3': {}}}
            for re in meta_data['re']:
                if re in df_data['re'].unique():
                    dict_data['re']['vmax_p1'][f'{re}'] = {}
                    dict_data['re']['vmax_p2'][f'{re}'] = {}
                    dict_data['re']['vmax_p3'][f'{re}'] = {}

            for stage in meta_data['stages']:
                data = (meta_data['deck_date'] + relativedelta(weeks=+stage-1))
                data_fim = (data + relativedelta(days=6)).replace(day=1)
                data = data.replace(day=1)
                for re in meta_data['re']:
                    if re in df_data['re'].unique():
                        if stage == min(meta_data['stages']):
                            data = data_fim
                        if data.strftime('%Y-%m-%d') in df_data['mes_ano'].unique():
                            df_filtred = df_data[(df_data['re'] == re) & (df_data['mes_ano'] == data.strftime('%Y-%m-%d'))]
                            dict_data['re']['vmax_p1'][f'{re}'][f'{stage}'] = int(df_filtred.loc[(df_filtred['patamar'] == 'pesada'), 'valor'].values[0])
                            dict_data['re']['vmax_p2'][f'{re}'][f'{stage}'] = int(df_filtred.loc[(df_filtred['patamar'] == 'media'), 'valor'].values[0])
                            dict_data['re']['vmax_p3'][f'{re}'][f'{stage}'] = int(df_filtred.loc[(df_filtred['patamar'] == 'leve'), 'valor'].values[0])

            if len(dict_data['re']['vmax_p1'][list(dict_data['re']['vmax_p1'].keys())[0]]) > 0:
                process_decomp(deepcopy(DecompParams(**params_decomp)), dict_data)
            else:
                logger.warning(f"Data do deck {meta_data['deck_date'].strftime('%d/%m/%Y')} não encontrada na base de dados de REs, ignorando atualização para este deck.")

        self.send_all_dadger_update(params['id_estudo'], params['path_download'], logger, logging_name, tag_update)
        return params

    def carga_nw_to_decomp(self, params, df_data):
        logging_name = 'logging_carga_nw_to_decomp.log'
        logger = criar_logger(logging_name, os.path.join(params['path_download'], logging_name))
        logger.info("Starting carga_nw_to_decomp function")
        
        MAP_COLUMNS = {
            'carga_mmgd': 'vl_carga_global',
            'exp_cgh': 'vl_exp_pch_mmgd',
            'exp_ute': 'vl_exp_pct_mmgd',
            'exp_eol': 'vl_exp_eol_mmgd',
            'exp_ufv': 'vl_exp_ufv_mmgd'
        }
        MAP_PAT = {'leve': 'leve', 'medio': 'media', 'pesada': 'pesada'}
        
        date_start = SemanaOperativa.get_next_saturday(datetime.now())
        logger.debug(f"Starting date for operative weeks: {date_start}")
        
        df_decomp = pd.DataFrame()
        data_produto = df_data['data_produto'].unique()[0] if len(df_data['data_produto'].unique()) > 0 else None
        if data_produto is None:
            logger.error("No unique data_produto found in df_data")
            return df_decomp
        logger.debug(f"Data produto: {data_produto}")
        
        for semana in range(50):
            date = date_start + relativedelta(weeks=semana)
            logger.debug(f"Processing operative week {semana + 1} for date {date.strftime('%Y-%m-%d')}")
            
            date_m1 = date.replace(day=1).strftime("%Y-%m-%d")
            date_m2 = (date + relativedelta(months=1)).replace(day=1).strftime("%Y-%m-%d")
            logger.debug(f"Dates for interpolation: month1={date_m1}, month2={date_m2}")
            
            for ss in df_data['submercado'].unique():
                logger.debug(f"Processing submercado: {ss}")
                
                for pat, valor in MAP_PAT.items():
                    logger.debug(f"Processing patamar: {pat} (mapped to {valor})")
                    dict_carga = {
                        'semana_operativa': date.strftime("%Y-%m-%d"),
                        'data_produto': data_produto,
                        'submercado': ss,
                        'patamar': valor
                    }
                    
                    for colum, coluna in MAP_COLUMNS.items():
                        valor_m1 = df_data.loc[
                            (df_data['data_referente'] == date_m1) &
                            (df_data['submercado'] == ss) &
                            (df_data['patamar'] == pat), coluna
                        ].values[0]
                        valor_m2 = df_data.loc[
                            (df_data['data_referente'] == date_m2) &
                            (df_data['submercado'] == ss) &
                            (df_data['patamar'] == pat), coluna
                        ].values[0]
                        
                        logger.debug(f"Values for {colum}: month1={valor_m1}, month2={valor_m2}")
                        
                        days = days_per_month(date, date + timedelta(days=7))
                        logger.debug(f"Days per month for {colum}: {days}")
                        
                        dict_carga[colum] = round((valor_m1 * days[1] + valor_m2 * days[2]) / 7,0)
                        logger.info(f"Values for {colum.rjust(10)} in submercado: {ss.rjust(2)}, patamar: {pat.rjust(6)}, value: {str(dict_carga[colum]).rjust(7)}")
                    
                    df_decomp = pd.concat([df_decomp, pd.DataFrame([dict_carga])], axis=0, ignore_index=True)
        
        df_decomp['submercado'] = df_decomp['submercado'].replace('SE', 'SECO')
        logger.info(f"Completed processing. Output DataFrame shape: {df_decomp.shape}")
        
        return df_decomp
            
    def criar_dict_dp(self):
        periods = [f'valor_p{i}' for i in range(1, 4)]
        inner_keys = [str(i) for i in range(1, 5)]
        data = {'dp': {}}
        for period in periods:
            data['dp'][period] = {}
            for key in inner_keys:
                data['dp'][period][key] = {}
        return data['dp']

    def criar_dict_mmgd(self):
        periods = [f'valor_p{i}' for i in range(1, 4)]
        data = {'pq': {}}
        for period in periods:
            data['pq'][period] = {}
            for region in self.REGIONS_MMGD:
                for type_ in self.TYPES_MMGD:
                    key = f'{region}_{type_}'
                    data['pq'][period][key] = {}
        return data['pq']

    def criar_dict_weol(self):
        periods = [f'valor_p{i}' for i in range(1, 4)]
        data = {'pq': {}}
        for period in periods:
            data['pq'][period] = {}
            for region in ['SUL', 'NE', 'N']:
                for type_ in ['EOL']:
                    key = f'{region}_{type_}'
                    data['pq'][period][key] = {}
        return data['pq']  
    
if __name__ == '__main__':
    updater = DecompUpdater()
