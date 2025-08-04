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
import os
import re
import mimetypes

from json import dumps
from datetime import datetime

from ... import Produto
from ... import Configuration
from ..base_produto import BaseProduto
from ee_ampere_consultoria.produtos.flux.body_flux_upload import BodyFluxUpload


class FluxUpload(BaseProduto):
    def get_list(self) -> dict:
        """
        Retorna a lista de processos enviados pelo cliente

        :return: dict
        """
        try:
            p_key = self.request.request_prod_key(Produto.FLUX_UPLOAD.value)
            response = self.request.request_json('flux.upload.get_list?product_key={}'.format(p_key), '')
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']
                else:
                    print("Erro ao requisitar dados: {message}".format(message=response['message']))
            return None
        except Exception as e:
            error = "[EE FluxUpload] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def get_download_link(self, caso_id: int) -> str:
        """
        Retorna o link de download do caso.

        :return: str
        """
        try:
            p_key = self.request.request_prod_key(Produto.FLUX_UPLOAD.value)
            response = self.request.request_json('flux.upload.get_link?product_key={}'.format(p_key),
                                                 dumps({"caso_id": caso_id}))
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']['link']
                else:
                    print("Erro ao requisitar dados: {message}".format(message=response['message']))
            return None
        except Exception as e:
            error = "[EE FluxUpload] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)

    def upload_file(self, ds_nome_estudo: str, dt_inicio: datetime, dt_fim: datetime, file_path: str, options: dict={}) -> str:
        """
        Faz o Upload do arquivo contendo as informações para o caso.

        :param ds_nome_estudo: nome do estudo, apenas letras, número e hifen e undescore
        :type ds_nome_estudo: str
        :param dt_inicio: data de inicio do estudo
        :type dt_inicio: datetime
        :param dt_fim: data de fim do estudo
        :type dt_fim: datetime
        :param file_path: diretório para o arquivo que será enviado.
        :type file_path: str
        :return:
        """
        try:
            if dt_inicio.timestamp() > dt_fim.timestamp():
                raise Exception("[EE FluxUpload] - a data de inicio do estudo deve ser maior que a data de fim.")

            ds_nome_estudo = re.sub(r'[^A-z0-9_-]', '', str(ds_nome_estudo).upper())
            if len(ds_nome_estudo) <= 3:
                raise Exception("[EE FluxUpload] - O nome do estudo deve conter "
                                "mais de 3 caracteres válidos. [{}]".format(ds_nome_estudo))

            if not os.path.isfile(file_path):
                raise Exception("[EE FluxUpload] - arquivo '{}' não encontrado.".format(file_path))

            estudo = {
                       "id": None,
                       "is_file": True,
                       "ds_nome_estudo": ds_nome_estudo,
                       "dt_inicio": dt_inicio.timestamp(),
                       "dt_fim": dt_fim.timestamp()
            }
            if options == {}: options = BodyFluxUpload()
            json_options = BodyFluxUpload.get_options_json(options)
            estudo.update(json_options)

            p_key = self.request.request_prod_key(Produto.FLUX_UPLOAD.value)
            response = self.request.request_upload('flux.upload.upload'.format(p_key),
                                                   {
                                                       "product_key": p_key,
                                                       "data": dumps(estudo),
                                                       "file": (
                                                           os.path.basename(file_path),
                                                           open(file_path, 'rb'),
                                                           mimetypes.guess_type(file_path)[0]
                                                       )
                                                   })
            if response is not None:
                if response['status'] == 1 or response['status'] is True:
                    return response['data']
                else:
                    print("Erro ao requisitar dados: {message}".format(message=response['message']))
            return None
        except Exception as e:
            error = "[EE FluxUpload] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {}".format(str(e), self.username,
                                                         self.password)
            Configuration.debug_print(error, e)
            raise Exception(error)
