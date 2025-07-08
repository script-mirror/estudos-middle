#!/bin/bash -x

log=/WX2TB/Documentos/fontes/PMO/rodada_automatica_prospec/script/log/rodaProspecPzero.log

echo "Inicio: `date +%d-%m-%y_%H:%M:%S`" > $log

. /WX2TB/Documentos/fontes/PMO/scripts_unificados/env_activate

dt=$(date +"%d/%m/%Y")

#executa o estudo
python /WX2TB/Documentos/fontes/PMO/rodada_automatica_prospec/script/mainRodadaAutoProspec.py prevs PREVS_PLUVIA_PREC_ZERO rvs 7 

echo "Fim: `date +%d-%m-%y_%H:%M:%S`" >> $log


