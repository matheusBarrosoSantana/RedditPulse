import numpy as np
from gensim.models import KeyedVectors
import gensim.downloader as api
from itertools import combinations

# Carrega embeddings GloVe (pode trocar para fasttext-wiki-news-subwords-300, word2vec-google-news-300 etc.)
modelo_embedding = api.load("glove-wiki-gigaword-100")

def similaridade_cosseno(v1, v2):
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def calcular_ewetc(lista_topicos):
    resultados = []
    for topico in lista_topicos:
        palavras_validas = [p for p in topico if p in modelo_embedding.key_to_index]
        if len(palavras_validas) < 2:
            resultados.append(0.0)
            continue
        pares = combinations(palavras_validas, 2)
        similaridades = [similaridade_cosseno(modelo_embedding[p1], modelo_embedding[p2]) for p1, p2 in pares]
        resultados.append(np.mean(similaridades))
    return resultados
