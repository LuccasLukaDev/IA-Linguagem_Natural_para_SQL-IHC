from fastapi import FastAPI

from app.database.connection import create_db
from app.routers import produtos


app = FastAPI(
    title="IA Linguagem Natural para SQL"
)


create_db()

app.include_router(produtos.router)