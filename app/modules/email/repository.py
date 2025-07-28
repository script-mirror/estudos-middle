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


class EmailRepository:
    def __init__(self):
        self.host = settings.email_host
        self.port = settings.email_port
        self.user = settings.email_user
        self.password = settings.email_pass

    async def send_email(
        self,
        destinatario: str,
        assunto: str,
        mensagem: str,
        arquivos: Optional[List[UploadFile]] = None,
        user: Optional[str] = None
    ) -> EmailResponseDto:
        try:
            msg = MIMEMultipart()
            from_email = self.user
            if user:
                try:
                    from_email = EmailUser[user.lower()].value
                    msg['From'] = '{} <{}>'.format(
                        from_email.split('@')[0].upper(),
                        from_email
                    )
                except KeyError:
                    msg['From'] = '{} <{}>'.format(
                        user,
                        from_email
                    )
            msg['To'] = destinatario
            msg['Subject'] = assunto

            content_type = 'html'

            msg.attach(MIMEText(mensagem, content_type))

            if arquivos:
                for arquivo in arquivos:
                    if arquivo is None:
                        continue
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

            server = smtplib.SMTP(self.host, self.port)
            server.starttls() 
            server.login(self.user, self.password)
            
            text = msg.as_string()
            server.sendmail(self.user, destinatario, text)
            server.quit()

            return EmailResponseDto(
                sucesso=True,
                mensagem="Email enviado com sucesso",
                data_envio=datetime.datetime.now(),
                destinatario=destinatario,
                remetente=from_email
            )

        except Exception as e:
            return EmailResponseDto(
                sucesso=False,
                mensagem=f"Erro ao enviar email: {str(e)}",
                data_envio=datetime.datetime.now(),
                destinatario=destinatario,
                remetente=from_email if 'from_email' in locals() else self.user
            )
