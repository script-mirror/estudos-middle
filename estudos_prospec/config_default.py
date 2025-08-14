from datetime import datetime
from frozendict import frozendict
from middle.utils._constants import Constants 

const = Constants() 
# frozendict Não permite alterar
EMAIL_CONFIG = frozendict({
    'NEXT-RV': frozendict({
        'description': 'Rodadas proxima RV',
        'emails': [const.EMAIL_MIDDLE, const.EMAIL_FRONT],
        'whats': const.WHATSAPP_PRECO,
        'n_estudos': 1,
        'path_prevs': 'next_rv',
        'aguardar_fim': True,
        "considerar_rv": 'sem',
        'rodada':{'Preliminar':['ECMWF_ENS-Preliminar-SMAP', 'GEFS-Preliminar-SMAP', 'ECMWF_ENS-00-Preliminar-SMAP', 'GEFS-00-Preliminar-SMAP', 'ONS_Pluvia-Preliminar-SMAP', 'ONS_ETAd_1_Pluvia-Preliminar-SMAP'],
                  'Definitiva':['ECMWF_ENS-SMAP', 'GEFS-SMAP', 'ECMWF_ENS-00-SMAP', 'GEFS-00-SMAP', 'ONS_Pluvia-SMAP', 'ONS_ETAd_1_Pluvia-SMAP']}
    }),
    'UPDATE': frozendict({
        'description': 'Rodadas proxima RV',
        'emails': [const.EMAIL_MIDDLE, const.EMAIL_FRONT],
        'whats': const.WHATSAPP_PRECO,
        'n_estudos': 1,
        'path_prevs': 'update',
        'aguardar_fim': True,
        "considerar_rv": 'sem',
        'rodada':{'Preliminar':['ONS_Pluvia-Preliminar-SMAP'],
                  'Definitiva':['ONS_Pluvia-SMAP']}
                                      
    }),
    'P.CONJ': frozendict({
        'description': 'Rodadas P. Conjunto',
        'emails': [const.EMAIL_MIDDLE, const.EMAIL_FRONT],
        'whats': const.WHATSAPP_PRECO,
        'n_estudos': 10,
        'path_prevs': 'p_conj',
        'aguardar_fim': True,
        "considerar_rv": 'sem',
        'rodada':{'Preliminar': ['ONS_Pluvia-Preliminar-SMAP'],
                  'Definitiva':['ONS_Pluvia-SMAP']}
    }),
    'CENARIOS': frozendict({
        'description': 'Rodadas Cenarios Raizen',
        'emails': [const.EMAIL_MIDDLE, const.EMAIL_FRONT],
        'whats': const.WHATSAPP_PRECO,
        'n_estudos': 10,
        'path_prevs': 'cenarios',
        'aguardar_fim': True,
        "considerar_rv": '_s1',
        'rodada':{'Preliminar':['Usuario_MEDIA_CFS_3_DIAS-Preliminar-SMAP']}
    }),
    'P.ZERO': frozendict({
        'description': 'Rodadas Chuva Zero',
        'emails': [const.EMAIL_MIDDLE, const.EMAIL_FRONT],
        'whats': const.WHATSAPP_PRECO,
        'n_estudos': 1,
        'path_prevs': 'p_zero',
        'aguardar_fim': True, 
        "considerar_rv": 'sem',      
        'rodada':{'Preliminar':['PrecZero_60-Preliminar-SMAP'],
                  'Definitiva':['PrecZero_60-SMAP']}
    }),
    'P.APR': frozendict({
        'description': 'Rodadas P. Conjunto Precipitação Agrupada',
        'emails': [const.EMAIL_GILSEU],
        'whats': const.WHATSAPP_GILSEU,
        'n_estudos': 1,
        'path_prevs': 'p_agrupada',
        'aguardar_fim': True,
        "considerar_rv": 'sem',
        'rodada':{'Preliminar':['ONS_Pluvia-AgrupadoPrecipitacao-Preliminar-SMAP'],
                  'Definitiva':['ONS_Pluvia-AgrupadoPrecipitacao-SMAP']}
    }),
    'CONSISTIDO': frozendict({
        'description': 'Rodadas Não Consistidas',
        'emails': [const.EMAIL_MIDDLE, const.EMAIL_FRONT],
        'whats': const.WHATSAPP_PRECO,
        'n_estudos': 1,
        'aguardar_fim': True,
        "considerar_rv": 'sem',
        'path_prevs': 'nao_consistido',
        'rodada':{'Preliminar':['CONSISTIDO'],
                  'Definitiva':['CONSISTIDO']}
    }),
    'EC-EXT': frozendict({
        'description': 'Rodadas EC EXT',
        'emails': [const.EMAIL_MIDDLE, const.EMAIL_FRONT],
        'whats': const.WHATSAPP_PRECO,
        'n_estudos': 5,
        'path_prevs': 'ec_ext',
        'aguardar_fim': True,
        "considerar_rv": 'sem',
        'rodada':{'Definitiva':['ECMWF_ENS_ext-SMAP']}
    }),
    'ONS-GRUPOS': frozendict({
        'description': 'Rodadas ONS Agrupados',
        'emails': [const.EMAIL_MIDDLE, const.EMAIL_FRONT],
        'whats': const.WHATSAPP_PRECO,
        'n_estudos': 10,
        'path_prevs': 'ons_grupos',
        'aguardar_fim': False,
        "considerar_rv": 'sem',
        'rodada':{'Definitiva':[ "ONS_Pluvia-Grupo01-SMAP", "ONS_Pluvia-Grupo02-SMAP", "ONS_Pluvia-Grupo03-SMAP", "ONS_Pluvia-Grupo04-SMAP", "ONS_Pluvia-Grupo05-SMAP",
                                 "ONS_Pluvia-Grupo06-SMAP", "ONS_Pluvia-Grupo07-SMAP", "ONS_Pluvia-Grupo08-SMAP", "ONS_Pluvia-Grupo09-SMAP", "ONS_Pluvia-Grupo10-SMAP"]}
    }),
    'SENS': frozendict({
        'description': 'Rodadas sensibilidades',
        'emails': [const.EMAIL_GILSEU],
        'whats': const.WHATSAPP_GILSEU,
        'n_estudos': 1,
        'path_prevs': 'sens',
        'aguardar_fim': False,
        "considerar_rv": 'sem',
        'rodada':{'Preliminar': ['ONS_Pluvia-Preliminar-SMAP'],
                  'Definitiva':['ONS_Pluvia-SMAP']}
    }),
    'AMPERE': frozendict({
        'description': 'Rodadas p.conjunto AMPERE',
        'emails': [const.EMAIL_GILSEU],
        'whats': const.WHATSAPP_GILSEU,
        'n_estudos': 1,
        'path_prevs': 'ampere',
        'aguardar_fim': True,
        "considerar_rv": 'sem',
        'rodada':{'Preliminar': ['ONS-OFICIAL-NT00752020-RVEXT-VMEDPONDERADA'],
                  'Definitiva': ['ONS-OFICIAL-NT00752020-RVEXT-VMEDPONDERADA']}
    }),
    'DECOMP': frozendict({
        'description': 'Rodadas decomp convertido',
        'emails': [const.EMAIL_GILSEU],
        'whats': const.WHATSAPP_GILSEU,
        "considerar_rv": '_s1',
        'n_estudos': 1
    })
})
#datetime.strptime("01/06/2025", "%d/%m/%Y")
# Parâmetros globais predefinidos
PARAMETROS =  {
        "rodada": 'Preliminar',
        "data": datetime.now(),
        "apenas_email": False,
        "assunto_email": None,
        "corpo_email": None,
        "list_email": [const.EMAIL_GILSEU],
        "considerar_rv": 'sem',
        "path_name": None,
        "back_teste": False,
        "aguardar_fim": True,
        "executar_estudo": True,
        "media_rvs": False,
        "n_membros": 0,
        "n_tentativas": 15,
        "percentis_ec": [],
        "nome_estudo": None,
        "sensibilidade": "NAO_INFORMADA",
        "tag": None,
        "id_estudo": None,
        "list_whats":const.WHATSAPP_GILSEU,
        "cenario":10,
        "prevs_name": None
    }

