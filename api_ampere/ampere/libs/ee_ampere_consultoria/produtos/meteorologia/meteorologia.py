# -*- coding: utf-8 -*-
"""
    --------------------------------------------------------------------------------------------------------------------

    Description: 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Obs.: 

    Author:           @diego.yosiura
    Last Update:      21/07/2021 16:09
    Created:          21/07/2021 16:09
    Copyright:        (c) Ampere Consultoria Ltda
    Original Project: espaco_exclusivo_package
    IDE:              PyCharm
"""
import json
from json import dumps
from datetime import date

from ... import Produto
from ... import Configuration
from . import Prazo
from . import BodyComparador
from . import BodyChuvaObservada
from . import ModelosDataStore
from . import VariaveisMeteorologicas
from . import NiveisAtm
from . import RemocaoVies
from . import Runtime
from . import Membro
from ..base_produto import BaseProduto


class Meteorologia(BaseProduto):
    def get_images(self, prazo: Prazo, dia: int, mes: int, ano: int, index: int) -> dict:
        """
        Retorna um dicionário contendo as imagens de curto, médio ou longo prazo no formato base64.

        :param prazo: [cp, mp ou lp]
        :type prazo: Prazo
        :param dia: Dia em que a previsão foi feita
        :type dia: int
        :param mes: Mês em que a previsão foi feita
        :type mes: int
        :param ano: Ano em que a previsão foi feita
        :type ano: int
        :param index: Número que corresponde ao dia da previsão, de 1 -> Máximo de dias de cada modelo.
        :type index: int
        :return: dict
        """
        try:
            p_key = self.request.request_prod_key(Produto.METEOROLOGIA.value)
            response = self.request.request_json('meteorologia.get_images?'
                                                 'product_key={}&'
                                                 'tipo={}&'
                                                 'day={}&'
                                                 'month={}&'
                                                 'year={}&'
                                                 'index={}'.format(p_key,
                                                                    prazo.value, dia, mes, ano, index), '')
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']
                else:
                    print("Erro ao requisitar dados: {message}".format(message=response['message']))
            return None
        except Exception as e:
            error = "[EE Meteorologia] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def comparar(self, body_comparador: BodyComparador) -> dict:
        """
        Compara dois modelos com base nos parâmetros informados no objeto BodyComparador.


        :param body_comparador: Corpo da requisição com as informações de comparação.
        :type body_comparador: BodyComparador
        :return: dict
        """
        try:
            p_key = self.request.request_prod_key(Produto.METEOROLOGIA.value)
            response = self.request.request_json('meteorologia.comparador?product_key={}'.format(p_key),
                                                 dumps({
                                                     "method": "solicitar_comparacao",
                                                     "params": {
                                                         "tipo": "comparacao",
                                                         "comparacao": body_comparador.get_json()
                                                     },
                                                     "broadcast": False,
                                                     "room": "",
                                                     "user": "exclusivo_comparador_client"
                                                 }))
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']['params']
                else:
                    print("Erro ao requisitar dados: {message}".format(message=response['message']))
            return None
        except Exception as e:
            error = "[EE Meteorologia] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def chuva_observada(self, body_chuva_observada: BodyChuvaObservada) -> dict:
        """

        :param body_chuva_observada:
        :param body_comparador: Corpo da requisição com as informações de comparação.
        :type body_comparador: BodyComparador
        :return: dict
        """
        try:
            p_key = self.request.request_prod_key(Produto.METEOROLOGIA.value)
            response = self.request.request_json('meteorologia.comparador?product_key={}'.format(p_key),
                                                 dumps({
                                                     "method": "solicitar_comparacao",
                                                     "params": {
                                                         "tipo": "acumulado",
                                                         "acumulado": body_chuva_observada.get_json()
                                                     },
                                                     "broadcast": False,
                                                     "room": "",
                                                     "user": "exclusivo_comparador_client"
                                                 }))
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']['params']
                else:
                    print("Erro ao requisitar dados: {message}".format(message=response['message']))
            return None
        except Exception as e:
            error = "[EE Meteorologia] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def data_store_download(self, modelo: ModelosDataStore, data_previsao: date, nivel_atm: NiveisAtm,
                            var_met: VariaveisMeteorologicas, runtime: Runtime, rmv: RemocaoVies, membro: Membro,
                            data_inicial: date = None, data_final: date = None, file_name: str = '', png: bool = False) -> bytes:
        """
        Faz o download de um arquivo dentro do espaço exclusivo.

        :param file_id: Identificador do arquivo obtido no método 'get_list'.
        :type file_id: str
        :param file_name: [Opcional] - Nome do arquivo destino, caso seja omitido, as informações em bytes serão retornadas.
        :type file_name: str
        :return: bytes
        """
        try:
            payload = {
                "modelo": modelo.value,
                "data_previsao":
                    f"{data_previsao.year}-{str(data_previsao.month).zfill(2)}-{str(data_previsao.day).zfill(2)}",
                "nivel_atm": nivel_atm.value,
                "var_met": var_met.value,
                "runtime": runtime.value,
                "rmv": 1 if rmv.value else 0,
                "membro": membro.value,
                "png": png if png else None
            }
            if data_inicial is not None and data_final is not None:
                payload['data_inicial'] = f"{data_inicial.year}-{str(data_inicial.month).zfill(2)}-{str(data_inicial.day).zfill(2)}"
                payload['data_final'] = f"{data_final.year}-{str(data_final.month).zfill(2)}-{str(data_final.day).zfill(2)}"

            p_key = self.request.request_prod_key(Produto.METEOROLOGIA.value)
            response = self.request.request_file('meteorologia.data_store?'
                                                 'product_key={}'.format(p_key), json.dumps(payload))
            if response is not None:
                if file_name != '' and file_name is not None:
                    with open(file_name, 'wb') as f:
                        f.write(response)
                return response
            return None
        except Exception as e:
            error = "[EE FileViewer] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)