import logging
import os
import re
import pandas as pd
import codecs
from informacao_blocos import info_blocos

ABS_PATH = '/projetos/estudos-middle/decomp/manipula_decomp'
# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(ABS_PATH + '/output/log/logging.log', mode='w'),  # Log to file
        logging.StreamHandler()  # Also log to console
    ]
)
logger = logging.getLogger(__name__)

def leitura_dadger(filePath):
    logger.info(f"Starting to read file: {filePath}")
    
    try:
        file = open(filePath, 'r', encoding='latin-1')
        arquivo = file.readlines()
        file.close()
        logger.debug(f"Successfully read {len(arquivo)} lines from {filePath}")
    except Exception as e:
        logger.error(f"Error reading file {filePath}: {str(e)}")
        raise

    coment = []
    comentarios = {}
    blocos = {}
    for iLine in range(len(arquivo)):
        line = arquivo[iLine]
        if line[0] == '&':
            coment.append(line)
            logger.debug(f"Found comment line at index {iLine}")
        elif line[0].strip() == '':
            logger.debug(f"Skipping empty line at index {iLine}")
            continue
        else:
            mnemonico = line.split()[0]
            if mnemonico not in info_blocos:
                error_msg = f"Unknown mnemonic {mnemonico} at line {iLine}"
                logger.error(error_msg)
                raise ValueError(error_msg)
                
            infosLinha = re.split(info_blocos[mnemonico]['regex'], line)
            if len(infosLinha) < 2:
                error_msg = f"Invalid line format for mnemonic {mnemonico} at line {iLine}"
                logger.error(error_msg)
                raise ValueError(error_msg)

            if mnemonico not in blocos:
                blocos[mnemonico] = []
                comentarios[mnemonico] = {}
                logger.debug(f"Initialized new block for mnemonic {mnemonico}")
                
            if len(coment) > 0:
                comentarios[mnemonico][len(blocos[mnemonico])] = coment
                logger.debug(f"Stored {len(coment)} comments for {mnemonico}")
                coment = []
            
            blocos[mnemonico].append(infosLinha[1:-2])   # ultimo termo da lista e o que sobra da expressao regex (/n)
            logger.debug(f"Added data to block {mnemonico}")
        
    if len(coment) > 0:
        comentarios[mnemonico][len(blocos[mnemonico])] = coment
        logger.debug(f"Stored final {len(coment)} comments for {mnemonico}")
        
    df_dadger = {}
    for mnemonico in blocos:
        try:
            df_dadger[mnemonico] = pd.DataFrame(blocos[mnemonico], columns=info_blocos[mnemonico]['campos'])
            logger.debug(f"Created DataFrame for mnemonic {mnemonico} with {len(df_dadger[mnemonico])} rows")
        except Exception as e:
            logger.error(f"Error creating DataFrame for mnemonic {mnemonico}: {str(e)}")
            raise
    
    logger.info(f"File reading completed successfully")
    return df_dadger, comentarios

