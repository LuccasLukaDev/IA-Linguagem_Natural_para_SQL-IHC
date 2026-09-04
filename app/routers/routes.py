from fastapi import APIRouter

from app.schemas.sqlQuery import SQLQuery
from app.services.sql_service import executar_sql
from app.services.listar_produto_service import listar_produtos


router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"]
)


@router.post("/perguntar")
def perguntar(sql_query: SQLQuery):

    resultado = executar_sql(sql_query.sql_query)

    return {
        "resultado": resultado
    }


@router.get("/listar")
def listar():

    lista_produtos = listar_produtos()

    return {
        "resultado": lista_produtos
    }