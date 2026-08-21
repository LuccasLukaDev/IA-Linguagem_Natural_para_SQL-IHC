import sqlite3

import dspy

from app.server.bd import get_connection

from app.config.database import DB_SCHEMA

class TextToSQL(dspy.Signature):
    """
    Gera uma consulta SQL a partir de uma pergunta em linguagem natural.

    Antes de gerar o SQL, interprete a intenção do usuário.
    Considere possíveis erros de digitação, ortografia e pequenas
    variações nas palavras.

    Exemplos:
    - "arros" deve ser interpretado como "arroz"
    - "sabonete" pode aparecer com pequenas variações de escrita
    - "departameto" deve ser interpretado como "departamento"

    Sempre utilize os nomes reais das colunas e dos valores existentes
    no banco de dados quando forem conhecidos.
    """

    dbschema = dspy.InputField(
        desc="Schema do banco de dados SQLite"
    )

    question = dspy.InputField(
        desc="Pergunta do usuário em linguagem natural, podendo conter erros de digitação"
    )

    sql_query = dspy.OutputField(
        desc="Consulta SQL válida para SQLite, corrigindo mentalmente pequenos erros de digitação"
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

    try:

        generator = ReliableSQLGenerator()

        prediction = generator(
            schema=DB_SCHEMA,
            question=question
        )

        sql = prediction.sql_query.strip()

        if not sql.upper().startswith("SELECT"):
            raise ValueError("Apenas consultas SELECT são permitidas.")

        valido, erro = validar_sql(sql, DB_SCHEMA)

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