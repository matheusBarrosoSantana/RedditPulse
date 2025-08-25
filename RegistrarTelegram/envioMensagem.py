from datetime import datetime
import re
import os
from dotenv import load_dotenv
load_dotenv()

def escape_markdown(texto):
    if not texto:
        return ""
    # Inclui todos os caracteres reservados do MarkdownV2
    escape_chars = r"_*[]()~`>#+-=|{}.!?"
    return re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", texto)

async def enviar_resposta(tema, modelo, resposta, topicos, coerencia, context):
    """
    Envia a resposta para o usuário solicitante e uma cópia detalhada para você.
    """
    MEU_USER_ID = int(os.getenv('USER_TELEGRAM_ID'))  # seu ID numérico do Telegram

    # Junta os tópicos em uma string antes de passar para a f-string
    topicos_texto ='-'
    topicos_texto += '\n-'.join(topicos)
    topicos_escapados = escape_markdown(topicos_texto)

    mensagem_log = (
        f"📌 Tema: {escape_markdown(tema)}\n\n"
        f"🛠 Método: {escape_markdown(modelo.upper())}\n\n"
        f"⏰ Data/Hora: {escape_markdown(datetime.now().strftime('%d-%m-%Y %H:%M:%S'))}\n\n"
        f"📂 Tópicos:\n {topicos_escapados}\n\n"
        f"📊 Coerência: {escape_markdown(str(coerencia))}\n\n"
        f"💬 Resposta:\n {escape_markdown(resposta)}\n\n"
    )

    # Envia o log para você
    await context.bot.send_message(
        chat_id=MEU_USER_ID,
        text=mensagem_log,
        parse_mode="MarkdownV2"
    )
