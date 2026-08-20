import sqlite3

import dspy

from app.database.connection import get_connection


class TextToSQL(dspy.Signature):
    """
    Gera uma consulta SQL a partir de uma pergunta em linguagem natural.
    """

    dbschema = dspy.InputField(
        desc="Schema do banco de dados"
    )

    question = dspy.InputField(
        desc="Pergunta em linguagem natural"
    )

    sql_query = dspy.OutputField(
        desc="Consulta SQL válida para SQLite"
    )


class ReliableSQLGenerator(dspy.Module):

    def __init__(self):
        super().__init__()

        self.generate_sql = dspy.ChainOfThought(TextToSQL)

    def forward(self, schema, question):
        return self.generate_sql(
            dbschema=schema,
            question=question
        )


lm = dspy.LM(
    "openai/gemma-4-E2B-it-IQ4_XS",
    api_base="http://localhost:1337/v1",
    api_key="not-needed"
)

dspy.configure(lm=lm)


def validar_sql(sql, schema):

    try:
        conn = sqlite3.connect(":memory:")

        conn.executescript(schema)

        conn.execute(sql)

        conn.close()

        return True, None

    except Exception as e:
        return False, str(e)


def generate(question: str):

    schema = """
    CREATE TABLE produtos (
        id INTEGER PRIMARY KEY,
        nome VARCHAR(50),
        departamento VARCHAR(50),
        fabricante TEXT,
        data_venc TEXT,
        data_fabri TEXT,
        cod_barra TEXT,
        origem TEXT,
        quantidade INTEGER
    );
    """

    try:

        generator = ReliableSQLGenerator()

        prediction = generator(
            schema=schema,
            question=question
        )

        sql = prediction.sql_query.strip()

        if not sql.upper().startswith("SELECT"):
            raise ValueError("Apenas consultas SELECT são permitidas.")

        valido, erro = validar_sql(sql, schema)

        if not valido:
            raise ValueError(f"SQL inválido: {erro}")

        # Se passou pelas validações, executa no banco real
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