#!/bin/bash -x



# echo "Inicio: `date +%d-%m-%y_%H:%M:%S`" > $log
echo "Inicio: `date +%d-%m-%y_%H:%M:%S`"

. /WX2TB/Documentos/fontes/PMO/scripts_unificados/env_activate

#executa o estudo
python /WX2TB/Documentos/fontes/PMO/rodada_automatica_prospec/script/mainRodadaAutoProspec.py prevs PREVS_PLUVIA_2_RV rvs 2 preliminar 0 

# echo "Fim: `date +%d-%m-%y_%H:%M:%S`" >> $log
echo "Fim: `date +%d-%m-%y_%H:%M:%S`"


