# 🤖 Linguagem Natural para SQL

Projeto desenvolvido para transformar perguntas feitas em **linguagem natural** em consultas **SQL**, utilizando Inteligência Artificial.

A aplicação recebe perguntas através de uma **API REST desenvolvida com FastAPI** ou através de um **Bot do Telegram**.

Para realizar a conversão de linguagem natural para SQL, o projeto utiliza:

- 🧠 **DSPy** para estruturar a geração da consulta;
- 🤖 **Gemma** executado localmente;
- 🗄️ **SQLite** como banco de dados;
- 🎤 **Whisper** para transcrição de mensagens de voz no Telegram.

Antes de executar uma consulta no banco real, o SQL gerado pelo modelo passa por validações para garantir que apenas consultas permitidas sejam executadas.

---

# 📌 Tecnologias utilizadas

- 🐍 Python 3.14
- ⚡ FastAPI
- 🚀 Uvicorn
- 🧠 DSPy
- 🤖 Gemma — modelo de linguagem local
- 🗄️ SQLite
- 🧪 Pydantic
- 🤖 Telegram Bot API
- 🎤 Whisper
- 🔐 python-dotenv
- 📚 Swagger
- 🧰 Thunder Client

---

# 📂 Estrutura do projeto

```text
Projeto/
│
├── app/
│   │
│   ├── Bot/
│   │   ├── telegram_bot.py
│   │   └── env.py
│   │
│   ├── config/
│   │   └── database.py
│   │
│   ├── docs/
│   │
│   ├── routers/
│   │   └── routes.py
│   │
│   ├── schemas/
│   │   ├── pergunta.py
│   │   └── produto.py
│   │
│   ├── server/
│   │   ├── bd.py
│   │   └── main.py
│   │
│   ├── services/
│   │   ├── listar_produto_service.py
│   │   └── sql_service.py
│   │
│   └── __init__.py
│
├── .venv/
├── .gitignore
├── lojas.db
├── requirements.txt
└── README.md
```

---

# 📁 Descrição das pastas

## `app/`

Contém todo o código principal da aplicação.

---

## `app/Bot/`

Contém a integração com o Telegram.

Principais arquivos:

```text
telegram_bot.py
env.py
```

### `telegram_bot.py`

Responsável por:

- Inicializar o Bot do Telegram;
- Receber comandos;
- Receber mensagens de texto;
- Receber mensagens de voz;
- Enviar perguntas para o `generate()`;
- Retornar os resultados para o usuário.

O bot possui suporte para:

```text
/start
/listar
```

Além de mensagens normais de texto e mensagens de voz.

### `env.py`

Responsável por disponibilizar o token utilizado pelo Bot do Telegram.

> ⚠️ O token real não deve ser publicado no GitHub.

---

## `app/config/`

Contém configurações utilizadas pela aplicação.

### `database.py`

Centraliza o schema utilizado pela aplicação através da constante:

```python
DB_SCHEMA = """
CREATE TABLE IF NOT EXISTS produtos (
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
```

O `DB_SCHEMA` é utilizado tanto para a criação da tabela quanto para fornecer ao modelo de IA a estrutura do banco.

Isso evita duplicar a definição da tabela em diferentes arquivos.

---

## `app/docs/`

Contém documentação adicional relacionada ao projeto.

---

## `app/routers/`

Contém as rotas da API FastAPI.

Atualmente o projeto possui:

```text
POST /produtos/perguntar
GET  /produtos/listar
```

O arquivo principal das rotas é:

```text
app/routers/routes.py
```

---

## `app/schemas/`

Contém os modelos Pydantic utilizados para validação dos dados da API.

### `pergunta.py`

Define o formato das perguntas recebidas pela API.

Exemplo:

```python
from pydantic import BaseModel


class Pergunta(BaseModel):
    question: str
```

### `produto.py`

Define o modelo utilizado para representar um produto.

---

## `app/server/`

Contém a configuração do servidor e a conexão com o banco.

### `main.py`

É o ponto de entrada principal da aplicação FastAPI.

Responsável por:

- Criar a aplicação FastAPI;
- Inicializar o banco;
- Registrar os routers;
- Inicializar o Bot do Telegram.

A aplicação é executada através de:

