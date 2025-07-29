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
        """Execute a Prospec study with given parameters"""
        try:
            return await self.service.run_prospec_study(parametros)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/study/{study_id}",
               response_model=StudyInfoReadDto,
               )
    async def get_study_info(self, study_id: str):
        """Get information about a specific study"""
        try:
            return await self.service.get_study_info(study_id)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Study not found: {str(e)}")

    @router.post("/download-results",
                response_model=DownloadResultDto,
                )
    async def download_results(self, parametros: StudyExecutionDto):
        """Download results from an existing study"""
        if not parametros.id_estudo:
            raise HTTPException(status_code=400, detail="id_estudo is required for download")
        
        parametros.apenas_email = True
        try:
            return await self.service.run_prospec_study(parametros)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/back-test",
                response_model=StudyResultDto,
                )
    async def run_back_test(self, parametros: StudyExecutionDto):
        """Run a back test study"""
        parametros.back_teste = True
        try:
            return await self.service.run_prospec_study(parametros)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/base-studies",
               response_model=list,
               )
    async def get_base_study_ids(self):
        """Get IDs of all base studies"""
        try:
            return await self.service.get_base_study_ids()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.post("/start-study/{study_id}")
    async def start_study(self, study_id: str):
        """Start execution of a specific study"""
        try:
            await self.service.start_study_execution(study_id)
            return {"message": "Study started successfully", "study_id": study_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error starting study: {str(e)}")

    @router.post("/abort-study/{study_id}")
    async def abort_study(self, study_id: str):
        """Abort execution of a specific study"""
        try:
            await self.service.abort_study_execution(study_id)
            return {"message": "Study aborted successfully", "study_id": study_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error aborting study: {str(e)}")

    @router.get("/study/{study_id}/status")
    async def get_study_status(self, study_id: str):
        """Get current status of a specific study"""
        try:
            status = await self.service.get_study_status(study_id)
            return {"study_id": study_id, "status": status}
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Study not found: {str(e)}")
