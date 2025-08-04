import datetime
from dateutil.relativedelta import relativedelta

def getLastWeekday(data, weekday):
    """Retorna a última data do dia da semana especificado antes ou igual à data fornecida."""
    while data.weekday() != weekday:
        data -= datetime.timedelta(days=1)
    return data

def diffWeek(data1, data2):
    """Calcula a diferença em semanas entre duas datas."""
    return abs((data1 - data2).days) // 7

def countElecWeek(data1, data2):
    """Conta o número de semanas elétricas entre duas datas."""
    return diffWeek(data1, data2)

def getPesoSemanas(primeiroDiaMes):
    """Calcula o peso das semanas a partir da data de início."""
    vetor_pesos = []
    vetor_pesos.append((primeiroDiaMes + datetime.timedelta(days=6)).day)
    mes_pmo = (primeiroDiaMes + datetime.timedelta(days=6)).month
    j = 1
    while (primeiroDiaMes + datetime.timedelta(days=7 * j)).month == mes_pmo:
        vetor_pesos.append(7)
        j += 1
    vetor_pesos.pop(-1)
    vetor_pesos.append(8 - (primeiroDiaMes + datetime.timedelta(days=7 * j)).day)

    while len(vetor_pesos) < 6:
        vetor_pesos.append(0)
    return vetor_pesos

class ElecData:
    """Classe para manipular dados elétricos baseados em datas."""
    
    def __init__(self, data):
        
        if isinstance(data, datetime.datetime):
            data = data.date()
            
        elif not isinstance(data, datetime.date):
            raise ValueError("A data deve ser uma instância de datetime.date.")
        
        self.data = data
        self.primeiroDiaMes = getLastWeekday(datetime.date(data.year, data.month, 1), 5)
        primeiroDiaMesProximoMes = datetime.date(data.year, data.month, 1) + relativedelta(months=1)
        self.primeiroDiaProximoMes = getLastWeekday(primeiroDiaMesProximoMes, 5)
        self.ultimoDiaMes = self.primeiroDiaProximoMes - datetime.timedelta(days=1)

        if data > self.primeiroDiaMes:
            data_aux = self.data + datetime.timedelta(days=6)
            self.primeiroDiaAno = getLastWeekday(datetime.date(data_aux.year, 1, 1), 5)
            self.ultimoDiaAno = getLastWeekday(datetime.date(data_aux.year, 12, 31), 4)
            self.primeiroDiaMes = getLastWeekday(datetime.date(data_aux.year, data_aux.month, 1), 5)
        else:
            self.primeiroDiaAno = getLastWeekday(datetime.date(self.data.year, 1, 1), 5)
            self.ultimoDiaAno = getLastWeekday(datetime.date(self.data.year, 12, 31), 4)

        self.atualRevisao = countElecWeek(self.primeiroDiaMes, data)
        self.inicioSemana = self.primeiroDiaMes + datetime.timedelta(days=7 * self.atualRevisao)
        self.numSemanas = countElecWeek(self.primeiroDiaAno, getLastWeekday(self.data, 5)) + 1
        self.numSemanasPrimeiroDiaMes = countElecWeek(self.primeiroDiaAno, self.primeiroDiaMes) + 1
        self.numSemanasAno = countElecWeek(self.primeiroDiaAno, self.ultimoDiaAno + datetime.timedelta(days=1))
        self.mesReferente = (self.primeiroDiaMes + datetime.timedelta(days=6)).month
        self.anoReferente = self.ultimoDiaAno.year
        self.mesEletrico = datetime.datetime(self.anoReferente, self.mesReferente, 1)

    def getPesoSemanas(self):
        """Retorna o peso das semanas do mês elétrico."""
        return getPesoSemanas(self.primeiroDiaMes)

if __name__ == '__main__':
    dt = datetime.datetime.now().date()
    while dt.weekday() != 5:
        dt -= datetime.timedelta(days=1)
    
    anoOperacional = ElecData(dt)

    print('primeiroDiaAno', anoOperacional.primeiroDiaAno)
    print('ultimoDiaAno', anoOperacional.ultimoDiaAno)
    print('primeiroDiaMes', anoOperacional.primeiroDiaMes)
    print('ultimoDiaMes', anoOperacional.ultimoDiaMes)
    print('inicioSemana', anoOperacional.inicioSemana)
    print('atualRevisao', anoOperacional.atualRevisao)
    print('numSemanas', anoOperacional.numSemanas)
    print('numSemanasAno', anoOperacional.numSemanasAno)
    print('mesReferente', anoOperacional.mesReferente)
    print('numSemanasPrimeiroDiaMes', anoOperacional.numSemanasPrimeiroDiaMes)