```powershell
uvicorn app.server.main:app --reload
```

### `bd.py`

Responsável pela conexão e criação do banco SQLite.

Utiliza o `DB_SCHEMA` localizado em:

```text
app/config/database.py
```

---

## `app/services/`

Contém a lógica principal da aplicação.

### `sql_service.py`

Responsável pelo processo de transformação de linguagem natural para SQL.

O fluxo é:

```text
Pergunta
   ↓
DB_SCHEMA
   ↓
DSPy
   ↓
Gemma
   ↓
SQL
   ↓
Validação
   ↓
SQLite
   ↓
Resultado
```

### `listar_produto_service.py`

Responsável por consultar e listar os produtos cadastrados no banco.

---

# 🗄️ Banco de dados

O projeto utiliza **SQLite**.

O arquivo utilizado é:

```text
lojas.db
```

A tabela principal é:

```sql
CREATE TABLE IF NOT EXISTS produtos (
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
```

## 📋 Colunas

| Coluna | Tipo | Descrição |
|---|---|---|
| `id` | INTEGER | Identificador do produto |
| `nome` | VARCHAR(50) | Nome do produto |
| `departamento` | VARCHAR(50) | Departamento do produto |
| `fabricante` | TEXT | Fabricante |
| `data_venc` | TEXT | Data de vencimento |
| `data_fabri` | TEXT | Data de fabricação |
| `cod_barra` | TEXT | Código de barras |
| `origem` | TEXT | Origem do produto |
| `quantidade` | INTEGER | Quantidade disponível |

---

# 🧩 Schema centralizado

O schema da tabela está centralizado em:

```text
app/config/database.py
```

através da constante:

```python
DB_SCHEMA
```

Esse schema possui duas funções principais:

1. Criar a tabela no SQLite;
2. Informar ao modelo de IA quais tabelas e colunas estão disponíveis.

O fluxo é:

```text
                 DB_SCHEMA
                /         \
               ↓           ↓
        Criação SQLite    DSPy
                           ↓
                       Gemma local
```

Dessa forma, não é necessário manter a mesma definição da tabela em vários arquivos.

---

# 🌱 Seed do banco de dados

O projeto possui um arquivo:

```text
app/database/seed.py
```

responsável por inserir dados iniciais na tabela `produtos`.

Exemplo de dados:

| Produto | Departamento | Fabricante | Quantidade |
|---|---|---|---:|
| sabonete | higiene | Nivea | 50 |
| agua | bebidas | Crystal | 100 |
| coca | bebidas | Coca-Cola | 80 |
| arroz | alimentos | Tio João | 30 |

## ▶️ Executando o Seed

Com a virtual environment ativada e na pasta principal do projeto:

```powershell
python -m app.database.seed
```

### ⚠️ Atenção

O `seed.py` utiliza `INSERT`.

Portanto, executar o seed várias vezes pode inserir os mesmos produtos novamente.

Caso queira começar novamente:

```text
1. Remova lojas.db
2. Inicie a aplicação
3. Execute o seed novamente
```

---

# 🤖 Configuração do modelo local

O projeto utiliza um modelo **Gemma executado localmente**.

O DSPy acessa o modelo através de uma API compatível com OpenAI.

Configuração utilizada:

```python
lm = dspy.LM(
    "openai/gemma-4-E2B-it-IQ4_XS",
    api_base="http://localhost:1337/v1",
    api_key="not-needed"
)
```

O servidor local do modelo deve estar disponível na porta:

```text
1337
```

Endpoint:

```text
http://localhost:1337/v1
```

## Testando o servidor

No PowerShell:

```powershell
Test-NetConnection localhost -Port 1337
```

Resultado esperado:

```text
TcpTestSucceeded : True
```

Caso apareça:

```text
TcpTestSucceeded : False
```

o servidor do modelo local não está disponível na porta `1337`.

---

# 🧠 DSPy e geração de SQL

O DSPy é utilizado para estruturar a interação entre a pergunta do usuário, o schema do banco e o modelo de linguagem.

A assinatura utilizada é semelhante a:

```python
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
```

O gerador utiliza `ChainOfThought`:

```python
class ReliableSQLGenerator(dspy.Module):

    def __init__(self):
        super().__init__()

        self.generate_sql = dspy.ChainOfThought(TextToSQL)

    def forward(self, schema, question):
        return self.generate_sql(
            dbschema=schema,
            question=question
        )
```

