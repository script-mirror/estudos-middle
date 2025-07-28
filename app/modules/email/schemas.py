from pydantic import BaseModel, EmailStr
from typing import Optional
from fastapi import UploadFile
import datetime
from enum import Enum


class EmailUser(str, Enum):
    sst = "sst@climenergy.com"
    ipdo = "ipdo@climenergy.com"
    acomph = "acomph@climenergy.com"
    rdh = "rdh@climenergy.com"
    info_bbce = "info_bbce@climenergy.com"
    dessem = "dessem@climenergy.com"
    rev_ena = "rev_ena@climenergy.com"
    processos = "processos@climenergy.com"
    rodadas = "rodadas@climenergy.com"
    rev_carga = "rev_carga@climenergy.com"
    cmo = "cmo@climenergy.com"
    diferenca_cv = "diferenca_cv@climenergy.com"
    pauta_aneel = "pauta_aneel@climenergy.com"
    mapas = "mapas@climenergy.com"


class EmailResponseDto(BaseModel):
    sucesso: bool
    mensagem: str
    data_envio: datetime.datetime
    destinatario: str
    remetente: str
