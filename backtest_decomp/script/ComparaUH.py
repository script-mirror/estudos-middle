
import os
import csv
import sys
import xlrd
import time
#from EARMsubm import EARMmax_subm
#def main():
def Comparador_Reservatorio(pathCadUsi,path_cadastro,path_dadger):
#     pathRDH ='C:\\dev\\RDH18MAI.xlsx'
#     pathCadUsi ='C:\\dev\\CadUsH2.dat'
#     path_cadastro ='C:\\dev\\Comparador_ENA\\CadastroPostos.csv'
#     path_dadger = 'C:\\dev\\DC201906-sem1\\dadger.rv0'
     # RDH
#     dictRDH = Leitor_RDH_arm(pathRDH)
     dictUH = Leitura_blocoUH(path_dadger)
     dictCadUsi, dictSubm_EARMmax, dictREE_EARMmax = EARMmax_subm(pathCadUsi,path_cadastro)

#     dictARM = AplicaRDH_EARMmax(dictCadUsi,dictRDH)
     dictARM = AplicaUH_EARMmax(dictCadUsi,dictUH)

     listRee =['1','6','7','5','10','12','2','11','3','4','8','9']

     dictSubm_EARM,dictREE_EARM = CompilaEARM(dictARM,listRee,'EARM')
     
     dictCompiladoUH ={'subm':dictSubm_EARM,'ree':dictREE_EARM,'submMAX':dictSubm_EARMmax,'reeMAX': dictREE_EARMmax}
     return dictCompiladoUH

def Leitura_blocoUH(pathDadger):
     dictUH ={}
     with open(pathDadger) as f:
        for line in f:
            if (line[0] != '&') and(line[0] != '\n') :
                 bloco = line[:2]
                 if bloco =='UH':
                      listParam =line.split()
                      cod = listParam[1].strip()
                      ree = listParam[2].strip()
                      arm = float(listParam[3].strip())
                      dictUH[cod] = {}
                      dictUH[cod]['ree'] = ree
                      dictUH[cod]['arm'] = arm

     # Ajusta Ficticios NE
     dictUH['308'] ={'ree':'3','arm':dictUH['155']['arm']}
     dictUH['294'] ={'ree':'3','arm':dictUH['162']['arm']}
     dictUH['295'] ={'ree':'3','arm':dictUH['156']['arm']}

     # Ajusta Ficticios N
     dictUH['291'] ={'ree':'4','arm':dictUH['251']['arm']} # S. MEsa
     dictUH['292'] ={'ree':'4','arm':dictUH['252']['arm']} # Cana Br
#     dictUH['299'] ={'ree':'4','arm':dictUH['269']['arm']} # Couto M
     dictUH['302'] ={'ree':'4','arm':dictUH['261']['arm']} # Lajeado
     dictUH['303'] ={'ree':'4','arm':dictUH['257']['arm']} # Peixe A
     dictUH['306'] ={'ree':'4','arm':dictUH['253']['arm']} # Sao Sal


     return dictUH

def AplicaUH_EARMmax(dictCad,dictUH):

     for cod in dictUH.keys():
          arm = dictUH[cod]['arm']/100.00
          prod = Produt_jusante(dictCad,cod)
          volmax = float(dictCad[cod]["Vol.Max.(hm3)"].replace(',','.'))
          volmin = float(dictCad[cod]["Vol.min.(hm3)"].replace(',','.'))
          volutil = volmax-volmin
          volutil = volutil*arm
          dictUH[cod]['prod_acumm'] = prod
          dictUH[cod]['EARM'] = prod*volutil

     return dictUH


def AplicaRDH_EARMmax(dictCad,dictRDH):

     for cod_uhe in dictCad:
          EARMmax = dictCad[cod_uhe]['EARMmax']
          ree = dictCad[cod_uhe]['ree']
          for cod_posto in dictRDH:
               if cod_posto == dictCad[cod_uhe]['Posto']:
                    arm = dictRDH[cod_posto]['arm']
                    dictRDH[cod_posto]['EARM'] = float(arm*EARMmax/100)
                    dictRDH[cod_posto]['ree'] = ree
                    

     return dictRDH

