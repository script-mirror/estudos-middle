from fastapi import APIRouter, HTTPException
from fastapi_restful.cbv import cbv

from app.modules.prospec.repository import ProspecRepository
from app.modules.prospec.service import ProspecService
from .schemas import (
    StudyExecutionDto, StudyResultDto, StudyInfoReadDto, 
    DownloadResultDto
)

router = APIRouter(prefix="/prospec", tags=["Prospec"])


@cbv(router)
class ProspecController:
    def __init__(self):
        self.repository = ProspecRepository()
        self.service = ProspecService(self.repository)

    @router.post("/run-study",
                response_model=StudyResultDto,
                )
    async def run_study(self, parametros: StudyExecutionDto):
        """
        Executa um estudo Prospec com os parâmetros fornecidos.

        Este endpoint inicia a execução de um estudo Prospec utilizando os parâmetros informados.
        Retorna o resultado do estudo após a execução.
        """
        try:
            return await self.service.run_prospec_study(parametros)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/study/{study_id}",
               response_model=StudyInfoReadDto,
               )
    async def get_study_by_id(self, study_id: str):
        """
        Consulta informações detalhadas de um estudo específico.

        Forneça o ID do estudo para obter informações detalhadas sobre o mesmo.
        """
        try:
            return await self.service.get_study_by_id(study_id)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Study not found: {str(e)}")


    @router.get("/base-studies",
               response_model=list,
               )
    async def get_base_study_ids(self):
        """
        Lista os IDs de todos os estudos base disponíveis.

        Retorna uma lista contendo os identificadores dos estudos base cadastrados no sistema.
        """
        try:
            return await self.service.get_base_study_ids()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @router.post("/start-study/{study_id}")
    async def start_study(self, study_id: str):
        """
        Inicia a execução de um estudo específico.

        Forneça o ID do estudo para iniciar sua execução. Retorna mensagem de sucesso e o ID do estudo.
        """
        try:
            await self.service.start_study_execution(study_id)
            return {"message": "Estudo iniciado com sucesso", "study_id": study_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao iniciar estudo: {str(e)}")


    @router.post("/abort-study/{study_id}")
    async def abort_study(self, study_id: str):
        """
        Aborta a execução de um estudo específico.

        Forneça o ID do estudo para abortar sua execução. Retorna mensagem de sucesso e o ID do estudo.
        """
        try:
            await self.service.abort_study_execution(study_id)
            return {"message": "Estudo abortado com sucesso", "study_id": study_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao abortar estudo: {str(e)}")


    @router.get("/study/{study_id}/status")
    async def get_study_status(self, study_id: str):
        """
        Consulta o status atual de um estudo específico.

        Forneça o ID do estudo para obter o status atual da execução.
        """
        try:
            status = await self.service.get_study_status(study_id)
            return {"study_id": study_id, "status": status}
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Study not found: {str(e)}")

