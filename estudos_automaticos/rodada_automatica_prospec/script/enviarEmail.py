import os
import sys

def run():
    listTeste = []
    for i in range (23):
        
        listEstudos = f"[ \"{18920+(i*3)+i}\",\"{19180+(i*3)+i}\",  \"{18920+(i*3)+i+1}\",\"{19180+(i*3)+i+1}\", \"{18920+(i*3)+i+2}\", \"{19180+(i*3)+i+2}\"]"
        #listEstudos = f"[ \"{19307+i}\",\"{19331+i}\",  \"{19354+i}\",\"{19377+i}\"]"
        cmd =   f"python  /WX2TB/Documentos/fontes/PMO/rodada_automatica_prospec/script/mainRodadaAutoProspec.py apenas_email 1 aguardar_fim 0 media_rvs 1 considerar_rv 'sem1' assunto_email 'Rodada  2024' list_email '[ \"gilseu.muhlen@raizen.com\", \"celso.trombetta@raizen.com\"]' id_estudo '{listEstudos}';"#.format( 1, 0, 1, 'sem1','Rodada  2024' ,  '["gilseu.muhlen@raizen.com"]',listEstudos)
        os.system(cmd)
if __name__ == "__main__":
    run()


