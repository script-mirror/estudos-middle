from io import StringIO
import pandas as pd
from bs4 import BeautifulSoup
import datetime
import httpx
from app.core.config import settings
from .schemas import CvuDataAtualizacaoReadDto, TipoCvuEnum


class CceeRepository():
    def __init__(self):
        pass

    async def get_cvu_from_csv(
        self,
        url: str,
    ):
        async with httpx.AsyncClient() as client:
            res = await client.get(url)
            df = pd.read_csv(
                StringIO(res.text),
                sep=",",
                na_values=None
            )
            df = df.replace('-', None)
            return df

    async def get_data_atualizacao_cvu(
        self, tipo_cvu: TipoCvuEnum
    ) -> CvuDataAtualizacaoReadDto:
        search_url = f"{settings.url_dados_abertos_ccee}/{tipo_cvu.name}"

        async with httpx.AsyncClient() as client:
            response = await client.get(search_url)

            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                section = soup.find("section", class_="additional-info")
                tabela = section.find("tbody")

                if tabela:
                    linhas_tabela = tabela.find_all("th")
                    for i, linha in enumerate(linhas_tabela):
                        if "atualização" in linha.text.lower():
                            date_atualizacao = datetime.datetime.strptime(
                                tabela.find_all("tr")[i].find(
                                    "span").text.strip(),
                                "%B %d, %Y, %H:%M (BRT)"
                                )
                            return CvuDataAtualizacaoReadDto(
                                tipo_cvu=tipo_cvu,
                                data_atualizacao=date_atualizacao
                            )
                else:
                    raise ValueError(
                        "Nenhuma tabela encontrada com a classe"
                        " 'additional-info'."
                    )
            else:
                raise httpx.HTTPError(
                    f"Erro ao acessar a página {search_url}:"
                    f" {response.status_code}"
                )
