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
from ..meteorologia import Modelos

from . import BlocoFluxPersonalizado


class CenarioFluxPersonalizado:
    ds_nome = None
    blocos = None

    def set_nome_cenario(self, nome_cenario):
        nome_tratado = nome_cenario.replace(" ","-").replace("_","-").replace("/","-")
        self.ds_nome = re.sub(r'[^A-z0-9_-]', '', str(nome_tratado).upper())

    def add_bloco(self, ds_modelo: Modelos, dt_data_prev: datetime, ck_rmv: bool,
                  dt_inicio: datetime, dt_fim: datetime, runtime='0', membro='0'):
        try:
            dt_data_prev = datetime(dt_data_prev.year, dt_data_prev.month, dt_data_prev.day).date()
            dt_inicio = datetime(dt_inicio.year, dt_inicio.month, dt_inicio.day).date()
            dt_fim = datetime(dt_fim.year, dt_fim.month, dt_fim.day).date()

            if self.blocos is None:
                self.blocos = []

            for bloco in self.blocos:
                if bloco.dt_inicio >= dt_inicio and dt_inicio <= bloco.dt_fim:
                    raise Exception(f"[EE CenarioFluxPersonalizado] - O inicio sobrescreve o"
                                    " período de um dos blocos {dt_inicio} - Bloco {bloco.ds_modelo}.")
                if bloco.dt_inicio > dt_fim and dt_fim <= bloco.dt_fim:
                    raise Exception(f"[EE CenarioFluxPersonalizado] - O fim sobrescreve o"
                                    " período de um dos blocos {dt_fim} - Bloco {bloco.ds_modelo}.")

            bl = BlocoFluxPersonalizado(ds_modelo, dt_data_prev, ck_rmv, dt_inicio, dt_fim, runtime=runtime, membro=membro)
            self.blocos.append(bl)
            self.validate()
        except Exception as e:
            error = f"[EE CenarioFluxPersonalizado] - Erro não tratado: {e}"
            Configuration.debug_print(error, e)
            raise Exception(error)

    def validate(self):
        if self.ds_nome is None:
            raise Exception("[EE CenarioFluxPersonalizado] - O nome do cenário não pode ser nulo.")
        self.ds_nome = re.sub(r'[^A-z0-9_-]', '', str(self.ds_nome).upper())
        if len(self.ds_nome) <= 3:
            raise Exception(f"[EE CenarioFluxPersonalizado] - O nome do cenário deve conter "
                            "mais de 3 caracteres válidos. [{self.ds_nome}]")

        self.sort_blocos()

        for i in range(0, len(self.blocos) - 1):
            self.blocos[i].validate()

            n_day = self.blocos[i].dt_fim + timedelta(days=1)
            if self.blocos[i + 1].dt_inicio.day == self.blocos[i].dt_fim.day:
                continue
            if self.blocos[i + 1].dt_inicio.day != n_day.day or \
                    self.blocos[i + 1].dt_inicio.month != n_day.month or \
                    self.blocos[i + 1].dt_inicio.year != n_day.year:
                raise Exception(f"[EE CenarioFluxPersonalizado] - Os blocos devem ser contínuos, o inicio"
                                " do bloco [{i + 1}] deve ser o proximo dia do bloco {i}.")

    def sort_blocos(self):
        self.blocos.sort(reverse=False, key=CenarioFluxPersonalizado.__fn_sort_blocos)

    @staticmethod
    def __fn_sort_blocos(bloco):
        return bloco.dt_inicio
