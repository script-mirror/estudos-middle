import logging
import os
import pandas as pd
import calendar
import warnings
from datetime import datetime, timedelta
from typing import Dict, List, Union, Tuple
from dadger_processor import leitura_dadger, escrever_dadger
from patamar_processor import read_patamar_carga, read_patamar_pq

warnings.filterwarnings("ignore")  # Ignore all warnings
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.getcwd(), 'output/log', 'logging.log'), mode='w'),  # Log to file
        logging.StreamHandler()  # Log to console
    ]
)
logger = logging.getLogger(__name__)

FONTE_MAP = {'PCH': 1, 'PCT': 2, 'EOL': 3, 'UFV': 4, 'PCHgd': 5, 'PCTgd': 6, 'EOLgd': 7, 'UFVgd': 8}
SUBMERCADO_MAP = {1: 'SECO', 2: 'S', 3: 'NE', 4: 'N'}


def validate_stages(df: Dict[str, Dict[str, pd.DataFrame]], stages: List[int]) -> None:
    for block, df_1 in df.items():
        str_list = list(df_1.keys())
        int_list = list(map(int, str_list))
        if max(int_list) > max(stages):
            logger.error("Dictionary: %s, contains more stages than dadger", df_1)
            logger.error("Stages in dadger: %s, Stages in dictionary: %s", max(stages), max(int_list))
            raise RuntimeError("Invalid stages: number of stages in dictionary exceeds those in dadger")
    logger.info("Stages validated successfully")


def days_per_month(start_date: datetime, end_date: datetime) -> Dict[int, int]:
    logger.debug("Entering days_per_month with start=%s, end=%s", start_date, end_date)
    result = {}
    if start_date.month == end_date.month:
        result[1] = 0
        result[2] = 7
        logger.debug("Same month, returning %s", result)
        return result
    result[1] = min(7, calendar.monthrange(start_date.year, start_date.month)[1] - start_date.day + 1)
    result[2] = 7 - result[1]
    logger.debug("Cross-month, returning %s", result)
    return result


def retrieve_data_stages(params: Dict[str, Union[str, pd.DataFrame]]) -> Tuple[datetime, List[int]]:
    logger.info("Retrieving date and number of stages")
    df_dadger, comments = leitura_dadger(params['dadger_path'])
    deck_date = datetime(int(df_dadger['DT']['ano'].iloc[0]), int(df_dadger['DT']['mes'].iloc[0]), int(df_dadger['DT']['dia'].iloc[0]))
    df_dadger['DP']['id'] = df_dadger['DP']['id'].astype(int)
    expected_stages = list(range(1, df_dadger['DP']['id'].max() + 1))
    logger.info("Deck date=%s, stages=%s", deck_date, expected_stages)
    return deck_date, expected_stages


def retrieve_load_levels(df_dadger: Dict[str, pd.DataFrame], load_level_data: pd.DataFrame) -> Dict[int, pd.DataFrame]:
    logger.debug("Processing load levels")
    year = int(df_dadger['DT']['ano'].iloc[0])
    month = int(df_dadger['DT']['mes'].iloc[0])
    day = int(df_dadger['DT']['dia'].iloc[0])
    deck_date = datetime(year, month, day)
    df_dadger['DP']['id'] = df_dadger['DP']['id'].astype(int)
    expected_stages = range(1, df_dadger['DP']['id'].max() + 1)

    end_rv_date = deck_date
    rv_date = deck_date
    stage_data = dict()
    for estagio in expected_stages:
        end_rv_date = rv_date + timedelta(days=6)
        days_each_month = days_per_month(rv_date, end_rv_date)
        logger.debug("Estagio %s: days per month=%s", estagio, days_each_month)

        df_1 = load_level_data.loc[(load_level_data['ano'].astype(int) == rv_date.year) & 
                                   (load_level_data['mes'].astype(int) == rv_date.month)].reset_index(drop=True).drop(['ano', 'mes'], axis=1)
        df_2 = load_level_data.loc[(load_level_data['ano'].astype(int) == end_rv_date.year) & 
                                   (load_level_data['mes'].astype(int) == end_rv_date.month)].reset_index(drop=True).drop(['ano', 'mes'], axis=1)
        df_1['carga_pu'] = df_1['carga_pu'] * (days_each_month[1] / 7)
        df_2['carga_pu'] = df_2['carga_pu'] * (days_each_month[2] / 7)

        stage_data[estagio] = df_1
        merged_df = pd.merge(df_1, df_2, on=['sub', 'patamar'], suffixes=('_df1', '_df2'))
        stage_data[estagio]['carga_pu'] = merged_df['carga_pu_df1'] + merged_df['carga_pu_df2']
        rv_date = rv_date + timedelta(days=7)
    logger.info("Load level processing complete, returning %s stages", len(stage_data))
    return stage_data


