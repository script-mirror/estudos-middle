import pandas as pd
import locale
from datetime import datetime, timedelta
from pathlib import Path
import warnings
import numpy as np
from typing import Union, List
from middle.utils import Constants 
consts = Constants()
import requests
from middle.utils.auth import get_auth_header, setup_logger
from middle.utils import SemanaOperativa
logger = setup_logger()
# Configurações iniciais
warnings.filterwarnings("ignore")
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

class Paths:
    BASE_PATH = Path(consts.PATH_PROJETOS + '/estudos-middle')
    OUTPUT = BASE_PATH / 'api_prospec/calculo_volume'

class VolumeUHEProcessor:
    
    def __init__(self):
        self.paths = Paths()
        self.today = datetime.today()
        self.url_get = consts.POST_DADOS_HIDRAULICOS_UHE
   
    def get_data_from_database(self, data_referente) -> None:
        try:
            logger.debug("Sending GET request to %s with %d records", self.url_get)
            res: requests.Response = requests.get(
                self.url_get,
                params={'data_inicial': data_referente.date()},
                headers=get_auth_header()
            )
            logger.debug("Received GET response with status code: %d", res.status_code)
            
            if res.status_code != 200:
                logger.error("Failed to post GET data to database: status %d, response: %s",
                            res.status_code, res.text)
                res.raise_for_status()
            return pd.DataFrame(res.json())
        except Exception as e:
            logger.error("Failed to get EAR data to database: %s", str(e), exc_info=True)
            raise
 
    def regress_post(self, nposto: str, df: pd.DataFrame, 
                    cadastro: pd.DataFrame, diasproj: int) -> float:
        nregred = cadastro.loc[nposto]['d_regred']
        usina = cadastro.loc[nposto]['usina']
        fator = ((df.loc[usina][1] - df.loc[usina][nregred]) / nregred)
        a = df.loc[usina][1] + (fator * diasproj)
        return round(a, 2)

    def formula_itaipu(self, vol: float) -> float:
        """Calcula a cota para Itaipu com base no volume."""
        a0 = 1.640E+02
        a1 = 4.807E-03
        a2 = -1.894E-07
        a3 = 4.205E-12
        a4 = -3.772223E-17
        cota = a0 + a1 * vol + a2 * (vol ** 2) + a3 * (vol ** 3) + a4 * (vol ** 4)
        return round(cota, 2)

    def volume_itaipu(self, cota: float) -> float:
        """Converte cota para volume percentual para Itaipu."""
        if cota <= 219:
            vol_p = 0
        elif cota >= 220.3:
            vol_p = 1
        else:
            vol_min = 27695.19
            vol_max = 29403.91
            vol_p = 0
            vol_1 = vol_min
            while self.formula_itaipu(vol_1) < cota:
                vol_p += 0.0001
                vol_1 = vol_min + (vol_max - vol_min) * vol_p
        return vol_p * 100

    def volume_itaipu_rdh(self, df_itaipu, cadastro,dias_proj) -> float:

        vol_itaipu = round(self.volume_itaipu(df_itaipu.loc[66][1]) + 
                          ((self.volume_itaipu(df_itaipu.loc[66][1]) - 
                            self.volume_itaipu(df_itaipu.loc[66][5])) / 5) * dias_proj, 2)
        if vol_itaipu >= 100:
            vol_itaipu = 100
        if vol_itaipu <= 0:
            vol_itaipu = 0
        return vol_itaipu

    def generate_volume_uhe(self, df_data: pd.DataFrame, df_itaipu: pd.DataFrame, cadastro: pd.DataFrame, dias_proj:int) -> bool:
        """Gera o arquivo volume_uhe.csv."""
        print('Gerando volume_uhe.csv...')        
        projecao = [self.regress_post(x, df_data, cadastro, dias_proj) for x in cadastro.index]
        projecao = pd.concat([pd.DataFrame(cadastro.iloc[:,1]).reset_index().drop(["posto"], axis=1),
                            pd.DataFrame(projecao)], axis=1)
        projecao.columns = ["Posto", "EARM"]
        
        lista_volume = pd.read_csv(self.paths.OUTPUT / "volume_uhe_lista.csv", sep=";")
        lista_volume.columns = ["Posto"]
        lista_volume["Posto"] = lista_volume["Posto"].astype(str)
        projecao["Posto"] = projecao["Posto"].astype(str)
        
        df_1 = pd.DataFrame({'' : [1] * len(lista_volume)})
        df_projecao = pd.merge(lista_volume, projecao, how='left', on="Posto")
        df_projecao = df_projecao.fillna(0)
        df_projecao = pd.concat([df_projecao, df_1], axis=1)
        
        df_projecao['EARM'].values[df_projecao['EARM'].values > 100] = 100
        df_projecao['EARM'].values[df_projecao['EARM'].values < 0] = 0
        df_projecao['EARM'][df_projecao['Posto'] == '73'] = 100
        df_projecao['EARM'][df_projecao['Posto'] == '66'] = self.volume_itaipu_rdh(df_itaipu, cadastro,dias_proj)
        
        df_projecao.to_csv(self.paths.OUTPUT / "volume_uhe.csv", mode='w', index=False, header=True, sep=";")

        return (self.paths.OUTPUT / "volume_uhe.csv").exists()

    def run(self) -> bool:

        cadastro  = pd.read_csv(self.paths.OUTPUT / "diasregred.csv", sep=";")
        cadastro  = cadastro.set_index('posto')
        df_data   = self.get_data_from_database( datetime.now()-timedelta(days=8))
        df_itaipu = df_data[['cd_usina', 'data_referente', 'nivel_montante']]
        df_itaipu = df_itaipu[df_itaipu['cd_usina']==66]
        df_itaipu = df_itaipu.pivot(index='cd_usina', columns='data_referente', values='nivel_montante')
        df_data   = df_data[['cd_usina', 'data_referente', 'volume']]
        df_data   = df_data.dropna(subset=['cd_usina'])
        df_data   = df_data.dropna(subset=['volume'])
        df_data   = df_data[df_data['cd_usina'].isin(cadastro['usina'])].reset_index(drop=True)
        df_data   = df_data.pivot(index='cd_usina', columns='data_referente', values='volume')
        max_data  = pd.to_datetime(max(df_data.keys()))
        dias_proj =  (SemanaOperativa.get_next_saturday(max_data) -max_data).days-1
        df_data.columns   = list(range( len(df_data.keys()), 0,-1))
        df_itaipu.columns = list(range( len(df_data.keys()), 0,-1))

        return self.generate_volume_uhe(df_data,df_itaipu, cadastro,dias_proj)

def gera_ear():
    """Função principal."""
    processor = VolumeUHEProcessor()
    return processor.run()

if __name__ == '__main__':
    gera_ear()
    