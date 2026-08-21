import dspy 

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