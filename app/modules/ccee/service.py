from middle.utils import sanitize_string, convert_date_columns
from app.modules.ccee.repository import CceeRepository
from .schemas import TipoCvuEnum, CvuDataAtualizacaoReadDto, CvuReadDto
from .constants import MAPEAMENTO_CVU
import pandas as pd
import numpy as np


class CceeService():
    def __init__(self, repository: CceeRepository):
        self.repository = repository

    async def tratar_dataframe_cvu(
        self,
        df: pd.DataFrame,
        tipo_cvu: TipoCvuEnum,
    ):
        df.columns = [sanitize_string(col, '_').lower() for col in df.columns]
        if df['mes_referencia'].dtype == 'object':
            df = df.loc[df['mes_referencia'].str[0] != '*'].copy()
        df.rename(
            columns={'codigo_modelo_preao': 'codigo_modelo_preco'},
            errors='ignore',
            inplace=True,
            )

        df = df.astype(MAPEAMENTO_CVU[tipo_cvu.value]['columns'])
        df = convert_date_columns(df)
        data_atualizacao_result = await self.get_data_atualizacao_cvu(
            tipo_cvu=tipo_cvu
        )
        df['dt_atualizacao'] = data_atualizacao_result.data_atualizacao.date()
        df.columns = [col.lower() for col in df.columns]
        rename_dict = {
            "cvu_cf": "vl_cvu_cf",
            "cvu_scf": "vl_cvu_scf",
            "cvu_conjuntural": "vl_cvu",
            "cvu_estrutural": "vl_cvu",
            "codigo_modelo_preco": "cd_usina"
        }
        df.rename(
            columns=rename_dict,
            errors='ignore',
            inplace=True
        )
        df.round(2)
        df.replace({np.nan: None, np.inf: None, -np.inf: None}, inplace=True)
        df['tipo_cvu'] = tipo_cvu.value.replace(
            '_revisado', ''
        )
        df['fonte'] = "CCEE_" + tipo_cvu.value
        df['ano_horizonte'] = df['mes_referencia'].astype(str).str[:4]

        return df

    async def get_cvu_from_csv(
        self,
        tipo_cvu: TipoCvuEnum
    ):
        df = await self.repository.get_cvu_from_csv(
            MAPEAMENTO_CVU[tipo_cvu.value]['url']
        )
        df = await self.tratar_dataframe_cvu(df, tipo_cvu)
        return [CvuReadDto.model_validate(x) for x in df.to_dict('records')]

    async def get_data_atualizacao_cvu(
        self, tipo_cvu: TipoCvuEnum
    ) -> CvuDataAtualizacaoReadDto:
        return await self.repository.get_data_atualizacao_cvu(tipo_cvu)

    async def get_cvu_mapping(
        self,
    ):
        return {"tipos_cvu": list(MAPEAMENTO_CVU.keys())}