O modelo recebe:

```text
Schema do banco
       +
Pergunta do usuário
       ↓
     DSPy
       ↓
  Gemma local
       ↓
   SQL gerado
```

---

# 🔐 Validação e segurança do SQL

O SQL gerado pelo modelo não é executado diretamente no banco real.

Primeiro é realizada uma validação.

A aplicação verifica se a consulta começa com:

```python
if not sql.upper().startswith("SELECT"):
    raise ValueError("Apenas consultas SELECT são permitidas.")
```

Dessa forma, comandos como:

```text
INSERT
UPDATE
DELETE
DROP
ALTER
```

não são permitidos pelo fluxo atual.

Depois, o SQL é testado em um banco SQLite em memória utilizando o `DB_SCHEMA`.

```text
SQL gerado
    ↓
É SELECT?
    │
    ├── NÃO → Erro
    │
    ▼
Validação SQLite
    │
    ├── Inválido → Erro
    │
    ▼
SQLite real
    │
    ▼
Resultado
```

> A validação atual é uma camada de proteção do projeto, mas não deve ser considerada uma solução completa de segurança para ambientes de produção.

---

# 🏗️ Service de geração SQL

O principal service está localizado em:

```text
app/services/sql_service.py
```

A função principal é:

```python
generate(question)
```

Exemplo:

```python
generate("Qual o departamento do sabonete?")
```

O service:

1. Recebe a pergunta;
2. Utiliza `DB_SCHEMA`;
3. Envia schema e pergunta ao DSPy;
4. Recebe o `Prediction`;
5. Obtém `prediction.sql_query`;
6. Verifica se o SQL é permitido;
7. Valida a consulta;
8. Executa a consulta no SQLite;
9. Retorna os dados encontrados.

## Retorno

Quando a consulta é executada com sucesso:

```python
[
    ("higiene",)
]
```

O retorno é normalmente uma:

```text
list[tuple]
```

Quando ocorre um erro:

```python
{
    "erro": "Mensagem do erro"
}
```

Nesse caso, o retorno é um:

```text
dict[str, str]
```

---

# 🌐 API FastAPI

A aplicação utiliza FastAPI para disponibilizar uma API REST.

## Perguntar

```text
POST /produtos/perguntar
```

Body:

```json
{
    "question": "qual o departamento do sabonete?"
}
```

Fluxo:

```text
Pergunta
   ↓
Router
   ↓
generate()
   ↓
DSPy
   ↓
Gemma
   ↓
SQL
   ↓
Validação
   ↓
SQLite
   ↓
Resultado
```

---

# 📋 Listar produtos

A API também possui:

```text
GET /produtos/listar
```

Essa rota utiliza:

```text
app/services/listar_produto_service.py
```

para consultar os produtos cadastrados.

---

# 🤖 Bot do Telegram

O projeto possui integração com o **Telegram Bot API**.

O Bot utiliza os mesmos services da API.

Isso significa que a lógica de geração SQL não fica dentro do Telegram.

O Telegram apenas recebe a mensagem e encaminha para:

```python
generate()
```

O fluxo é:

```text
Usuário
   ↓
Telegram
   ↓
Bot
   ↓
generate()
   ↓
DSPy
   ↓
Gemma
   ↓
SQL
   ↓
SQLite
   ↓
Resultado
   ↓
Telegram
```

---

# `/start`

O comando:

```text
/start
```

inicia a interação com o bot.

Resposta:

```text
Olá! 🤖
Você pode me perguntar algo sobre os produtos.
```

---

# `/listar`

O comando:

```text
/listar
```

consulta os produtos cadastrados utilizando:

```python
listar_produtos()
```

e retorna os dados para o usuário.

---

# 💬 Perguntas por texto

O usuário pode enviar diretamente uma pergunta:

```text
Qual o departamento do sabonete?
```

O Telegram disponibiliza o conteúdo da mensagem através de:

```python
message.text
```

Esse conteúdo é enviado para:

```python
generate(message.text)
```

O resultado é convertido para uma resposta adequada antes de ser enviado novamente ao Telegram.

Por exemplo:

