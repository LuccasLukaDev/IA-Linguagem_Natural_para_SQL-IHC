import dspy
import sqlite3
import os


# Caminho do banco
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "lojas.db")


# Configuração do modelo no Jan.ai
lm = dspy.LM(
    "openai/gemma-4-E2B-it-IQ4_XS",
    api_base="http://localhost:1337/v1",
    api_key="not-needed"
)

dspy.configure(lm=lm)


# Define o que a IA deve fazer
class TextToSQL(dspy.Signature):
    """
    Generate a valid SQLite SQL query from a natural language question.
    Use only the tables and columns provided in the database schema.
    """

    dbschema = dspy.InputField(desc="Database schema")
    question = dspy.InputField(desc="Natural language question")
    sql_query = dspy.OutputField(desc="Valid SQL query")


# Módulo responsável por gerar o SQL
class ReliableSQLGenerator(dspy.Module):

    def __init__(self):
        super().__init__()
        self.generate_sql = dspy.ChainOfThought(TextToSQL)

    def forward(self, schema, question):
        return self.generate_sql(
            dbschema=schema,
            question=question
        )


# Schema do banco que será informado para a IA
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


# Cria o gerador
generator = ReliableSQLGenerator()


# Pergunta que queremos transformar em SQL
question = "qual o departamento do sabonete?"


# Gera o SQL
result = generator(schema, question)


print("Resultado:")
print(result)

print("\nSQL gerado:")
print(result.sql_query)


# Abre o banco SQLite
conn = sqlite3.connect(db_path)


# Executa o SQL gerado pela IA
resultado = conn.execute(result.sql_query).fetchall()


# Fecha a conexão
conn.close()


# Mostra o resultado encontrado no banco
print("\nResultado do banco:")
print(resultado)
