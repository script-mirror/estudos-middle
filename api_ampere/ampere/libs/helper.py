
import os
import sys
import datetime

# libsDir = os.path.dirname(os.path.abspath(__file__))
# appDir = os.path.dirname(libsDir)
# appsDir = os.path.dirname(appDir)
# rootDir = os.path.dirname(appsDir)

homePath =  os.path.expanduser('~')
downloadsPath = os.path.join(homePath, 'Downloads')

def printHelper():
    data = datetime.datetime.now()
    path_zip = os.path.join(downloadsPath,'flux-automatic-daily-1730309199.zip')
    lista_modelos = ['ONS-OFICIAL-NT00752020-RVEXT-VMEDPONDERADA','GFS','GEFS','ETA40','RVEXT-VMEDPONDERADA-CLIMATOLOGIA','ONS-OFICIAL-NT00752020-RVEXT-CLUSTER01']
    print(f'python {sys.argv[0]} data {data.strftime('%d/%m/%Y')}')
    print(f'python {sys.argv[0]} listar_rodadas_disponiveis data_previsao {data.strftime('%d/%m/%Y')} pos_acomph 1 pos_psat 1')
    print(f'python {sys.argv[0]} baixar_rodada modelo GFS data_previsao {data.strftime('%d/%m/%Y')} pos_acomph 1 pos_psat 1')
    print(f'python {sys.argv[0]} inserir_rodadas_banco lista_modelos "[\'{"','".join(lista_modelos[:3])}\']" data_previsao {data.strftime('%d/%m/%Y')} pos_acomph 1 pos_psat 1')
    print(f'python {sys.argv[0]} inserir_rodadas_banco_ja_baixadas path_zip {path_zip} modelo {lista_modelos[1]} data_previsao {data.strftime('%d/%m/%Y')} pos_acomph 1 pos_psat 1')
    print(f'python {sys.argv[0]} baixar_arquivos_rodada_automatica lista_modelos "[\'{"','".join(lista_modelos[:3])}\']" data_previsao {data.strftime('%d/%m/%Y')} pos_acomph 1 pos_psat 1')
    
    
    exit()


def parametrosDefault(parametros:dict ={}):
    
    if 'data' not in parametros or parametros['data'] is None:
        parametros['data'] = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        
    return parametros


if __name__ == '__main__':
    print(parametrosDefault())