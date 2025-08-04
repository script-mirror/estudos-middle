# -*- coding: utf-8 -*-
"""
    --------------------------------------------------------------------------------------------------------------------

    Description:
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Obs.:

    Author:           @diego.yosiura
    Last Update:      21/07/2021 19:49
    Created:          21/07/2021 19:49
    Copyright:        (c) Ampere Consultoria Ltda
    Original Project: espaco_exclusivo_package
    IDE:              PyCharm
"""
from enum import Enum


class VariaveisMeteorologicas(Enum):
    HGT = 'hgt'
    TMP = 'tmp'
    TMAX = 'tmax'
    TMIN = 'tmin'
    PREC = 'prec'
    RH = 'rh'
    UWIND = 'uwind'
    VWIND = 'vwind'
    PRESSUP = 'pressup'
    TCC = 'tcc'
    DSWRF = 'dswrf'
    UWIND10M = 'uwind10m'
    VWIND10M = 'vwind10m'
    WIND_SPEED10M = 'wind-speed10m'
    TMED2M = 'tmed2m'
    PRESMSL = 'presmsl'
    UWIND100M = 'uwind100m'
    VWIND100M = 'vwind100m'
    WIND_SPEED100M = 'wind-speed100m'
    UWIND120M = 'uwind120m'
    VWIND120M = 'vwind120m'
    WIND_SPEED120M = 'wind-speed120m'
