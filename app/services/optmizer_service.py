import dspy

from app.config.database import DB_SCHEMA
from app.services.sql_service import ReliableSQLGenerator
from dspy.teleprompt import GEPA


trainset = [
    dspy.Example(
        schema=DB_SCHEMA,
        question="qual o departamento do sabonete?",
        sql_query="SELECT departamento FROM produtos WHERE nome = 'sabonete'"
    ).with_inputs("schema", "question"),

    dspy.Example(
        schema=DB_SCHEMA,
        question="qual o fabricante da coca?",
        sql_query="SELECT fabricante FROM produtos WHERE nome = 'coca'"
    ).with_inputs("schema", "question"),

    dspy.Example(
        schema=DB_SCHEMA,
        question="qual a quantidade de agua?",
        sql_query="SELECT quantidade FROM produtos WHERE nome = 'agua'"
    ).with_inputs("schema", "question"),

    dspy.Example(
        schema=DB_SCHEMA,
        question="liste os produtos do departamento bebidas",
        sql_query="SELECT nome FROM produtos WHERE departamento = 'bebidas'"
    ).with_inputs("schema", "question"),
]



def sql_metric(gold, pred, trace=None, pred_name=None, pred_trace=None):

    sql_esperado = gold.sql_query.strip().lower()
    sql_gerado = pred.sql_query.strip().lower()

    return sql_esperado == sql_gerado


reflection_lm = dspy.LM(
    "openai/gemma-4-E2B-it-IQ4_XS",
    api_base="http://localhost:1337/v1",
    api_key="not-needed"
)

optimizer = GEPA(
    metric=sql_metric,
    auto="light",
    reflection_lm=reflection_lm
)

generator = ReliableSQLGenerator()

optimized_generator = optimizer.compile(
    generator,
    trainset=trainset
)

optimized_generator.save("optimized_generator.json")

print("Modelo otimizado com sucesso!")