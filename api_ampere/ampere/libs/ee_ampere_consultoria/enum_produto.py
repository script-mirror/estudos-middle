# -*- coding: utf-8 -*-
"""
    --------------------------------------------------------------------------------------------------------------------

    Description: 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Obs.: 

    Author:           @diego.yosiura
    Last Update:      21/07/2021 21:32
    Created:          21/07/2021 21:32
    Copyright:        (c) Ampere Consultoria Ltda
    Original Project: espaco_exclusivo_package
    IDE:              PyCharm
"""
from enum import Enum


class Produto(Enum):
    FILE_VIEWER = 'file-viewer'
    METEOROLOGIA = 'meteorologia'
    FLUX_PERSONALIZADO = 'prevs-personalizado'
    FLUX_UPLOAD = 'prevs-personalizado'
    FLUX_AUTOMATICO = 'prevs-automatico'
    FLUX_HISTORICO = 'prevs-historico'
    FLUX_GT = 'prevs-gt'
    FLUX_EC46 = 'ec46-multimembros'
    Flux_ENADiaria = 'prevs-automatico'
