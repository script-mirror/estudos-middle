import pandas as pd

def read_patamar_carga(file_path):
    current_submarket = None
    carga_data = []
    capture_data = False
    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()

            # Verifica se a linha contém apenas um número (indicando submercado)
            if line.isdigit() and capture_data:
                current_submarket = int(line)
                continue

            # Verifica se a linha indica o início do bloco CARGA(P.U.DEMANDA MED.)
            if "CARGA(P.U.DEMANDA MED.)" in line:
                capture_data = True
                continue

            # Para de capturar se encontrar a linha "9999"
            if "SUBSISTEMA" in line:
                capture_data = False
                continue
            # Captura os dados se estiver no bloco correto e no submercado atual
            if capture_data and current_submarket is not None:
                values = line.split()
                if len(values) == 13:  # Espera 1 ano + 12 valores mensais
                    patamar = 1
                    year = int(values[0])
                    monthly_data = [float(v) for v in values[1:]]
                    # Cria um registro para cada mês
                    for i, value in enumerate(monthly_data):
                        carga_data.append({
                            'sub': current_submarket,
                            'ano': year,
                            'mes': months[i],
                            'patamar':patamar,
                            'carga_pu': value
                        })
                elif len(values) == 12:
                    patamar += 1
                    monthly_data = [float(v) for v in values]
                    for i, value in enumerate(monthly_data):
                        carga_data.append({
                        'sub': current_submarket,
                        'ano': year,
                        'mes': months[i],
                        'patamar':patamar,
                        'carga_pu': value
                    })
                
    # Cria o DataFrame
    df = pd.DataFrame(carga_data)
    df['sub'] = df['sub'].astype(int)
    df['ano']        = df['ano'].astype(int)
    df['mes']        = df['mes'].astype(int)
    return df


def read_patamar_pq(file_path):
    current_submarket = None
    current_fonte     = None
    carga_data = []
    capture_data = False
    months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()

            # Verifica se a linha contém apenas um número (indicando submercado)
            if len(line.split()) == 2 and capture_data:
                current_submarket = int(line.split()[0])
                current_fonte     = int(line.split()[1])
                continue

            # Verifica se a linha indica o início do bloco CARGA(P.U.DEMANDA MED.)
            if "USINAS NAO SIMULADAS" in line:
                capture_data = True
                continue

            # Para de capturar se encontrar a linha "9999"
            if "SUBSISTEMA" in line:
                capture_data = False
                continue
            # Captura os dados se estiver no bloco correto e no submercado atual
            if capture_data and current_submarket is not None:
                values = line.split()
                if len(values) == 13:  # Espera 1 ano + 12 valores mensais
                    patamar = 1
                    year = int(values[0])
                    monthly_data = [float(v) for v in values[1:]]
                    # Cria um registro para cada mês
                    for i, value in enumerate(monthly_data):
                        carga_data.append({
                            'sub': current_submarket,
                            'tipo': current_fonte,
                            'ano': year,
                            'mes': months[i],
                            'patamar':patamar,
                            'carga_pu': value
                        })
                elif len(values) == 12:
                    patamar += 1
                    monthly_data = [float(v) for v in values]
                    for i, value in enumerate(monthly_data):
                        carga_data.append({
                        'sub': current_submarket,
                        'tipo': current_fonte,
                        'ano': year,
                        'mes': months[i],
                        'patamar':patamar,
                        'carga_pu': value
                    })
                
    # Cria o DataFrame
    df = pd.DataFrame(carga_data)
    df['sub'] = df['sub'].astype(int)
    df['ano']        = df['ano'].astype(int)
    df['mes']        = df['mes'].astype(int)
    return df


# Exemplo de uso
#file_path = "input/patamar/patamar.dat"
#df_carga = read_patamar_pq(file_path)

# Exibe as primeiras linhas do DataFrame
#print(df_carga.head(20))

# Opcional: Salva o DataFrame em um arquivo CSV
#df_carga.to_csv("carga_pu.csv", index=False)