def escrever_bloco_restricoes(fileOut, df_dadger, mnemonico_restricao, submnemonicos_restricao, comentarios):
    logger.debug(f"Writing restrictions block for {mnemonico_restricao}")
    
    try:
        if mnemonico_restricao == 'HE':
            for index, row in df_dadger[mnemonico_restricao].iterrows():
                if index in comentarios[mnemonico_restricao]:
                    for coment in comentarios[mnemonico_restricao][index]:
                        fileOut.write(coment)
                        logger.debug(f"Writing comment for HE at index {index}")
                fileOut.write('{}\n'.format(info_blocos[mnemonico_restricao]['formatacao'].format(*row.values).strip()))
                logger.debug(f"Writing HE row at index {index}")
                
                restricoes_mesma_rhe = df_dadger[mnemonico_restricao].loc[df_dadger[mnemonico_restricao]['id'] == row['id']]
                
                if row.name == restricoes_mesma_rhe.iloc[-1].name:
                    id_restr = int(row['id'])
                    for mnemon in ['CM']:
                        restricoes_mnemon = df_dadger[mnemon].loc[df_dadger[mnemon]['id'].astype('int') == id_restr].drop_duplicates()
                        for index, row in restricoes_mnemon.iterrows():
                            if index in comentarios[mnemon]:
                                for coment in comentarios[mnemon][index]:
                                    fileOut.write(coment)
                                    logger.debug(f"Writing comment for CM at index {index}")
                            fileOut.write('{}\n'.format(info_blocos[mnemon]['formatacao'].format(*row.values).strip()))
                            logger.debug(f"Writing CM row at index {index}")

            if index+1 in comentarios[mnemon]:
                for coment in comentarios[mnemon][index+1]:
                    fileOut.write(coment)
                    logger.debug(f"Writing final comment for CM at index {index+1}")
        
        else:
            for index, row in df_dadger[mnemonico_restricao].iterrows():
                if index in comentarios[mnemonico_restricao]:
                    for coment in comentarios[mnemonico_restricao][index]:
                        fileOut.write(coment)
                        logger.debug(f"Writing comment for {mnemonico_restricao} at index {index}")
                fileOut.write('{}\n'.format(info_blocos[mnemonico_restricao]['formatacao'].format(*row.values).strip()))
                logger.debug(f"Writing {mnemonico_restricao} row at index {index}")
                id_restr = int(row['id'])
                
                for mnemon in submnemonicos_restricao:
                    restricoes_mnemon = df_dadger[mnemon].loc[df_dadger[mnemon]['id'].astype('int') == id_restr]
                    
                    for index, row in restricoes_mnemon.iterrows():
                        if index in comentarios[mnemon]:
                            for coment in comentarios[mnemon][index]:
                                fileOut.write(coment)
                                logger.debug(f"Writing comment for {mnemon} at index {index}")
                        fileOut.write('{}\n'.format(info_blocos[mnemon]['formatacao'].format(*row.values).strip()))
                        logger.debug(f"Writing {mnemon} row at index {index}")
    except Exception as e:
        logger.error(f"Error writing restrictions block {mnemonico_restricao}: {str(e)}")
        raise

def escrever_dadger(df_dadger, comentarios, filePath):
    logger.info(f"Starting to write dadger file: {filePath}")
    
    blocos_restricoes = {}
    blocos_restricoes['RE'] = ['LU', 'FU', 'FT', 'FI']
    blocos_restricoes['HQ'] = ['LQ', 'CQ']
    blocos_restricoes['HV'] = ['LV', 'CV']
    blocos_restricoes['HE'] = ['CM']
    
    bloco_dependentes = {}
    bloco_dependentes['VL'] = ['VU']
    
    blocos_infos_restricoes = []
    for mnemonico_rest in blocos_restricoes:
        blocos_infos_restricoes += blocos_restricoes[mnemonico_rest]

    try:
        fileOut = codecs.open(filePath, 'w+', 'utf-8')
        for mnemonico in df_dadger:
            if mnemonico in blocos_restricoes:
                logger.debug(f"Processing restriction block {mnemonico}")
                escrever_bloco_restricoes(fileOut, df_dadger, mnemonico, blocos_restricoes[mnemonico], comentarios)

            elif mnemonico in blocos_infos_restricoes:
                logger.debug(f"Skipping block {mnemonico} as it's part of restrictions")
                continue
            
            else:
                for index, row in df_dadger[mnemonico].iterrows():
                    if index in comentarios[mnemonico]:
                        for coment in comentarios[mnemonico][index]:
                            fileOut.write(coment)
                            logger.debug(f"Writing comment for {mnemonico} at index {index}")
                    fileOut.write('{}\n'.format(info_blocos[mnemonico]['formatacao'].format(*row.values).strip()))
                    logger.debug(f"Writing {mnemonico} row at index {index}")

                    if mnemonico in bloco_dependentes:
                        for dep in bloco_dependentes[mnemonico]:
                            mnemon_depend = df_dadger[dep].loc[df_dadger[dep]['id'].astype('int') == int(row['id'])]
                            df_dadger[dep].drop(mnemon_depend.index, inplace=True)
                            logger.debug(f"Removed {len(mnemon_depend)} dependent rows for {dep}")
                            
                            for index, row in mnemon_depend.iterrows():
                                if index in comentarios[dep]:
                                    for coment in comentarios[dep][index]:
                                        fileOut.write(coment)
                                        logger.debug(f"Writing comment for dependent {dep} at index {index}")
                                fileOut.write('{}\n'.format(info_blocos[dep]['formatacao'].format(*row.values).strip()))
                                logger.debug(f"Writing dependent {dep} row at index {index}")

        fileOut.close()
        logger.info(f"Successfully wrote to {filePath}")
        print(filePath)
        return filePath
    except Exception as e:
        logger.error(f"Error writing dadger file {filePath}: {str(e)}")
        raise
