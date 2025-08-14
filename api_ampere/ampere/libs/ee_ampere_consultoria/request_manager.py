# -*- coding: utf-8 -*-
"""
    --------------------------------------------------------------------------------------------------------------------

    Description: 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Obs.: 

    Author:           @diego.yosiura
    Last Update:      21/07/2021 15:26
    Created:          21/07/2021 15:26
    Copyright:        (c) Ampere Consultoria Ltda
    Original Project: espaco_exclusivo_package
    IDE:              PyCharm
"""
import sys
from datetime import datetime
from datetime import timedelta

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from json import loads
from json import dumps
from . import Configuration


class RequestManager:
    def __init__(self, user_token: str, access_token: str, ssl_verify=True, proxy=None):
        """
        Classe auxiliar responsável pela padronização das requisições feitas pelo pacote.

        :param user_token: Token de usuário obtido no Espaço Exclusivo.
        :type user_token: str

        :param access_token: [Opcional] Access Token, obtido pelo método Get Authentication Code da API
        :type access_token: str
        """
        try:
            self.user_token = user_token
            self.access_token = access_token
            self.prod_key = None
            self.prod_key_date = None
            self.ssl_verify = ssl_verify
            self.proxy = proxy
        except Exception as e:
            error = "[EE RequestManager] - Erro não tratado: {}".format(str(e))
            Configuration.debug_print(error, e)
            sys.exit()

    def set_access_token(self, access_token: str):
        """
        Método utilizado para setar o valor da propriedade self.access_token

        :param access_token: Access Token, obtido pelo método Get Authentication Code da API
        :type access_token: str
        """
        try:
            self.access_token = access_token
        except Exception as e:
            error = "[EE RequestManager] - Erro não tratado: {}".format(str(e))
            Configuration.debug_print(error, e)
            sys.exit()

    def request_prod_key(self, product: str) -> str:
        """
        Método usado para requisitar o token de autorização de uso do produto.

        :param product:
        :type product: str
        :return: str
        """
        if self.prod_key is not None:
            if datetime.now() < self.prod_key_date:
                return self.prod_key

        uri = 'auth.check_user_permission?item={}'.format(product)
        try:
            response = self.request_json(uri, '')
            if response is None:
                return None

            if response['status'] == 1 or response['status'] is True:
                self.prod_key = response['data']['product_key']
                self.prod_key_date = datetime.now() + timedelta(hours=1)
                return self.prod_key
            return None
        except Exception as e:
            error = "[EE RequestManager] - Erro não tratado: {}\nURI: {}".format(str(e), uri)
            Configuration.debug_print(error, e)
            sys.exit()

    def request_upload(self, uri: str, payload: dict) -> dict:
        """
        Faz uma requisição com o payload como um Multipart.

        :param uri: referencia para a URI no arquivo de configurações.
        :type uri: str
        :param payload: [Opcional] dados do corpo da requisição em formato dict
        :type payload: dict
        :return: dict
        """
        try:
            mp_encoder = MultipartEncoder(fields=payload)
            response = self.__request(uri, {
                'x-user-token': self.user_token,
                'x-access-token': self.access_token,
                'Content-Type': mp_encoder.content_type
            }, '', mp_encoder)
            if response is None:
                return None

            return loads(response.text)
        except Exception as e:
            error = "[EE RequestManager] - Erro não tratado: {}\nURI: {}".format(str(e), uri)
            Configuration.debug_print(error, e)
            sys.exit()

    def request_json(self, uri: str, payload: str) -> dict:
        """
        Faz uma requisição com o header application/json.

        :param uri: referencia para a URI no arquivo de configurações.
        :type uri: str
        :param payload: [Opcional] dados do corpo da requisição em formato string
        :type payload: str
        :return: dict
        """
        try:
            response = self.__request(uri, {
                'x-user-token': self.user_token,
                'x-access-token': self.access_token,
                'Content-Type': 'application/json'
            }, payload)
            if response is None:
                return None

            return loads(response.text)
        except Exception as e:
            error = "[EE RequestManager] - Erro não tratado: {}\nURI: {}".format(str(e), uri)
            Configuration.debug_print(error, e)
            sys.exit()

    def request_file(self, uri: str, payload: str) -> bytes:
        """
        Faz uma requisição com o header application/json e retorna uma cadeia de bytes

        :param uri: referencia para a URI no arquivo de configurações.
        :type uri: str
        :param payload: [Opcional] dados do corpo da requisição em formato string
        :type payload: str
        :return: bytes
        """

        try:
            Configuration.debug_print("Baixando arquivo")
            response = self.__request(uri, {
                'x-user-token': self.user_token,
                'x-access-token': self.access_token,
                'Content-Type': 'application/json'
            }, payload)
            if response is None:
                return None
            Configuration.debug_print("Arquivo baixado")
            return response.content
        except Exception as e:
            error = "[EE RequestManager] - Erro não tratado: {}\nURI: {}".format(str(e), uri)
            Configuration.debug_print(error, e)
            sys.exit()

    def __request(self, uri: str, headers: dict, payload: str, mp_data: MultipartEncoder = None) -> requests.Response:
        """
        Faz uma requisição com o header application/json e retorna um objeto do tipo requests.Response

        :param uri: referencia para a URI no arquivo de configurações.
        :type uri: str
        :param headers: [Opcional] cabeçalho com informações da requisição.
        :type headers: dict
        :param payload: [Opcional] dados do corpo da requisição em formato string.
        :type payload: str
        :param mp_data: [Opcional] dados do corpo da requisição em formato multipart.
        :type mp_data: MultipartEncoder
        :return: requests.Response
        """
        method = ''
        try:
            uri, method = Configuration.get_uri(uri)
            if self.proxy is None:
                response = requests.request(method, uri, headers=headers, data=payload if mp_data is None else mp_data,
                                            verify=self.ssl_verify)
            else:
                response = requests.request(method, uri, headers=headers, data=payload if mp_data is None else mp_data,
                                            verify=self.ssl_verify, proxies=self.proxy)
            if response.status_code == 200:
                return response
            raise Exception("Invalid Status Code [{code}]: {text}".format(code=response.status_code,
                                                                          text=response.text))
        except Exception as e:
            error = "[EE RequestManager] - Erro não tratado: {}\nURI: {} | Method: {}".format(str(e), uri, method)
            Configuration.debug_print(error, e)
            sys.exit()


