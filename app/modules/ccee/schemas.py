import datetime
from pydantic import BaseModel
from enum import Enum
from typing import Optional
from decimal import Decimal


class TipoCvuEnum(str, Enum):
    custo_variavel_unitario_conjuntural = "conjuntural"
    custo_variavel_unitario_estrutural = "estrutural"
    custo_variavel_unitario_conjuntural_revisado = "conjuntural_revisado"
    custo_variavel_unitario_merchant = "merchant"


class CvuDataAtualizacaoReadDto(BaseModel):
    tipo_cvu: TipoCvuEnum
    data_atualizacao: datetime.datetime

class CvuReadDto(BaseModel):
    cd_usina: Optional[int] = None
    vl_cvu: Optional[float] = None
    tipo_cvu: Optional[str] = None
    mes_referencia: Optional[str] = None
    ano_horizonte: Optional[int] = None
    dt_atualizacao: datetime.date
    fonte: Optional[str] = None
    agente_vendedor: Optional[str] = None
    tipo_combustivel: Optional[str] = None
    custo_combustivel: Optional[Decimal] = None
    codigo_parcela_usina: Optional[str] = None
    inicio_suprimento: Optional[datetime.date] = None
    termino_suprimento: Optional[datetime.date] = None
    sigla_parcela: Optional[str] = None
    leilao: Optional[str] = None
    cnpj_agente_vendedor: Optional[str] = None
    produto: Optional[str] = None
    vl_cvu_cf: Optional[float] = None
    vl_cvu_scf: Optional[float] = None
    empreendimento: Optional[str] = None
    despacho: Optional[str] = None
    recuperacao_custo_fixo: Optional[str] = None
    data_inicio: Optional[datetime.date] = None
    data_fim: Optional[datetime.date] = None
    origem_da_cotacao: Optional[str] = None
    mes_referencia_cotacao: Optional[str] = None