def CompilaEARM(dictCad,listRegiao,tipo_earm):
     dictREE_EARM = {}
     #print '\n######'
     #print tipo_earm
     for regiao in listRegiao:
          soma = 0.0
          for cod_posto in dictCad.keys():
               if dictCad[cod_posto]['ree'] == regiao:
                    soma+=dictCad[cod_posto][tipo_earm]

          #print 'REE: '+str(regiao)+ ' '+str(round(soma/2.6784,1))
          dictREE_EARM[regiao] = round(soma/2.6784,1)



     dictSubm_REE ={'SE':['1','10','12','6','5','7'], #17 bacias
                    'S':['2','11'],
                    'NE':['3'],
                    'N':['4','8','9']}

     dictSubm_EARM ={}
     listSUBM = ['SE','S','NE','N']
     for subm in listSUBM:
          somaSub = 0.0
          for ree in dictSubm_REE[subm]:
               somaSub+=dictREE_EARM[ree]
          dictSubm_EARM[subm] = round(somaSub,2)
          #print 'SUBM: '+str(subm)+ ' '+str(round(somaSub,2))

     return dictSubm_EARM,dictREE_EARM


def Leitor_RDH_arm(path):
#     dictMudaCad = {'66':'266',
#                    '40':'240',
#                    '42':'242',
#                    '43':'243',
#                    '45':'245',
#                    '46':'246',
#                    '75':'76',
#                    '299':'130',
#                    '37':'237',
#                    '38':'238',
#                    '39':'239',
#                    '299':'130'
#               }
     arquivo = path
     dictPostoDataRDH ={}
     book = xlrd.open_workbook(arquivo)
     sheet= book.sheet_by_index(0)
     j =7 # Procura coluna correspondente do posto
     celula_valida = 1
     while celula_valida:
          try:
               codigo_posto = sheet.cell(j,4).value
               if (codigo_posto == 'ND'):
                    pass
               else:
                    codigo_posto = str(int(codigo_posto))
                    try:
                         dictPostoDataRDH[codigo_posto]
                    except:
                         dictPostoDataRDH[codigo_posto] ={}
                    dictPostoDataRDH[codigo_posto] ={}

                    arm = sheet.cell(j,15).value
                    niv = sheet.cell(j,14).value
                    dictPostoDataRDH[codigo_posto]['arm'] = Try_float(arm)
                    dictPostoDataRDH[codigo_posto]['niv'] = Try_float(niv)
          except:
               celula_valida = 0
          j =j+1


     return dictPostoDataRDH


def Try_float(valor):
    try:
        new_value = float(valor)
    except:
        new_value = '-'
    return new_value

def EARMmax_subm(pathCadUsi,path_cadastro):

     dictCadastro,listSubm, listBacia, listRee = Leitura_Cadastro(path_cadastro)

     dictCadUsi = Leitor_CadUsi(pathCadUsi)
     dictCadUsi = Modif_AC(dictCadUsi)



     dictCadUsi = Add_Ree_dictCad(dictCadastro,dictCadUsi)
     dictCadUsi.pop('216')
     dictCadUsi.pop('225')
     dictCadUsi.pop('80')
     dictCadUsi.pop('185')
     dictCadUsi.pop('88')
     dictCadUsi.pop('85')
     dictCadUsi.pop('313')
     dictCadUsi.pop('22')
     dictCadUsi.pop('289')
     dictCadUsi.pop('282')
     dictCadUsi.pop('44')
     dictCadUsi.pop('132')
     dictCadUsi.pop('138')
     dictCadUsi.pop('128')
     dictCadUsi.pop('269')
     dictCadUsi.pop('194')
     dictCadUsi.pop('105')
     dictCadUsi.pop('186')
     dictCadUsi.pop('149')

#     sys.exit()
#     dictCadUsi.pop('289')
#     dictCadUsi.pop('289')
#     dictCadUsi.pop('289')



     dictCadUsi['294']['ree'] = '3'
     dictCadUsi['295']['ree'] = '3'
     dictCadUsi['298']['ree'] = '3'
     dictCadUsi['307']['ree'] = '3'
     dictCadUsi['308']['ree'] = '3'
     dictCadUsi['175']['ree'] = '3'




#     dictCadUsi['186']['ree'] = '1'
     dictCadUsi['119']['ree'] = '1'
     dictCadUsi['118']['ree'] = '1'
     dictCadUsi['117']['ree'] = '1'
#     dictCadUsi['194']['ree'] = '1'
     dictCadUsi['305']['ree'] = '1'
     dictCadUsi['133']['ree'] = '1'
     dictCadUsi['131']['ree'] = '1'
     dictCadUsi['183']['ree'] = '1'
     dictCadUsi['182']['ree'] = '1'
     dictCadUsi['184']['ree'] = '1'
#     dictCadUsi['149']['ree'] = '1'
#     dictCadUsi['269']['ree'] = '1'

