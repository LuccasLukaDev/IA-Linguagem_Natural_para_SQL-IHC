from fastapi import APIRouter

from app.schemas.pergunta import Pergunta
from app.services.sql_service import generate
from app.services.listar_produto_service import listar_produtos


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


@router.get("/listar")
def listar():

    listaProdutos = listar_produtos()

    return {
        "resultado" : listaProdutos
    }