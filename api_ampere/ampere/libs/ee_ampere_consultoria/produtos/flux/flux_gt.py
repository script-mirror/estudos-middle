# -*- coding: utf-8 -*-
"""
    --------------------------------------------------------------------------------------------------------------------

    Description: 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Obs.: 

    Author:           @diego.yosiura
    Last Update:      23/07/2021 12:16
    Created:          23/07/2021 12:16
    Copyright:        (c) Ampere Consultoria Ltda
    Original Project: espaco-exclusivo-package
    IDE:              PyCharm
"""
from ... import Produto
from ... import Configuration
from ..base_produto import BaseProduto


class FluxGT(BaseProduto):
    def get_gt_data(self) -> dict:
        """
        Retorna um dicionário com o histórico de MLT separado por Submercado, por Reservatório Equivalente e uma lista
        de arquivos ZIP com as saidas do GT-SMAPH.

        :return: dict
        """
        try:
            p_key = self.request.request_prod_key(Produto.FLUX_GT.value)
            response = self.request.request_json('flux.gt.get_data?product_key={}'.format(p_key), '')
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']
                else:
                    print("Erro ao requisitar dados: {message}".format(message=response['message']))
            return None
        except Exception as e:
            error = "[EE FluxGT] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def download(self, zip_name: str, file_name: str = '') -> bytes:
        """
        Faz o download do arquivo ZIP contendo as informações do produto Flux Historico.

        :param zip_name: nome do arquivo zip, os arquivos disponíveis estão descritos na propriedade 'zip'
        do método 'get_hist_data'.

        :type zip_name: str
        :param file_name: [Opcional] - Nome do arquivo destino, caso seja omitido, as informações em bytes serão retornadas.
        :type file_name: str
        :return:
        :rtype: bytes
        """
        try:
            p_key = self.request.request_prod_key(Produto.FLUX_GT.value)
            response = self.request.request_file('flux.gt.download_zip?product_key={}&'
                                                 'file-id={}'.format(p_key, zip_name), '')
            if response is not None:
                if file_name != '' and file_name is not None:
                    with open(file_name, 'wb') as f:
                        f.write(response)
                return response
            return None
        except Exception as e:
            error = "[EE FluxGT] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)
