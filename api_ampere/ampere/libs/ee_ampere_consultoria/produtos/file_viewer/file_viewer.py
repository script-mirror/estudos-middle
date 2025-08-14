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
import os

from ... import Configuration
from ... import Produto
from ..base_produto import BaseProduto


class FileViewer(BaseProduto):

    def get_list(self) -> dict:
        """
        Retorna um dicionário com uma lista de arquivos e diretórios.

        :return: dict
        """
        try:
            p_key = self.request.request_prod_key(Produto.FILE_VIEWER.value)
            response = self.request.request_json('file_viewer.list?product_key={}'.format(p_key), '')
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']
                else:
                    print("Erro ao requisitar dados: {message}".format(message=response['message']))
            return None
        except Exception as e:
            error = "[EE FileViewer] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def download(self, file_id: str, file_name: str = '') -> bytes:
        """
        Faz o download de um arquivo dentro do espaço exclusivo.

        :param file_id: Identificador do arquivo obtido no método 'get_list'.
        :type file_id: str
        :param file_name: [Opcional] - Nome do arquivo destino, caso seja omitido, as informações em bytes serão retornadas.
        :type file_name: str
        :return: bytes
        """
        try:
            p_key = self.request.request_prod_key(Produto.FILE_VIEWER.value)
            response = self.request.request_file('file_viewer.download?'
                                                 'product_key={}&file-id={}'.format(p_key, file_id), '')
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
