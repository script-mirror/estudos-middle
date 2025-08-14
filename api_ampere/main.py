import os
import datetime
import pandas as pd
from ampere.ampere import list_estudos, get_estudos

homePath =  os.path.expanduser('~')
downloadsPath = os.path.join(homePath, 'Downloads')

if __name__ == "__main__":
    
    data_prev = datetime.datetime.now()
    data_acomph = data_prev - datetime.timedelta(days=1)
    data_acomph = data_prev
    hoje = datetime.datetime.today().strftime('%Y%m%d')
    modelo = 'ONS-OFICIAL-NT00752020-RVEXT-VMEDPONDERADA'
    str_acomph = f'ACOMPH{data_acomph.strftime('%Y%m%d')}'
    str_prev = data_prev.strftime('%Y%m%d')
    
    # # Todos os estudos disponíveis
    estudos_TODOS = pd.DataFrame(list_estudos())
    estudos_TODOS[estudos_TODOS['data_previsao'].str.contains(hoje+'-PSAT')]
    
    # # estudos com acomph do dia 20250605
    # estudos_acomph_ontem = pd.DataFrame(list_estudos(acomph=str_acomph, data_prev=None, modelo=None))
    # print(estudos_acomph_ontem)
    
    # # Estudos rodados hoje
    # estudos_de_hoje = pd.DataFrame(list_estudos(acomph=None, data_prev=str_prev, modelo=None))
    # print(estudos_de_hoje)
    # print('Estudos disponiveis de hoje:')
    # print(estudos_de_hoje.cenario.unique())
    
    # # Estudos com nome de gfs
    # estudos_gfs = pd.DataFrame(list_estudos(acomph=None, data_prev=None, modelo='GFS'))
    # print(estudos_gfs)
    #ONS-OFICIAL-NT00752020-RVEXT-VMEDPONDERADA
    
    path_zip = os.path.join('', f'{str_prev}_{str_acomph}_{modelo}.zip')
    if get_estudos(acomph=str_acomph, data_prev=str_prev, modelo=modelo, nomezip=path_zip):
        print(f'Arquivo baixado: {path_zip}')
    