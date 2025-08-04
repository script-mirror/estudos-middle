# -*- coding: utf-8 -*-
"""
    --------------------------------------------------------------------------------------------------------------------

    Description: 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Obs.: 

    Author:           @diego.yosiura
    Last Update:      21/07/2021 16:11
    Created:          21/07/2021 16:11
    Copyright:        (c) Ampere Consultoria Ltda
    Original Project: espaco_exclusivo_package
    IDE:              PyCharm
"""
from .. import Configuration
from ..auth import User


class BaseProduto:
    auth_status = False

    def __init__(self, username: str = '', password: str = '', token: str = '', user: User = None, ssl_verify=True,
                 proxy=None, path: str = None):
        try:
            self.user = User(username, password, token, ssl_verify, proxy, path)
            self.username = username
            self.password = password
            self.token = token
            self.access_token = None
            self.request = self.user.request
        except Exception as e:
            error = "[EE Auth] - Erro não tratado: {}\n" \
                    "Username: {} | Password: {} | Token: {}".format(str(e), username, password, token)
            Configuration.debug_print(error, e)
            raise Exception(error)