def complete_stages(df: pd.DataFrame, id_list: Union[str, int]) -> pd.DataFrame:
    logger.info("Completing stages for block")
    complete_df = pd.DataFrame(columns=df.columns)
    df['estagio'] = df['estagio'].astype(int)
    min_stage = int(min(df['estagio']))
    max_stage = int(max(df['estagio']))
    for name in df['id'].unique():
        df_name = df[df['id'] == name]
        stages = df_name['estagio'].astype(int).tolist()
        if name == id_list:
            for estagio in range(min_stage, max_stage + 1):
                if estagio not in stages:
                    logger.debug("Adding missing estagio %s for id=%s", estagio, name)
                    base_row = df_name.iloc[estagio-2].copy()
                    base_row['estagio'] = estagio
                    df_name = pd.concat([df_name, pd.DataFrame([base_row])], ignore_index=True)
                    df_name = df_name.sort_values(by=['id', 'estagio']).reset_index(drop=True)
        complete_df = pd.concat([complete_df, df_name], ignore_index=True)
    complete_df = complete_df.drop_duplicates(['id', 'estagio'])
    logger.info("Estagio completion done, %s rows", len(complete_df))
    return complete_df


def adjust_dp_block(df_dadger: Dict[str, pd.DataFrame], load_adjust_data: Dict[str, Dict[str, float]], type_param: str, absolute: bool = False, params: Dict[str, Union[str, pd.DataFrame, Dict]] = None) -> Dict[str, pd.DataFrame]:
    logger.info("Manipulating DP block")

    
    for submarket, value_list in load_adjust_data.items():
        for week, value in value_list.items():
            week = int(week)            
            condition = (df_dadger['DP']['id'].astype(int) == int(week)) & (df_dadger['DP']['sub'].astype(int) == int(submarket))

            if type_param == 'carga':

                load_level_data = params['load_level_data']
                load_level_df = retrieve_load_levels(df_dadger, load_level_data)
                df = load_level_df[week].loc[load_level_df[week]['sub'].astype(int) == int(submarket)]
                deck_value_p1 = df_dadger['DP'].loc[condition, 'valor_p1'].values[0].strip()
                deck_value_p2 = df_dadger['DP'].loc[condition, 'valor_p2'].values[0].strip()
                deck_value_p3 = df_dadger['DP'].loc[condition, 'valor_p3'].values[0].strip()

                if not absolute:
                    value += (float(deck_value_p1) / df['carga_pu'][df['patamar'] == 1].values[0] +
                              float(deck_value_p2) / df['carga_pu'][df['patamar'] == 2].values[0] +
                              float(deck_value_p3) / df['carga_pu'][df['patamar'] == 3].values[0]) / 3                 
                                        
                df_dadger['DP'].loc[condition, 'valor_p1'] = round(value * df['carga_pu'][df['patamar'] == 1].values[0], 0)
                df_dadger['DP'].loc[condition, 'valor_p2'] = round(value * df['carga_pu'][df['patamar'] == 2].values[0], 0)
                df_dadger['DP'].loc[condition, 'valor_p3'] = round(value * df['carga_pu'][df['patamar'] == 3].values[0], 0)

                logger.info("Adjusting DP: Submarket=%s, type=valor_p1, week=%s, current value=%s, new value=%s", submarket, week, deck_value_p1, df_dadger['DP'].loc[condition, 'valor_p1'].values[0])
                logger.info("Adjusting DP: Submarket=%s, type=valor_p2, week=%s, current value=%s, new value=%s", submarket, week, deck_value_p2, df_dadger['DP'].loc[condition, 'valor_p2'].values[0])
                logger.info("Adjusting DP: Submarket=%s, type=valor_p3, week=%s, current value=%s, new value=%s", submarket, week, deck_value_p3, df_dadger['DP'].loc[condition, 'valor_p3'].values[0])

            else:
                deck_value = df_dadger['DP'].loc[condition, type_param].values[0].strip()
                df_dadger['DP'].loc[condition, type_param] = round(value, 0) 
                logger.info("Adjusting DP: Submarket=%s, type=%s, week=%s, current value=%s, new value=%s", submarket, type_param, week, deck_value, df_dadger['DP'].loc[condition, type_param].values[0])
   
    logger.info("DP block manipulation complete")
    return df_dadger


