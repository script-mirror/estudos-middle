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


class NiveisAtm(Enum):
    SingleLevel = "single_level"
    Mb200 = "200mb"
    Mb500 = "500mb"
    Mb700 = "700mb"
    Mb850 = "850mb"
    Mb1000 = "1000mb"
