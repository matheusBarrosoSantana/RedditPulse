# analisarIA.py

import os
from CalculoEWETC.ewetc import calcular_ewetc
import dotenv
import re
import requests
import json
from datetime import datetime
from RedditApi.redditbot import buscar_posts_reddit
from RegistroExcel.registrarExcel import registrar_excel
from RespostaEstruturada.structureResponse import gerar_pesquisa_ia
from RegistrarTelegram.envioMensagem import enviar_resposta
import numpy as np
from gensim.models.coherencemodel import CoherenceModel
from gensim.corpora.dictionary import Dictionary

dotenv.load_dotenv()

def preprocess(texto):
    return re.findall(r'\b\w+\b', texto.lower())

async def analisar_topicos_ia(tema, quantidade, context):
    posts = await buscar_posts_reddit(tema, quantidade=quantidade)
    if not posts:
        return "Nenhum post encontrado para análise."

    # Prompt para IA
    prompt = f"""
Você é um assistente que identifica os tópicos mais importantes em um conjunto de textos.
Aqui estão os textos coletados do Reddit sobre o tema '{tema}':
{chr(10).join(posts)}

Liste os topicos que resumam os assuntos mais relevantes.

Retorne apenas a lista de tópicos.
"""
    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    }
    headers = {
        "Authorization": f'Bearer {os.getenv("OPENROUTER_API_KEY")}',
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(payload)
    )
    if response.status_code != 200:
        return f"Erro na requisição: {response.status_code} - {response.text}"

    data = response.json()
    try:
        texto_ia = data['choices'][0]['message']['content']
    except:
        return "Não foi possível interpretar a resposta da IA."

    # Converter em lista de tópicos
    if "\n" in texto_ia:
        topicos_extraidos = [t.strip() for t in texto_ia.split("\n") if t.strip()]
    else:
        topicos_extraidos = [t.strip() for t in texto_ia.split(",") if t.strip()]

    # Tokenizar posts e tópicos


    # Garantir que cada tópico seja uma lista de tokens válida
    topicos_tokenizados = []
    for t in topicos_extraidos:
        tokens = preprocess(t)
        if tokens:  # ignora tópicos vazios
            topicos_tokenizados.append(tokens)

    # Coerência
    # if topicos_tokenizados:
    #     cm = CoherenceModel(
    #         topics=topicos_tokenizados,
    #         texts=textos_tokenizados,
    #         dictionary=dicionario,
    #         coherence='c_v'
    #     )
    #     coerencia_valor = cm.get_coherence()
    # else:
    ewetc_scores = calcular_ewetc(topicos_extraidos)
    coerencia_valor = np.mean(ewetc_scores)
    print("Coerência (c_v):", coerencia_valor)

    # Resumo via IA
    resumo = await gerar_pesquisa_ia("\n".join(topicos_extraidos))
    if not resumo:
        resumo = "Não foi possível gerar o resumo da IA."

    # Registrar no Excel e enviar log
    registrar_excel("IA", tema, posts, topicos_extraidos, coerencia_valor, resumo)
    await enviar_resposta(tema, 'IA', resumo, topicos_extraidos, coerencia_valor, context)

    return resumo
