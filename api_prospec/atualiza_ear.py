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
        logger.info("Initialized VolumeUHEProcessor with base path: %s", self.paths.BASE_PATH)

    def get_data_from_database(self, data_referente) -> None:
        logger.info("Fetching data from database for date: %s", data_referente.date())
        try:
            logger.debug("Sending GET request to %s with date %s", self.url_get, data_referente.date())
            res: requests.Response = requests.get(
                self.url_get,
                params={'data_inicial': data_referente.date()},
                headers=get_auth_header()
            )
            logger.debug("Received GET response with status code: %d", res.status_code)
            
            if res.status_code != 200:
                logger.error("Failed to fetch data from database: status %d, response: %s",
                            res.status_code, res.text)
                res.raise_for_status()
            logger.info("Successfully fetched data from database")
            return pd.DataFrame(res.json())
        except Exception as e:
            logger.error("Failed to get EAR data from database: %s", str(e), exc_info=True)
            raise

    def regress_post(self, nposto: str, df: pd.DataFrame, 
                    cadastro: pd.DataFrame, diasproj: int) -> float:
        logger.debug("Calculating regression for posto: %s", nposto)
        try:
            nregred = cadastro.loc[nposto]['d_regred']
            usina = cadastro.loc[nposto]['usina']
            logger.debug("Using nregred: %d, usina: %s", nregred, usina)
            fator = ((df.loc[usina][1] - df.loc[usina][nregred]) / nregred)
            a = df.loc[usina][1] + (fator * diasproj)
            result = round(a, 2)
            logger.debug("Regression result for posto %s: %.2f", nposto, result)
            return result
        except Exception as e:
            logger.error("Error in regression for posto %s: %s", nposto, str(e), exc_info=True)
            raise

    def formula_itaipu(self, vol: float) -> float:
        """Calcula a cota para Itaipu com base no volume."""
        logger.debug("Calculating Itaipu cota for volume: %.2f", vol)
        a0 = 1.640E+02
        a1 = 4.807E-03
        a2 = -1.894E-07
        a3 = 4.205E-12
        a4 = -3.772223E-17
        cota = a0 + a1 * vol + a2 * (vol ** 2) + a3 * (vol ** 3) + a4 * (vol ** 4)
        result = round(cota, 2)
        logger.debug("Calculated Itaipu cota: %.2f", result)
        return result

    def volume_itaipu(self, cota: float) -> float:
        """Converte cota para volume percentual para Itaipu."""
        logger.debug("Converting cota %.2f to volume for Itaipu", cota)
        try:
            if cota <= 219:
                logger.debug("Cota <= 219, returning volume: 0")
                return 0
            elif cota >= 220.3:
                logger.debug("Cota >= 220.3, returning volume: 1")
                return 1
            else:
                vol_min = 27695.19
                vol_max = 29403.91
                vol_p = 0
                vol_1 = vol_min
                while self.formula_itaipu(vol_1) < cota:
                    vol_p += 0.0001
                    vol_1 = vol_min + (vol_max - vol_min) * vol_p
                result = vol_p * 100
                logger.debug("Calculated volume for cota %.2f: %.2f%%", cota, result)
                return result
        except Exception as e:
            logger.error("Error converting cota to volume: %s", str(e), exc_info=True)
            raise

    def volume_itaipu_rdh(self, df_itaipu, cadastro, dias_proj) -> float:
        logger.info("Calculating Itaipu volume for projection days: %d", dias_proj)
        try:
            vol_itaipu = round(self.volume_itaipu(df_itaipu.loc[66][1]) + 
                            ((self.volume_itaipu(df_itaipu.loc[66][1]) - 
                                self.volume_itaipu(df_itaipu.loc[66][5])) / 5) * dias_proj, 2)
            if vol_itaipu >= 100:
                logger.warning("Itaipu volume capped at 100 (original: %.2f)", vol_itaipu)
                vol_itaipu = 100
            if vol_itaipu <= 0:
                logger.warning("Itaipu volume capped at 0 (original: %.2f)", vol_itaipu)
                vol_itaipu = 0
            logger.debug("Calculated Itaipu volume: %.2f", vol_itaipu)
            return vol_itaipu
        except Exception as e:
            logger.error("Error calculating Itaipu volume: %s", str(e), exc_info=True)
            raise

    def generate_volume_uhe(self, df_data: pd.DataFrame, df_itaipu: pd.DataFrame, cadastro: pd.DataFrame, dias_proj: int) -> bool:
        """Gera o arquivo volume_uhe.csv."""
        logger.info("Generating volume_uhe.csv for %d projection days", dias_proj)
        try:
            projecao = [self.regress_post(x, df_data, cadastro, dias_proj) for x in cadastro.index]
            logger.debug("Completed regression calculations for all postos")
            projecao = pd.concat([pd.DataFrame(cadastro.iloc[:,1]).reset_index().drop(["posto"], axis=1),
                                pd.DataFrame(projecao)], axis=1)
            projecao.columns = ["Posto", "EARM"]
            logger.debug("Created projection DataFrame with shape: %s", projecao.shape)
            
            lista_volume = pd.read_csv(self.paths.OUTPUT / "volume_uhe_lista.csv", sep=";")
            logger.debug("Loaded volume_uhe_lista.csv with shape: %s", lista_volume.shape)
            lista_volume.columns = ["Posto"]
            lista_volume["Posto"] = lista_volume["Posto"].astype(str)
            projecao["Posto"] = projecao["Posto"].astype(str)
            
            df_1 = pd.DataFrame({'' : [1] * len(lista_volume)})
            df_projecao = pd.merge(lista_volume, projecao, how='left', on="Posto")
            logger.debug("Merged projection DataFrame with lista_volume, shape: %s", df_projecao.shape)
            df_projecao = df_projecao.fillna(0)
            df_projecao = pd.concat([df_projecao, df_1], axis=1)
            
            df_projecao['EARM'].values[df_projecao['EARM'].values > 100] = 100
            df_projecao['EARM'].values[df_projecao['EARM'].values < 0] = 0
            logger.debug("Applied EARM bounds (0-100)")
            df_projecao['EARM'][df_projecao['Posto'] == '73'] = 100
            df_projecao['EARM'][df_projecao['Posto'] == '66'] = self.volume_itaipu_rdh(df_itaipu, cadastro, dias_proj)
            logger.debug("Set specific EARM values for postos 73 and 66")
            
            output_file = self.paths.OUTPUT / "volume_uhe.csv"
            df_projecao.to_csv(output_file, mode='w', index=False, header=True, sep=";")
            logger.info("Successfully saved volume_uhe.csv to %s", output_file)
            
            file_exists = output_file.exists()
            logger.info("File %s exists: %s", output_file, file_exists)
            return file_exists
        except Exception as e:
            logger.error("Error generating volume_uhe.csv: %s", str(e), exc_info=True)
            raise

    def run(self) -> bool:
        logger.info("Starting VolumeUHEProcessor run")
        try:
            cadastro = pd.read_csv(self.paths.OUTPUT / "diasregred.csv", sep=";")
            logger.debug("Loaded diasregred.csv with shape: %s", cadastro.shape)
            cadastro = cadastro.set_index('posto')
            
            df_data = self.get_data_from_database(datetime.now() - timedelta(days=8))
            logger.debug("Retrieved data from database with shape: %s", df_data.shape)
            
            df_itaipu = df_data[['cd_usina', 'data_referente', 'nivel_montante']]
            df_itaipu = df_itaipu[df_itaipu['cd_usina'] == 66]
            df_itaipu = df_itaipu.pivot(index='cd_usina', columns='data_referente', values='nivel_montante')
            logger.debug("Processed Itaipu data with shape: %s", df_itaipu.shape)
            
            df_data = df_data[['cd_usina', 'data_referente', 'volume']]
            df_data = df_data.dropna(subset=['cd_usina'])
            df_data = df_data.dropna(subset=['volume'])
            df_data = df_data[df_data['cd_usina'].isin(cadastro['usina'])].reset_index(drop=True)
            df_data = df_data.pivot(index='cd_usina', columns='data_referente', values='volume')
            logger.debug("Processed main data with shape: %s", df_data.shape)
            
            max_data = pd.to_datetime(max(df_data.keys()))
            dias_proj = (SemanaOperativa.get_next_saturday(max_data) - max_data).days - 1
            logger.info("Calculated projection days: %d (max data: %s)", dias_proj, max_data)
            
            df_data.columns = list(range(len(df_data.keys()), 0, -1))
            df_itaipu.columns = list(range(len(df_data.keys()), 0, -1))
            logger.debug("Renamed DataFrame columns")
            
            result = self.generate_volume_uhe(df_data, df_itaipu, cadastro, dias_proj)
            logger.info("VolumeUHEProcessor run completed successfully: %s", result)
            return result
        except Exception as e:
            logger.error("Error in run method: %s", str(e), exc_info=True)
            raise

def gera_ear():
    """Função principal."""
    logger.info("Starting gera_ear function")
    try:
        processor = VolumeUHEProcessor()
        result = processor.run()
        logger.info("gera_ear completed with result: %s", result)
        return result
    except Exception as e:
        logger.error("Error in gera_ear: %s", str(e), exc_info=True)
        raise

if __name__ == '__main__':
    logger.info("Executing main script")
    gera_ear()