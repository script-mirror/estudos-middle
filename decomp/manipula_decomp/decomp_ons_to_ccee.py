# -*- coding: utf-8 -*-
import locale
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Union
import os
import shutil
import zipfile
from time import sleep

locale.setlocale(locale.LC_ALL, 'pt_BR.utf8')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constant for restriction codes
RESTRICTIONS = [
    "141", "143", "145", "147", "272", "449", "451", "453", "464", "470",
    "471", "501", "503", "505", "509", "513", "515", "517", "519", "521",
    "525", "527", "529", "531", "533", "535", "537", "539", "541", "543",
    "545", "547", "561", "562", "564", "570", "571", "604", "606", "608",
    "654", "611", "612", "613", "614", "615"
]

def validate_inputs(input_path: Union[str, Path], output_path: Union[str, Path], rev: str, dt_decomp: datetime) -> None:
    input_path = Path(input_path)
    output_path = Path(output_path)

    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    if not rev.strip():
        raise ValueError("Revision number cannot be empty")
    if not isinstance(dt_decomp, datetime):
        raise ValueError("dt_decomp must be a datetime object")

def dadger_ons_to_ccee(dadger_in_path: Union[str, Path], dadger_out_path: Union[str, Path], rev: str, dt_decomp: datetime) -> None:
    # Process dadger file, commenting specific lines and adding a TE header.

    validate_inputs(dadger_in_path, dadger_out_path, rev, dt_decomp)

    try:
        with open(dadger_in_path, 'r', encoding='utf-8') as dadger_in, open(dadger_out_path, 'w', encoding='utf-8') as dadger_out:
            for line in dadger_in:
                if line.startswith('TE'):
                    dadger_out.write(f"TE  {rev} - {dt_decomp.strftime('%B/%Y')} - ONS TO CCEE - RODADA AUTOMATICA \n")
                elif line.startswith(('RE', 'FU', 'LU', 'FT', 'FI')) and line[4:7] in RESTRICTIONS:
                    dadger_out.write(f"&{line}")
                else:
                    dadger_out.write(line)
        logger.info(f"Successfully processed dadger file: {dadger_in_path} -> {dadger_out_path}")
    except IOError as e:
        logger.error(f"Error processing dadger file: {e}")
        raise

def dadgnl_ons_to_ccee(dadgnl_in_path: Union[str, Path], dadgnl_out_path: Union[str, Path]) -> None:
    # Process dadgnl file, commenting and modifying specific lines.

    validate_inputs(dadgnl_in_path, dadgnl_out_path, "N/A", datetime.now())

    try:
        with open(dadgnl_in_path, 'r', encoding='utf-8') as dadgnl_in, open(dadgnl_out_path, 'w', encoding='utf-8') as dadgnl_out:
            flag = False
            for i, line in enumerate(dadgnl_in, 1):
                if 'eletrica' in line.lower():
                    logger.info(f"Line {i}: Found 'eletrica': {line.strip()}")
                    flag = True
                    dadgnl_out.write('& Bloco alterado na conversao WX\n')
                elif 'merito' in line.lower():
                    logger.info(f"Line {i}: Found 'merito': {line.strip()}")
                    flag = False
                    dadgnl_out.write('& Bloco nao alterado na conversao WX\n')
                
                if flag and not line.startswith('&'):
                    # Replace specific positions with '00.0' for columns 23-28, 38-43, 53-58
                    for offset in [0, 15, 30]:
                        if len(line) >= 28 + offset:
                            line = line[:23 + offset] + '00.0' + line[28 + offset:]
                    dadgnl_out.write(line)
                else:
                    dadgnl_out.write(line)
        logger.info(f"Successfully processed dadgnl file: {dadgnl_in_path} -> {dadgnl_out_path}")
    except IOError as e:
        logger.error(f"Error processing dadgnl file: {e}")
        raise

def cria_diretorio(path: str) -> None:
    os.makedirs(path, exist_ok=True)
    
def converte_decomp_ons_to_ccee(input_path: Union[str, Path], output_path: Union[str, Path], arqzip: str, arqdec: str, rev: str, dt_decomp: datetime) -> None:
    pathOut = str(Path(output_path))
    pathIn = str(Path(input_path))

    if os.path.exists(os.path.join(pathIn, arqzip)):
        print(arqzip + ' encontrado!')

        # DECOMP
        shutil.rmtree(pathOut, ignore_errors=True)
        cria_diretorio(pathOut)

        try:
            with zipfile.ZipFile(os.path.join(pathIn, arqzip), 'r') as zip_ref:
                zip_ref.extractall(pathIn)
            sleep(2)
        except Exception as e:
            print("Nao foi possivel dezipar arquivo PMO_deck_preliminar")
            logger.error(f"Error unzipping PMO: {e}")

        try:
            with zipfile.ZipFile(os.path.join(pathIn, arqdec), 'r') as zip_ref:
                zip_ref.extractall(pathOut)
            sleep(2)
        except Exception as e:
            print("Nao foi possivel dezipar arquivo DEC_ONS_")
            logger.error(f"Error unzipping DEC: {e}")

        dadger = None
        dadgercp = None
        dadgnl = None
        dadgnlcp = None

        for arquivo in os.listdir(pathOut):
            if 'dadger' in arquivo.lower():
                dadger = os.path.join(pathOut, arquivo)
                dadgercp = os.path.join(pathOut, arquivo + 'cp')
            if 'dadgnl' in arquivo.lower():
                dadgnl = os.path.join(pathOut, arquivo)
                dadgnlcp = os.path.join(pathOut, arquivo + 'cp')

        if dadgnl:
            try:
                shutil.copy(dadgnl, dadgnlcp)
            except Exception as e:
                print("Nao foi possivel fazer copia DADGNL")
                logger.error(f"Error copying DADGNL: {e}")

        if dadger:
            try:
                shutil.copy(dadger, dadgercp)
            except Exception as e:
                print("Nao foi possivel fazer copia DADGER")
                logger.error(f"Error copying DADGER: {e}")

        # comenta dadger e dadgnl para PLD
        if dadger and dadgercp:
            dadger_ons_to_ccee(dadgercp, dadger, rev, dt_decomp)

        if dadgnl and dadgnlcp:
            dadgnl_ons_to_ccee(dadgnlcp, dadgnl)

        try:
            if dadgercp:
                os.remove(dadgercp)
        except Exception as e:
            print("Arquivo DADGERcp nao encontrado")
            logger.warning(f"DADGERcp not found: {e}")

        try:
            if dadgnlcp:
                os.remove(dadgnlcp)
        except Exception as e:
            print("Arquivo DADGNLcp nao encontrado")
            logger.warning(f"DADGNLcp not found: {e}")

        shutil.make_archive(pathOut, 'zip', pathOut)
        shutil.rmtree(pathIn, ignore_errors=True)
        cria_diretorio(pathIn)

    else:
        print('Arquivo ' + arqzip + ' ainda nao disponivel!')
        print('SAINDO')
        # quit()  # Commented to avoid exiting, raise error instead
        raise FileNotFoundError(f"Arquivo {arqzip} nao encontrado em {pathIn}")


