import os
import shutil
from datetime import date, datetime, timedelta
import sys
import time

def getNextFriday(data):
    dataReturn = data
    if data.isoweekday() == 7:
        dataReturn = data + timedelta(days= 12)
    elif data.isoweekday() == 6:
        dataReturn = data + timedelta(days= 13)
    else :
        dataReturn = data + timedelta(days= 12 - data.isoweekday())
    return dataReturn

def copiaPrevsWxProspec(parametros, limparPasta):
    print('Copiando prevs Raizen para o a pasta do prospec')
    pathOutput    = parametros['path_out']
    pathPrevsPrel = parametros['path_prevs_prel']
    pathPrevsDef  = parametros['path_prevs_def']
    listPrevs = []
    data      = datetime.now()  

    if limparPasta:
        for pasta in os.listdir(pathOutput):
            try: 
                shutil.rmtree(pathOutput + '/' + pasta)
            except:
                    print('Não foi possivel deletar o diretório: ' + pathOutput + '/' + pasta)
                    print('Favor deletar manualmente o diretório: '+ pathOutput + '/' + pasta)

    for mes in range(int(data.month),int(data.month + 3)):
        if os.path.exists (pathOutput + str(mes)) == False: os.mkdir (pathOutput + str(mes))

    listaPrevPreliminar = []
    listaPrevDefinitivo = []

    try:
        for file in os.listdir(pathPrevsPrel):
            if 'prevs' in file or 'PREVS' in file:
                listaPrevPreliminar.append(file)
    except:
        print('Não foi encontrado nenhum prevs preliminar')

    try:
        for file in os.listdir(pathPrevsDef):
            if 'prevs' in file or 'PREVS' in file:
                listaPrevDefinitivo.append(file)
    except:
        print('Não foi encontrado nenhum prevs definitivo')
    if len (listaPrevDefinitivo) > 0:
        for prevs in listaPrevDefinitivo:
            if os.path.exists (pathOutput + str(getNextFriday(data).month) +'/prevs.rv' + prevs[len(prevs)-1:len(prevs)]) == False:
                os.rename(pathPrevsDef + '/' + prevs, pathOutput + str(getNextFriday(data).month) + '/prevs.rv'+ prevs[len(prevs)-1:len(prevs)])
                listPrevs.append(prevs[0:len(prevs)-4] +'_raizen')
                print(prevs + ' impresso em ' + pathOutput + str(getNextFriday(data).month) + '/prevs.rv'+ prevs[len(prevs)-1:len(prevs)])

            else:
                os.rename(pathPrevsDef + '/' + prevs, pathOutput + str(getNextFriday(data).month) +'/'+ prevs[0:len(prevs)-4] +'_raizen.rv' +  prevs[len(prevs)-1:len(prevs)])
                print(prevs + ' impresso em ' + pathOutput + str(getNextFriday(data).month) +'/'+ prevs[0:len(prevs)-4] +'_raizen.rv' +  prevs[len(prevs)-1:len(prevs)])
    
    if len (listaPrevPreliminar) > 0:   
        for prevs in listaPrevPreliminar:
            if prevs[0:len(prevs)-24] + prevs[len(prevs)-9:len(prevs)] not in listaPrevDefinitivo:
            
                if os.path.exists (pathOutput + str(getNextFriday(data).month)+ '/prevs.rv' + prevs[len(prevs)-1:len(prevs)]) == False:
                    os.rename(pathPrevsPrel + '/' + prevs, pathOutput + str(getNextFriday(data).month) +'/prevs.rv'+ prevs[len(prevs)-1:len(prevs)])
                    listPrevs.append(prevs[0:len(prevs)-4] +'_raizen')
                    print(prevs + ' impresso em ' + pathOutput + str(getNextFriday(data).month) + '/prevs.rv'+ prevs[len(prevs)-1:len(prevs)])

                else:
                    os.rename(pathPrevsPrel + '/' + prevs, pathOutput + str(getNextFriday(data).month) +'/'+ prevs[0:len(prevs)-4] +'_raizen.rv' +  prevs[len(prevs)-1:len(prevs)])
                    print(prevs + ' impresso em ' + pathOutput + str(getNextFriday(data).month) +'/'+ prevs[0:len(prevs)-4] +'_raizen.rv' +  prevs[len(prevs)-1:len(prevs)])
        for arquivos in os.listdir(pathPrevsPrel): 
            try: os.remove(pathPrevsPrel + '/' + arquivos) 
            except: (print('Não foi possivel excluir o aqruivo: ' + pathPrevsPrel + '/' + arquivos))
    
    if len (listaPrevDefinitivo) > 0:
        for arquivos in os.listdir(pathPrevsDef): 
            try: os.remove(pathPrevsDef + '/' + arquivos) 
            except: (print('Não foi possivel excluir o aqruivo: ' + pathPrevsDef + '/' + arquivos))
    if len(listPrevs) == 0:
        print('Não foi encontrou nenhum prevs Raizen , por favor conferir processo!')
        if parametros['prevs'] == 'PREVS_RAIZEN':
            sys.exit()    
    return listPrevs
 
