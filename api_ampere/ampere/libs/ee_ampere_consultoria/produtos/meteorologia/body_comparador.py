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


class BodyComparador:
    __tipo = None
    __definir_periodo = None
    __data_prev_base = None
    __data_inicial = None
    __data_final = None
    __modelo_base = None
    __rmv_base = None
    __data_prev_confrontante = None
    __modelo_confrontante = None
    __rmv_confrontante = None

    def set_periodo_analise_acumulada(self, data_inicio: datetime, data_fim: datetime):
        """
        Seta datas de inicio e fim de previsão para gerar a comparação de dados acumulados.

        :param data_inicio: data de inicio do período de análise
        :type data_inicio: datetime
        :param data_fim: data de fim do período de análise
        :type data_fim: datetime

        """
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

        if self.__tipo is None:
            raise Exception("Defina um tipo de período antes de setar a data {}.".format(type(data_inicio)))

        if type(data_inicio) != datetime:
            raise Exception("Tipo {} não é um objeto date válido.".format(type(data_inicio)))

        if self.__tipo == TipoComparacao.PREVISAO_VS_PREVISAO.value:
            if data_inicio.date() <= datetime.today().date():
                raise Exception("A data {} deve ser maior que hoje.".format(data_inicio))
        else:
            if data_inicio.date() > datetime.today().date():
                raise Exception("A data {} deve ser menor que hoje e maior ou igual à data "
                                "de previsão do modelo.".format(data_inicio))

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

    def set_tipo_comparacao(self, tipo: TipoComparacao):
        """
        Seta o tipo de comparação.

        :param tipo: [PREVISAO_VS_PREVISAO, PREVISAO_VS_OBSERVADA]
        :type tipo: TipoComparacao
        """
        self.__tipo = None

        if TipoComparacao.PREVISAO_VS_PREVISAO.value != tipo.value and\
                TipoComparacao.PREVISAO_VS_OBSERVADA.value != tipo.value:
            raise Exception("Tipo de comparação {} inválida".format(tipo))
        self.__tipo = tipo.value

    def set_modelo_confrontante(self, modelo: Modelos):
        """
        Seta o modelo confrontante.

        :param modelo: []
        :type modelo: Modelos
        """
        self.__modelo_confrontante = None
        for m in Modelos:
            if m.value == modelo.value:
                self.__modelo_confrontante = m.value
                return
        raise Exception("Modelo {} não é um modelo válido".format(modelo))

    def set_modelo_confrontante_rmv(self, val: bool):
        """
        Define se o modelo confrontante terá ou não remção de viés.

        :param val:
        :type val: bool
        """
        self.__rmv_confrontante = None

        if type(val) != bool:
            raise Exception("Tipo {} não é um objeto boleano válido.".format(type(val)))
        self.__rmv_confrontante = val

    def set_data_previsao_confrontante(self, data_previsao: datetime):
        """
        Define a data em que a previsão do modelo confrontante foi feita.

        :param data_previsao:
        :type data_previsao: datetime
        """
        self.__data_prev_confrontante = None

        if type(data_previsao) != datetime:
            raise Exception("Tipo {} não é um objeto date válido.".format(type(data_previsao)))

        if data_previsao > datetime.today():
            raise Exception("A data {} deve ser menor ou igual à hoje.".format(data_previsao))
        self.__data_prev_confrontante = data_previsao.timestamp()

    def set_modelo_base(self, modelo: Modelos):
        """
        Define o modelo base de comparação.

        :param modelo:
        :type modelo: Modelos
        """
        self.__modelo_base = None

        for m in Modelos:
            if m.value == modelo.value:
                self.__modelo_base = m.value
                return
        raise Exception("Modelo {} não é um modelo válido".format(modelo))

    def set_modelo_base_rmv(self, val: bool):
        """
        Define se o modelo base terá ou não remção de viés.

        :param val:
        :type val: bool
        """
        self.__rmv_base = None

        if type(val) != bool:
            raise Exception("Tipo {} não é um objeto boleano válido.".format(type(val)))
        self.__rmv_base = val

    def set_data_previsao_base(self, data_previsao: datetime):
        """
        Define a data em que a previsão do modelo base foi feita.

        :param data_previsao:
        :type data_previsao: datetime
        """
        self.__data_prev_base = None

        if type(data_previsao) != datetime:
            raise Exception("Tipo {} não é um objeto date válido.".format(type(data_previsao)))

        if data_previsao > datetime.today():
            raise Exception("A data {} deve ser menor ou igual à hoje.".format(data_previsao))
        self.__data_prev_base = data_previsao.timestamp()

    def validate_data(self):
        """
        Valida as informações enviadas com base nas regras do modelo de comparação, caso encontre alguma inconsistencia,
        retorna uma exception com a informação do erro.
        """
        if self.__tipo is None:
            raise Exception("Tipo de comparação não selecionada")

        if self.__definir_periodo is None:
            raise Exception("Tipo de periodo não selecionado")

        if self.__data_prev_base is None:
            raise Exception("Data de previsão base não selecionada")

        if self.__data_inicial is None:
            raise Exception("Data de inicio do período não selecionado")

        if self.__data_final is None:
            raise Exception("Data de fim do período não selecionado")

        if self.__modelo_base is None:
            raise Exception("Modelo base não selecionado")

        if self.__rmv_base is None:
            raise Exception("Remoção de viés base não selecionado")

        if self.__data_prev_confrontante is None:
            raise Exception("Data de previsão do modelo confrontante não selecionada")

        if self.__modelo_confrontante is None:
            raise Exception("Modelo confrontante não selecionado")

        if self.__rmv_confrontante is None:
            raise Exception("Remoção de viés do modelo confrontante não selecionado")

        if TipoComparacao.PREVISAO_VS_PREVISAO.value != self.__tipo and\
                TipoComparacao.PREVISAO_VS_OBSERVADA.value != self.__tipo:
            raise Exception("Tipo de comparação {} inválida".format(self.__tipo))

        if TipoPeriodoComparacao.DIARIO.value != self.__definir_periodo and\
                TipoPeriodoComparacao.ACUMULADO.value != self.__definir_periodo:
            raise Exception("Tipo de período {} inválido".format(self.__definir_periodo))

        if self.__data_prev_base > datetime.today().timestamp():
            raise Exception("A data de previsão base {} deve ser um objeto do tipo date e "
                            "menor ou igual à hoje.".format(self.__data_prev_base))

        if TipoPeriodoComparacao.DIARIO.value == self.__definir_periodo:
            if self.__tipo == TipoComparacao.PREVISAO_VS_PREVISAO:
                if self.__data_inicial <= datetime.today().timestamp():
                    raise Exception("A data {} deve ser maior que hoje.".format(self.__data_inicial))
            else:
                if self.__data_inicial > datetime.today().timestamp():
                    raise Exception("A data {} deve ser menor que hoje e maior ou igual à data "
                                    "de previsão do modelo.".format(self.__data_inicial))
        else:
            if self.__tipo == TipoComparacao.PREVISAO_VS_PREVISAO:
                if self.__data_inicial <= datetime.today().timestamp():
                    raise Exception("A data {} deve ser um objeto do timpo date e "
                                    "maior que hoje.".format(self.__data_inicial))

                if self.__data_final <= datetime.today().timestamp() or self.__data_inicial > self.__data_final:
                    raise Exception("A data {} deve ser um objeto do timpo date e "
                                    "maior que hoje e maior que a data de inicio.".format(self.__data_final))
            else:
                if self.__data_inicial > datetime.today().timestamp():
                    raise Exception("A data {} deve ser menor que hoje e maior ou igual à data "
                                    "de previsão do modelo.".format(self.__data_inicial))
            if self.__data_final <= datetime.today().timestamp():
                raise Exception("A data {} deve ser um objeto do timpo date e "
                                "maior que hoje e maior que a data de inicio.".format(self.__data_final))
        found = False
        for m in Modelos:
            if m.value == self.__modelo_base:
                found = True
                break
        if not found:
            raise Exception("O modelo base {} não é um modelo válido.".format(self.__modelo_base))

        found = False
        for m in Modelos:
            if m.value == self.__modelo_confrontante:
                found = True
                break
        if not found:
            raise Exception("O modelo confrontante {} não é um modelo válido.".format(self.__modelo_confrontante))

        if self.__data_prev_confrontante > datetime.today().timestamp():
            raise Exception("A datade previsão do modelo confrontante {} deve ser um objeto date e"
                            " menor ou igual à hoje.".format(self.__data_prev_confrontante))

        if type(self.__rmv_base) != bool:
            raise Exception("A remoção de viés do modelo base {}"
                            " deve ser um objeto boleano válido.".format(self.__rmv_base))

        if type(self.__rmv_confrontante) != bool:
            raise Exception("A remoção de viés do modelo confrontante {}"
                            " deve ser um objeto boleano válido.".format(self.__rmv_confrontante))

    def get_json(self) -> dict:
        """
        Retorna um dicionário com as informações para enviar no método comparar de meteorologia.

        :return: dict
        """

        return {
            "tipo": self.__tipo,
            "definir_periodo": self.__definir_periodo,
            "data_prev_base": self.__data_prev_base,
            "data_inicial": self.__data_inicial,
            "data_final": self.__data_final,
            "modelo_base": self.__modelo_base,
            "rmv_base": self.__rmv_base,
            "data_prev_confrontante": self.__data_prev_confrontante,
            "modelo_confrontante": self.__modelo_confrontante,
            "rmv_confrontante": self.__rmv_confrontante
        }
