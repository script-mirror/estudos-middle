# -*- coding: utf-8 -*-
"""
    --------------------------------------------------------------------------------------------------------------------

    Description: 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Obs.: 

    Author:           @diego.yosiura
    Last Update:      10/12/2021 07:16
    Created:          23/07/2021 8:30
    Copyright:        (c) Ampere Consultoria Ltda
    Original Project: espaco-exclusivo-package
    IDE:              PyCharm
"""
from json import dumps

from ... import Produto
from ... import Configuration
from ..base_produto import BaseProduto


class FluxENADiaria(BaseProduto):
    def get_simulacoes(self) -> dict:
        """
        Retorna um dicionário com o histórico de simulações disponíveis.

        :return: dict
        """
        try:
            p_key = self.request.request_prod_key(Produto.Flux_ENADiaria.value)
            response = self.request.request_json('flux.ena_diaria.get_options?product_key={}'.format(p_key), '')
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']['cenarios']
                else:
                    print("Erro ao requisitar dados: {message}".format(message=response['message']))
            return None
        except Exception as e:
            error = "[EE FluxENADiaria] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def get_ena(self, run_time: str, modelo: str, versao: str, subdivisao: str) -> list:
        """
        Retorna um dicionário contendo todos as ENAs.
        Os dados necessário são retornados pelo método `get_simulacoes`.


        :param run_time: Data em que a simulação foi executada.
        :type run_time: str
        :param modelo: Modelo simulado.
        :type modelo: str
        :param versao: Versão do modelo.
        :type versao: str
        :param subdivisao: Subdivisão - Submercado, REE, BACIA ETC.
        :type subdivisao: str
        :param tipo: Diferençiar pedido com MLT.
        :type tipo: str
        :return: Retorna uma lista com as ENAs para os dados selecionados.
        :rtype: dict
        """
        try:
            p_key = self.request.request_prod_key(Produto.FLUX_AUTOMATICO.value)
            response = self.request.request_json('flux.ena_diaria.get_cenario?product_key={}'.format(p_key), dumps({
                "run_time": run_time,
                "modelo": modelo,
                "versao": versao,
                "subdivisao": subdivisao
            }))
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    filter_result = []
                    for i, j in enumerate(response['data']['0']):
                        filter_result.append({"fcast": j['fcast'], "ena": j['ena']})
                    return filter_result
                else:
                    print("Erro ao requisitar dados: {message}".format(message=response['message']))
            return None
        except Exception as e:
            error = "[EE FluxENADiaria] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)
