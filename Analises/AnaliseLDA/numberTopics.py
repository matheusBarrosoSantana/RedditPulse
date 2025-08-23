import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

async def sugerir_numero_topicos(posts):
    """
    Recebe uma lista de posts e usa a IA para sugerir o número ideal de tópicos para LDA.
    """
    # Monta o texto para a IA
    prompt = (
        "Você é um assistente que ajuda a determinar o número ideal de tópicos "
        "para análise de texto usando LDA. "
        "Receba uma lista de posts e sugira quantos tópicos seriam mais relevantes, "
        "com base na diversidade de assuntos abordados. "
        "Retorne apenas o número inteiro.\n\n"
    )

    for i, post in enumerate(posts):  # usa só os 20 primeiros posts para não ficar gigante
        prompt += f"Post {i}: {post}\n"

    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt}
                ]
            }
        ]
    }

    headers = {
        "Authorization": f'Bearer {os.getenv("OPENROUTER_API_KEY")}',  # Use sua chave de API aqui
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code == 200:
        data = response.json()
        try:
            resposta = data['choices'][0]['message']['content']
            print(f"Resposta da IA: {resposta}")  # Debug: mostra a resposta completa da IA
            # Tenta extrair o número inteiro da resposta
            for token in resposta.split():
                if token.isdigit():
                    return int(token)
            return 5  # padrão se não conseguir extrair
        except:
            return 5
    else:
        return 5