```text
Qual o departamento do sabonete?
```

pode resultar em:

```text
higiene
```

---

# 🎤 Perguntas por voz

O bot também possui suporte para mensagens de voz.

O fluxo é:

```text
🎤 Áudio
   ↓
Telegram
   ↓
Bot
   ↓
Whisper
   ↓
Texto transcrito
   ↓
generate()
   ↓
DSPy
   ↓
Gemma
   ↓
SQL
   ↓
SQLite
   ↓
Resultado
   ↓
Telegram
```

A transcrição utiliza Whisper:

```python
def transcricao_whisper(filepath: str, model="tiny") -> str:

    whisper_model = whisper.load_model(model)

    result = whisper_model.transcribe(filepath)

    return result["text"]
```

O modelo utilizado atualmente é:

```text
tiny
```

Modelos maiores podem apresentar maior qualidade de transcrição, porém exigem mais memória e processamento.

---

# 🔐 Token do Telegram

O token do Telegram é utilizado pelo Bot através do arquivo:

```text
app/Bot/env.py
```

O token **não deve ser colocado diretamente no código do bot**.

O ideal é utilizar uma variável de ambiente.

Exemplo:

```env
API_TOKEN=SEU_TOKEN_DO_TELEGRAM
```

E no código:

```python
import os
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv("API_TOKEN")
```

O arquivo `.env` deve estar no `.gitignore`.

Exemplo:

```gitignore
.env
.venv/
__pycache__/
*.db
```

> ⚠️ Nunca publique o token real do Telegram no GitHub.

---

# 🧵 Inicialização do Bot junto com o FastAPI

O Bot é inicializado junto com a aplicação FastAPI.

Para evitar que o `polling()` bloqueie o servidor principal, o bot é executado em uma `Thread`.

Conceitualmente:

```text
                 FastAPI
                    │
              ┌─────┴─────┐
              │           │
           API REST    Thread
                          │
                     Telegram Bot
```

Assim, a aplicação consegue manter simultaneamente:

- o servidor FastAPI;
- o Bot do Telegram.

A aplicação é iniciada apenas através do servidor FastAPI.

---

# 🚀 Executando o projeto

## 1. Criar a virtual environment

Na pasta principal:

```powershell
python -m venv .venv
```

---

## 2. Ativar a virtual environment

No Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

O terminal deverá apresentar algo semelhante a:

```text
(.venv) PS C:\...\Projeto>
```

---

## 3. Instalar dependências

```powershell
pip install -r requirements.txt
```

---

## 4. Configurar o token do Telegram

Configure o token utilizado pelo Bot de acordo com a configuração do projeto.

O token não deve ser versionado no Git.

---

## 5. Iniciar o servidor do modelo local

Certifique-se de que o Gemma esteja disponível em:

```text
http://localhost:1337/v1
```

Teste:

```powershell
Test-NetConnection localhost -Port 1337
```

O resultado esperado é:

```text
TcpTestSucceeded : True
```

---

## 6. Iniciar a aplicação

Na pasta principal do projeto:

```powershell
uvicorn app.server.main:app --reload
```

A aplicação estará disponível em:

```text
http://127.0.0.1:8000
```

O banco também será inicializado durante a inicialização da aplicação.

---

## 7. Executar o Seed

Em outro terminal, com a virtual environment ativada:

```powershell
python -m app.database.seed
```

---

## 8. Utilizar o Telegram

Não é necessário executar o arquivo `telegram_bot.py` separadamente.

O Bot é iniciado pela aplicação principal junto com o FastAPI.

Portanto, basta executar:

```powershell
uvicorn app.server.main:app --reload
```

Depois abra o Telegram e envie uma mensagem para o Bot.

Exemplo:

```text
/start
```

Depois:

```text
Qual o departamento do sabonete?
```

---

# 📚 Documentação Swagger

O FastAPI disponibiliza automaticamente uma documentação interativa.

Acesse:

```text
http://127.0.0.1:8000/docs
```

As principais rotas são:

```text
POST /produtos/perguntar
GET  /produtos/listar
```

---

# 🧪 Testando com Swagger

1. Acesse:

```text
http://127.0.0.1:8000/docs
```

2. Localize:

```text
POST /produtos/perguntar
```

3. Clique em:

