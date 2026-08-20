from pydantic import BaseModel


class Produto(BaseModel):
    id: int
    nome: str
    departamento: str
    fabricante: str
    data_venc: str
    data_fabri: str
    cod_barra: str
    origem: str
    quantidade: int