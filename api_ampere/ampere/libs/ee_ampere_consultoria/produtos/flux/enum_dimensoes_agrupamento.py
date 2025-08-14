# -*- coding: utf-8 -*-
"""
    --------------------------------------------------------------------------------------------------------------------

    Description:
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Obs.:

    Author:           @andre.deoliveira
    Last Update:      24/02/2022 15:26
    Created:          24/02/2022 15:26
    Copyright:        (c) Ampere Consultoria Ltda
    Original Project: espaco_exclusivo_package
    IDE:              PyCharm
"""
from enum import Enum

class DimensoesAgrupamento(Enum):
    SE_NE_vs_S_N = ["SE+NE", "S+N"]
    SE_S_vs_NE_N = ["SE+S", "NE+N"]
    SE_N_vs_S_NE = ["SE+N", "S+NE"]
    SE_vs_S_NE_N = ["SE", "S+NE+N"]
    SE_vs_S_vs_NE_vs_N = ["SE", "S", "NE", "N"]