#     dictCadUsi['22']['ree'] = '10'
#     dictCadUsi['22']['ree'] = '10'
#     dictCadUsi['289']['ree'] = '10'
#     dictCadUsi['282']['ree'] = '10'
#     dictCadUsi['313']['ree'] = '10'

     dictCadUsi['288']['ree'] = '8'


     dictCadUsi['273']['ree'] = '4'
     dictCadUsi['299']['ree'] = '4'
     dictCadUsi['268']['ree'] = '4'
     dictCadUsi['302']['ree'] = '4'
     dictCadUsi['306']['ree'] = '4'
     dictCadUsi['303']['ree'] = '4'
     dictCadUsi['291']['ree'] = '4'
     dictCadUsi['292']['ree'] = '4'

     dictCadUsi['58']['ree'] = '12'
     dictCadUsi['301']['ree'] = '12'

     dictCadUsi['55']['ree'] = '11'
     dictCadUsi['54']['ree'] = '11'
     dictCadUsi['318']['ree'] = '11'
     dictCadUsi['81']['ree'] = '11'
     dictCadUsi['75']['ree'] = '11'

     dictCadUsi['317']['ree'] = '12'
     dictCadUsi['318']['ree'] = '12'
     dictCadUsi['319']['ree'] = '12'

     dictCadUsi['107']['ree'] = '10'

     dictCadUsi = CalculaProdut(dictCadUsi)
     dictCadUsi = CalculaEARMmax(dictCadUsi)

     #### PRINTANDO DEBUG
#     for cod in ['267','275','272','288','314','280','204','277','286','284']:
#          #print cod, dictCadUsi[cod]['prod_acumm'], dictCadUsi[cod]['Jusante']
#     sys.exit()

     listRee =['1','6','7','5','10','12','2','11','3','4','8','9']
     dictSubm_EARM,dictREE_EARM = CompilaEARM(dictCadUsi,listRee,'EARMmax')
     return dictCadUsi, dictSubm_EARM, dictREE_EARM


def Modif_AC(dictCad):
     # JUSMED 285
     dictCad['285']['Canal Fuga Medio(m)'] = '74.44'
     # JUSMED 287
     dictCad['287']['Canal Fuga Medio(m)'] = '53.54'

     dictCad['275']['Canal Fuga Medio(m)'] = '6.23'
     # cotvol 285
     dictCad['285']['PCV(0)'] = '90.00'
     dictCad['285']['PCV(1)'] = '0.00'
     dictCad['285']['PCV(2)'] = '0.00'
     dictCad['285']['PCV(3)'] = '0.00'
     dictCad['285']['PCV(4)'] = '0.00'
     # cotvol 287
     dictCad['287']['PCV(0)'] = '71.30'
     dictCad['287']['PCV(1)'] = '0.00'
     dictCad['287']['PCV(2)'] = '0.00'
     dictCad['287']['PCV(3)'] = '0.00'
     dictCad['287']['PCV(4)'] = '0.00'

     #Jusante I. Solteira
     dictCad['34']['Jusante'] = '44'
     #Jusante T. Irmaos
     dictCad['43']['Jusante'] = '45'
     #volmin I. Solteira
     dictCad['34']['Vol.min.(hm3)'] = '15563'
     # Def. de postos de vazao natural
     dictCad['119']['Posto'] = '300'
     dictCad['305']['Posto'] = '300'
#     dictCad['133']['Posto'] = '300'
     dictCad['118']['Posto'] = '300'
     dictCad['181']['Jusante'] = '129'
     dictCad['183']['Posto'] = '300'
     dictCad['131']['Posto'] = '300'
     dictCad['182']['Posto'] = '300'
     dictCad['184']['Posto'] = '300'
#     dictCad['175']['Posto'] = '300'
     dictCad['129']['Posto'] = '129'
#     dictCad['169']['Posto'] = '168'
     # Correções
     dictCad['127']['Posto'] = '129'
     dictCad['117']['Posto'] = '108'
     # Belo Monte
     dictCad['314']['Posto'] = '288'
     dictCad['288']['Posto'] = '300'
     # Jusena
     dictCad['125']['Jusante'] = '131'
     dictCad['117']['Jusante'] = '118'
     dictCad['118']['Jusante'] = '119'
     dictCad['172']['Jusante'] = '176'

     # Ficticios
     dictCad['172']['Jusante'] = '176'
     # [S. Quebrada] manda pra pqp
     dictCad['267']['Jusante'] = '275'

     dictCad['57']['Jusante'] = '0'
     dictCad['130']['Jusante'] = '0'

     # Alterando
     dictCad['34']['Jusante'] = '45'
     dictCad['43']['Jusante'] = '45'
     dictCad['290']['Jusante'] = '34'
     dictCad['312']['Jusante'] = '315'
     dictCad['148']['Jusante'] = '154'
