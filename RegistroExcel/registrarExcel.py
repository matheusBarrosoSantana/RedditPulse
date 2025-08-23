import pandas as pd
import os
from datetime import datetime

def registrar_excel( modelo, tema, posts, topicos, coerencia, resumo, arquivo_excel='./RegistroExcel/resultados.xlsx'):
    """
    Registra os resultados de análise de tópicos em um arquivo Excel.
    
    arquivo_excel: caminho do arquivo (str)
    modelo: nome do modelo (ex: "LDA", "BERTopic")
    tema: tema pesquisado (str)
    posts: lista de posts (list[str])
    topicos: lista de tópicos extraídos (list[str])
    coerencia: valor numérico da métrica de qualidade (float)
    """
    data_hora_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    dados = {
        "modelo": [modelo],
        "tema": [tema],
        "posts": [" | ".join(posts)],
        "topicos": [" | ".join(topicos)],
        "coerencia": [coerencia],
        "resumo": [resumo],
        "data_hora": [data_hora_atual]
    }

    df_novo = pd.DataFrame(dados)

    if os.path.exists(arquivo_excel):
        df_antigo = pd.read_excel(arquivo_excel)
        df_final = pd.concat([df_antigo, df_novo], ignore_index=True)
    else:
        df_final = df_novo

    df_final.to_excel(arquivo_excel, index=False)
