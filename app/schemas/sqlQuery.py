from pydantic import BaseModel


class SQLQuery(BaseModel):
    sql_query: str