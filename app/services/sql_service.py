import sqlite3

from app.server.bd import get_connection
from app.config.database import DB_SCHEMA


def validar_sql(sql, schema):

    try:
        conn = sqlite3.connect(":memory:")

        conn.executescript(schema)

        conn.execute(sql)

        conn.close()

        return True, None

    except Exception as e:
        return False, str(e)


def executar_sql(sql_query: str):

    try:
        sql = sql_query.strip()

        if not sql.upper().startswith("SELECT"):
            raise ValueError("Apenas consultas SELECT são permitidas.")

        valido, erro = validar_sql(sql, DB_SCHEMA)

        if not valido:
            raise ValueError(f"SQL inválido: {erro}")

        conn = get_connection()

        try:
            resultado = conn.execute(sql).fetchall()

            return resultado

        finally:
            conn.close()

    except Exception as e:
        return {
            "erro": str(e)
        }