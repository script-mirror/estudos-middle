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

class BodyFluxPersonalizado:
    __ds_nome_estudo = None
    __dt_inicio = None
    __dt_fim = None


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


    __cenarios = []

    def set_nome_estudo(self, nome: str):
        self.__ds_nome_estudo = re.sub(r'[^A-z0-9_-]', '', str(nome).upper())
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


    def add_cenario(self, cenario):
        try:
            self.__cenarios.append(cenario)
        except Exception as e:
            error = "[EE BodyFluxPersonalizado] - Erro não tratado: {}".format(str(e))
            Configuration.debug_print(error, e)
            raise Exception(error)

    def get_json(self):
        datetime_inicio = datetime(self.__dt_inicio.year, self.__dt_inicio.month, self.__dt_inicio.day, 12)
        datetime_fim = datetime(self.__dt_fim.year, self.__dt_fim.month, self.__dt_fim.day, 12)
        json_response = {
            'ds_nome_estudo': self.__ds_nome_estudo,
            'dt_inicio': datetime_inicio.timestamp(),
            'dt_fim': datetime_fim.timestamp(),

            "flag_produzir_mapas": self.__option_produzir_mapas,
            "flag_produzir_arquivo_pmed_xlsx": self.__option_produzir_arquivo_pmed_xlsx,
            "flag_produzir_arquivos_dessem": self.__option_produzir_arquivos_dessem,
            "flag_produzir_ena_diaria": self.__option_produzir_ena_diaria,
            "flag_tabelar_prevs_produzidos": self.__option_tabelar_prevs_produzidos,
            "flag_produzir_prevs_mensais": self.__option_produzir_prevs_mensais,
            "flag_produzir_vazpast": self.__option_produzir_vazpast,

            'cenarios': [],
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

        for c in self.__cenarios:
            c.validate()
            blocos = []
            if c.blocos[0].dt_inicio != self.__dt_inicio or c.blocos[-1].dt_fim != self.__dt_fim:
                raise Exception("Os blocos de cada cenário devem compreender todo o período de estudo. "
                                "{} - {} | Inicio Bloco 01 [{}] | Fim Bloco n [{}]".format(self.__dt_inicio,
                                                                                           self.__dt_fim,
                                                                                           c.blocos[0].dt_inicio,
                                                                                           c.blocos[-1].dt_fim))
            for b in c.blocos:
                datetime_dataprev = datetime(b.dt_data_prev.year, b.dt_data_prev.month, b.dt_data_prev.day,12)
                datetime_binicio = datetime(b.dt_inicio.year, b.dt_inicio.month, b.dt_inicio.day,12)
                datetime_bfim = datetime(b.dt_fim.year, b.dt_fim.month, b.dt_fim.day,12)

                blocos.append({
                    "ds_modelo": b.ds_modelo.value,
                    "dt_data_prev": datetime_dataprev.timestamp(),
                    "ck_rmv": b.ck_rmv,
                    "dt_inicio": datetime_binicio.timestamp(),
                    "dt_fim": datetime_bfim.timestamp(),
                    "runtime": b.runtime,
                    "membro": b.membro,
                })

            json_response['cenarios'].append({'ds_nome': c.ds_nome, 'blocos': blocos})
        return json_response
