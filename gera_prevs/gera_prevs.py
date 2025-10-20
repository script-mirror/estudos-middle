import sys
import os
import requests
import shutil
import pandas as pd
import glob
import struct
from datetime import timedelta, datetime
from middle.utils import SemanaOperativa
from pathlib import Path
from middle.utils import setup_logger, Constants, get_auth_header, extract_zip

# Configura o logger globalmente uma única vez
logger = setup_logger()

class GeraPrevs():
    
    def __init__(self):
        self.logger = logger  # Usa o logger global
        self.logger.info("Initialized geraPrevs")
        self.conts = Constants()
        
    
    def run_workflow(self):
        logger.info("Starting workflow for GeraPrevs")
        self.run_process(start_year=None, end_year=None)
   
    def run_process(self, start_year, end_year):
        for year in range(start_year, end_year + 1):
            df_rdh   = self.get_data(self.conts.GET_DADOS_HIDRAULICOS_UHE, {'data_inicial': f'{year}-01-01','data_final': f'{year}-12-31'})
            df_hist  = self.get_data(self.conts.ENDPOINT_HISTORICO_VAZOES, year)    
            df_prevs = self.gera_prevs(df_rdh, df_hist, year)
            self.save_prevs(df_prevs, self.conts.PATH_PREVS)
        logger.info("Running process for GeraPrevs")

            
    def get_data(self, url, params) -> dict:
        try:
            res = requests.get(
                url=url,
                params=params,
                headers=get_auth_header()
            )
            if res.status_code != 200:
                res.raise_for_status()
            
            return pd.DataFrame(res.json())
        
        except Exception as e:
            self.logger.error("Failed to get data from database: %s", str(e), exc_info=True)
            raise    
 
    def gera_prevs(self,df_rdh, df_hist, year) -> pd.DataFrame:
        end_month = 12
        if datetime(year, 12, 31) > datetime.now():
            end_month = datetime.now().month

        dt_start = SemanaOperativa.get_last_saturday(datetime(year, 1, 1))
        dt_end = SemanaOperativa.get_last_saturday(datetime(year, end_month, 30)) 
        
        
        df = pd.DataFrame(index=pd.date_range(start=dt_start, end=dt_end))
        
        logger.info("Generating forecasts for year: %s", year)
        # Exemplo de implementação
        data = {
            'Posto1': [100, 200, 300],
            'Posto2': [150, 250, 350],
            'Posto3': [120, 220, 320]
        }
        df = pd.DataFrame(data, index=['2024-07-01', '2024-07-02', '2024-07-03'])
        return df
    

    
        

    
    def save_prevs(self, df: pd.DataFrame, path: str):
        nomePrevs = 'prevs.' 
        prevs_file_out = open(path  + '/' + nomePrevs,'w')
        numLine = 1
        for posto in df.index:
            line = str(numLine).rjust(6) + str(posto).rjust(5)
            for vazao in df.loc[posto]:
                if int(vazao) == 0: vazao = 1
                line += str(int(vazao)).rjust(10)    
            line += "\n"
            prevs_file_out.write(line)
            numLine += 1        
        prevs_file_out.close()
        

if __name__ == '__main__':
    logger.info("Starting GeraPrevs script execution")
    try:
        carga = GeraPrevs()
        carga.run_process(2024, 2024)
        logger.info("Script execution completed successfully")
    except Exception as e:
        logger.error("Script execution failed: %s", str(e), exc_info=True)
        raise