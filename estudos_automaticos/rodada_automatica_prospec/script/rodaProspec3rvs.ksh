#!/bin/bash -x

log=/WX2TB/Documentos/fontes/PMO/rodada_automatica_prospec/script/log/rodaProspec3rvs.log

echo "Inicio: `date +%d-%m-%y_%H:%M:%S`" > $log

. /WX2TB/Documentos/fontes/PMO/scripts_unificados/env_activate

dt=$(date +"%d/%m/%Y")

#executa o estudo
python /WX2TB/Documentos/fontes/PMO/rodada_automatica_prospec/script/mainRodadaAutoProspec.py prevs PREVS_PLUVIA_2_RV rvs 3 preliminar 1 data $dt

echo "Fim: `date +%d-%m-%y_%H:%M:%S`" >> $log


