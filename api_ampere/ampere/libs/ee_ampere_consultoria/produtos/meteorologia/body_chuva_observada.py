# -*- coding: utf-8 -*-
"""
    --------------------------------------------------------------------------------------------------------------------

    Description: 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Obs.: 

    Author:           @diego.yosiura
    Last Update:      21/07/2021 19:53
    Created:          21/07/2021 19:53
    Copyright:        (c) Ampere Consultoria Ltda
    Original Project: espaco_exclusivo_package
    IDE:              PyCharm
"""
from datetime import datetime
from json import dumps

from . import Modelos
from . import TipoComparacao
from . import TipoPeriodoComparacao


class BodyChuvaObservada:
    __definir_periodo = None
    __data_inicial = None
    __data_final = None

    def set_periodo_analise_acumulada(self, data_inicio: datetime, data_fim: datetime):
        """
        Seta datas de inicio e fim de previsão para gerar a comparação de dados acumulados.

        :param data_inicio: data de inicio do período de análise
        :type data_inicio: datetime
        :param data_fim: data de fim do período de análise
        :type data_fim: datetime
        """
        self.__data_inicial = None
        self.__data_final = None

        if type(data_inicio) != datetime:
            raise Exception("Tipo {} não é um objeto date válido.".format(type(data_inicio)))
        if type(data_fim) != datetime:
            raise Exception("Tipo {} não é um objeto date válido.".format(type(data_fim)))

        if data_inicio > datetime.today():
            raise Exception("A data {} deve ser menor ou igual à hoje.".format(data_inicio))

        if data_fim > datetime.today() or data_inicio > data_fim:
            raise Exception("A data {} deve ser menor ou igual à hoje e maior que a data de inicio.".format(data_fim))

        self.__data_inicial = data_inicio.timestamp()
        self.__data_final = data_fim.timestamp()

    def set_periodo_analise_diaria(self, data_inicio: datetime):
        """
        Seta da data da previsão para uma análise diária.

        :param data_inicio: data de previsão.
        :type data_inicio: datetime
        """
        self.__data_inicial = None
        self.__data_final = None

        if type(data_inicio) != datetime:
            raise Exception("Tipo {} não é um objeto date válido.".format(type(data_inicio)))

        if data_inicio > datetime.today():
            raise Exception("A data {} deve ser menor ou igual à hoje.".format(data_inicio))
        self.__data_inicial = data_inicio.timestamp()
        self.__data_final = data_inicio.timestamp()

    def set_tipo_de_periodo(self, tipo: TipoPeriodoComparacao):
        """
        Seta o tipo do período de análise, diário ou acumulado.

        :param tipo: [DIARIO, ACUMULADO]
        :type tipo: TipoPeriodoComparacao
        """
        self.__definir_periodo = None

        if TipoPeriodoComparacao.DIARIO.value != tipo.value and\
                TipoPeriodoComparacao.ACUMULADO.value != tipo.value:
            raise Exception("Tipo de período {} inválido".format(tipo))
        self.__definir_periodo = tipo.value

    def validate_data(self):
        """
        Valida as informações enviadas com base nas regras do modelo de chuva observada, caso encontre alguma inconsistencia,
        retorna uma exception com a informação do erro.
        """
        if self.__definir_periodo is None:
            raise Exception("Tipo de periodo não selecionado")

        if self.__data_inicial is None:
            raise Exception("Data de inicio do período não selecionado")

        if self.__data_final is None:
            raise Exception("Data de fim do período não selecionado")

        if TipoPeriodoComparacao.DIARIO.value != self.__definir_periodo and\
                TipoPeriodoComparacao.ACUMULADO.value != self.__definir_periodo:
            raise Exception("Tipo de período {} inválido".format(self.__definir_periodo))

        if TipoPeriodoComparacao.DIARIO.value == self.__definir_periodo:
            if self.__data_inicial > datetime.today().timestamp():
                raise Exception("O período de análise {} deve ser um objeto do tipo date e"
                                " menor ou igual à hoje.".format(self.__data_inicial))
        else:
            if self.__data_inicial > datetime.today().timestamp():
                raise Exception("A data {} deve ser um objeto do tipo date e "
                                "menor ou igual à hoje.".format(self.__data_inicial))

            if self.__data_final > datetime.today().timestamp() or self.__data_inicial > self.__data_final:
                raise Exception("A data {} deve ser um objeto do timpo date e "
                                "menor ou igual à hoje e maior que a data de inicio.".format(self.__data_final))

    def get_json(self) -> dict:
        """
        Retorna um dicionário com as informações para enviar no método comparar de meteorologia.

        :return: dict
        """
        self.validate_data()

        return {
            "tipo": "acumulado",
            "definir_periodo": self.__definir_periodo,
            "data_inicial": self.__data_inicial,
            "data_final": self.__data_final
        }