def copiaPrevsMultiRvsRaizenProspec(parametros, limparPasta ):
    print('Copiando prevs Raizen para o a pasta do prospec')
    pathOutput = parametros['path_output_encad']
    pathPrevsEncad = parametros['path_prevs_encad']
    listPrevs = []
    data      = datetime.now()  

    if limparPasta:
        for pasta in os.listdir(pathOutput):
            try: 
                shutil.rmtree(pathOutput + '/' + pasta)
            except:
                    print('Não foi possivel deletar o diretório: ' + pathOutput + '/' + pasta)
                    print('Favor deletar manualmente o diretório: '+ pathOutput + '/' + pasta)

    for mes in range(int(data.month),int(data.month + 5)):
        mesAux = mes
        if mes > 12:  mesAux = mes-12
        if os.path.exists (pathOutput + str(mesAux)) == False: os.mkdir (pathOutput + str(mesAux))

    def copiaPrevs(pathPrevs):
  
        for file in os.listdir(pathPrevs):
            if 'prevs' in file or 'PREVS' in file:   
                fileSplit = file.split('-')
               # print(fileSplit)
                mes = str(int(fileSplit[len(fileSplit)-1][4:6]))
                #mes = str(int(file[len(file)-6:len(file)-4]))
                print(mes)
                rv = file[len(file)-1:len(file)]
                if os.path.exists (pathOutput + mes +'/prevs.rv' + rv)== False:
                    os.rename(pathPrevs + '/' + file, pathOutput + mes + '/prevs.rv'+ rv)
                    listPrevs.append(file[0:len(file)-4] +'_raizen')
                    print(file + ' impresso em ' + pathOutput + mes + '/prevs.rv'+ rv)
                else:
                    os.rename(pathPrevs + '/' + file, pathOutput + mes +'/'+ file[0:len(file)-4] +'_raizen.rv' +  rv)
                    print(file + ' impresso em ' + pathOutput + mes +'/'+ file[0:len(file)-4] +'_raizen.rv' +  rv)
        try: 
            shutil.rmtree(pathPrevs)
        except:
            pass
    #copiaPrevs(pathPrevsEncad)
    
    if parametros['path_prevs'] != '':
        copiaPrevs(pathPrevsEncad + '/'+ parametros['path_prevs'])

    else:
        cont = 0
        while len(os.listdir(pathPrevsEncad)) < 12:
            print ("Prevs Prontos:", os.listdir(pathPrevs))
            print ("Aguardando prevs!")
            time.sleep(300)
            cont +=1
            if cont > 20:
                break
        for pathInDir in os.listdir(pathPrevsEncad):
            pathPrevs = pathPrevsEncad + '/'+ pathInDir
            copiaPrevs(pathPrevs)
     
    return listPrevs

def copiaPrevsTokProspec(parametros, limparPasta ):
    print('Copiando prevs TOK para o a pasta do prospec') 
    pathOutput = parametros['path_output_tok']
    pathPrevsEncad = parametros['path_prevs_tok']
    listPrevs = []
    data      = datetime.now()  

    if limparPasta:
        for pasta in os.listdir(pathOutput):
            try: 
                shutil.rmtree(pathOutput + '/' + pasta)
            except:
                    print('Não foi possivel deletar o diretório: ' + pathOutput + '/' + pasta)
                    print('Favor deletar manualmente o diretório: '+ pathOutput + '/' + pasta)

    for mes in range(int(data.month),int(data.month + 3)):
        mesAux = mes
        if mes > 12:  mesAux = mes-12
        if os.path.exists (pathOutput + str(mesAux)) == False: os.mkdir (pathOutput + str(mesAux))

    def copiaPrevs(pathPrevs):
        for file in os.listdir(pathPrevs):
            if 'prevs' in file or 'PREVS' in file and not '.txt' in file:  
                if not '.txt' in file:   
                    fileSplit = file.split('_')
                    mes = str(int(fileSplit[3]))
                    print(mes)
                    rv = file[len(file)-1:len(file)]
                    os.rename(pathPrevs + '/' + file, pathOutput + mes + '/prevs.rv'+ rv)
                    listPrevs.append(fileSplit[4] +'_TOK')
                    print(file + ' impresso em ' + pathOutput + mes + '/prevs.rv'+ rv)
        try: 
            shutil.rmtree(pathPrevs)
        except:
            pass
    if parametros['path_prevs'] != '':
        copiaPrevs(pathPrevsEncad + '/'+ parametros['path_prevs'])

    else:
        for pathInDir in os.listdir(pathPrevsEncad):
            pathPrevs = pathPrevsEncad + '/'+ pathInDir
            copiaPrevs(pathPrevs)

    if len(listPrevs) == 0: 
        print('Não foi encontrou nenhum prevs  Raizen , por favor conferir processo!')
        sys.exit()        
    return listPrevs
