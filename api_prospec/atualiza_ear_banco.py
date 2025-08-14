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
from middle.utils.auth import get_auth_header
from middle.utils import SemanaOperativa

# Configurações iniciais
warnings.filterwarnings("ignore")
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

class Paths:
    """Constantes para caminhos de diretórios."""
    BASE_PATH = Path(consts.PATH_PROJETOS + '/estudos-middle')
    OUTPUT = BASE_PATH / 'api_prospec/calculo_volume'

class VolumeUHEProcessor:
    """Processador de dados de volume UHE a partir de relatórios RDH."""
    
    def __init__(self):
        self.paths = Paths()
        self.today = datetime.today()
   
    def get_rdh(self, data_referente):
        url = f"{consts.BASE_URL}/api/v2/ons/rdh"
        headers = get_auth_header()
        response = requests.get(
            url,
            params={"data_referente": data_referente.strftime('%Y-%m-%d')},
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
 
    def process_rdh_data(self) -> pd.DataFrame:
        """Processa dados RDH para múltiplos dias."""
        df_combined = None
        dias_regred = None
        for i in range(10):
            data  = self.today - timedelta(days=i)            
            df2 = pd.DataFrame(self.get_rdh(data))
            
            if not df2.empty:              
                
                df2 = df2[['cd_posto', 'vl_vol_arm_perc']].rename(columns={'cd_posto': 'Posto', 'vl_vol_arm_perc': f'd-{i-1}'})
                if df_combined is None:
                    df_combined = df2.copy()                   
                    dias_regred = (SemanaOperativa.get_next_saturday(data) -data).days
                else:
                    df_combined = pd.merge(df_combined, df2, on='Posto', how='inner')
        
        df_combined = df_combined.set_index('Posto')
        return df_combined, dias_regred

    def regress_post(self, nposto: str, df: pd.DataFrame, 
                    cadastro: pd.DataFrame, diasproj: int) -> float:
        """Calcula projeção de volume para um posto."""
        nregred = cadastro.loc[nposto][0]
        fator = ((df.loc[nposto][-1] - df.loc[nposto][5 - nregred]) / nregred)
        a = df.loc[nposto][-1] + (fator * diasproj)
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

    def volume_itaipu_rdh(self, rdh_df, cadastro,dias_proj) -> float:
        """Calcula o volume projetado para Itaipu a partir dos dados RDH."""
 
        df_itaipu = pd.DataFrame(rdh_df.loc[266])
        
        
        df_itaipu.columns = ['d-5', 'd-4', 'd-3', 'd-2', 'd-1']
        df_itaipu = df_itaipu.reset_index(drop=True)
        vol_itaipu = round(self.volume_itaipu(df_itaipu['d-1'].iloc[0]) + 
                          ((self.volume_itaipu(df_itaipu.iloc[:,-1][0]) - 
                            self.volume_itaipu(df_itaipu.iloc[:,0][0])) / 5) * dias_proj, 2)
        
        if vol_itaipu >= 100:
            vol_itaipu = 100
        if vol_itaipu <= 0:
            vol_itaipu = 0
        return vol_itaipu

    def generate_volume_uhe(self, rdh_df: pd.DataFrame, cadastro: pd.DataFrame, dias_proj:int) -> bool:
        """Gera o arquivo volume_uhe.csv."""
        print('Gerando volume_uhe.csv...')        
        projecao = [self.regress_post(x, rdh_df, cadastro, dias_proj) for x in cadastro.index]
        projecao = pd.concat([pd.DataFrame(cadastro.iloc[:,1]).reset_index().drop(["Posto"], axis=1),
                            pd.DataFrame(projecao)], axis=1)
        projecao.columns = ["Posto", "EARM"]
        
        lista_volume = pd.read_csv(self.paths.OUTPUT / "volume_uhe_lista.csv", sep=";")
        lista_volume.columns = ["Posto"]
        lista_volume["Posto"] = lista_volume["Posto"].astype(str)
        projecao["Posto"] = projecao["Posto"].astype(str)
        
        df_1 = pd.DataFrame({'' : [1] * len(lista_volume)})
        projecao_csv = pd.merge(lista_volume, projecao, how='left', on="Posto")
        projecao_csv = projecao_csv.fillna(0)
        projecao_csv = pd.concat([projecao_csv, df_1], axis=1)
        
        projecao_csv['EARM'].values[projecao_csv['EARM'].values > 100] = 100
        projecao_csv['EARM'].values[projecao_csv['EARM'].values < 0] = 0
        projecao_csv['EARM'][projecao_csv['Posto'] == '73'] = 100
        projecao_csv['EARM'][projecao_csv['Posto'] == '66'] = self.volume_itaipu_rdh(rdh_df, cadastro,dias_proj)
        
        projecao_csv.to_csv(self.paths.OUTPUT / "volume_uhe.csv", mode='w', index=False, header=True, sep=";")
        print('volume_uhe.csv impresso em:', self.paths.OUTPUT / "volume_uhe.csv")
        print('-------------------------------------------------------------------')
        print(' ')
        return (self.paths.OUTPUT / "volume_uhe.csv").exists()

    def run(self) -> bool:
        """Executa o processamento principal."""
        print(' ')
        print('-------------------------------------------------------------------')
        
        cadastro = pd.read_csv(self.paths.OUTPUT / "diasregred.csv", sep=";")
        cadastro = cadastro.set_index('Posto')
        df_rdh, dias_proj = self.process_rdh_data()
        return self.generate_volume_uhe(df_rdh, cadastro,dias_proj)

def gera_ear():
    """Função principal."""
    processor = VolumeUHEProcessor()
    return processor.run()

if __name__ == '__main__':
    gera_ear()
    