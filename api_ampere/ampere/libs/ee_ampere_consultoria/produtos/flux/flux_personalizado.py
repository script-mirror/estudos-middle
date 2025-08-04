# -*- coding: utf-8 -*-
"""
    --------------------------------------------------------------------------------------------------------------------

    Description: 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Obs.: 

    Author:           @diego.yosiura
    Last Update:      01/02/2022 15:50
    Created:          23/07/2021 12:16
    Copyright:        (c) Ampere Consultoria Ltda
    Original Project: espaco-exclusivo-package
    IDE:              PyCharm
"""
from json import dumps

from . import BodyFluxPersonalizado
from ... import Produto
from ... import Configuration
from ..base_produto import BaseProduto


class FluxPersonalizado(BaseProduto):
    def get_list(self) -> list:
        """
        Retorna uma lista de estudos enviados pela empresa.

        :return: dict
        """
        try:
            p_key = self.request.request_prod_key(Produto.FLUX_PERSONALIZADO.value)
            response = self.request.request_json('flux.personalizado.get_list?product_key={}'.format(p_key), '')
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']
                else:
                    print("Erro ao requisitar dados: {message}".format(message=response['message']))
            return None
        except Exception as e:
            error = "[EE FluxPersonalizado] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def get_download_link(self, id_estudo: int) -> str:
        """
        Retorna o link para download do estudo caso ja tenha sido concluido.

        :param id_estudo: identificador do estudo.
        :type id_estudo: int
        :return: str
        """
        try:
            p_key = self.request.request_prod_key(Produto.FLUX_PERSONALIZADO.value)
            response = self.request.request_json('flux.personalizado.get_link?product_key={}'.format(p_key),
                                                 dumps({"caso_id": id_estudo}))
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']['link']
                else:
                    print("Erro ao requisitar dados: {message}".format(message=response['message']))
            return None
        except Exception as e:
            error = "[EE FluxPersonalizado] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def get_preview(self, id_estudo: int) -> str:
        """
        Retorna a composicao dos mapas para o estudo `id_estudo`

        :param id_estudo: identificador do estudo.
        :type id_estudo: int
        :return: str
        """
        try:
            p_key = self.request.request_prod_key(Produto.FLUX_PERSONALIZADO.value)
            response = self.request.request_json('flux.personalizado.get_preview?product_key={}&'
                                                 'estudo={}'.format(p_key, id_estudo),
                                                 '')
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']
                else:
                    print("Erro ao requisitar dados: {message}".format(message=response['message']))
            return None
        except Exception as e:
            error = "[EE FluxPersonalizado] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def create_request(self, estudo: BodyFluxPersonalizado) -> dict:
        """
        Cria uma requisição de estudo mas não envia para a fila de exevução.

        :param estudo: objeto contendo as informações do estudo solicitado.
        :type estudo: BodyFluxPersonalizado
        :return: dict
        """
        try:
            p_key = self.request.request_prod_key(Produto.FLUX_PERSONALIZADO.value)
            response = self.request.request_json('flux.personalizado.create_request?product_key={}'.format(p_key),
                                                 dumps(estudo.get_json()))
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']
                else:
                    print("Erro ao requisitar dados: {message}".format(message=response['message']))
            return None
        except Exception as e:
            error = "[EE FluxPersonalizado] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def execute(self, estudo: dict) -> dict:
        """
        Envia o processo criado em `create_request` para a fila de requisição.

        :param estudo: dicionário resposta do método `create_request`.
        :type estudo: dict
        :return: dict
        """
        try:
            p_key = self.request.request_prod_key(Produto.FLUX_PERSONALIZADO.value)
            response = self.request.request_json('flux.personalizado.execution_queue?product_key={}&'
                                                 'estudo={}'.format(p_key, estudo['id']),
                                                 dumps(estudo))
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']
                else:
                    print("Erro ao requisitar dados: {message}".format(message=response['message']))
            return None
        except Exception as e:
            error = "[EE FluxPersonalizado] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)
