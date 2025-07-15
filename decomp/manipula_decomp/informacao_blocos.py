info_blocos = {
    'TE': {
        'campos': ['mnemonico', 'comentario'],
        'regex': r'(.{2})  (.*)(.*)',
        'formatacao': '{:>2}  {}'
    },
    'SB': {
        'campos': ['mnemonico', 'id', 'sub'],
        'regex': r'(.{2})  (.{2})   (.{1,})(.*)',
        'formatacao': '{:>2}  {:>2}   {:<2}'
    },
    'UH': {
        'campos': ['mnemonico', 'id', 'ree', 'vini', 'defmin', 'evap', 'oper', 'vmortoini', 'lim_sup', 'fator', 'nw'],
        'regex': r'(.{2})  (.{3})  (.{2})   (.{10})(.{10})     (.{1}) {0,4}(.{0,2}) {0,3}(.{0,10})(.{0,10})(.{0,1})(.{0,3})(.*)',
        'formatacao': '{:>2}  {:>3}  {:>2}   {:>10}{:>10}     {:>1}    {:>2}   {:>10}{:>10}{:>1}{:>2}'
    },
    'CT': {
        'campos': ['mnemonico', 'id', 'sub', 'nome', 'estagio', 'inflex_p1', 'disp_p1', 'cvu_p1', 'inflex_p2', 'disp_p2', 'cvu_p2', 'inflex_p3', 'disp_p3', 'cvu_p3'],
        'regex': r'(.{2})  (.{3})  (.{2})   (.{10})(.{2})   (.{5})(.{5})(.{10})(.{5})(.{5})(.{10})(.{5})(.{5})(.{10})(.*)',
        'formatacao': '{:>2}  {:>3}  {:>2}   {:>10}{:>2}   {:>5}{:>5}{:>10}{:>5}{:>5}{:>10}{:>5}{:>5}{:>10}'
    },
    'UE': {
        'campos': ['mnemonico', 'id', 'sub', 'nome', 'montante', 'jusante', 'bomb_min', 'bomb_max', 'taxa_cons'],
        'regex': r'(.{2})  (.{3})  (.{2})   (.{12})   (.{3})  (.{3})  (.{10})(.{10})(.{10})(.*)',
        'formatacao': '{:>2}  {:>3}  {:>2}   {:>12}   {:>3}  {:>3}  {:>10}{:>10}{:>10}'
    },
    'DP': {
        'campos': ['mnemonico', 'id', 'sub', 'pat', 'valor_p1', 'horas_p1', 'valor_p2', 'horas_p2', 'valor_p3', 'horas_p3'],
        'regex': r'(.{2})  (.{2})   (.{2})  (.{3})   (.{010})(.{10})(.{10})(.{10})(.{10})(.{10})(.*)',
        'formatacao': '{:>2}  {:>2}   {:>2}  {:>3}   {:>10}{:>10}{:>10}{:>10}{:>10}{:>10}'
    },
    'CD': {
        'campos': ['mnemonico', 'id', 'sub', 'nome', 'ind', 'lim_sup_p1', 'custo_p1', 'lim_sup_p2', 'custo_p2', 'lim_sup_p3', 'custo_p3'],
        'regex': r'(.{2})  (.{2})   (.{2})   (.{10})(.{2})   (.{5})(.{10})(.{5})(.{10})(.{5})(.{10})(.*)',
        'formatacao': '{:>2}  {:>2}   {:>2}   {:>10}{:>2}   {:>5}{:>10}{:>5}{:>10}{:>5}{:>10}'
    },
    'BE': {
        'campos': ['mnemonico', 'id', 'sub', 'est_ger', 'valor_p1', 'valor_p2', 'valor_p3', 'earm', 'earm_max', 'eaf'],
        'regex': r'(.{2})  (.{10})(.{2})   (.{3})  (.{5})(.{5})(.{5})(.{0,5})(.{0,5})(.{0,5})(.*)',
        'formatacao': '{:>2}  {:>10}{:>2}   {:>3}  {:>5}{:>5}{:>5}{:>5}{:>5}{:>5}'
    },
    'PQ': {
        'campos': ['mnemonico', 'id', 'sub', 'estagio', 'valor_p1', 'valor_p2', 'valor_p3'],
        'regex': r'(.{2})  (.{11})(.{1})   (.{2})   (.{5})(.{5})(.{5})(.*)',
        'formatacao': '{:>2}  {:<11}{:>1}   {:>2}   {:>5}{:>5}{:>5}'
    },
    'RI': {
        'campos': ['mnemonico', 'id', 'estagio', 'sub', 'min60_p1', 'max60_p1', 'min50_p1', 'max50_p1', 'ande_p1', 'min60_p2', 'max60_p2', 'min50_p2', 'max50_p2', 'ande_p2', 'min60_p3', 'max60_p3', 'min50_p3', 'max50_p3', 'ande_p3'],
        'regex': r'(.{2})  (.{3})   (.{1})   (.{1}) (.{7})(.{7})(.{7})(.{7})(.{7})(.{7})(.{7})(.{7})(.{7})(.{7})(.{7})(.{7})(.{7})(.{7})(.{7})(.*)',
        'formatacao': '{:>2}  {:>3}   {:>1}   {:>1} {:>7}{:>7}{:>7}{:>7}{:>7}{:>7}{:>7}{:>7}{:>7}{:>7}{:>7}{:>7}{:>7}{:>7}{:>7}'
    },
    'IA': {
        'campos': ['mnemonico', 'estagio', 's1', 's2', 'de_para_p1', 'para_de_p1', 'de_para_p2', 'para_de_p2', 'de_para_p3', 'para_de_p3'],
        'regex': r'(.{2})  (.{2})   (.{2})   (.{2})   (.{10})(.{10})(.{10})(.{10})(.{10})(.{10})(.*)',
        'formatacao': '{:>2}  {:>2}   {:>2}   {:>2}   {:>10}{:>10}{:>10}{:>10}{:>10}{:>10}'
    },
    'RC': {
        'campos': ['mnemonico', 'escada'],
        'regex': r'(.{2})  (.{6})(.*)',
        'formatacao': '{:>2}  {:>6}'
    },
    'TX': {
        'campos': ['mnemonico', 'valor'],
        'regex': r'(.{2})  (.{5})(.*)',
        'formatacao': '{:>2}  {:>5}'
    },
    'GP': {
        'campos': ['mnemonico', 'valor'],
        'regex': r'(.{2})  (.{10})(.*)',
        'formatacao': '{:>2}  {:>10}'
    },
    'NI': {
        'campos': ['mnemonico', 'valor'],
        'regex': r'(.{2})  (.{3})(.*)',
        'formatacao': '{:>2}  {:>3}'
    },
    'PD': {
        'campos': ['mnemonico', 'algoritmo'],
        'regex': r'(.{2})  (.{6})(.*)',
        'formatacao': '{:>2}  {:>6}'
    },
    'DT': {
        'campos': ['mnemonico', 'dia', 'mes', 'ano'],
        'regex': r'(.{2})  (.{2})   (.{2})   (.{4})(.*)',
        'formatacao': '{:>2}  {:>2}   {:>2}   {:>4}'
    },
    'MP': {
        'campos': ['mnemonico', 'id', 'hz', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12'],
        'regex': r'(.{2})  (.{3})(.{2})(.{5})(.{5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.*)',
        'formatacao': '{:>2}  {:>3}{:>2}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}'
    },
    'FD': {
        'campos': ['mnemonico', 'id', 'hz', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17'],
        'regex': r'(.{2})  (.{3})(.{2})(.{5})(.{5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.*)',
        'formatacao': '{:>2}  {:>3}{:>2}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}'
    },
    'VE': {
        'campos': ['mnemonico', 'id', 'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8', 'f9', 'f10', 'f11', 'f12', 'f13', 'f14', 'f15', 'f16', 'f17'],
        'regex': r'(.{2})  (.{3})  (.{5})(.{5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.*)',
        'formatacao': '{:>2}  {:>3}  {:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}'
    },
    'RE': {
        'campos': ['mnemonico', 'id', 'est_inicial', 'est_final'],
        'regex': r'(.{2})  (.{4}) (.{2})   (.{2})(.*)',
        'formatacao': '{:>2}  {:<4} {:>2}   {:>2}'
    },
    'LU': {
        'campos': ['mnemonico', 'id', 'estagio', 'vmin_p1', 'vmax_p1', 'vmin_p2', 'vmax_p2', 'vmin_p3', 'vmax_p3'],
        'regex': r'(.{2})  (.{4}) (.{2})   (.{10})(.{10})(.{10})(.{10})(.{0,10})(.{0,10})(.*)',
        'formatacao': '{:>2}  {:>4} {:>2}   {:>10}{:>10}{:>10}{:>10}{:>10}{:>10}'
    },
    'FU': {
        'campos': ['mnemonico', 'id', 'estagio', 'uh', 'fator', 'freq_itaipu'],
        'regex': r'(.{2})  (.{4}) (.{2})   (.{3})  (.{10}) {0,1}(.{0,2})(.*)',
        'formatacao': '{:>2}  {:<4} {:>2}   {:>3}  {:>10} {:>2}'
    },
    'FT': {
        'campos': ['mnemonico', 'id', 'estagio', 'ut', 'sub', 'fator'],
        'regex': r'(.{2})  (.{4}) (.{2})   (.{3})  (.{2})   (.{10})(.*)',
        'formatacao': '{:>2}  {:<4} {:>2}   {:>3}  {:>2}   {:>10}'
    },
    'FI': {
        'campos': ['mnemonico', 'id', 'estagio', 'sub_de', 'sub_para', 'fator'],
        'regex': r'(.{2})  (.{4}) (.{2})   (.{2})   (.{2})   (.{10})(.*)',
        'formatacao': '{:>2}  {:<4} {:>2}   {:>2}   {:>2}   {:>10}'
    },
    'FE': {
        'campos': ['mnemonico', 'id', 'estagio', 'ci_ce', 'sub', 'fator'],
        'regex': r'(.{2})  (.{4}) (.{2})   (.{3})  (.{2})   (.{10})(.*)',
        'formatacao': '{:>2}  {:>4} {:>2}   {:>3}  {:>2}   {:>10}'
    },
    'VI': {
        'campos': ['mnemonico', 'id', 'dur', 'qdef1', 'qdef2', 'qdef3', 'qdef4', 'qdef5', 'qdef6', 'qdef7', 'qdef8', 'qdef9'],
        'regex': r'(.{2})  (.{3})  (.{3})  (.{5})(.{5})(.{5})(.{5})(.{5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.*)',
        'formatacao': '{:>2}  {:>3}  {:>3}  {:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}{:>5}'
    },
    'AC': {
        'campos': ['mnemonico', 'id', 'param_mod', 'valor', 'mes', 'semana', 'ano'],
        'regex': r'(.{2})  (.{3})  (.{6}) {0,4}(.{0,50})(.{0,3}) {0,2}(.{0,1}) {0,1}(.{0,4})(.*)',
        'formatacao': '{:>2}  {:>3}  {:>6}    {:<50}{:>3}  {:>1} {:>4}'
    },
    'RV': {
        'campos': ['mnemonico', 'rv', 'est_inicial', 'est_final'],
        'regex': r'(.{2})  (.{7})   (.{1})    (.{1})(.*)',
        'formatacao': '{:>2}  {:>7}   {:>1}    {:>1}'
    },
    'FP': {
        'campos': ['mnemonico', 'id', 'estagio', 'tipo', 'num_pontos', 'qmin', 'qmax', 'tipo_2', 'num_pontos_2', 'vmin', 'vmax', 'ghmin', 'ghmax', 'tolerancia', 'flag_d', 'tipo_3', 'percent_n1', 'percent_n2', 'num_iter', 'verif'],
        'regex': r'(.{2})  (.{3})  (.{3})  (.{1}) (.{4}) (.{5}) (.{5})  (.{1}) (.{4}) (.{5}) (.{5})  (.{5}) (.{5}) (.{3})  (.{1})    (.{1}) (.{5}) (.{5}) (.{2})   (.{1})(.*)',
        'formatacao': '{:>2}  {:>3}  {:>3}  {:>1} {:>4} {:>5} {:>5}  {:>1} {:>4} {:>5} {:>5}  {:>5} {:>5} {:>3}  {:>1}    {:>1} {:>5} {:>5} {:>2}   {:>1}'
    },
    'IR': {
        'campos': ['mnemonico', 'arq_saida', 'est_limite', 'lim_linhas_pag'],
        'regex': r'(.{2})  (.{1,7}) {0,}(.{0,2}) {0,}(.{0,2})(.*)',
        'formatacao': '{:>2}  {:<7}   {:>2}   {:>2}'
    },
    'CI': {
        'campos': ['mnemonico', 'id', 'sub', 'nome', 'estagio', 'lim_inf_p1', 'lim_sup_p1', 'custo_p1', 'lim_inf_p2', 'lim_sup_p2', 'custo_p2', 'lim_inf_p3', 'lim_sup_p3', 'custo_p3'],
        'regex': r'(.{2})  (.{3}) (.{2}) (.{10})   (.{2})   (.{5})(.{5})(.{10})(.{5})(.{5})(.{10})(.{5})(.{5})(.{10})(.*)',
        'formatacao': '{:>2}  {:>3} {:>2} {:>10}   {:>2}   {:>5}{:>5}{:>10}{:>5}{:>5}{:>10}{:>5}{:>5}{:>10}'
    },
    'RS': {
        'campos': ['mnemonico', 'arq_defl_pass', 'arq_saida'],
        'regex': r'(.{2})  (.{5})     (.{59})(.*)',
        'formatacao': '{:>2}  {:>5}     {:>59}'
    },
    'FC': {
        'campos': ['mnemonico', 'arq_info', 'nome_arq'],
        'regex': r'(.{2})  (.{6})    (.{0,48})(.*)',
        'formatacao': '{:>2}  {:>6}    {:<48}'
    },
    'TI': {
        'campos': ['mnemonico', 'id', 'estg1', 'estg2', 'estg3', 'estg4', 'estg5', 'estg6'],
        'regex': r'(.{2})  (.{3})  (.{5})(.{5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.*)',
        'formatacao': '{:>2}  {:>3}  {:>5}{:>5}{:>5}{:>5}{:>5}{:>5}'
    },
    'RQ': {
        'campos': ['mnemonico', 'id', 'estg1', 'estg2', 'estg3', 'estg4', 'estg5', 'estg6'],
        'regex': r'(.{2})  (.{2})   (.{5})(.{5})(.{0,5})(.{0,5})(.{0,5})(.{0,5})(.*)',
        'formatacao': '{:>2}  {:>2}   {:>5}{:>5}{:>5}{:>5}{:>5}{:>5}'
    },
    'EZ': {
        'campos': ['mnemonico', 'id', 'vol_util'],
        'regex': r'(.{2})  (.{3})  (.{5})(.*)',
        'formatacao': '{:>2}  {:>3}  {:>5}'
    },
    'HV': {
        'campos': ['mnemonico', 'id', 'est_inicial', 'est_final'],
        'regex': r'(.{2})  (.{3})  (.{2})   (.{2})(.*)',
        'formatacao': '{:>2}  {:>3}  {:>2}   {:>2}'
    },
    'LV': {
        'campos': ['mnemonico', 'id', 'estagio', 'lim_inf', 'lim_sup'],
        'regex': r'(.{2})  (.{3})  (.{2})   (.{10})(.{0,10})(.*)',
        'formatacao': '{:>2}  {:>3}  {:>2}   {:>10}{:>10}'
    },
    'CV': {
        'campos': ['mnemonico', 'id', 'estagio', 'uhe_ue', 'coef_hv', 'tipo_restr'],
        'regex': r'(.{2})  (.{3})  (.{2})   (.{3})  (.{10})     (.{4})(.*)',
        'formatacao': '{:>2}  {:>3}  {:>2}   {:>3}  {:>10}     {:>4}'
    },
    'HQ': {
        'campos': ['mnemonico', 'id', 'est_inicial', 'est_final'],
        'regex': r'(.{2})  (.{3})  (.{2})   (.{2})(.*)',
        'formatacao': '{:>2}  {:>3}  {:>2}   {:>2}'
    },
    'LQ': {
        'campos': ['mnemonico', 'id', 'estagio', 'lim_inf_p1', 'lim_sup_p1', 'lim_inf_p2', 'lim_sup_p2', 'lim_inf_p3', 'lim_sup_p3'],
        'regex': r'(.{2})  (.{3})  (.{2})   (.{10})(.{10})(.{10})(.{10})(.{10})(.{0,10})(.*)',
        'formatacao': '{:>2}  {:>3}  {:>2}   {:>10}{:>10}{:>10}{:>10}{:>10}{:>10}'
    },
    'CQ': {
        'campos': ['mnemonico', 'id', 'estagio', 'uhe', 'coef', 'tipo_restr'],
        'regex': r'(.{2})  (.{3})  (.{2})   (.{3})  (.{10})     (.{4})(.*)',
        'formatacao': '{:>2}  {:>3}  {:>2}   {:>3}  {:>10}     {:>4}'
    },
    'AR': {
        'campos': ['mnemonico', 'estagio', 'lamb', 'alfa'],
        'regex': r'(.{2})   (.{3}) {0,}(.{0,5}) {0,}(.{0,5})(.*)',
        'formatacao': '{:>2}   {:>3}   {:>5} {:>5}'
    },
    'EV': {
        'campos': ['mnemonico', 'modelo', 'vol_ref'],
        'regex': r'(.{2})  (.{1})    (.{3})(.*)',
        'formatacao': '{:>2}  {:>1}    {:>3}'
    },
    'FJ': {
        'campos': ['mnemonico', 'nome_arq'],
        'regex': r'(.{2})  (.{12})(.*)',
        'formatacao': '{:>2}  {:>12}'
    },
    'HE': {
        'campos': ['mnemonico', 'id', 'tipo', 'lim_inf_ear', 'estagio', 'penalid', 'flag_produtiv', 'flag_tipo_valores', 'flag_tratamento', 'nome_arq', 'flag_tolerancia'],
        'regex': r'(.{2})  (.{3})  (.{1})    (.{10}) (.{2}) (.{10}) (.{1}) (.{1}) (.{1}) {0,}(.{0,60}) {0,1}(.{0,1})(.*)',
        'formatacao': '{:>2}  {:>3}  {:>1}    {:>10} {:>2} {:>10} {:>1} {:>1} {:>1} {:>60} {:>1}'
    },
    'CM': {
        'campos': ['mnemonico', 'id', 'indice_ree', 'coef'],
        'regex': r'(.{2})  (.{3})  (.{3})  (.{10})(.*)',
        'formatacao': '{:>2}  {:>3}  {:>3}  {:>10}'
    },
    'VL': {
        'campos': ['mnemonico', 'id', 'fator', 'coef0', 'coef1', 'coef2', 'coef3', 'coef4'],
        'regex': r'(.{2})  (.{4})  (.{1,15}) {0,}(.{0,15}) {0,}(.{0,15}) {0,}(.{0,15}) {0,}(.{0,15}) {0,}(.{0,15})(.*)',
        'formatacao': '{:>2}  {:<4}  {:<15} {:<15} {:<15} {:<15} {:<15} {:<15}'
    },
    'VU': {
        'campos': ['mnemonico', 'id', 'id_uh_influenc', 'fator'],
        'regex': r'(.{2})  (.{4})  (.{4})  (.{1,15})(.*)',
        'formatacao': '{:>2}  {:>4}  {:>4}  {:<15}'
    },
    'VA': {
        'campos': ['mnemonico', 'id', 'id_uh', 'fator'],
        'regex': r'(.{2})  (.{4})  (.{4})  (.{1,15})(.*)',
        'formatacao': '{:>2}  {:>4}  {:>4}  {:<15}'
    },
    'CX': {
        'campos': ['mnemonico', 'cod_1', 'cod_2'],
        'regex': r'(.{2})   (.{3})  (.{3})(.*)',
        'formatacao': '{:>2}   {:>3}  {:>3}'
    },
    'FA': {
        'campos': ['mnemonico', 'nome_arq'],
        'regex': r'^(.{2})\s{2}(.{1,11})(.*)',
        'formatacao': '{:>2}  {:<12}'
    }
}