#     dictCad['125']['Jusante'] = '0'
     dictCad['127']['Jusante'] = '0'

     dictCad['120']['Jusante'] = '123'
     dictCad['261']['Jusante'] = '0'
     dictCad['148']['Jusante'] = '0'
     dictCad['156']['Jusante'] = '0'
     dictCad['162']['Jusante'] = '0'
     # Forcando fio dagua
     dictCad['280']['Vol.Max.(hm3)'] = '139.0'
     dictCad['280']['Vol.min.(hm3)'] = '139.0'

     # Forcando fio dagua JIRAU
     dictCad['285']['Vol.Max.(hm3)'] = '2747.0'
     dictCad['285']['Vol.min.(hm3)'] = '2747.0'
     return dictCad


def Add_Ree_dictCad(dictCadastro,dictCadUsi):
     for cod_posto_cad in dictCadastro.keys():
          ree = dictCadastro[cod_posto_cad]['ree']
          for cod_uhe in dictCadUsi.keys():
               if cod_posto_cad == dictCadUsi[cod_uhe]['Posto']:
                    dictCadUsi[cod_uhe]['ree'] = ree
     # Ajusta itaipu
     dictCadUsi['66']['ree'] = '5'
     return dictCadUsi




def CalculaEARMmax(dictCad):

     for cod in dictCad.keys():
          prod = Produt_jusante(dictCad,cod)
          volmax = float(dictCad[cod]["Vol.Max.(hm3)"].replace(',','.'))
          volmin = float(dictCad[cod]["Vol.min.(hm3)"].replace(',','.'))
          volutil = volmax-volmin
          if cod in ['291']:
               volutil = 0.55*volutil

          dictCad[cod]['prod_acumm'] = prod
          dictCad[cod]['EARMmax'] = prod*volutil


     return dictCad

def Produt_jusante(dictCad,cod):
     prod = dictCad[cod]['produtib']

     cod_jusante = dictCad[cod]["Jusante"]
     if  cod_jusante == '0':
          pass
     else:
          prod+= Produt_jusante(dictCad,cod_jusante)


     return prod

def CalculaProdut(dictCad):
     for cod in dictCad.keys():
          volmax = float(dictCad[cod]["Vol.Max.(hm3)"].replace(',','.'))
          volmin = float(dictCad[cod]["Vol.min.(hm3)"].replace(',','.'))
          coefCV = []
          coefCV.append(float(dictCad[cod]["PCV(0)"].replace(',','.')))
          coefCV.append(float(dictCad[cod]["PCV(1)"].replace(',','.')))
          coefCV.append(float(dictCad[cod]["PCV(2)"].replace(',','.')))
          coefCV.append(float(dictCad[cod]["PCV(3)"].replace(',','.')))
          coefCV.append(float(dictCad[cod]["PCV(4)"].replace(',','.')))

          altura = 0.0
          for i in range(5):
               volutil = (volmax-volmin)*0.65+volmin
               if cod in['251','291']: # Tucurui
                    volutil = (volmax-volmin)*0.55+volmin

               altura +=Integral_coef(i,coefCV[i],volutil)


          cfuga = float(dictCad[cod]["Canal Fuga Medio(m)"].replace(',','.'))
          phid = float(dictCad[cod]["Valor Perdas"].replace(',','.'))
          prod = float(dictCad[cod]["Valor Perdas"].replace(',','.'))
          HEQ = altura - cfuga
          if dictCad[cod]["Tipo Perdas(1=%/2=M/3=K)"] =='1':
               HEQ = HEQ*(1-phid/100)
          else:
               HEQ = HEQ - phid
          prod = float(dictCad[cod]["Prod.Esp.(MW/m3/s/m)"].replace(',','.'))
          teif = float(dictCad[cod]["TEIF(%)"].replace(',','.'))
          ip = float(dictCad[cod]["IP(%)"].replace(',','.'))
          prod =prod

#          HEQ=HEQ - cfuga
          produt = prod*HEQ

          dictCad[cod]['produtib'] = produt

     return dictCad
def Integral_coef(ordem,coef,var):

#     ordem = ordem+1
     termo = coef
     for i in range(ordem):
          termo = termo*var
#     termo = termo/float(ordem)

     return termo

def Leitor_CadUsi(path):
     dictCad ={}
     with open(path, mode='r') as csv_file:
          csv_reader = csv.DictReader(csv_file,delimiter =';')

          for row in csv_reader:
               dictCad[row['CodUsina']] = row
               dictCad[row['CodUsina']]['Jusante'] = row['Jusante'].split('-')[0].strip()


     return dictCad