```text
Try it out
```

4. Envie:

```json
{
    "question": "qual o departamento do sabonete?"
}
```

5. Clique em:

```text
Execute
```

A pergunta será enviada para o service, que utilizará DSPy e o modelo Gemma para gerar a consulta SQL.

---

# 🧪 Testando com Thunder Client

Também é possível testar a API através do Thunder Client no VS Code.

## Método

```text
POST
```

## URL

```text
http://127.0.0.1:8000/produtos/perguntar
```

## Header

```text
Content-Type: application/json
```

## Body

```json
{
    "question": "qual o departamento do sabonete?"
}
```

---

# 📤 Exemplo de resposta da API

Para uma pergunta como:

```text
Qual o departamento do sabonete?
```

A API pode retornar:

```json
{
    "resultado": [
        [
            "higiene"
        ]
    ]
}
```

Isso acontece porque o SQLite retorna as linhas através de:

```python
fetchall()
```

No Telegram, o resultado pode ser formatado para uma resposta mais amigável:

```text
higiene
```

em vez de:

```text
[["higiene"]]
```

---

# 🔎 Exemplos de perguntas

Algumas perguntas possíveis:

```text
Qual o departamento do sabonete?
```

```text
Qual o fabricante da coca?
```

```text
Qual a quantidade de água?
```

```text
Qual a origem do sabonete?
```

```text
Qual o código de barras da coca?
```

```text
Qual a data de vencimento do sabonete?
```

```text
Quais produtos pertencem ao departamento de bebidas?
```

O modelo interpreta a pergunta e tenta gerar uma consulta SQL correspondente ao schema disponível.

---

# ⚠️ Limitações atuais

Como a geração de SQL é realizada por um modelo de linguagem local, algumas perguntas podem não ser interpretadas corretamente.

Por exemplo, erros de digitação podem resultar em uma consulta que não encontre resultados:

```text
Qual o departamento do arros?
```

quando o produto cadastrado é:

```text
arroz
```

Da mesma forma, mensagens sem relação com os produtos podem ser interpretadas incorretamente pelo modelo.

Uma possível evolução do projeto é implementar uma etapa de **validação/classificação da intenção da pergunta** antes da geração do SQL, além de mecanismos para lidar com erros de digitação e aproximação dos nomes dos produtos.

---

# ⚠️ Problemas comuns

## `ModuleNotFoundError: No module named 'app'`

Certifique-se de executar os comandos na pasta principal:

```text
Projeto/
```

e utilize:

```powershell
uvicorn app.server.main:app --reload
```

---

## `uvicorn não é reconhecido`

Ative a virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Depois:

```powershell
uvicorn app.server.main:app --reload
```

---

## `table produtos already exists`

O schema deve utilizar:

```sql
CREATE TABLE IF NOT EXISTS produtos
```

O projeto já centraliza essa definição através de:

```python
DB_SCHEMA
```

---

## API retorna `404 Not Found`

A aplicação pode não possuir uma rota `/`.

Utilize:

```text
http://127.0.0.1:8000/docs
```

ou:

```text
http://127.0.0.1:8000/produtos/perguntar
```

---

## Erro `422 Unprocessable Entity`

Verifique se o JSON possui o campo:

```json
{
    "question": "qual o departamento do sabonete?"
}
```

O campo `question` é obrigatório.

---

## Erro ao conectar com o modelo

Verifique se o servidor local está funcionando na porta:

```text
1337
```

Execute:

```powershell
Test-NetConnection localhost -Port 1337
```

Resultado esperado:

```text
TcpTestSucceeded : True
```

---

## Erro relacionado ao Whisper ou FFmpeg

A funcionalidade de voz depende do Whisper e do FFmpeg.

Teste o FFmpeg:

```powershell
ffmpeg -version
```

Caso o comando não seja reconhecido, o FFmpeg não está disponível no `PATH` do sistema.

---

## Bot do Telegram não responde

Verifique:

1. Se o token do Telegram está configurado corretamente;
2. Se a aplicação FastAPI está em execução;
3. Se o Bot foi iniciado pela `main.py`;
4. Se o servidor local do modelo está funcionando;
5. Se o terminal apresenta erros relacionados ao `polling`.

A aplicação deve ser iniciada com:

