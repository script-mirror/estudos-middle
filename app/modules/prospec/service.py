import re
import os
import asyncio
import datetime
import pandas as pd
from typing import List
from fastapi import UploadFile
from app.core.config import settings
from .repository import ProspecRepository
from .schemas import (
    StudyExecutionDto, StudyResultDto, 
    DownloadResultDto, StudyInfoReadDto
)
from middle.utils import setup_logger
logger = setup_logger()


class ProspecService:
    def __init__(self, repository: ProspecRepository):
        self.repository = repository

    async def run_prospec_study(self, parametros: StudyExecutionDto) -> StudyResultDto:
        """Main function to run Prospec studies"""
        logger.info('')
        logger.info('--------------------------------------------------------------------------------#')
        logger.info(f'#-API do Prospec Iniciado: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

        if parametros.apenas_email:
            logger.info(f'Iniciando download dos resultados do estudo com id: {parametros.id_estudo}')
            return await self._download_resultados(parametros)
        
        elif not parametros.back_teste:
            return await self._run_regular_study(parametros)
        

    async def get_status_estudo(self, id_estudo: str) -> str:
        status = await self.repository.get_status_estudo(id_estudo)
        logger.info(f"Study status: {status}")
        return status


    async def _run_regular_study(self, parametros: StudyExecutionDto) -> StudyResultDto:
        """Run regular Prospec study"""
        await self.repository.authenticate()
        
        config = await self._get_study_configuration(parametros)
        
        id_estudo = await self._duplicate_and_configure_study(config, parametros)
        
        if config.get('send_volume', True):
            await self._send_volume_files(id_estudo)
        
        await self._associate_cuts_and_volumes(id_estudo, config)
        
        if parametros.executar_estudo:
            await self._start_execution(id_estudo, config)
        
        if parametros.aguardar_fim:
            return await self._wait_for_completion(id_estudo, config)
        
        return StudyResultDto(
            id_estudo=id_estudo,
            compilation_file="",
            status="ready",
            n_decks=0
        )


    async def _get_study_configuration(self, parametros: StudyExecutionDto) -> dict:
        """Get study configuration based on parameters"""
        config = {}
        
        # Get base study ID
        base_studies = await self.repository.get_studies_by_tag({
            'page': 1, 
            'pageSize': 1, 
            'tags': f"BASE-{parametros.rvs}-RV"
        })
        config['base_id_estudo'] = str(base_studies['ProspectiveStudies'][0]['Id'])
        
        # Get FCF study ID
        fcf_studies = await self.repository.get_studies_by_tag({
            'page': 1, 
            'pageSize': 1, 
            'tags': 'FCF'
        })
        config['fcf_id_estudo'] = str(fcf_studies['ProspectiveStudies'][0]['Id'])
        
        # Get volume study ID
        config['volume_id_estudo'] = await self._get_volume_id_estudo()
        
        # Configure study name
        base_study_info = await self.repository.get_estudo_por_id(config['base_id_estudo'])
        config['study_name'] = await self._get_study_name(base_study_info)
        config['study_name'] = f"{config['study_name']}__{parametros.sensibilidade}".upper()
        
        return config


    async def _get_volume_id_estudo(self) -> str:
        """Get ID of volume study"""
        studies = await self.repository.get_studies_by_tag({
            'page': 1, 
            'pageSize': 30, 
            'tags': 'EAR'
        })
        
        for study in studies['ProspectiveStudies']:
            if study['Status'] == 'Concluído' and len(study['Decks']) > 2:
                return str(study['Id'])
        
        return ""


    async def _get_study_name(self, study_info: dict) -> str:
        """Generate study name from deck information"""
        for deck in study_info['Decks']:
            if deck['Model'] == 'DECOMP':
                return f"DC{deck['Year']}{str(deck['Month']).zfill(2)}-RV{deck['Revision']}"
        return ""


    async def _duplicate_and_configure_study(self, config: dict, parametros: StudyExecutionDto) -> str:
        """Duplicate and configure study"""
        date = datetime.datetime.today()
        
        tags = [
            [f'DUP-FROM: {config["base_id_estudo"]}', 'black', 'white'],
            [f'FCF-FROM: {config["fcf_id_estudo"]}', 'black', 'white'],
            [f'EAR-FROM: {config["volume_id_estudo"]}', 'black', 'white'],
            ['EAR', 'white', 'white'],
            [parametros.tag, 'black', 'white']
        ]
        
        title = f"{config['study_name']}_{date.day}/{str(date.month).zfill(2)}-hr-{date.hour}:{date.minute}"
        
        id_estudo = await self.repository.duplicate_study(
            config['base_id_estudo'],
            title,
            'Rodada Automatica',
            tags
        )
        
        return id_estudo


    async def _send_volume_files(self, id_estudo: str) -> None:
        """Send volume files to study"""
        study_info = await self.repository.get_estudo_por_id(id_estudo)
        
        for deck in study_info['Decks']:
            if deck['Model'] == 'DECOMP':
                volume_path = os.path.join(settings.path_projetos, 'estudos-middle/api_prospec/calculo_volume/volume_uhe.csv')
                await self.repository.send_file_to_deck(id_estudo, deck['Id'], volume_path, 'volume_uhe.csv')
                break


    async def _associate_cuts_and_volumes(self, id_estudo: str, config: dict) -> None:
        """Associate cuts and volumes"""
        study_info = await self.repository.get_estudo_por_id(id_estudo)
        
        # Associate cuts
        destination_cuts_id = []
        for deck in study_info['Decks']:
            if deck['Model'] == 'DECOMP':
                destination_cuts_id = [deck['Id']]
                break
        
        if destination_cuts_id and config.get('fcf_id_estudo'):
            associations = [{
                'DestinationDeckId': destination_cuts_id[0],
                'SourceStudyId': config['fcf_id_estudo']
            }]
            await self.repository.associate_cuts(id_estudo, associations)
        
        # Associate volumes
        if config.get('volume_id_estudo'):
            volume_associations = [{
                'DestinationDeckId': destination_cuts_id[0],
                'SourceStudyId': config['volume_id_estudo'],
                'PreviousStage': False
            }]
            await self.repository.associate_volumes(id_estudo, volume_associations)


    async def _start_execution(self, id_estudo: str, config: dict) -> None:
        """Start study execution"""
        study_info = await self.repository.get_estudo_por_id(id_estudo)
        
        # Check if contains NEWAVE
        contains_newave = any(deck['Model'] == 'NEWAVE' for deck in study_info['Decks'])
        
        execution_config = {
            "EphemeralInstanceType": 'c5.18xlarge' if contains_newave else 'm5.4xlarge',
            "ServerPurchaseOption": 1,
            "ExecutionMode": 0,
            "InfeasibilityHandling": 1,
            "InfeasibilityHandlingSensibility": 2,
            "MaxTreatmentRestarts": 2,
            "SpotBreakdownOption": 2,
            "MaxTreatmentRestartsSensibility": 1
        }
        
        await self.repository.run_execution(id_estudo, execution_config)


    async def _wait_for_completion(self, id_estudo: str, config: dict) -> StudyResultDto:
        """Wait for study completion and download results"""
        # Wait initial period
        await asyncio.sleep(90)
        
        # Wait for completion
        for i in range(90):
            if i == 0:
                await asyncio.sleep(600)  # 10 minutes first wait
            else:
                await asyncio.sleep(600)  # 10 minutes between checks
            
            status = await self.get_status_estudo(id_estudo)
            
            if status in ['Finished', 'Aborted', 'Failed']:
                break
        
        # Download compilation
        compilation_file = f'Estudo_{id_estudo}_compilation.zip'
        download_path = os.path.join(settings.path_arquivos, compilation_file)
        
        if status == 'Finished':
            await self.repository.download_compilation(id_estudo, download_path)
        
        # Count decks
        study_info = await self.repository.get_estudo_por_id(id_estudo)
        n_decks = sum(1 for deck in study_info['Decks'] 
                     if deck['Model'] == 'DECOMP' and deck['SensibilityInfo'] == 'Original')
        
        return StudyResultDto(
            id_estudo=id_estudo,
            compilation_file=compilation_file,
            status=status.lower(),
            n_decks=n_decks
        )


    async def _download_resultados(self, parametros: StudyExecutionDto) -> DownloadResultDto:
        """Download results from existing study"""
        id_estudo = parametros.id_estudo
        await self.repository.authenticate()
        
        if parametros.aguardar_fim:
            for i in range(60):
                if i > 0:
                    await asyncio.sleep(600)
                
                status = await self.get_status_estudo(id_estudo)
                
                if status in ['Finished', 'Aborted', 'Failed']:
                    break
        
        # Download compilation
        compilation_file = f'Estudo_{id_estudo}_compilation.zip'
        download_path = os.path.join(settings.path_arquivos, compilation_file)
        
        status = await self.get_status_estudo(id_estudo)
        if status == 'Finished':
            await self.repository.download_compilation(id_estudo, download_path)
        
        # Get study info
        study_info = await self.repository.get_estudo_por_id(id_estudo)
        n_decks = sum(1 for deck in study_info['Decks'] 
                     if deck['Model'] == 'DECOMP' and deck['SensibilityInfo'] == 'Original')
        
        return DownloadResultDto(
            compilation_file=compilation_file,
            status=status.lower(),
            study_title=study_info['Title'],
            n_decks=n_decks
        )


    async def get_estudo_por_id(self, id_estudo: str) -> StudyInfoReadDto:
        """Get study information"""
        await self.repository.authenticate()
        study_info = await self.repository.get_estudo_por_id(id_estudo)
        
        return StudyInfoReadDto(
            id=id_estudo,
            title=study_info['Title'],
            description=study_info.get('Description', ''),
            status=study_info['Status'].lower(),
            decks=study_info['Decks'],
            creation_date=datetime.datetime.now()
        )


    async def get_base_id_estudos(self) -> list:
        """Get IDs of base studies"""
        await self.repository.authenticate()
        list_id = []
        
        for i in range(1, 9):
            studies = await self.repository.get_studies_by_tag({
                'page': 1, 
                'pageSize': 1, 
                'tags': f"BASE-{i}-RV"
            })
            list_id.append(studies['ProspectiveStudies'][0]['Id'])
        
        return list_id

    
    async def update_tag(self, id_estudo: int, tag:str, text_color: str, background_color: str) -> None:
        tags_to_delete_base = await self.get_estudo_por_id(id_estudo)['Tags']
        tag_prefix = tag.split(' ')[0]
        tags_delete = []
        for _tag in tags_to_delete_base:
            if _tag['Text'].split(' ')[0] in tag_prefix:
                tags_delete.append(_tag)
        self.repository.remove_study_tags(id_estudo, tags_delete)
        tags_to_add = [{
            'Text': tag,
            'TextColor': text_color,
            'BackgroundColor': background_color
        }]
        self.repository.add_study_tags(id_estudo, tags_to_add)

    async def update_estudos(
        self,
        id_estudo: str,
        files: List[UploadFile],
        tag: str
    ):
        estudo = await self.get_estudo_por_id(id_estudo)
        df_estudo = pd.DataFrame(estudo.decks)

        patterns = [r"NW(\d{6})", r"DC\d{6}-sem\d"]

        await self.update_tag(id_estudo, tag, "#FFF", "#44F")
        for file in files:
            filename = file.filename
            match = re.search(patterns[0], filename)
            if not match:
                match = re.search(patterns[1], filename)
            if not match:
                logger.info(f'Nome do arquivo {filename} não corresponde aos padrões esperados.')
                continue

            nome_estudo = match.group() + ".zip"
            deck_rows = df_estudo[df_estudo['FileName'] == nome_estudo]
            if deck_rows.empty:
                logger.info(f'Deck não encontrado para arquivo {filename}')
                continue
            id_deck = int(deck_rows['Id'].values[0])

            file_bytes = await file.read()
            arquivo_enviado = await self.repository.update_estudos(id_estudo, id_deck, filename, file_bytes)

            if 'filesUploaded' in arquivo_enviado:
                logger.info(f'{arquivo_enviado["filesUploaded"][0]} - OK')
            else:
                logger.info(f'Falha ao enviar estudo {id_estudo}')
