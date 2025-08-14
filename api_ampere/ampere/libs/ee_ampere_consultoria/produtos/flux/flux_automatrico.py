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
import time
from json import dumps

from ... import Produto
from ... import Configuration
from ..base_produto import BaseProduto


class FluxAutomatico(BaseProduto):
    def get_list(self) -> dict:
        """
        Retorna a lista de arquivos do produto Flux automático.

        :return: dict
        """
        try:
            p_key = self.request.request_prod_key(Produto.FLUX_AUTOMATICO.value)
            response = self.request.request_json('flux.automatico.get_list?product_key={}'.format(p_key), '')
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']
                else:
                    print("Erro ao requisitar dados: {message}".format(message=response['message']))
            return None
        except Exception as e:
            error = "[EE FluxAutomatico] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def download(self, acomph: str, data_prev: str, modelo: str, file_name: str = '') -> bytes:
        """
        Faz o download do arquivo ZIP contendo as informações do produto Flux Automático.

        :param acomph: versão do AcompH - Ex. ACOMPH20200325
        :type acomph: str
        :param data_prev: data da previsão no formato AAAAMMDD
        :type data_prev: str
        :param modelo: O modelo deve ser consultado no retorno do método get_list.
        :type modelo: str
        :param file_name: [Opcional] - Nome do arquivo destino, caso seja omitido, as informações em bytes serão retornadas.
        :type file_name: str
        :return:
        :rtype: bytes
        """
        try:
            do_loop = True
            counter = 0
            while do_loop:
                p_key = self.request.request_prod_key(Produto.FLUX_AUTOMATICO.value)
                response = self.request.request_file('flux.automatico.download_zip?product_key={}&'
                                                     'acomph={}&'
                                                     'data_prev={}&'
                                                     'modelos={}'.format(p_key, acomph, data_prev, modelo), '')
                __decoded = None

                try:
                    __decoded = response.decode()
                except:
                    __decoded = None

                if response is not None and \
                        __decoded != '{"status": 0, "type": 0, "code": 200, "title": "Erro", ' \
                                     '"message": "Nenhum dado recebido.", "data": null}':
                    if file_name != '' and file_name is not None:
                        with open(file_name, 'wb') as f:
                            f.write(response)
                    return response
                if counter > 1:
                    do_loop = False
                time.sleep(1)
                counter += 1
            return None
        except Exception as e:
            error = "[EE FluxAutomatico] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def verify_last_results(self, acomph: str = None, data_prev: str = None, modelo: str = None) -> list:
        """
        Antes de realizar o download, é recomendado que o usuário use esta rota, para verificar se houve alguma
        ultima mudança nos estudos requisitados.

        :param acomph: versão do AcompH - Ex. ACOMPH20200325
        :type acomph: str
        :param data_prev: data da previsão no formato AAAAMMDD
        :type data_prev: str
        :param modelo: O modelo deve ser consultado no retorno do método get_list.
        :type modelo: str
        :return:
        :rtype: list
        """
        try:
            dump = {} if not acomph and not data_prev and not modelo else {"data_acomph": acomph, "data_previsao": data_prev, "cenario": modelo}

            p_key = self.request.request_prod_key(Produto.FLUX_AUTOMATICO.value)
            response = self.request.request_json('flux.automatico.verify-last-results-automatico?product_key={}'.format(p_key),
                                                 dumps(dump))
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']
                else:
                    print("Erro ao requisitar dados: {message}".format(message=response['message']))
            return None
        except Exception as e:
            error = "[EE FluxAutomatico] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)
