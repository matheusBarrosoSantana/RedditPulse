import requests
import json
import os
from dotenv import load_dotenv
load_dotenv()

async def gerar_pesquisa_ia(topicos):
    """
    Recebe uma lista de tópicos (cada tópico é uma string de palavras-chave)
    e retorna uma mensagem estruturada pronta para enviar ao usuário como pesquisa de opinião.
    
    topicos = [
        "learning, machine, deep, IA, importantes",
        "futebol, inteligência, artificial, emocionante, competitivo"
    ]
    """
    # Monta o texto que será enviado para a IA
    prompt = (
        "Você é um assistente que cria um resumo informativo baseado em tópicos extraídos de postagens. "
        "Liste ao final os topicos, de forma entendivel.\n\n"
        "Para cada tópico, explique brevemente os assuntos que estão sendo discutidos. "
        "Conecte os tópicos de forma coerente e produza um texto claro e conciso, fácil de entender pelo usuário. "
        "Utilize só os topicos fornecidos como insumo. "  
        'Atenção: nao envie caracteres que possam quebrar o Markdown, como "*", "_", etc.\n\n'
        'Cuidado: a resposta não pode ser muito longa, para não quebrar, pois vai ser enviada via telegram ao usuario. '
    )
    prompt += topicos

    prompt += "\nPor favor, gere um resumo baseado nos tópicos acima."

    print(f"Prompt enviado para a IA: {prompt}")  # Debug: mostra o prompt enviado

    payload = {
        "model": "deepseek/deepseek-r1:free",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
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
        print(f"Resposta da IA: {data}")  # Debug: mostra a resposta completa da IA
        # A resposta da IA geralmente vem em data['choices'][0]['message']['content'][0]['text']
        # Dependendo do modelo, você precisa inspecionar o JSON retornado
        try:
            texto_ia = data['choices'][0]['message']['content']
            return texto_ia
        except:
            return "Não foi possível interpretar a resposta da IA."
    else:
        return f"Erro na requisição: {response.status_code} - {response.text}"
