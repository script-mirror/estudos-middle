from fastapi_restful.cbv import cbv
from fastapi import APIRouter

from app.modules.ccee.repository import CceeRepository
from app.modules.ccee.service import CceeService
from .schemas import CvuDataAtualizacaoReadDto, TipoCvuEnum, CvuReadDto

router = APIRouter(prefix="/ccee", tags=["CCEE"])


@cbv(router)
class CceeController:
    def __init__(self):
        self.repository = CceeRepository()
        self.service = CceeService(self.repository)

    @router.get("/cvu-mapping",
                )
    async def get_cvu_mapping(self):
        return await self.service.get_cvu_mapping()

    @router.get("/{tipo_cvu}/ultima-atualizacao",
                response_model=CvuDataAtualizacaoReadDto,
                )
    async def get_data_atualizacao_cvu(self, tipo_cvu: TipoCvuEnum):
        return await self.service.get_data_atualizacao_cvu(tipo_cvu)

    @router.get("/{tipo_cvu}",
                response_model=list[CvuReadDto],
                )
    async def get_latest_cvu(self, tipo_cvu: TipoCvuEnum):
        return await self.service.get_cvu_from_csv(tipo_cvu)

