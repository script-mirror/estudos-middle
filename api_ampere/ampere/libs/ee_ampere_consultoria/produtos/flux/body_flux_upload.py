# -*- coding: utf-8 -*-
"""
    --------------------------------------------------------------------------------------------------------------------

    Description:
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Obs.:

    Author:           @diego.yosiura
    Last Update:      01/02/2022 15:50
    Created:          23/07/2021 16:57
    Copyright:        (c) Ampere Consultoria Ltda
    Original Project: espaco-exclusivo-package
    IDE:              PyCharm
"""
import re
from datetime import datetime
from datetime import timedelta

from ... import Configuration
from ...utils import check_global_max_date
from .enum_dimensoes_agrupamento import DimensoesAgrupamento

class BodyFluxUpload:
    __ds_nome_estudo = None
    __dt_inicio = None
    __dt_fim = None
    __zip = None

    __option_produzir_mapas = True
    __option_produzir_arquivo_pmed_xlsx = True
    __option_produzir_arquivos_dessem = True
    __option_produzir_ena_diaria = True
    __option_tabelar_prevs_produzidos = True
    __option_produzir_prevs_mensais = True
    __option_produzir_vazpast = True

    __option_previvaz_produzir_todas_revisoes_intermediarias = False
    __option_previvaz_produzir_somente_rv0_intermediarias  = False
    __option_previvaz_produzir_somente_revisoes_rvf = False

    __option_produzir_vmed = False
    __option_produzir_vpercentil = False
    __option_cenarios_vpercentil = []

    __option_produzir_cenarios_por_agrupamento = False
    __option_numero_agrupamentos = None
    __option_dimensoes_para_agrupamento = None


    def set_nome_estudo(self, nome: str):
        nome_tratado = nome.replace("_","-").replace("/","-").replace(" ","-").upper()
        self.__ds_nome_estudo = re.sub(r'[^A-z0-9_-]', '', str(nome_tratado).upper())
        if len(self.__ds_nome_estudo) <= 3:
            raise Exception("[EE BodyFluxPersonalizado] - O nome do estudo deve conter "
                            "mais de 3 caracteres válidos. [{}]".format(self.__ds_nome_estudo))

    def set_periodo_analise(self, inicio: datetime, fim: datetime):
        inicio = datetime(inicio.year, inicio.month, inicio.day).date()
        fim = datetime(fim.year, fim.month, fim.day).date()

        if fim > check_global_max_date():
            raise Exception("[EE BodyFluxPersonalizado] - O fim do estudo {} excede o "
                            "período máximo de estudo {}.".format(fim, check_global_max_date()))

        now = datetime.utcnow() - timedelta(hours=3)
        today = now.date()
        tomorrow = today + timedelta(days=1)

        if not inicio == tomorrow:
            raise Exception("[EE BodyFluxPersonalizado] - O inicio do estudo deve ser a data de amanha (D+1).")
        if fim <= inicio:
            raise Exception("[EE BodyFluxPersonalizado] - O fim do estudo deve ser maior que a data de inicio.")
        self.__dt_inicio = inicio
        self.__dt_fim = fim

    def set_option_produzir_mapas(self, flag: bool):
        if type(flag) != bool:
            raise Exception("[EE BodyFluxPersonalizado] - O valor do flag de opção {} deve ser "
                            "booleano válido.".format(flag))
        self.__option_produzir_mapas = flag

    def set_option_produzir_arquivo_pmed_xlsx(self, flag: bool):
        if type(flag) != bool:
            raise Exception("[EE BodyFluxPersonalizado] - O valor do flag de opção {} deve ser "
                            "booleano válido.".format(flag))
        self.__option_produzir_arquivo_pmed_xlsx = flag

    def set_option_produzir_arquivos_dessem(self, flag: bool):
        if type(flag) != bool:
            raise Exception("[EE BodyFluxPersonalizado] - O valor do flag de opção {} deve ser "
                            "booleano válido.".format(flag))
        self.__option_produzir_arquivos_dessem = flag

    def set_option_produzir_ena_diaria(self, flag: bool):
        if type(flag) != bool:
            raise Exception("[EE BodyFluxPersonalizado] - O valor do flag de opção {} deve ser "
                            "booleano válido.".format(flag))
        self.__option_produzir_ena_diaria = flag

    def set_option_tabelar_prevs_produzidos(self, flag: bool):
        if type(flag) != bool:
            raise Exception("[EE BodyFluxPersonalizado] - O valor do flag de opção {} deve ser "
                            "booleano válido.".format(flag))
        self.__option_tabelar_prevs_produzidos = flag

    def set_option_produzir_prevs_mensais(self, flag: bool):
        if type(flag) != bool:
            raise Exception("[EE BodyFluxPersonalizado] - O valor do flag de opção {} deve ser "
                            "booleano válido.".format(flag))
        self.__option_produzir_prevs_mensais = flag

    def set_option_produzir_vazpast(self, flag: bool):
        if type(flag) != bool:
            raise Exception("[EE BodyFluxPersonalizado] - O valor do flag de opção {} deve ser "
                            "booleano válido.".format(flag))
        self.__option_produzir_vazpast = flag

    def set_option_previvaz_produzir_todas_revisoes_intermediarias(self, flag: bool):
        if type(flag) != bool:
            raise Exception("[EE BodyFluxPersonalizado] - O valor do flag de opção {} deve ser "
                            "booleano válido.".format(flag))
        self.__option_previvaz_produzir_todas_revisoes_intermediarias = flag

    def set_option_previvaz_produzir_somente_rv0_intermediarias(self, flag: bool):
        if type(flag) != bool:
            raise Exception("[EE BodyFluxPersonalizado] - O valor do flag de opção {} deve ser "
                            "booleano válido.".format(flag))
        self.__option_previvaz_produzir_somente_rv0_intermediarias = flag

    def set_option_previvaz_produzir_somente_revisoes_rvf(self, flag: bool):
        if type(flag) != bool:
            raise Exception("[EE BodyFluxPersonalizado] - O valor do flag de opção {} deve ser "
                            "booleano válido.".format(flag))
        self.__option_previvaz_produzir_somente_revisoes_rvf = flag

    def set_option_produzir_vmed(self, flag: bool):
        if type(flag) != bool:
            raise Exception("[EE BodyFluxPersonalizado] - O valor do flag de opção {} deve ser "
                            "booleano válido.".format(flag))
        self.__option_produzir_vmed = flag

    def set_option_produzir_vpercentil(self, flag: bool):
        if type(flag) != bool:
            raise Exception("[EE BodyFluxPersonalizado] - O valor do flag de opção {} deve ser "
                            "booleano válido.".format(flag))
        self.__option_produzir_vpercentil = flag

    def set_option_cenarios_vpercentil(self, lista_cenarios: list):
        if type(lista_cenarios) != list:
            raise Exception("[EE BodyFluxPersonalizado] - O argumento da função {} deve ser "
                            "uma lista de números inteiros válida.".format(lista_cenarios))
        for p in lista_cenarios:
            if type(p) != int or p < 0 or p > 100:
                raise Exception("[EE BodyFluxPersonalizado] - O argumento da função {} deve ser "
                                "uma lista de números inteiros válida.".format(lista_cenarios))
        self.__option_cenarios_vpercentil = ",".join([str(c) for c in lista_cenarios])

    def set_option_produzir_cenarios_por_agrupamento(self, flag: bool):
        if type(flag) != bool:
            raise Exception("[EE BodyFluxPersonalizado] - O valor do flag de opção {} deve ser "
                            "booleano válido.".format(flag))
        self.__option_produzir_cenarios_por_agrupamento = flag

    def set_option_numero_agrupamentos(self, n: int):
        if type(n) != int or n <= 1:
            raise Exception("[EE BodyFluxPersonalizado] - O argumento da função {} deve ser "
                            "um número inteiro válido, maior que 1 e menor que o número de ."
                            "cenarios planejados".format(n))
        self.__option_numero_agrupamentos = n

    def set_option_dimensoes_para_agrupamento(self, dim: list):
        check1 = dim == DimensoesAgrupamento.SE_NE_vs_S_N.value
        check2 = dim == DimensoesAgrupamento.SE_S_vs_NE_N.value
        check3 = dim == DimensoesAgrupamento.SE_N_vs_S_NE.value
        check4 = dim == DimensoesAgrupamento.SE_vs_S_NE_N.value
        check5 = dim == DimensoesAgrupamento.SE_vs_S_vs_NE_vs_N.value
        dimensao_valida = check1 or check2 or check3 or check4 or check5
        if type(dim) != list or not dimensao_valida:
            raise Exception("[EE BodyFluxPersonalizado] - O argumento da função {} deve ser "
                            "uma lista válida elencada dentre as opções previstas.".format(dim))
        self.__option_dimensoes_para_agrupamento = dim


    def get_options_json(self):
        json_response = {
            "flag_produzir_mapas": self.__option_produzir_mapas,
            "flag_produzir_arquivo_pmed_xlsx": self.__option_produzir_arquivo_pmed_xlsx,
            "flag_produzir_arquivos_dessem": self.__option_produzir_arquivos_dessem,
            "flag_produzir_ena_diaria": self.__option_produzir_ena_diaria,
            "flag_tabelar_prevs_produzidos": self.__option_tabelar_prevs_produzidos,
            "flag_produzir_prevs_mensais": self.__option_produzir_prevs_mensais,
            "flag_produzir_vazpast": self.__option_produzir_vazpast,

        }

        if not self.__option_previvaz_produzir_todas_revisoes_intermediarias == False:
            json_response["flag_produzir_todas_revisoes_intermediarias"] = self.__option_previvaz_produzir_todas_revisoes_intermediarias

        if not self.__option_previvaz_produzir_somente_rv0_intermediarias == False:
            json_response["flag_produzir_somente_rv0_intermediarias"] = self.__option_previvaz_produzir_somente_rv0_intermediarias

        if not self.__option_previvaz_produzir_somente_revisoes_rvf == False:
            json_response["flag_produzir_somente_revisoes_rvf"] = self.__option_previvaz_produzir_somente_revisoes_rvf

        if not self.__option_produzir_vmed == False:
            json_response["flag_produzir_vmed"] = self.__option_produzir_vmed

        if not self.__option_produzir_vpercentil == False:
            json_response["flag_produzir_vpercentil"] = self.__option_produzir_vpercentil
            json_response["cenarios_vpercentil"] = self.__option_cenarios_vpercentil

        if not self.__option_produzir_cenarios_por_agrupamento == False:
            json_response["flag_produzir_cenarios_por_agrupamento"] = self.__option_produzir_cenarios_por_agrupamento
            if not self.__option_numero_agrupamentos == None:
                if self.__option_numero_agrupamentos >= len(self.__cenarios):
                    raise Exception("[EE BodyFluxPersonalizado] - O argumento da função {} deve ser "
                                    "um número inteiro válido, maior que 1 e menor que o número de ."
                                    "cenarios planejados".format(self.__option_numero_agrupamentos))
                json_response["numero_agrupamentos"] = self.__option_numero_agrupamentos
            if not self.__option_dimensoes_para_agrupamento == None:
                json_response["dimensoes_para_agrupamento"] = self.__option_dimensoes_para_agrupamento

        return json_response
