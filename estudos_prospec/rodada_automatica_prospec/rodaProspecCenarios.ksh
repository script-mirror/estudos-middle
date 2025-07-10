#!/bin/bash -x

model=$1


echo "Inicio: `date +%d-%m-%y_%H:%M:%S`" 

. /WX2TB/Documentos/fontes/PMO/scripts_unificados/env_activate

dt=$(date +"%d/%m/%Y")

#executa o estudo
python /WX2TB/Documentos/fontes/PMO/rodada_automatica_prospec/script/mainRodadaAutoProspec.py prevs PREVS_PLUVIA_USUARIO preliminar 1 rvs 7 cenario ${model} 

echo "Fim: `date +%d-%m-%y_%H:%M:%S`" 