def validate_plant(id: int, df: pd.DataFrame, condition: pd.Series, value: float, type_param: str, load_level: str) -> float:
    logger.debug("Validating %s for load level=%s, value=%s", type_param, load_level, value)
    if type_param == 'inflex':
        max_inflex = max(min(value, int(float(df.loc[condition, 'disp' + load_level]))), 0)
        if max_inflex < value:
            logger.warning("Inflex exceeds plant availability, UTE=%s, provided=%s, used=%s", id, value, max_inflex)
        logger.debug("Returning max_inflex=%s", max_inflex)
        return max_inflex

    elif type_param == 'disp':
        min_dispatch = max(0, value, int(float(df.loc[condition, 'inflex' + load_level])))
        if min_dispatch > value:
            logger.warning("Dispatch below plant inflexibility, UTE=%s, provided=%s, used=%s", id, value, min_dispatch)
        logger.debug("Returning min_dispatch=%s", min_dispatch)
        return min_dispatch

    else:
        logger.debug("Returning value=%s", max(value, 0))
        return max(value, 0)
    

def adjust_ct_block(df_dadger: Dict[str, pd.DataFrame], df: Dict[str, Dict[str, float]], type_param: str, absolute: bool = True , params: Dict[str, Union[str, pd.DataFrame, Dict]] = None) -> Dict[str, pd.DataFrame]:
    logger.info("Manipulating CT block for type=%s, absolute=%s", type_param, absolute)
    df_ct = df_dadger['CT']
    df_ct['id'] = df_ct['id'].astype(int)
    df_ct['estagio'] = df_ct['estagio'].astype(int)

    for id, value_list in df.items():
        id = int(id)
        df_ct = complete_stages(df_ct, id)
        for week, value in value_list.items():
            week = int(week)
            logger.info("Adjusting CT: id=%s, week=%s, value=%s", id, week, value)
            condition = (df_ct['id'] == id) & (df_ct['estagio'] == week)

            deck_value_p1 = df_ct.loc[condition, type_param + '_p1'].values[0].strip()
            deck_value_p2 = df_ct.loc[condition, type_param + '_p2'].values[0].strip()
            deck_value_p3 = df_ct.loc[condition, type_param + '_p3'].values[0].strip()

            if not absolute:
                df_ct.loc[condition, type_param + '_p1'] = validate_plant(id, df_ct, condition, value + int(float(df_ct.loc[condition, type_param + '_p1'])), type_param, '_p1')
                df_ct.loc[condition, type_param + '_p2'] = validate_plant(id, df_ct, condition, value + int(float(df_ct.loc[condition, type_param + '_p2'])), type_param, '_p2')
                df_ct.loc[condition, type_param + '_p3'] = validate_plant(id, df_ct, condition, value + int(float(df_ct.loc[condition, type_param + '_p3'])), type_param, '_p3')
            else:
                df_ct.loc[condition, type_param + '_p1'] = validate_plant(id, df_ct, condition, value, type_param, '_p1')
                df_ct.loc[condition, type_param + '_p2'] = validate_plant(id, df_ct, condition, value, type_param, '_p2')
                df_ct.loc[condition, type_param + '_p3'] = validate_plant(id, df_ct, condition, value, type_param, '_p3')
            
            logger.info("Adjusting CT: UTE=%s, type=%s_p1, week=%s, current value=%s, new value=%s", id, type_param, week, deck_value_p1, df_ct.loc[condition, type_param + '_p1'].values[0])
            logger.info("Adjusting CT: UTE=%s, type=%s_p2, week=%s, current value=%s, new value=%s", id, type_param, week, deck_value_p2, df_ct.loc[condition, type_param + '_p2'].values[0])
            logger.info("Adjusting CT: UTE=%s, type=%s_p3, week=%s, current value=%s, new value=%s", id, type_param, week, deck_value_p3, df_ct.loc[condition, type_param + '_p3'].values[0])

    df_dadger['CT'] = df_ct.copy()
    del df_ct
    logger.info("CT block manipulation complete")
    return df_dadger


