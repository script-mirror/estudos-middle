from datetime import datetime
from frozendict import frozendict
from middle.utils.constants import Constants 

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
        'rodada':{'Preliminar':{'precipitacao': ["GEFS", "ONS_Pluvia", "ONS_ETAd_1_Pluvia", "ECMWF_ENS", "ECMWF_ENS", "GEFS"],
                                      'membro': ["ENSEMBLE", "NULO", "NULO", "ENSEMBLE", "00", "00"]},
                  'Definitiva':{'precipitacao': ["GEFS", "ONS_Pluvia", "ONS_ETAd_1_Pluvia", "ECMWF_ENS", "ECMWF_ENS", "GEFS"],
                                      'membro': ["ENSEMBLE", "NULO", "NULO", "ENSEMBLE", "00", "00"]}}
    }),
    'UPDATE': frozendict({
        'description': 'Rodadas proxima RV',
        'emails': [const.EMAIL_MIDDLE, const.EMAIL_FRONT],
        'whats': const.WHATSAPP_PRECO,
        'n_estudos': 1,
        'path_prevs': 'update',
        'aguardar_fim': True,
        'rodada':{'Preliminar':{'precipitacao': ["ONS_Pluvia"],
                                      'membro': ["NULO"]},
                  'Definitiva':{'precipitacao': ["ONS_Pluvia"],
                                      'membro': ["NULO"]}}
    }),
    'P.CONJ': frozendict({
        'description': 'Rodadas P. Conjunto',
        'emails': [const.EMAIL_MIDDLE, const.EMAIL_FRONT],
        'whats': const.WHATSAPP_PRECO,
        'n_estudos': 10,
        'path_prevs': 'p_conj',
        'aguardar_fim': True,
        'rodada':{'Preliminar':{'precipitacao': ['ONS_Pluvia'], 'membro':['NULO']},
                  'Definitiva':{'precipitacao': ['ONS'], 'membro':['NULO']}}
    }),
    'CENARIOS': frozendict({
        'description': 'Rodadas Cenarios Raizen',
        'emails': [const.EMAIL_MIDDLE, const.EMAIL_FRONT],
        'whats': const.WHATSAPP_PRECO,
        'n_estudos': 10,
        'path_prevs': 'cenarios',
        'aguardar_fim': True,
        'rodada':{'Preliminar':{'precipitacao': ['Usuário'], 'membro':['NULO']},
                  'Definitiva':{'precipitacao': ['Usuário'], 'membro':['NULO']}}
    }),
    'P.ZERO': frozendict({
        'description': 'Rodadas Chuva Zero',
        'emails': [const.EMAIL_MIDDLE, const.EMAIL_FRONT],
        'whats': const.WHATSAPP_PRECO,
        'n_estudos': 1,
        'path_prevs': 'p_zero',
        'aguardar_fim': True,       
        'rodada':{'Preliminar':{'precipitacao': ['Prec. Zero'], 'membro':['NULO']},
                  'Definitiva':{'precipitacao': ['Prec. Zero'], 'membro':['NULO']}}  
    }),
    'P.APR': frozendict({
        'description': 'Rodadas P. Conjunto Precipitação Agrupada',
        'emails': [const.EMAIL_GILSEU],
        'whats': const.WHATSAPP_GILSEU,
        'n_estudos': 1,
        'path_prevs': 'p_agrupada',
        'aguardar_fim': True,
        'rodada':{'Preliminar':{'precipitacao': ['ONS_Pluvia'], 'membro':['AgrupadoPrecipitacao']},
                  'Definitiva':{'precipitacao': ['ONS_Pluvia'], 'membro':['AgrupadoPrecipitacao']}}
    }),
    'NAO-CONSISTIDO': frozendict({
        'description': 'Rodadas Não Consistidas',
        'emails': [const.EMAIL_MIDDLE, const.EMAIL_FRONT],
        'whats': const.WHATSAPP_PRECO,
        'n_estudos': 1,
        'aguardar_fim': True,
        'path_prevs': 'nao_consistido'
    }),
    'EC-EXT': frozendict({
        'description': 'Rodadas EC EXT',
        'emails': [const.EMAIL_MIDDLE, const.EMAIL_FRONT],
        'whats': const.WHATSAPP_PRECO,
        'n_estudos': 5,
        'path_prevs': 'ec_ext',
        'aguardar_fim': False,
        'rodada':{'Definitiva':{'precipitacao': ['ECMWF_ENS_EXT'], 'membro':['ENSEMBLE']}}
    }),
    'ONS-GRUPOS': frozendict({
        'description': 'Rodadas ONS Agrupados',
        'emails': [const.EMAIL_MIDDLE, const.EMAIL_FRONT],
        'whats': const.WHATSAPP_PRECO,
        'n_estudos': 1,
        'path_prevs': 'ons_grupos',
        'aguardar_fim': False,
        'rodada':{'Preliminar':{'precipitacao': ['ONS_Pluvia'], 'membro':[ "Grupo01", "Grupo02", "Grupo03", "Grupo04", "Grupo05", "Grupo06", "Grupo07", "Grupo08", "Grupo09", "Grupo10"]},
                  'Definitiva':{'precipitacao': ['ONS_Pluvia'], 'membro':[ "Grupo01", "Grupo02", "Grupo03", "Grupo04", "Grupo05", "Grupo06", "Grupo07", "Grupo08", "Grupo09", "Grupo10"]}}
    }),
    'SENS': frozendict({
        'description': 'Rodadas sensibilidades',
        'emails': [const.EMAIL_GILSEU],
        'whats': const.WHATSAPP_GILSEU,
        'n_estudos': 1,
        'path_prevs': 'sens',
        'aguardar_fim': False,
        'rodada':{'Preliminar':{'precipitacao': ['ONS_Pluvia'], 'membro':['NULO']},
                  'Definitiva':{'precipitacao': ['ONS'], 'membro':['NULO']}}
    }),
    'DECOMP': frozendict({
        'description': 'Rodadas decomp convertido',
        'emails': [const.EMAIL_GILSEU],
        'whats': const.WHATSAPP_GILSEU,
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

