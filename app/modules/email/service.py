from app.modules.email.repository import EmailRepository
from .schemas import EmailResponseDto
from fastapi import UploadFile
from typing import Optional, List


class EmailService:
    def __init__(self, repository: EmailRepository):
        self.repository = repository

    async def send_email(
        self,
        destinatario: List[str],
        assunto: str,
        mensagem: str,
        arquivos: Optional[List[UploadFile]] = None,
        user: Optional[str] = None
    ) -> EmailResponseDto:
        destinatario = destinatario[0].split(",")
        return await self.repository.send_email(
            destinatario, assunto, mensagem, arquivos, user
        )
