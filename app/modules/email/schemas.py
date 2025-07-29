from pydantic import BaseModel
import datetime
from enum import Enum


class EmailUser(str, Enum):
    sst = "sst@climenergy.com"
    rdh = "rdh@climenergy.com"
    cmo = "cmo@climenergy.com"
    ipdo = "ipdo@climenergy.com"
    mapas = "mapas@climenergy.com"
    acomph = "acomph@climenergy.com"
    dessem = "dessem@climenergy.com"
    rodadas = "rodadas@climenergy.com"
    rev_ena = "rev_ena@climenergy.com"
    processos = "processos@climenergy.com"
    info_bbce = "info_bbce@climenergy.com"
    rev_carga = "rev_carga@climenergy.com"
    pauta_aneel = "pauta_aneel@climenergy.com"
    diferenca_cv = "diferenca_cv@climenergy.com"
    intervencoes = "intervencoes@climenergy.com"


class EmailResponseDto(BaseModel):
    sucesso: bool
    mensagem: str
    data_envio: datetime.datetime
    destinatario: list[str]
    remetente: str
