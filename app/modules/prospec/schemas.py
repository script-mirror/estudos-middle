import datetime
from pydantic import BaseModel
from enum import Enum
from typing import Optional, List
from decimal import Decimal


class EstudoStatusEnum(str, Enum):
    concluido = "Concluído"
    em_andamento = "Em andamento"
    falhou = "Falhou"
    cancelado = "Cancelado"


class PrevsTypeEnum(str, Enum):
    prevs_ons_grupos = "PREVS_ONS_GRUPOS"
    prevs_pluvia_2_rv = "PREVS_PLUVIA_2_RV"
    prevs_pluvia_ec_ext = "PREVS_PLUVIA_EC_EXT"
    prevs_pluvia_raizen = "PREVS_PLUVIA_RAIZEN"


class DeckReadDto(BaseModel):
    model: Optional[str] = None
    year: Optional[int] = None
    month: Optional[int] = None
    revision: Optional[int] = None


class EstudoReadDto(BaseModel):
    id: str
    name: Optional[str] = None
    status: Optional[EstudoStatusEnum] = None
    decks: Optional[List[DeckReadDto]] = None
    tags: Optional[List[str]] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None


class EstudoCreateRequestDto(BaseModel):
    sensibilidade: str
    rvs: str
    executar_estudo: bool = True
    aguardar_fim: bool = True
    tag: Optional[str] = None
    prevs: Optional[PrevsTypeEnum] = None
    nome_estudo: Optional[str] = None


class EstudoBackTestRequestDto(BaseModel):
    deck: str
    path_deck: str
    wait_to_finish: bool = True


class EstudoResultadoRequestDto(BaseModel):
    id_estudo: str


class EstudoResponseDto(BaseModel):
    id: str
    status: str
    message: Optional[str] = None


class StudyStatusEnum(str, Enum):
    executing = "Executing"
    finished = "Finished"
    aborted = "Aborted"
    failed = "Failed"
    ready = "Ready"
    not_ready = "NotReady"


class StudyCreateDto(BaseModel):
    title: str
    description: str
    decomp_version_id: int
    newave_version_id: int


class StudyDuplicateDto(BaseModel):
    study_id_to_duplicate: str
    title: str
    description: str
    tags: List[List[str]]
    vazoes_dat: int = 2
    vazoes_rvx: int = 1
    prevs_condition: int = 1


class StudyExecutionDto(BaseModel):
    apenas_email: bool = False
    back_teste: bool = False
    executar_estudo: bool = True
    aguardar_fim: bool = True
    sensibilidade: str = ""
    tag: str = ""
    rvs: str = ""
    prevs: str = ""
    nome_estudo: str = ""
    wait_to_finish: bool = True
    id_estudo: Optional[str] = None
    path_deck: Optional[str] = None
    deck: Optional[str] = None


class StudyInfoReadDto(BaseModel):
    id: str
    title: str
    description: str
    status: StudyStatusEnum
    decks: List[dict]
    creation_date: datetime.datetime


class StudyResultDto(BaseModel):
    study_id: str
    compilation_file: str
    status: StudyStatusEnum
    n_decks: int


class BackTestDto(BaseModel):
    study_name: str
    path_to_file: str
    name_file_decomp: str
    wait_to_finish: bool = True


class DownloadResultDto(BaseModel):
    compilation_file: str
    status: StudyStatusEnum
    study_title: str
    n_decks: int