```powershell
uvicorn app.server.main:app --reload
```

Não é necessário executar o `telegram_bot.py` separadamente.

---

## Produtos duplicados

O `seed.py` utiliza `INSERT`.

Executar o seed várias vezes pode inserir os mesmos produtos novamente.

Para começar novamente:

```text
1. Remova lojas.db
2. Inicie a aplicação
3. Execute o seed
```

---

# 🔄 Fluxo completo da aplicação

## API

```text
┌─────────────────────────┐
│        Usuário          │
│                         │
│ "Qual o departamento    │
│      do sabonete?"      │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│        FastAPI          │
│                         │
│ POST /produtos/         │
│ perguntar               │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│         Router          │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│         Service         │
│                         │
│ Pergunta + DB_SCHEMA    │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│          DSPy           │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│      Gemma local        │
│                         │
│       Gera SQL          │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│       Validação         │
│                         │
│    Apenas SELECT        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│         SQLite          │
│                         │
│      Executa SQL        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│        Resultado        │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│        FastAPI          │
│                         │
│       Retorna JSON      │
└─────────────────────────┘
```

---

# 🤖 Fluxo do Telegram

```text
┌─────────────────────────┐
│        Usuário          │
│                         │
│ Texto ou áudio          │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│     Telegram Bot        │
└────────────┬────────────┘
             │
        ┌────┴────┐
        │         │
      Texto      Áudio
        │         │
        │         ▼
        │      Whisper
        │         │
        │         ▼
        └────► Texto
                  │
                  ▼
             generate()
                  │
                  ▼
                DSPy
                  │
                  ▼
             Gemma local
                  │
                  ▼
             SQL gerado
                  │
                  ▼
              Validação
                  │
                  ▼
                SQLite
                  │
                  ▼
              Resultado
                  │
                  ▼
            Telegram
```

---

# 🧵 Arquitetura de execução

A aplicação utiliza o FastAPI como ponto de entrada principal.

O Bot do Telegram é executado em uma thread separada para não bloquear o servidor HTTP.

```text
                  main.py
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
       FastAPI               Thread
          │                     │
          │                     ▼
          │                Telegram Bot
          │                     │
          ▼                     ▼
       Routers              generate()
          │                     │
          └──────────┬──────────┘
                     │
                     ▼
                   DSPy
                     │
                     ▼
                Gemma local
                     │
                     ▼
                   SQLite
```

---

# 🚀 Resumo rápido

Depois de clonar ou baixar o projeto:

### 1. Entre na pasta

```powershell
cd IA-Linguagem_Natural_para_SQL-IHC
```

### 2. Crie a virtual environment

```powershell
python -m venv .venv
```

### 3. Ative

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Instale as dependências

```powershell
pip install -r requirements.txt
```

### 5. Configure o token do Telegram

Configure o token utilizado pelo Bot de acordo com o arquivo de configuração do projeto.

Não publique o token no GitHub.

### 6. Inicie o servidor do modelo local

Certifique-se de que o Gemma esteja disponível em:

```text
http://localhost:1337/v1
```

Teste:

```powershell
Test-NetConnection localhost -Port 1337
```

### 7. Inicie a aplicação

```powershell
uvicorn app.server.main:app --reload
```

### 8. Execute o Seed

Em outro terminal:

```powershell
python -m app.database.seed
```

### 9. Acesse o Swagger

```text
http://127.0.0.1:8000/docs
```

### 10. Abra o Telegram

Envie:

```text
/start
```

Depois faça uma pergunta:

```text
Qual o departamento do sabonete?
```

---

# 🎯 Objetivo do projeto

O projeto tem como objetivo estudar a integração entre:

- 🗣️ Linguagem natural
- 🤖 Inteligência Artificial
- 🧠 Modelos de linguagem locais
- 🔄 Geração automática de SQL
- 🛡️ Validação de consultas
- 🌐 APIs REST
- 🗄️ Banco de dados SQLite
- 📱 Telegram Bot
- 🎤 Reconhecimento de voz
- 🧩 DSPy

A aplicação demonstra como uma pergunta feita em linguagem natural pode ser transformada em uma consulta SQL executável utilizando um modelo de linguagem local, passando por uma camada de validação antes do acesso ao banco de dados.

---