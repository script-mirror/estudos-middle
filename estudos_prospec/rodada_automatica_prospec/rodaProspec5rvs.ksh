#!/bin/bash -x

echo "Inicio: `date +%d-%m-%y_%H:%M:%S`" > $log

. /WX2TB/Documentos/fontes/PMO/scripts_unificados/env_activate


#executa o estudo
python /WX2TB/Documentos/fontes/PMO/rodada_automatica_prospec/script/mainRodadaAutoProspec.py prevs PREVS_PLUVIA_EC_EXT rvs 5 preliminar 0 

echo "Fim: `date +%d-%m-%y_%H:%M:%S`" >> $log


