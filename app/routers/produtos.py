from fastapi import APIRouter

from app.schemas.pergunta import Pergunta
from app.services.sql_service import generate


router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"]
)


@router.post("/perguntar")
def perguntar(pergunta: Pergunta):

    resultado = generate(pergunta.question)

    return {
        "resultado": resultado
    }