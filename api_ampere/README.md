## Descrição

Este projeto permite listar e baixar estudos disponíveis da plataforma Ampere, incluindo previsões meteorológicas (GFS) e dados de acompanhamento energético.

## Requisitos

- Python 3.12+
- Bibliotecas listadas em `requirements.txt`

## Instalação

1. Clone ou baixe o projeto
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

Execute o script principal:
```bash
python main.py
```

O script irá:
- Consultar estudos disponíveis baseados na data atual
- Baixar arquivo ZIP com os dados do modelo GFS
- Salvar o arquivo na pasta Downloads

## Estrutura do Projeto

- `main.py` - Script principal
- `ampere/` - Módulo principal com funções de API
- `requirements.txt` - Dependências do projeto
- `arquivos/` - Dados e arquivos baixados

## Funcionalidades

- ✅ Listar estudos disponíveis
- ✅ Filtrar por modelo (GFS), data e acompanhamento  
- ✅ Download automático de arquivos ZIP
- ✅ Processamento de dados meteorológicos