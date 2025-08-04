from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List
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

    @router.get("/study/{id_estudo}",
               response_model=StudyInfoReadDto,
               )
    async def get_estudo_por_id(self, id_estudo: str):
        """
        Consulta informações detalhadas de um estudo específico.

        Forneça o ID do estudo para obter informações detalhadas sobre o mesmo.
        """
        try:
            return await self.service.get_estudo_por_id(id_estudo)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Study not found: {str(e)}")


    @router.get("/base-studies",
               response_model=list,
               )
    async def get_base_id_estudos(self):
        """
        Lista os IDs de todos os estudos base disponíveis.

        Retorna uma lista contendo os identificadores dos estudos base cadastrados no sistema.
        """
        try:
            return await self.service.get_base_id_estudos()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


    @router.post("/start-study/{id_estudo}")
    async def start_study(self, id_estudo: str):
        """
        Inicia a execução de um estudo específico.

        Forneça o ID do estudo para iniciar sua execução. Retorna mensagem de sucesso e o ID do estudo.
        """
        try:
            await self.service.start_study_execution(id_estudo)
            return {"message": "Estudo iniciado com sucesso", "id_estudo": id_estudo}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao iniciar estudo: {str(e)}")


    @router.post("/abort-study/{id_estudo}")
    async def abort_study(self, id_estudo: str):
        """
        Aborta a execução de um estudo específico.

        Forneça o ID do estudo para abortar sua execução. Retorna mensagem de sucesso e o ID do estudo.
        """
        try:
            await self.service.abort_study_execution(id_estudo)
            return {"message": "Estudo abortado com sucesso", "id_estudo": id_estudo}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao abortar estudo: {str(e)}")


    @router.get("/study/{id_estudo}/status")
    async def get_status_estudo(self, id_estudo: str):
        """
        Consulta o status atual de um estudo específico.

        Forneça o ID do estudo para obter o status atual da execução.
        """
        try:
            status = await self.service.get_status_estudo(id_estudo)
            return {"id_estudo": id_estudo, "status": status}
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Study not found: {str(e)}")

    @router.patch("/study/{id_estudo}/update-study")
    async def update_estudos(
        self,
        id_estudo: str,
        files: List[UploadFile] = File(...),
        tag: str = Form(...)
    ):
        """
        Recebe múltiplos arquivos e atualiza tags do estudo.
        """
        try:
            await self.service.update_estudos(id_estudo, files, tag)
            return {"message": "Tags and files updated successfully"}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error updating tags/files: {str(e)}")
