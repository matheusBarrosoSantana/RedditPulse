import asyncpraw
import os
from dotenv import load_dotenv
load_dotenv()

async def buscar_posts_reddit(tema, quantidade=100):
    CLIENT_ID = os.getenv("client_id_reddit")
    CLIENT_SECRET = os.getenv("client_secret_reddit")
    USER_AGENT = os.getenv("user_agent_reddit")

    reddit = asyncpraw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=USER_AGENT
    )

    posts = []

    # Obter o subreddit de forma assíncrona
    subreddit = await reddit.subreddit("all")  # await necessário

    # Agora podemos iterar pelos posts
    async for submission in subreddit.search(tema, limit=quantidade):
        posts.append(submission.title)

    await reddit.close()
    return posts
