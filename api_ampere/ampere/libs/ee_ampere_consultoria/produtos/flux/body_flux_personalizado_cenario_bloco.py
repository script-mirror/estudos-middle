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
from datetime import datetime
from datetime import timedelta
from ..meteorologia import Modelos
from ...utils import check_modelo_max_date


class BlocoFluxPersonalizado:
    ds_modelo = None
    dt_data_prev = None
    ck_rmv = None
    runtime = None
    membro = None
    dt_inicio = None
    dt_fim = None


    def __init__(self, ds_modelo: Modelos, dt_data_prev: datetime, ck_rmv: bool,
                 dt_inicio: datetime, dt_fim: datetime, runtime='0', membro='0'):
        self.ds_modelo = ds_modelo
        self.dt_data_prev = dt_data_prev
        self.ck_rmv = ck_rmv
        self.dt_inicio = dt_inicio
        self.dt_fim = dt_fim
        self.runtime = str(runtime)
        self.membro = str(membro)
        self.validate()

    def validate(self):

        now = datetime.utcnow() - timedelta(hours=3)
        today = now.date()
        tomorrow = today + timedelta(days=1)

        found = False

        for m in Modelos:
            if m.value == self.ds_modelo.value:
                found = True

        if not found:
            raise Exception("[EE BlocoFluxPersonalizado] - O modelo {} não é válido".format(self.ds_modelo))

        modelo_max_date = check_modelo_max_date(self.ds_modelo, self.dt_data_prev)
        if modelo_max_date is None:
            raise Exception(f"[EE BlocoFluxPersonalizado] - O modelo {self.ds_modelo} não está especificado com uma "
                            "data máxima válida, entre emc ontato com o suporte")

        if self.dt_data_prev > today:
            raise Exception(f"[EE BlocoFluxPersonalizado] - A data de previsao {self.dt_data_prev} deve igual ou anterior "
                            "à hoje.")

        if type(self.ck_rmv) != bool:
            raise Exception(f"[EE BlocoFluxPersonalizado] - O valor de remoção de viés {self.ck_rmv} deve ser "
                            "booleano válido.")

        if self.dt_inicio <= today:
            raise Exception(f"[EE BlocoFluxPersonalizado] - O inicio do período de previsão deve "
                            "ser maior que hoje {self.dt_inicio}.")

        if self.dt_inicio > self.dt_fim:
            raise Exception(f"[EE BlocoFluxPersonalizado] - A data inicial do bloco deve ser menor "
                            "ou igual a data final do bloco {self.dt_inicio} - {self.dt_fim}.")

        if self.dt_fim > modelo_max_date:
            raise Exception(f"[EE BlocoFluxPersonalizado] - O fim do período excede o máximo ({modelo_max_date}) para o modelo "
                            "{self.ds_modelo.name} - {self.dt_fim}.")

        runtime_valido = self.runtime == '0' or self.runtime == '6' or self.runtime == '12' or self.runtime == '18'
        if not runtime_valido:
            raise Exception(f"[EE BlocoFluxPersonalizado] - Verificar valor de runtime da previsão ({self.runtime}) fornecido. "
                            "Runtime deve ter valor 0, 6, 12 ou 18.")

