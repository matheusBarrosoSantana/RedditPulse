from CalculoEWETC.ewetc import calcular_ewetc
from bertopic import BERTopic
from RedditApi.redditbot import buscar_posts_reddit
from RegistrarTelegram.envioMensagem import enviar_resposta
from RegistroExcel.registrarExcel import registrar_excel
from RespostaEstruturada.structureResponse import gerar_pesquisa_ia  # async function
from gensim.models.coherencemodel import CoherenceModel
from gensim.corpora.dictionary import Dictionary
import re
import numpy as np

def preprocess(texto):
    return re.findall(r'\b\w+\b', texto.lower())





async def analisar_topicos_bertopic(tema, quantidade,context):
    posts = await buscar_posts_reddit(tema, quantidade=quantidade)
    if not posts:
        return "Nenhum post fornecido para análise."

    modelo = BERTopic(language="multilingual")
    topicos, _ = modelo.fit_transform(posts)

    frequencia = modelo.get_topic_info()
    saida = ""
    termos_todos_topicos = []
    topicos =[]

    for i, row in frequencia.iterrows():
        if row['Topic'] == -1:
            continue
        termos = [palavra for palavra, _ in modelo.get_topic(row['Topic'])]
        termos_todos_topicos.append(termos)
        palavras_chave = ", ".join(termos)
        topicos.append(palavras_chave)
        saida += f"Tópico {row['Topic']}: {palavras_chave}\n"

    ewetc_scores = calcular_ewetc(topicos)
    coerencia_valor = np.mean(ewetc_scores)
    print("Coerência (c_v):", coerencia_valor)

    # cm = CoherenceModel(
    #     topics=termos_todos_topicos,
    #     texts=textos_tokenizados,
    #     dictionary=dicionario,
    #     coherence='c_v'
    # )
  

    resposta = await gerar_pesquisa_ia(saida)


    registrar_excel(
        modelo="BERTOPIC",
        tema=tema,
        posts=posts,
        topicos=topicos,
        coerencia=coerencia_valor,
        resumo=resposta
    )
    await enviar_resposta(tema, 'BERTOPIC', resposta, topicos, coerencia_valor, context)

    if not resposta:
        return "Não foi possível gerar a pesquisa de opinião."

    return resposta
