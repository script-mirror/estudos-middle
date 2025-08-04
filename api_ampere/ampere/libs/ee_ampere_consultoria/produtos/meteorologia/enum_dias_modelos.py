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
from enum import IntEnum


class DiasModelos(IntEnum):
    GDAPS = 11
    CMA = 9
    ARPEGE = 3
    COSMO = 5
    ETA = 10
    ICON = 6
    WRF = 3
    UKMO = 5
    GEM = 9
    ACCESSG = 9
    AMPERE = 10
    PREVC = 10
    NPREVC = 14
    GFS = 15
    GEFS = 15
    ECMWF = 9
    ECMWFENS = 14
    ECMWF46 = 45
    ECMWF46_PROB = 45
    MEMBROS_00 = 180
    MEMBROS_06 = 180
    MEMBROS_12 = 180
    MEMBROS_18 = 180
    TROPICAL = 180
    INFORMES = 180
    ZERO = 999
    CLIMATOLOGIA = 999
    MERGE = 999
    INTERSEMANAL = 60
    PREVCONSENSO = 999
