import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import datetime
import mimetypes
from fastapi import UploadFile
from typing import Optional, List
from app.core.config import settings
from .schemas import EmailResponseDto, EmailUser
from middle.utils import setup_logger

logger = setup_logger()
class EmailRepository:
    def __init__(self):
        self.host = settings.email_host
        self.port = settings.email_port
        self.user = settings.email_user
        self.password = settings.email_pass

    async def send_email(
        self,
        destinatario: List[str],
        assunto: str,
        mensagem: str,
        arquivos: Optional[List[UploadFile]] = None,
        user: Optional[str] = None
    ) -> EmailResponseDto:
        logger.info(f"Iniciando envio de email para: {destinatario} | Assunto: {assunto}")
        try:
            msg = MIMEMultipart()
            from_email = self.user
            if user:
                try:
                    from_email = EmailUser[user.lower()].value
                    logger.info(f"Remetente definido pelo usuário: {from_email}")
                    msg['From'] = '{} <{}>'.format(
                        from_email.split('@')[0].upper(),
                        from_email
                    )
                except KeyError:
                    logger.warning(f"Usuário '{user}' não encontrado em EmailUser. Usando padrão: {from_email}")
                    msg['From'] = '{} <{}>'.format(
                        user,
                        from_email
                    )
            else:
                logger.info(f"Remetente padrão utilizado: {from_email}")
            msg['To'] = ", ".join(destinatario)
            msg['Subject'] = assunto

            content_type = 'html'
            msg.attach(MIMEText(mensagem, content_type))
            logger.debug("Mensagem principal anexada ao email.")

            if arquivos:
                for arquivo in arquivos:
                    if arquivo is None or arquivo.filename == '':
                        logger.warning("Arquivo nulo encontrado na lista de anexos, ignorando.")
                        continue
                    logger.info(f"Anexando arquivo: {arquivo.filename}")
                    file_content = await arquivo.read()

                    mime_type, _ = mimetypes.guess_type(arquivo.filename)
                    if mime_type is None:
                        mime_type = 'application/octet-stream'

                    main_type, sub_type = mime_type.split('/', 1)
                    part = MIMEBase(main_type, sub_type)
                    part.set_payload(file_content)
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{arquivo.filename}"'
                    )
                    msg.attach(part)
                logger.debug("Todos os arquivos anexados.")

            logger.info(f"Conectando ao servidor SMTP: {self.host}:{self.port}")
            server = smtplib.SMTP(self.host, self.port)
            server.starttls()
            server.login(self.user, self.password)
            logger.info("Login SMTP realizado com sucesso.")

            text = msg.as_string()
            server.sendmail(self.user, destinatario, text)
            server.quit()
            logger.info(f"Email enviado com sucesso para: {destinatario}")

            return EmailResponseDto(
                sucesso=True,
                mensagem="Email enviado com sucesso",
                data_envio=datetime.datetime.now(),
                destinatario=destinatario,
                remetente=from_email
            )

        except Exception as e:
            logger.error(f"Erro ao enviar email para {destinatario}: {str(e)}", exc_info=True)
            return EmailResponseDto(
                sucesso=False,
                mensagem=f"Erro ao enviar email: {str(e)}",
                data_envio=datetime.datetime.now(),
                destinatario=destinatario,
                remetente=from_email if 'from_email' in locals() else self.user
            )
