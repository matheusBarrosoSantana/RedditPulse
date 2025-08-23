from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters
import os
from dotenv import load_dotenv
from Analises.analisarBertopic import analisar_topicos_bertopic
from Analises.analisarIA import analisar_topicos_ia
from Analises.AnaliseLDA.analisarLDA import analisar_topicos_lda

def main(): 
    load_dotenv()  # Carrega o .env


    estado_usuarios = {}
    quantidade_posts = 100
    # Função para iniciar o bot e enviar uma mensagem de boas-vindas
    # Função /start
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Defina a quantidade de posts que deseja buscar
        user_id_teste = int(os.getenv('USER_TELEGRAM_ID', 0))  # garante que seja int
        chat_id = update.message.chat_id

        if chat_id == user_id_teste:
            await update.message.reply_text(
                "⚠️ Aqui é só um *chat de testes*...\n\n"
                "Então não inventa moda, beleza? 😅\n"
                "Use direitinho ou o bot pode te dar *404 na amizade*! 🤖🚫",
                parse_mode="Markdown"
            )
            return
        print("Chat ID:", update.message.chat_id)
        texto = (
            "👋 Olá! Eu sou o *Reddit Insight Bot*.\n\n"
            "Escolha o modelo que deseja usar para pesquisar um tema:"
        )

        botoes = [
            [InlineKeyboardButton("📊 LDA", callback_data="modelo_lda")],
            [InlineKeyboardButton("🔎 BERTopic", callback_data="modelo_bertopic")],
            [InlineKeyboardButton("🤖 IA", callback_data="modelo_ia")]
        ]

        teclado = InlineKeyboardMarkup(botoes)

        await update.message.reply_text(
            texto,
            parse_mode="Markdown",
            reply_markup=teclado
        )

    # Clique nos botões iniciais
    async def tratar_clique(update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()

        usuario_id = query.from_user.id

        if query.data.startswith("modelo_"):
            modelo = query.data.split("_")[1]
            estado_usuarios[usuario_id] = {"estado": "aguardando_tema", "modelo": modelo}
            await query.message.reply_text(f"Digite o tema que deseja pesquisar usando *{modelo.upper()}*:", parse_mode="Markdown")

        elif query.data == "continuar":
            modelo = estado_usuarios[usuario_id]["modelo"]
            estado_usuarios[usuario_id]["estado"] = "aguardando_tema"
            await query.message.reply_text(f"Digite o próximo tema para pesquisar usando *{modelo.upper()}*:", parse_mode="Markdown")

        elif query.data == "encerrar":
            estado_usuarios.pop(usuario_id, None)
            await query.message.reply_text("👍 Obrigado pela interação! Até logo 👋")

    # Receber tema digitado
    async def receber_tema(update: Update, context: ContextTypes.DEFAULT_TYPE):
        usuario_id = update.message.from_user.id
        dados = estado_usuarios.get(usuario_id)

        if not dados or dados["estado"] != "aguardando_tema":
            return

        tema = update.message.text
        modelo = dados["modelo"]

        # Chama a função correspondente ao modelo
        if modelo == "lda":
            resposta = await processar_com_lda(tema, context)
        elif modelo == "bertopic":
            resposta = await processar_com_bertopic(tema, context)
        elif modelo == "ia":
            resposta = await processar_com_ia(tema, context)
        else:
            resposta = "Erro: modelo desconhecido."

        await update.message.reply_text(resposta, parse_mode="Markdown")

        # Pergunta se quer continuar
        botoes = [
            [
                InlineKeyboardButton("🔄 Continuar com mesmo modelo", callback_data="continuar"),
                InlineKeyboardButton("❌ Encerrar", callback_data="encerrar")
            ]
        ]
        teclado = InlineKeyboardMarkup(botoes)
        await update.message.reply_text("Deseja pesquisar outro tema com o mesmo modelo?", reply_markup=teclado)

    # Funções simuladas de processamento
    async def processar_com_lda(tema, context):
        resposta = await analisar_topicos_lda(tema, quantidade=quantidade_posts, context=context)  # Chama a função assíncrona
        return resposta  # Exemplo de uso da função de busca no Reddit

    async def processar_com_bertopic(tema, context):
        resposta = await analisar_topicos_bertopic(tema, quantidade=quantidade_posts, context=context)  # await aqui também
        return resposta # Exemplo de uso da função de análise BERTopic

    async def processar_com_ia(tema, context):
        resposta = await analisar_topicos_ia(tema, quantidade=quantidade_posts, context=context)  # await aqui também
        return resposta # Exemplo de uso da função de análise BERTopic




    # Cria a aplicação do bot
    Token = os.getenv("telegram_token")    
    app = ApplicationBuilder().token(Token).build()

    # Adiciona os handlers para os comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(tratar_clique))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receber_tema))
    # Inicia o bot
    print("Bot rodando...")
    app.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())  # ou a função que inicia seu bot