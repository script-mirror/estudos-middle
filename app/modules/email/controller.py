from fastapi_restful.cbv import cbv
from fastapi import APIRouter, Form, File, UploadFile
from typing import Optional, List

from app.modules.email.repository import EmailRepository
from app.modules.email.service import EmailService
from .schemas import EmailResponseDto

router = APIRouter(prefix="/email", tags=["Email"])


@cbv(router)
class EmailController:
    def __init__(self):
        self.repository = EmailRepository()
        self.service = EmailService(self.repository)

    @router.post("/send",
                 response_model=EmailResponseDto,
                 )
    async def send_email(
        self,
        destinatario: str = Form(...),
        assunto: str = Form(default="teste"),
        mensagem: str = Form(...),
        arquivos: Optional[List[UploadFile]] = File(None),
        user: Optional[str] = Form(None)
    ):
        return await self.service.send_email(destinatario, assunto, mensagem, arquivos, user)