def adjust_re_block(df_dadger: Dict[str, pd.DataFrame], input_df: Dict[str, Dict[str, float]], type_param: str, absolute: bool = True , params: Dict[str, Union[str, pd.DataFrame, Dict]] = None) -> Dict[str, pd.DataFrame]:
    logger.info("Manipulating RE block for type=%s, absolute=%s", type_param, absolute)
    df = df_dadger['LU']
    df['id'] = df['id'].astype(int)
    df['estagio'] = df['estagio'].astype(int)

    for id, value_list in input_df.items():
        id = int(id)
        df = complete_stages(df, id)
        for week, value in value_list.items():
            week = int(week)
            condition = (df['id'] == id) & (df['estagio'] == week)
            deck_value = int(float(df.loc[condition, type_param].iloc[0]))
            if not absolute:
                value += deck_value           

            df.loc[condition, type_param] = value

            logger.info("Adjusting LU: id=%s, type=%s, week=%s, current value=%s, new value=%s", id, type_param, week, deck_value, int(float(df.loc[condition, type_param].iloc[0])))

    df_dadger['LU'] = df.copy()
    del df
    logger.info("LU block manipulation complete")
    return df_dadger


def adjust_pq_block(df_dadger: Dict[str, pd.DataFrame], input_df: Dict[str, Dict[str, float]], type_param: str, absolute: bool = False, params: Dict[str, Union[str, pd.DataFrame, Dict]] = None) -> Dict[str, pd.DataFrame]:
    logger.info("Manipulating PQ block")
    pq_load_level = params['pq_load_level']
    df_dadger['PQ'] = df_dadger['PQ'].apply(lambda x: x.str.strip() if x.dtype == "object" else x)
       
    for source, value_list in input_df.items():
        df_dadger['PQ'] = complete_stages(df_dadger['PQ'], source) 
        source_load_level = FONTE_MAP[source.split('_')[1]]
        for week, value in value_list.items():
            week = int(week)
            condition_pq = (df_dadger['PQ']['estagio'].astype(int) == int(week)) & (df_dadger['PQ']['id'] == source)

            if type_param == 'geracao':
                
                load_level_df = retrieve_load_levels(df_dadger, pq_load_level[pq_load_level['tipo'].astype(int) == source_load_level])
                condition = (load_level_df[week]['sub'].astype(int) == int(df_dadger['PQ'][df_dadger['PQ']['id'] == source]['sub'].values[0])) & (load_level_df[week]['tipo'].astype(int) == source_load_level)
                df = load_level_df[week].loc[condition]

                deck_value_p1 = df_dadger['PQ'].loc[condition_pq, 'valor_p1'].values[0].strip()
                deck_value_p2 = df_dadger['PQ'].loc[condition_pq, 'valor_p2'].values[0].strip()
                deck_value_p3 = df_dadger['PQ'].loc[condition_pq, 'valor_p3'].values[0].strip()

                if not absolute:
                    value += (float(deck_value_p1) / df['carga_pu'][df['patamar'] == 1].values[0] +
                              float(deck_value_p2) / df['carga_pu'][df['patamar'] == 2].values[0] +
                              float(deck_value_p3) / df['carga_pu'][df['patamar'] == 3].values[0]) / 3                 
                                        
                df_dadger['PQ'].loc[condition_pq, 'valor_p1'] = str(round(value * df['carga_pu'][df['patamar'] == 1].values[0], 3))[:5]
                df_dadger['PQ'].loc[condition_pq, 'valor_p2'] = str(round(value * df['carga_pu'][df['patamar'] == 2].values[0], 3))[:5]
                df_dadger['PQ'].loc[condition_pq, 'valor_p3'] = str(round(value * df['carga_pu'][df['patamar'] == 3].values[0], 3))[:5]
                logger.info("Adjusting PQ: Source=%s, type=valor_p1, week=%s, current value=%s, new value=%s", source, week, deck_value_p1, df_dadger['PQ'].loc[condition_pq, 'valor_p1'].values[0])
                logger.info("Adjusting PQ: Source=%s, type=valor_p2, week=%s, current value=%s, new value=%s", source, week, deck_value_p2, df_dadger['PQ'].loc[condition_pq, 'valor_p2'].values[0])
                logger.info("Adjusting PQ: Source=%s, type=valor_p3, week=%s, current value=%s, new value=%s", source, week, deck_value_p3, df_dadger['PQ'].loc[condition_pq, 'valor_p3'].values[0])

            else:
                deck_value = df_dadger['PQ'].loc[condition_pq, type_param].values[0].strip()
                df_dadger['PQ'].loc[condition_pq, type_param] = str(round(value, 3))[:5] 
                logger.info("Adjusting PQ: Source=%s, type=%s, week=%s, current value=%s, new value=%s", source, type_param, week, deck_value, df_dadger['PQ'].loc[condition_pq, type_param].values[0])
   
    logger.info("PQ block manipulation complete")
    return df_dadger


