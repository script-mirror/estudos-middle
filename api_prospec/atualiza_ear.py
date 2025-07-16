import pandas as pd
import locale
from datetime import datetime, timedelta
from pathlib import Path
import os
import time
import warnings
import numpy as np
from typing import Union, List
import openpyxl

# Configurações iniciais
warnings.filterwarnings("ignore")
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

class Paths:
    """Constantes para caminhos de diretórios."""
    BASE_PATH = Path('/projetos/estudos-middle')
    COD = BASE_PATH / 'api_prospec/calculo_volume'
    RDH =  '/WX2TB/Documentos/fontes/PMO/monitora_ONS/plan_acomph_rdh'
    OUTPUT = BASE_PATH / 'api_prospec/gerar_decks/volume'

class VolumeUHEProcessor:
    """Processador de dados de volume UHE a partir de relatórios RDH."""
    
    def __init__(self):
        self.paths = Paths()
        self.today = datetime.today()

    def get_rdh_filename(self, days_back: int) -> Path:
        """Obtém o caminho do arquivo RDH para uma data específica."""
        date_str = (self.today - timedelta(days=days_back)).strftime('%d%b%Y')
        upper_filename = f'RDH_{date_str.upper()}.xlsx'
        lower_filename = f'rdh_{date_str.lower()}.xlsx'
        #print(self.paths.RDH +'/'+ upper_filename)
        if (self.paths.RDH +'/'+ upper_filename).exists():
            return self.paths.RDH +'/'+ upper_filename
        elif (self.paths.RDH +'/'+ lower_filename).exists():
            return self.paths.RDH +'/'+ lower_filename
        raise FileNotFoundError(f"RDH file not found for {date_str}")

    def find_header_row(self, file_path: Path, sheet_name: str, 
                       header_keyword: str = 'APROVEITAMENTO') -> int:
        """Encontra a linha onde o cabeçalho começa, procurando por uma palavra-chave."""
        workbook = openpyxl.load_workbook(file_path, data_only=True)
        sheet = workbook[sheet_name]
        
        for row_idx, row in enumerate(sheet.iter_rows(values_only=True), start=0):
            row_values = [str(cell).strip() if cell is not None else '' for cell in row]
            if any(header_keyword in val for val in row_values):
                return row_idx
        raise ValueError(f"Header with '{header_keyword}' not found in sheet '{sheet_name}'")

    def simplify_multiindex_columns(self, columns):
        """Simplifica os nomes do MultiIndex e mapeia para nomes padronizados."""
        column_aliases = {
            'APROVEITAMENTO': ['APROVEITAMENTO', 'USINA'],
            'POSTO': ['POSTO', 'CODIGO'],
            'RES.': ['RES.', 'NIVEL', 'NÍVEL'],
            'ARM.': ['ARM.', 'VOLUME', 'VOLUME (%VU)']
        }
        
        simplified_columns = {}
        for col in columns:
            simplified_name = None
            for level in col:
                if level and not level.startswith('Unnamed'):
                    simplified_name = level
                    break
            if simplified_name == 'VALORES DO DIA':
                simplified_name = col[-1]
            
            for standard_name, aliases in column_aliases.items():
                if simplified_name in aliases:
                    simplified_columns[col] = standard_name
                    break
            else:
                simplified_columns[col] = simplified_name
        
        return simplified_columns

    def read_hydro_data(self, file_path: Path, sheet_name: str = 'Hidráulico-Hidrológica') -> pd.DataFrame:
        """Lê dados hidráulicos de um arquivo Excel."""
        try:
            header_row = self.find_header_row(file_path, sheet_name)
            header_rows = [header_row, header_row + 1, header_row + 2]
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_rows)
            
            column_mapping = self.simplify_multiindex_columns(df.columns)
            df.columns = [column_mapping[col] for col in df.columns]
            
            columns_to_read = ['APROVEITAMENTO', 'POSTO', 'RES.', 'ARM.']
            missing_columns = [col for col in columns_to_read if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing columns: {missing_columns}")
            
            filtered_df = df[columns_to_read]
            filtered_df.columns = ['APROVEITAMENTO', 'APROVEITAMENTO_2', 'POSTO', 'RES.', 'ARM.']
            filtered_df = filtered_df.drop(filtered_df.columns[1], axis=1)
            
            filtered_df = filtered_df.dropna()
            print(f"Read {len(filtered_df)} rows from {file_path}")
            return filtered_df
            
        except FileNotFoundError:
            print(f"Error: File {file_path} not found.")
            raise
        except ValueError as ve:
            print(f"Error: {ve}")
            raise
        except Exception as e:
            print(f"Error processing file: {e}")
            raise

    def process_rdh_data(self, n: int) -> pd.DataFrame:
        """Processa dados RDH para múltiplos dias."""
        df_combined = None
        for i in range(4 + n, n - 1, -1):
            filename = self.get_rdh_filename(i)
            print(f'Using RDH: {filename}')
            
            df2 = self.read_hydro_data(filename)
            
            if df_combined is None:
                df2 = df2[['POSTO', 'ARM.']].rename(columns={'POSTO': 'Posto', 'ARM.': f'd-{i-1}'})
                df_combined = df2.copy()
            else:
                df2 = df2[['POSTO', 'ARM.']].rename(columns={'POSTO': 'Posto', 'ARM.': f'd-{i-1}'})
                df_combined = pd.merge(df_combined, df2, on='Posto', how='inner')
        
        df_combined = df_combined.set_index('Posto')
        return df_combined

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

    def volume_itaipu_rdh(self, n: int) -> float:
        """Calcula o volume projetado para Itaipu a partir dos dados RDH."""
        df_itaipu = pd.DataFrame()
        diasproj = (self.today - timedelta(days=n)).weekday()
        if diasproj == 6:
            diasproj = 6
        else:
            diasproj = 5 - diasproj
        
        for i in range(4 + n, n - 1, -1):
            filename = self.get_rdh_filename(i)
            df_base = self.read_hydro_data(filename)
            df_itaipu = pd.concat([df_itaipu, pd.DataFrame(df_base[df_base['POSTO'] == 266]['RES.'])], axis=1)
        
        df_itaipu.columns = ['d-5', 'd-4', 'd-3', 'd-2', 'd-1']
        df_itaipu = df_itaipu.reset_index(drop=True)
        vol_itaipu = round(self.volume_itaipu(df_itaipu.iloc[:,-1][0]) + 
                          ((self.volume_itaipu(df_itaipu.iloc[:,-1][0]) - 
                            self.volume_itaipu(df_itaipu.iloc[:,0][0])) / 5) * diasproj, 2)
        
        if vol_itaipu >= 100:
            vol_itaipu = 100
        if vol_itaipu <= 0:
            vol_itaipu = 0
        return vol_itaipu

    def generate_volume_uhe(self, rdh_df: pd.DataFrame, cadastro: pd.DataFrame, n: int) -> bool:
        """Gera o arquivo volume_uhe.csv."""
        ndias = n
        dia_semana = self.today.weekday()
        if dia_semana == 5:
            diasproj = 7 + n
        elif dia_semana == 6:
            diasproj = 6 + n
        else:
            diasproj = 5 + n - dia_semana
        print('Dias projeção: ', diasproj)
        
        projecao = [self.regress_post(x, rdh_df, cadastro, diasproj) for x in cadastro.index]
        projecao = pd.concat([pd.DataFrame(cadastro.iloc[:,1]).reset_index().drop(["Posto"], axis=1),
                            pd.DataFrame(projecao)], axis=1)
        projecao.columns = ["Posto", "EARM"]
        
        lista_volume = pd.read_csv(self.paths.COD / "volume_uhe_lista.csv", sep=";")
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
        projecao_csv['EARM'][projecao_csv['Posto'] == '66'] = self.volume_itaipu_rdh(n)
        
        projecao_csv.to_csv(self.paths.OUTPUT / "volume_uhe.csv", mode='w', index=False, header=True, sep=";")
        print('volume_uhe.csv impresso em:', self.paths.OUTPUT / "volume_uhe.csv")
        print('-------------------------------------------------------------------')
        print(' ')
        return (self.paths.OUTPUT / "volume_uhe.csv").exists()

    def run(self) -> bool:
        """Executa o processamento principal."""
        print(' ')
        print('-------------------------------------------------------------------')
        print('Gerando volume_uhe.csv a partir dos seguintes RD:')
        
        try:
            os.remove(self.paths.OUTPUT / "volume_uhe.csv")
        except:
            print("Nao existia volume_uhe")
        
        n = 0
        while n < 10:
            try:
                path_planilha_rdh = self.get_rdh_filename(n)
                break
            except FileNotFoundError:
                n += 1
                continue
            except Exception:
                time.sleep(20)
                n += 1
        
        if n >= 10:
            raise FileNotFoundError("No RDH file found within 10 days")
        
        cadastro = pd.read_csv(self.paths.COD / "diasregred.csv", sep=";")
        cadastro = cadastro.set_index('Posto')
        rdh = self.process_rdh_data(n)
        return self.generate_volume_uhe(rdh, cadastro, n)

def main():
    """Função principal."""
    processor = VolumeUHEProcessor()
    return processor.run()

if __name__ == '__main__':
    main()
    