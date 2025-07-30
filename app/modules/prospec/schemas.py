import datetime
from pydantic import BaseModel
from typing import Optional, List


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
    status: str
    decks: List[dict]
    creation_date: datetime.datetime


class StudyResultDto(BaseModel):
    study_id: str
    compilation_file: str
    status: str
    n_decks: int


class BackTestDto(BaseModel):
    study_name: str
    path_to_file: str
    name_file_decomp: str
    wait_to_finish: bool = True


class DownloadResultDto(BaseModel):
    compilation_file: str
    status: str
    study_title: str
    n_decks: int