def adjust_hq_block(df_dadger: Dict[str, pd.DataFrame], input_df: Dict[str, Dict[str, float]], type_param: str, absolute: bool = True , params: Dict[str, Union[str, pd.DataFrame, Dict]] = None)  -> Dict[str, pd.DataFrame]:
    logger.info("Manipulating HQ block for type=%s, absolute=%s", type_param, absolute)
    df = df_dadger['LQ']
    df['id'] = df['id'].astype(int)
    df['estagio'] = df['estagio'].astype(int)

    for id, value_list in input_df.items():
        id = int(id)
        df = complete_stages(df, id)
        for week, value in value_list.items():
            week = int(week)
            condition = (df['id'] == id) & (df['estagio'] == week)

            if type_param in ['lim_inf', 'lim_sup']:
                deck_value_p1 = df.loc[condition, type_param + '_p1'].values[0].strip()
                deck_value_p2 = df.loc[condition, type_param + '_p2'].values[0].strip()
                deck_value_p3 = df.loc[condition, type_param + '_p3'].values[0].strip()
                df.loc[condition, type_param + '_p1'] = value
                df.loc[condition, type_param + '_p2'] = value 
                df.loc[condition, type_param + '_p3'] = value
                logger.info("Adjusting LQ: id=%s, type=%s_p1, week=%s, current value=%s, new value=%s", id, type_param, week, deck_value_p1, int(float(df.loc[condition, type_param + '_p1'].iloc[0]))) 
                logger.info("Adjusting LQ: id=%s, type=%s_p1, week=%s, current value=%s, new value=%s", id, type_param, week, deck_value_p2, int(float(df.loc[condition, type_param + '_p2'].iloc[0]))) 
                logger.info("Adjusting LQ: id=%s, type=%s_p1, week=%s, current value=%s, new value=%s", id, type_param, week, deck_value_p3, int(float(df.loc[condition, type_param + '_p3'].iloc[0]))) 

            else:
                deck_value = int(float(df.loc[condition, type_param].iloc[0]))
                if not absolute:
                    value += deck_value 
                df.loc[condition, type_param] = value

                logger.info("Adjusting LQ: id=%s, type=%s, week=%s, current value=%s, new value=%s", id, type_param, week, deck_value, int(float(df.loc[condition, type_param].iloc[0])))

    df_dadger['LQ'] = df.copy()
    del df
    logger.info("LQ block manipulation complete")
    return df_dadger


def process_decomp(params: Dict[str, Union[str, pd.DataFrame, Dict]], sensitivity_df: Dict[str, Dict[str, Dict]]) -> None:
    try: 
        logger.info(" ")
        logger.info("Processing case=%s, date=%s", params['case'], datetime.now())
        logger.info(" ")
        
        logger.info("Starting process decomp with params=%s", sensitivity_df)
        logger.info("Study parameters updated: arquivo=%s", params['arquivo'])
        logger.info("Study parameters updated: dadger_path=%s", params['dadger_path'])
        logger.info("Study parameters updated: output_path=%s", params['output_path'])
        logger.info("Study parameters updated: id_estudo=%s", params['id_estudo'])
        params['load_level_path'] = os.path.abspath(os.path.abspath(os.getcwd() + '/input/patamar/patamar.dat'))    
        params['load_level_data'] = read_patamar_carga(params['load_level_path'])
        params['pq_load_level']   = read_patamar_pq(params['load_level_path']) 

        df_dadger, comments = leitura_dadger(params['dadger_path'])
        rv = int(params['dadger_path'].split('.')[1][-1:])
        deck_date, stages = retrieve_data_stages(params)

        logger.debug("Read dadger file, RV=%s", rv)
        
        for block, df_1 in sensitivity_df.items():
            for type_param, df in df_1.items():
                logger.info("============================================================================")
                
                absolute = True
                if 'absoluto' in df:
                    absolute = bool(df['absoluto'])
                    df.pop('absoluto')
                    logger.debug("Block=%s, type=%s, absolute=%s", block, type_param, absolute)

                validate_stages(df, stages)

                if block in BLOCK_FUNCTIONS:
                     df_dadger = BLOCK_FUNCTIONS[block](df_dadger, df, type_param, absolute, params)
                else:
                     raise ValueError("Unknown block type: %s", block)
  
        logger.info("============================================================================")
        logger.debug("Writing output for case %s", params['case'])
        escrever_dadger(df_dadger, comments, params['output_path'])        

    except Exception as e:
        logger.error("Error in analysis: %s", str(e))
        raise


