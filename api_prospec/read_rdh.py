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
from middle.utils._constants import Constants 
consts = Constants()




class RDHprocessor:
    """Processador de dados do relatórios RDH."""
    
    def __init__(self):
        self.today = datetime.today()


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

    def read_hydro_data(self, file_path: Path) -> pd.DataFrame:
        """Lê dados hidráulicos de um arquivo Excel."""
        sheet_name: str = 'Hidráulico-Hidrológica'
        try:
            header_row = self.find_header_row(file_path, sheet_name)
            header_rows = [header_row, header_row + 1, header_row + 2]
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_rows)
            
            column_mapping = self.simplify_multiindex_columns(df.columns)
            df.columns = [column_mapping[col] for col in df.columns]
            
            columns_to_read = ['APROVEITAMENTO', 'POSTO', 'RES.', 'ARM.', 'TUR.', 'VER.',  'DFL.',  'AFL.', 'INC.', 'Usos', 'EVP.']            
            missing_columns = [col for col in columns_to_read if col not in df.columns]
            if missing_columns:
                raise ValueError(f"Missing columns: {missing_columns}")
            
            filtered_df = df[columns_to_read]
            filtered_df.columns = ['APROVEITAMENTO', 'APROVEITAMENTO2','POSTO', 'RES.', 'ARM.', 'TUR.', 'VER.',  'DFL.',  'AFL.', 'INC.', 'Usos', 'EVP.']
            filtered_df = filtered_df.drop(filtered_df.columns[1], axis=1)
            # Tenta converter 'col1' para float e verifica se são inteiros
            df['col1_numeric'] = pd.to_numeric(filtered_df['POSTO'], errors='coerce')
            mask = df['col1_numeric'].notna() & (df['col1_numeric'] % 1 == 0)

            # Mantém apenas as linhas válidas e remove a coluna temporária
            filtered_df = filtered_df[mask].drop(columns='POSTO')


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


def gera_ear():

    processor = RDHprocessor()
    return processor.read_hydro_data(Path("C:/Users/cs341053/Downloads/RDH_05AGO2025.xlsx"))

if __name__ == '__main__':
    gera_ear()
    