# Função para comparar os arquivos e encontrar alterações
def comparar_arquivos(original_path, impresso_path):
    logger.info(f"Comparando arquivos: original ({original_path}) e impresso ({impresso_path})")
    
    try:
        with open(original_path, 'r', encoding='latin-1') as f_original:
            linhas_original = f_original.readlines()
        
        with open(impresso_path, 'r', encoding='utf-8') as f_impresso:
            linhas_impresso = f_impresso.readlines()
        
        # Garantir que ambas as listas tenham o mesmo tamanho (preenchendo com vazio se necessário)
        max_len = max(len(linhas_original), len(linhas_impresso))
        linhas_original.extend([''] * (max_len - len(linhas_original)))
        linhas_impresso.extend([''] * (max_len - len(linhas_impresso)))
        
        # Comparar linha por linha
        alteracoes = []
        for i, (linha_orig, linha_imp) in enumerate(zip(linhas_original, linhas_impresso), start=1):
            if linha_orig.strip() != linha_imp.strip():
                alteracoes.append((i, linha_orig.strip(), linha_imp.strip()))
        
        # Logar as alterações encontradas
        if alteracoes:
            logger.info(f" ")
            logger.info(f"Encontradas {len(alteracoes)} alterações entre os arquivos")
            for num_linha, orig, imp in alteracoes:
                logger.info(f" ")
                logger.info(f"Linha {num_linha}: Original: '{orig}'")
                logger.info(f"Linha {num_linha}: Impresso: '{imp}'")
                
        else:
            logger.info("Nenhuma alteração encontrada entre os arquivos")
            
    except Exception as e:
        logger.error(f"Erro ao comparar arquivos: {str(e)}")
        raise

if __name__ == '__main__':
    try:
        path_dadger = os.path.abspath(r"dadger.rv2")
        logger.info(f"Main: Starting processing with input file {path_dadger}")
        df_dadger, comentarios = leitura_dadger(path_dadger)

        # Modificar mwmed_p1 onde ip=1 e sub=1 com logging
        condition = (df_dadger['DP']['ip'].astype(int) == 1) & (df_dadger['DP']['sub'].astype(int) == 1)
        old_value = df_dadger['DP'].loc[condition, 'mwmed_p1'].iloc[0] 
        new_value = 1500.0 
        df_dadger['DP'].loc[condition, 'mwmed_p1'] = new_value
        logger.info(f"Main: Changed mwmed_p1 for DP where ip=1 and sub=1 from {old_value} to {new_value}")

        output_path = 'dadger_lido.rv2'
        escrever_dadger(df_dadger, comentarios, output_path)

        # Comparar os arquivos após a escrita
        comparar_arquivos(path_dadger, output_path)

        logger.info("Main: Processing completed successfully")
    except Exception as e:
        logger.error(f"Main: Fatal error occurred: {str(e)}")
        raise