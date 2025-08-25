from Analises.AnaliseLDA.numberTopics import sugerir_numero_topicos
from CalculoEWETC.ewetc import calcular_ewetc
from RedditApi.redditbot import buscar_posts_reddit
from RegistrarTelegram.envioMensagem import enviar_resposta
from RegistroExcel.registrarExcel import registrar_excel
from RespostaEstruturada.structureResponse import gerar_pesquisa_ia  # função assíncrona
from gensim import corpora, models
from gensim.models.coherencemodel import CoherenceModel
from nltk.corpus import stopwords
import re
import numpy as np
import asyncio

# ✅ Garante que stopwords estão disponíveis só uma vez
import nltk
from nltk.data import find
try:
    find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")


async def analisar_topicos_lda(tema, quantidade, context,n_topicos=None):
    """
    Analisa os tópicos mais relevantes de posts do Reddit usando LDA.
    Se n_topicos não for fornecido, a IA sugere o número ideal.
    """
    posts = await buscar_posts_reddit(tema, quantidade=quantidade)
    if not posts:
        return "Nenhum post fornecido para análise."

    # Se n_topicos não foi definido, usamos a IA para sugerir
    if n_topicos is None:
        n_topicos = await sugerir_numero_topicos(posts)  # retorna int

    # Pré-processamento dos textos
    stop_words = set(stopwords.words("portuguese"))
    # print(stop_words)
    textos_processados = []
    for post in posts:
        post_limpo = re.sub(r"[^a-zA-ZÀ-ÿ\s]", "", post)
        tokens = post_limpo.lower().split()
        tokens_filtrados = [t for t in tokens if t not in stop_words and len(t) > 1]
        textos_processados.append(tokens_filtrados)
    print('passos')
    # Cria dicionário e corpus
    dicionario = corpora.Dictionary(textos_processados)
    corpus = [dicionario.doc2bow(texto) for texto in textos_processados]

    # Treina o modelo LDA
    lda_modelo = models.LdaModel(
        corpus, num_topics=n_topicos, id2word=dicionario, passes=10
    )

    # # ✅ Corrigido: estava usando "tokens" (variável inexistente)
    # coerencia_modelo = CoherenceModel(
    #     model=lda_modelo, texts=textos_processados, dictionary=dicionario, coherence="c_v"
    # )
    # coerencia_valor = coerencia_modelo.get_coherence()


    # Extrai tópicos
    topicos_extraidos = []
    for i in range(n_topicos):
        palavras = lda_modelo.show_topic(i)
        palavras_chave = ", ".join([palavra for palavra, _ in palavras])
        topicos_extraidos.append(palavras_chave)

    ewetc_scores = calcular_ewetc(topicos_extraidos)
    coerencia_valor = np.mean(ewetc_scores)
    print("Coerência (c_v):", coerencia_valor)
    # Gera resumo com IA
    resumo = await gerar_pesquisa_ia("\n".join(topicos_extraidos))

    # Registra no Excel
    registrar_excel("LDA", tema, posts, topicos_extraidos, coerencia_valor, resumo)
    await enviar_resposta(tema, 'LDA', resumo, topicos_extraidos, coerencia_valor, context)

    if not resumo:
        return "Não foi possível gerar o resumo da IA."

    return resumo
