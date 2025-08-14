# -*- coding: utf-8 -*-
"""
    --------------------------------------------------------------------------------------------------------------------

    Description: 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Obs.: 

    Author:           @diego.yosiura
    Last Update:      01/02/2022 15:50
    Created:          23/07/2021 18:04
    Copyright:        (c) Ampere Consultoria Ltda
    Original Project: espaco-exclusivo-package
    IDE:              PyCharm
"""
from datetime import date
from datetime import datetime
from datetime import timedelta
import dateutils

from ..produtos.meteorologia import Modelos
from ..produtos.meteorologia import DiasModelos


def check_global_max_date() -> datetime:
    n_max = 0
    for m in DiasModelos:
        if m.value > n_max:
            n_max = m.value

    now = datetime.utcnow()
    global_max = now + + timedelta(days=n_max)
    return global_max.date()


def check_modelo_max_date(modelo: Modelos, dt_data_prev) -> datetime:
    m = getattr(DiasModelos, modelo.name)
    if m is None:
        return None
    days = m.value
    if modelo == Modelos.GEFS and dt_data_prev < date.today(): days = 35

    fim_m4 = date(dt_data_prev.year, dt_data_prev.month, 1) + dateutils.relativedelta(months=5) - timedelta(days=1)
    if modelo == Modelos.PREVCONSENSO: days = (fim_m4 - dt_data_prev).days

    now = datetime.utcnow()
    model_max = now + timedelta(days=days)
    return model_max.date()
