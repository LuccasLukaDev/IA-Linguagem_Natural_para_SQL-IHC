from fastapi import FastAPI
from threading import Thread

from app.server.bd import create_db
from app.routers.routes import router
from app.Bot.telegram_bot import bot


app = FastAPI(
    title="IA Linguagem Natural para SQL"
)


create_db()

app.include_router(router)


def iniciar_bot():
    bot.infinity_polling()


Thread(
    target=iniciar_bot,
    daemon=True
).start()