# -*- coding: utf-8 -*-
"""
    --------------------------------------------------------------------------------------------------------------------

    Description: 
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Obs.: 

    Author:           @diego.yosiura
    Last Update:      21/07/2021 14:56
    Created:          21/07/2021 14:56
    Copyright:        (c) Ampere Consultoria Ltda
    Original Project: espaco_exclusivo_package
    IDE:              PyCharm
"""
import re
import sys
import traceback

from datetime import datetime


class Configuration:
    ERROR_TEMPLATE = """
    # ######################################################################################################################
    # Title: {title}
    # Date: {exception_date}
    # Description: {description}
    # File Name: {file_name}
    # Code Line: {code_line}
    # Code Name: {code_name}
    # Exception Type: {exception_type}
    #
    # ----------------------------------------------------------------------------------------------------------------------
    # [TRACEBACK]
    # ===========
    # 
    # {traceback}
    # ######################################################################################################################
    """

    Debug = True
    BaseURL = 'https://exclusivo.ampereconsultoria.com.br'
    URI = {
        'auth': {
            'get_auth_code': ['{}/automated-login/'.format(BaseURL), 'PUT'],
            'check_user_permission': ['{}/admin/contratos/current-user-has-permission/'.format(BaseURL), 'GET']
        },
        'file_viewer': {
            'list': ['{}/produtos/file-viewer/get-file-list/'.format(BaseURL), 'GET'],
            'download': ['{}/produtos/file-viewer/get-file/'.format(BaseURL), 'GET']
        },
        'meteorologia': {
            'get_images': ['{}/produtos/meteorologia/imagens-clima/'.format(BaseURL), 'GET'],
            'comparador': ['{}/produtos/meteorologia/comparador-imagens-clima/'.format(BaseURL), 'POST'],
            'data_store': ['{}/produtos/meteorologia/data-store/'.format(BaseURL), 'POST']
        },
        'flux': {
            'automatico': {
                'get_list': ['{}/produtos/previvaz-automatico/get-list/'.format(BaseURL), 'GET'],
                'download_zip': ['{}/produtos/previvaz-automatico/get-zip/'.format(BaseURL), 'GET'],
                'verify-last-results-automatico': ['{}/produtos/previvaz-automatico/verify-last-results-automatico/'.format(BaseURL), 'POST']
            },
            'historico': {
                'get_data': ['{}/produtos/previvaz-historico/get-data/'.format(BaseURL), 'GET'],
                'download_zip': ['{}/produtos/previvaz-historico/download-data/'.format(BaseURL), 'GET']
            },
            'gt': {
                'get_data': ['{}/produtos/previvaz-gt/get-data/'.format(BaseURL), 'GET'],
                'download_zip': ['{}/produtos/previvaz-gt/download-data/'.format(BaseURL), 'GET']
            },
            'ec46': {
                'get_data': ['{}/produtos/ec46-multimembros/get-data/'.format(BaseURL), 'GET'],
                'download_zip': ['{}/produtos/ec46-multimembros/download-data/'.format(BaseURL), 'GET']
            },
            'ena_diaria': {
                'get_options': ['{}/produtos/previvaz-ena-diaria/get-data/'.format(BaseURL), 'GET'],
                'get_cenario': ['{}/produtos/previvaz-ena-diaria/get-cenario/'.format(BaseURL), 'POST']
            },
            'upload': {
                'get_list': ['{}/produtos/previvaz-arquivo/get-list/'.format(BaseURL), 'GET'],
                'upload': ['{}/produtos/previvaz-arquivo/save/'.format(BaseURL), 'POST'],
                'get_link': ['{}/produtos/previvaz-arquivo/get-download-link/'.format(BaseURL), 'POST']
            },
            'personalizado': {
                'create_request': ['{}/produtos/previvaz-personalizado/save/'.format(BaseURL), 'POST'],
                'get_preview': ['{}/produtos/previvaz-personalizado/get-preview-data/'.format(BaseURL), 'GET'],
                'get_list': ['{}/produtos/previvaz-personalizado/get-list/'.format(BaseURL), 'POST'],
                'execution_queue': ['{}/produtos/previvaz-personalizado/send-data/'.format(BaseURL), 'POST'],
                'get_link': ['{}/produtos/previvaz-personalizado/get-download-link/'.format(BaseURL), 'POST']
            }
        }
    }

    @staticmethod
    def get_uri(uri):
        try:
            ref = dict(Configuration.URI)
            spl_uri_args = str(uri).split('?')
            spl_uri = str(spl_uri_args[0]).split('.')
            for u in spl_uri:
                ref = ref[u]
            ref = ref[:]
            if len(spl_uri_args) == 2:
                ref[0] += '?' + spl_uri_args[1]
            return ref
        except Exception as e:
            error = "[EE RequestManager] - Erro não tratado: {}\nURI Ref: {}".format(str(e), uri)
            Configuration.debug_print(error, e)
            raise Exception(error)

    @staticmethod
    def debug_print(message, exception=None):
        if Configuration.Debug:
            if exception is not None:
                e_type, e_value, e_traceback = sys.exc_info()
                print(Configuration.ERROR_TEMPLATE.format(
                    title=message,
                    description='\n#              '.join(str(exception).split('\n')),
                    file_name=str(e_traceback.tb_frame.f_code.co_filename),
                    code_line=str(e_traceback.tb_lineno),
                    code_name=str(e_traceback.tb_frame.f_code.co_name),
                    exception_type=str(e_type.__name__),
                    exception_date=datetime.utcnow().strftime('%d/%m/%Y %H:%M:%S'),
                    traceback=re.sub(r'\n', '\n# ', traceback.format_exc())
                ))

        else:
            print(message)