BLOCK_FUNCTIONS = {
    'dp': adjust_dp_block,
    'ct': adjust_ct_block,
    're': adjust_re_block,
    'pq': adjust_pq_block,
    'hq': adjust_hq_block
}


def main(params: Dict[str, Union[str, pd.DataFrame, Dict]]) -> None:
    logger.info("Date=%s", datetime.now())
    logger.info("Starting sensitivity analysis with params=%s", params)
    params['dadger_path'] = "C:/WX2TB/Documentos/fontes/PMO/gera_sens_prospec/input/deck/dadger.rv0"
    params['output_path'] = "C:/WX2TB/Documentos/fontes/PMO/gera_sens_prospec/output/decomp/dadger_saida.rv0"


    # Exemplo de dados de sensibilidade
    params['sensibilidades'] = {
        "TESTE-FULL": {
            "hq": {
                'lim_sup':    {"215": {"1": 4700,"2": 4700,"3": 4700,"4": 4700}},
                'lim_inf':    {"215": {"1": 200, "2": 200, "3": 200, "4": 200}},
                'lim_sup_p1': {"215": {"1": 300, "2": 300, "3": 300, "4": 300}}
            }, 
            'ct': {
                'inflex': {'absoluto': True,  24: {1: 100}, 25: {1: 200}, 27: {1: 50}},
                'cvu':    {'absoluto': True,  24: {1: 0}, 25: {1: 0}, 27: {1: 0}},
                'disp':   {'absoluto': False, 24: {1: -250}, 25: {1: 0}, 27: {1: 0}}
            },             
            "pq": {
                "valor_p1": {
                    "NE_EOL": {"1": 6.0, "2": 2000, "3": 3000},
                    "SUL_EOL": {"1": 1000},
                "valor_p2": {
                    "NE_EOL": {"1": 6.0, "2": 2000, "3": 3000},
                    "SUL_EOL": {"1": 1000}
                }}
            },
             "dp": {
                "valor_p1": {"1": {"1": 44936, "2":46479 }, "2": {"1": 1000}},
                "valor_p2": {"1": {"1": 39527}, "2": {"1": 1000}},
                "valor_p3": {"1": {"1": 1000}, "2": {"1": 1000}}
            },
            "re": {
                'vmax_p1': {"409": {"1": 4700, "2": 4700, "3": 4700, "4": 4700}},
                'vmax_p2': {"409": {"1": 4700, "2": 4700, "3": 4700, "4": 4700}},
                'vmax_p3': {"409": {"1": 4700, "2": 4700, "3": 4700, "4": 4700}}
            }
        }
    }
    # Exemplo  {"menmonico": { "nome regex": {"submercado": {"estagio = 1, 2,3 ...": 44936, "2":46479 }, "2": {"1": 1000}},    
    atualizar_carga = {"dp": {
                "valor_p1": {"1": {"1": 44936, "2":46479 }, "2": {"1": 1000}},
                "valor_p2": {"1": {"1": 39527}, "2": {"1": 1000}},
                "valor_p3": {"1": {"1": 1000}, "2": {"1": 1000}}
                 }}
    
    params['case'] = "ATUALIZANDO-CARGA"
    process_decomp(params, atualizar_carga)

    #for sensitivity, sensitivity_df in params['sensibilidades'].items():
    #    params['case'] = sensitivity
    #    process_decomp(params, sensitivity_df)


if __name__ == '__main__':
    logger.info("Script execution started")
    params: Dict[str, Union[str, pd.DataFrame, Dict]] = {}
    main(params)