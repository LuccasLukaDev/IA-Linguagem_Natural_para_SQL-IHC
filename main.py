from ia import ReliableSQLGenerator
from banco import executar_sql


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


generator = ReliableSQLGenerator()


question = "qual o departamento do sabonete?"


# IA gera o SQL
result = generator(schema, question)


print("SQL gerado:")
print(result.sql_query)


# Banco executa o SQL
resultado = executar_sql(result.sql_query)


print("\nResultado do banco:")
print(resultado)