def Leitura_Cadastro(path):
     file = open(path,'r')
     arquivo = csv.reader(file,delimiter = ';')

     dictCadastro ={}
     listCSV = []
     for linha in arquivo:
          listCSV.append(linha)
     setSubm =set()
     setBacia =set()
     setRee =set()
     setBacia =set()
     for linha in listCSV[1:]:
          cod = linha[0]
          nome = linha[1]
          subm = linha[2]
          bacia = linha[3]
          ree = linha[4]
          try:
               prod = float(linha[5])
          except:
               #print linha[5]
               dictCadastro[cod] ={
                    'nome':nome,
                    'subm':subm,
                    'bacia':bacia,
                    'ree':ree,
                    'prod':prod,
                    }

          setSubm.add(subm.strip())
          setBacia.add(bacia.strip())
          setRee.add(ree.strip())
     return dictCadastro, list(setSubm), list(setBacia), sorted(list(setRee))


def Compila_table_UH(dictUH,pathSaidaUH):
     dictREE_Nome ={'1':'SUDESTE',
                    '10':'PARANA',
                    '12':'PRNPANEMA',
                    '6':'MADEIRA',
                    '5':'ITAIPU',
                    '7':'TPIRES',
                    '2':'SUL',
                    '11':'IGUACU',
                    '3':'NORDESTE',
                    '4':'NORTE',
                    '8':'BMONTE',
                    '9':'MAN-AP'}

     dictTableUH = {}
     listSubm =['SE','S','NE','N']
     listRee =['1','6','7','5','10','12','2','11','3','4','8','9']

     # Subm
     tableCSV = []
     tableCSV.append(['Subm','OFICIAL','EDP','delta'])
     for subm in listSubm:
          linha =[]
          UHMAX = dictUH['Oficial']['submMAX'][subm]
          UHOficial = dictUH['Oficial']['subm'][subm]
          UHEDP = dictUH['EDP']['subm'][subm]
          delta = round(UHOficial - UHEDP,1)

          UHOficial = str(UHOficial)+' ('+str(round(100*UHOficial/UHMAX,1))+'%)' 
          UHEDP = str(UHEDP)+' ('+str(round(100.0*UHEDP/UHMAX,1))+'%)'
          delta = str(delta)+' ('+str(round(100.0*delta/UHMAX,1))+'%)'

          linha.append(subm)
          linha.append(UHOficial)
          linha.append(UHEDP)
          linha.append(delta)
      
          tableCSV.append(linha)
     dictTableUH['subm'] = tableCSV

     # REE
     tableCSV = []
     tableCSV.append(['ree','OFICIAL','EDP','delta']) 
     for ree in listRee:
          linha =[]
          nome = dictREE_Nome[ree]
          linha.append(ree+' '+nome)
          UHMAX = dictUH['Oficial']['reeMAX'][ree]
          UHOficial = dictUH['Oficial']['ree'][ree]
          UHEDP = dictUH['EDP']['ree'][ree]
          delta = round(UHOficial - UHEDP,1)

          UHOficial = str(UHOficial)+' ('+str(round(100*UHOficial/UHMAX,1))+'%)' 
          UHEDP = str(UHEDP)+' ('+str(round(100.0*UHEDP/UHMAX,1))+'%)'
          delta = str(delta)+' ('+str(round(100.0*delta/UHMAX,1))+'%)'

          linha.append(UHOficial)
          linha.append(UHEDP)
          linha.append(delta)
      
          tableCSV.append(linha)
     dictTableUH['ree'] = tableCSV

     # Escreve log UH
     EscreveLogUH(dictTableUH,pathSaidaUH)

     return dictTableUH
     
     
def EscreveLogUH(dictTableUH,path):
     listReg = ['subm','ree']

     out = open(path, 'w')
     for i in range(3):
          if i ==0:
               deck = 'CCEE'
          if i ==1:
               deck = 'EDP'
          if i ==2:
               deck = 'delta'
          for regiao in listReg:
               for linha in dictTableUH[regiao][1:]:
                    cod = linha[0][:2].strip()
                    valor = linha[i+1].split('(')[0]
                    pct = linha[i+1].split('(')[1][:-1]
                    out.write('%s;' % deck)
                    out.write('%s;' % regiao)
                    out.write('%s;' % cod)
                    out.write('%s;' % valor)
                    out.write('%s;' % pct)
                    out.write('\n') 
               time.sleep(0.0005)

     out.close()
     #print( 'Escrito ' + path + '  com sucesso')
     return path


#if __name__ == '__main__':
#    main()