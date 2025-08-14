import requests
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.table as tbl
import io
from datetime import datetime
from middle.message import send_whatsapp_message
from middle.utils import Constants, get_auth_header
import logging

consts = Constants()





def get_cvu_banco(produto: str, fonte ='') -> dict:
    res = requests.get(consts.BASE_URL + '/api/v2/decks/'+ produto,
        params={ 'fonte': fonte},
        headers=get_auth_header()
    )
    if res.status_code != 200:
        res.raise_for_status()
    return pd.DataFrame(res.json())







   
def update_cvu(params):     
    
    if params['tipo_cvu'] == 'conjuntural_revisado':
            df_data = get_cvu_banco('cvu', 'conjuntural_revisado')
            df_data = df_data.sort_values('mes_referencia', ascending=False)
            df_data = df_data.drop_duplicates(subset=['cd_usina'], keep='first')
            df_data = df_data.reset_index(drop=True)
            df_data = df_data.sort_values('cd_usina').reset_index(drop=True)
             
    elif params['tipo_cvu'] == 'conjuntural':
        if params['dt_produto'].day > 15 and params['dt_produto'].day < 22:
            df_data = get_cvu_banco('cvu', 'conjuntural')
            df_data = df_data.sort_values('mes_referencia', ascending=False)
            df_data = df_data.drop_duplicates(subset=['cd_usina'], keep='first')
            df_data = df_data.reset_index(drop=True)
            df_data = df_data.sort_values('cd_usina').reset_index(drop=True)  
        else:
            send_whatsapp_message(consts.WHATSAPP_GILSEU,f"Erro na atualização CVU \nTipo: CVU {params['tipo_cvu']} \nData do produto: {params['dt_produto'].strftime('%d/%m/%Y')} \nNão confere com a data padrão de atualização.",'')
            raise ValueError(f"Data do produto {params['dt_produto'].strftime('%d/%m/%Y')} não está entre o 16º e o 21º dia do mês.")
        
    elif params['tipo_cvu'] == 'merchant':
        df_data = get_cvu_banco('cvu', 'merchant')
        df_data = df_data.sort_values('mes_referencia', ascending=False)
        df_data = df_data.drop_duplicates(subset=['cd_usina'], keep='first')
        df_data = df_data.reset_index(drop=True)
        df_data = df_data.sort_values('cd_usina').reset_index(drop=True) 
    else:
        send_whatsapp_message(consts.WHATSAPP_GILSEU,f"Erro na atualização CVU \nTipo: CVU {params['tipo_cvu']} \nData do produto: {params['dt_produto'].strftime('%d/%m/%Y')} \nNão confere com  nenhum padão de cvu.",'')
       