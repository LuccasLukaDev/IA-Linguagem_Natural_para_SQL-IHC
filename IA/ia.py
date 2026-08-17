import dspy


# Configuração do modelo no Jan.ai
lm = dspy.LM(
    "openai/gemma-4-E2B-it-IQ4_XS",
    api_base="http://localhost:1337/v1",
    api_key="not-needed"
)

dspy.configure(lm=lm)


class TextToSQL(dspy.Signature):
    """
    Generate a valid SQLite SQL query from a natural language question.
    Use only the tables and columns provided in the database schema.
    """

    dbschema = dspy.InputField(
        desc="Database schema"
    )

    question = dspy.InputField(
        desc="Natural language question"
    )

    sql_query = dspy.OutputField(
        desc="Valid SQLite SQL query"
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