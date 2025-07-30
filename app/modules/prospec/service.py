import asyncio
import os
import time
from datetime import datetime
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
        logger.info(f'#-API do Prospec Iniciado: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')

        if parametros.apenas_email:
            logger.info(f'Iniciando download dos resultados do estudo com id: {parametros.id_estudo}')
            return await self._download_resultados(parametros)
        
        elif not parametros.back_teste:
            return await self._run_regular_study(parametros)
        

    async def get_study_status(self, study_id: str) -> str:
        status = await self.repository.get_study_status(study_id)
        logger.info(f"Study status: {status}")
        return status


    async def _run_regular_study(self, parametros: StudyExecutionDto) -> StudyResultDto:
        """Run regular Prospec study"""
        await self.repository.authenticate()
        
        config = await self._get_study_configuration(parametros)
        
        study_id = await self._duplicate_and_configure_study(config, parametros)
        
        if config.get('send_volume', True):
            await self._send_volume_files(study_id)
        
        await self._associate_cuts_and_volumes(study_id, config)
        
        if parametros.executar_estudo:
            await self._start_execution(study_id, config)
        
        if parametros.aguardar_fim:
            return await self._wait_for_completion(study_id, config)
        
        return StudyResultDto(
            study_id=study_id,
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
        config['base_study_id'] = str(base_studies['ProspectiveStudies'][0]['Id'])
        
        # Get FCF study ID
        fcf_studies = await self.repository.get_studies_by_tag({
            'page': 1, 
            'pageSize': 1, 
            'tags': 'FCF'
        })
        config['fcf_study_id'] = str(fcf_studies['ProspectiveStudies'][0]['Id'])
        
        # Get volume study ID
        config['volume_study_id'] = await self._get_volume_study_id()
        
        # Configure study name
        base_study_info = await self.repository.get_study_by_id(config['base_study_id'])
        config['study_name'] = await self._get_study_name(base_study_info)
        config['study_name'] = f"{config['study_name']}__{parametros.sensibilidade}".upper()
        
        return config


    async def _get_volume_study_id(self) -> str:
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
        date = datetime.today()
        
        tags = [
            [f'DUP-FROM: {config["base_study_id"]}', 'black', 'white'],
            [f'FCF-FROM: {config["fcf_study_id"]}', 'black', 'white'],
            [f'EAR-FROM: {config["volume_study_id"]}', 'black', 'white'],
            ['EAR', 'white', 'white'],
            [parametros.tag, 'black', 'white']
        ]
        
        title = f"{config['study_name']}_{date.day}/{str(date.month).zfill(2)}-hr-{date.hour}:{date.minute}"
        
        study_id = await self.repository.duplicate_study(
            config['base_study_id'],
            title,
            'Rodada Automatica',
            tags
        )
        
        return study_id


    async def _send_volume_files(self, study_id: str) -> None:
        """Send volume files to study"""
        study_info = await self.repository.get_study_by_id(study_id)
        
        for deck in study_info['Decks']:
            if deck['Model'] == 'DECOMP':
                volume_path = os.path.join(settings.path_projetos, 'estudos-middle/api_prospec/calculo_volume/volume_uhe.csv')
                await self.repository.send_file_to_deck(study_id, deck['Id'], volume_path, 'volume_uhe.csv')
                break


    async def _associate_cuts_and_volumes(self, study_id: str, config: dict) -> None:
        """Associate cuts and volumes"""
        study_info = await self.repository.get_study_by_id(study_id)
        
        # Associate cuts
        destination_cuts_id = []
        for deck in study_info['Decks']:
            if deck['Model'] == 'DECOMP':
                destination_cuts_id = [deck['Id']]
                break
        
        if destination_cuts_id and config.get('fcf_study_id'):
            associations = [{
                'DestinationDeckId': destination_cuts_id[0],
                'SourceStudyId': config['fcf_study_id']
            }]
            await self.repository.associate_cuts(study_id, associations)
        
        # Associate volumes
        if config.get('volume_study_id'):
            volume_associations = [{
                'DestinationDeckId': destination_cuts_id[0],
                'SourceStudyId': config['volume_study_id'],
                'PreviousStage': False
            }]
            await self.repository.associate_volumes(study_id, volume_associations)


    async def _start_execution(self, study_id: str, config: dict) -> None:
        """Start study execution"""
        study_info = await self.repository.get_study_by_id(study_id)
        
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
        
        await self.repository.run_execution(study_id, execution_config)


    async def _wait_for_completion(self, study_id: str, config: dict) -> StudyResultDto:
        """Wait for study completion and download results"""
        # Wait initial period
        await asyncio.sleep(90)
        
        # Wait for completion
        for i in range(90):
            if i == 0:
                await asyncio.sleep(600)  # 10 minutes first wait
            else:
                await asyncio.sleep(600)  # 10 minutes between checks
            
            status = await self.get_study_status(study_id)
            
            if status in ['Finished', 'Aborted', 'Failed']:
                break
        
        # Download compilation
        compilation_file = f'Estudo_{study_id}_compilation.zip'
        download_path = os.path.join(settings.path_arquivos, compilation_file)
        
        if status == 'Finished':
            await self.repository.download_compilation(study_id, download_path)
        
        # Count decks
        study_info = await self.repository.get_study_by_id(study_id)
        n_decks = sum(1 for deck in study_info['Decks'] 
                     if deck['Model'] == 'DECOMP' and deck['SensibilityInfo'] == 'Original')
        
        return StudyResultDto(
            study_id=study_id,
            compilation_file=compilation_file,
            status=status.lower(),
            n_decks=n_decks
        )


    async def _download_resultados(self, parametros: StudyExecutionDto) -> DownloadResultDto:
        """Download results from existing study"""
        study_id = parametros.id_estudo
        await self.repository.authenticate()
        
        if parametros.aguardar_fim:
            for i in range(60):
                if i > 0:
                    await asyncio.sleep(600)
                
                status = await self.get_study_status(study_id)
                
                if status in ['Finished', 'Aborted', 'Failed']:
                    break
        
        # Download compilation
        compilation_file = f'Estudo_{study_id}_compilation.zip'
        download_path = os.path.join(settings.path_arquivos, compilation_file)
        
        status = await self.get_study_status(study_id)
        if status == 'Finished':
            await self.repository.download_compilation(study_id, download_path)
        
        # Get study info
        study_info = await self.repository.get_study_by_id(study_id)
        n_decks = sum(1 for deck in study_info['Decks'] 
                     if deck['Model'] == 'DECOMP' and deck['SensibilityInfo'] == 'Original')
        
        return DownloadResultDto(
            compilation_file=compilation_file,
            status=status.lower(),
            study_title=study_info['Title'],
            n_decks=n_decks
        )


    async def get_study_by_id(self, study_id: str) -> StudyInfoReadDto:
        """Get study information"""
        await self.repository.authenticate()
        study_info = await self.repository.get_study_by_id(study_id)
        
        return StudyInfoReadDto(
            id=study_id,
            title=study_info['Title'],
            description=study_info.get('Description', ''),
            status=study_info['Status'].lower(),
            decks=study_info['Decks'],
            creation_date=datetime.now()
        )

    async def get_base_study_ids(self) -> list:
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
