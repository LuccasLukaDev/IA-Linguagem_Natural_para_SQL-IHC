from pydantic import BaseModel


class Pergunta(BaseModel):
    question: str