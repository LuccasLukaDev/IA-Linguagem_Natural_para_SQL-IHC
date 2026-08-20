# 🤖 Linguagem Natural para SQL

Projeto desenvolvido para transformar perguntas feitas em **linguagem natural** em consultas **SQL**, utilizando inteligência artificial.

A aplicação recebe uma pergunta através de uma API desenvolvida com **FastAPI**, utiliza o **DSPy** para gerar a consulta SQL através de um modelo de linguagem local e executa essa consulta em um banco de dados **SQLite**.

> ⚠️ O projeto atualmente trabalha apenas com perguntas em texto.
> A funcionalidade de áudio utilizando Whisper ainda não está implementada nesta versão.

---

# 📌 Tecnologias utilizadas

- 🐍 Python 3.14
- ⚡ FastAPI
- 🚀 Uvicorn
- 🧠 DSPy
- 🤖 Gemma (modelo local)
- 🗄️ SQLite
- 📡 Thunder Client / Swagger
- 🧪 Pydantic

---

# 📂 Estrutura do projeto

```text
Projeto/
│
├── app/
│   │
│   ├── database/
│   │   └── connection.py
│   │
│   ├── docs/
│   │
│   ├── routers/
│   │   └── produtos.py
│   │
│   ├── schemas/
│   │   └── pergunta.py
│   │
│   ├── services/
│   │   └── sql_service.py
│   │
│   ├── __init__.py
│   └── main.py
│
├── .venv/
│
├── lojas.db
│
├── requirements.txt
│
└── README.md
```

## 📁 Descrição das pastas

### `app/`

Contém todo o código principal da aplicação FastAPI.

### `app/database/`

Responsável pela conexão e inicialização do banco SQLite.

### `app/routers/`

Contém as rotas da API.

Exemplo:

```text
POST /produtos/perguntar
```

### `app/schemas/`

Contém os modelos de dados utilizados pela API através do Pydantic.

### `app/services/`

Contém a lógica responsável por transformar a pergunta em SQL e executar a consulta no banco.

### `app/docs/`

Documentação adicional do projeto.

### `main.py`

Arquivo principal responsável por iniciar a aplicação FastAPI e registrar os routers.

### `lojas.db`

Banco de dados SQLite utilizado pelo projeto.

---

# 🧠 Como o projeto funciona

O funcionamento básico é:

```text
Pergunta do usuário
        │
        ▼
     FastAPI
        │
        ▼
    Router
        │
        ▼
    Service
        │
        ▼
      DSPy
        │
        ▼
Modelo Gemma local
        │
        ▼
    Consulta SQL
        │
        ▼
     SQLite
        │
        ▼
     Resultado
        │
        ▼
     FastAPI
        │
        ▼
      JSON
```

Por exemplo, o usuário envia:

```text
Qual o departamento do sabonete?
```

O modelo pode gerar:

```sql
SELECT departamento
FROM produtos
WHERE nome = 'sabonete';
```

A consulta é executada no SQLite e a API retorna o resultado.

---

# 🗄️ Banco de dados

O projeto utiliza SQLite.

A tabela principal é:

```sql
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
```

## Colunas

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

# 🐍 Configuração do Python

Recomenda-se utilizar um ambiente virtual para instalar as dependências do projeto.

## Criando o ambiente virtual

Na pasta principal do projeto:

```powershell
python -m venv .venv
```

---

# ▶️ Ativando a virtual environment

No Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Depois da ativação, o terminal deverá mostrar:

```text
(.venv) PS C:\...\Projeto>
```

Isso significa que o ambiente virtual está ativo.

---

# 📦 Instalando as dependências

Com a `.venv` ativada:

```powershell
pip install -r requirements.txt
```

O arquivo `requirements.txt` contém:

```text
fastapi
uvicorn
dspy
```

O SQLite não precisa ser instalado através do `pip`, pois o módulo `sqlite3` já faz parte da instalação padrão do Python.

---

# 🤖 Configuração do modelo local

O projeto utiliza um modelo Gemma executado localmente.

O DSPy está configurado para acessar o modelo através de uma API compatível com OpenAI.

Configuração utilizada:

```python
lm = dspy.LM(
    "openai/gemma-4-E2B-it-IQ4_XS",
    api_base="http://localhost:1337/v1",
    api_key="not-needed"
)
```

Isso significa que o servidor do modelo precisa estar rodando na porta:

```text
1337
```

O endereço utilizado pela aplicação é:

```text
http://localhost:1337/v1
```

## Testando o servidor do modelo

No PowerShell:

```powershell
Test-NetConnection localhost -Port 1337
```

O resultado esperado é:

```text
TcpTestSucceeded : True
```

Caso apareça:

```text
TcpTestSucceeded : False
```

o servidor do modelo local não está funcionando ou não está utilizando a porta `1337`.

---

# 🚀 Executando o projeto

Primeiro, abra o PowerShell na pasta principal do projeto:

```text
Projeto/
```

Ative a virtual environment:

```powershell
.\.venv\Scripts\Activate.ps1
```

Depois inicie o FastAPI:

```powershell
uvicorn app.main:app --reload
```

Se tudo estiver correto, aparecerá:

```text
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

A API estará disponível em:

```text
http://127.0.0.1:8000
```

---

# 📚 Documentação Swagger

O FastAPI disponibiliza automaticamente uma interface para testar as rotas.

Abra no navegador:

```text
http://127.0.0.1:8000/docs
```

A documentação deverá mostrar a rota:

```text
POST /produtos/perguntar
```

---

# 🧪 Testando com Swagger

No Swagger:

1. Acesse:

```text
http://127.0.0.1:8000/docs
```

2. Encontre:

```text
POST /produtos/perguntar
```

3. Clique em:

```text
Try it out
```

4. Envie um JSON como:

```json
{
    "question": "qual o departamento do sabonete?"
}
```

5. Clique em:

```text
Execute
```

A API irá enviar a pergunta para o DSPy, que utilizará o modelo local para gerar a consulta SQL.

---

# 🧪 Testando com Thunder Client

Também é possível utilizar o Thunder Client no VS Code.

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

Selecione:

```text
JSON
```

e envie:

```json
{
    "question": "qual o departamento do sabonete?"
}
```

---

# 📤 Exemplo de resposta

Dependendo dos dados existentes no banco, a API pode retornar:

```json
{
    "resultado": [
        [
            "higiene"
        ]
    ]
}
```

Caso existam dois registros que atendam à consulta:

```json
{
    "resultado": [
        [
            "higiene"
        ],
        [
            "higiene"
        ]
    ]
}
```

Isso acontece porque o SQLite retorna todas as linhas encontradas através do:

```python
fetchall()
```

---

# 🔎 Exemplos de perguntas

Como o sistema utiliza linguagem natural, algumas perguntas possíveis são:

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

O modelo irá interpretar a pergunta e tentar gerar uma consulta SQL correspondente.

---

# 🧠 DSPy

O DSPy é responsável por estruturar a interação com o modelo de linguagem.

O projeto utiliza uma assinatura semelhante a:

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

O schema enviado ao modelo é:

```sql
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
```

Dessa forma, o modelo conhece as tabelas e colunas disponíveis para construir a consulta SQL.

---

# 🏗️ Service

A geração da consulta SQL é realizada no service:

```text
app/services/sql_service.py
```

O service possui a responsabilidade de:

1. Receber a pergunta;
2. Enviar a pergunta e o schema para o DSPy;
3. Receber a consulta SQL gerada;
4. Executar a consulta no SQLite;
5. Retornar os resultados.

---

# 🌐 Router

A rota responsável por receber as perguntas está em:

```text
app/routers/produtos.py
```

A rota é:

```text
POST /produtos/perguntar
```

Ela recebe um objeto JSON:

```json
{
    "question": "qual o departamento do sabonete?"
}
```

e encaminha a pergunta para o service.

---

# 📋 Schema

O schema utilizado para validar a pergunta está em:

```text
app/schemas/pergunta.py
```

Exemplo:

```python
from pydantic import BaseModel


class Pergunta(BaseModel):
    question: str
```

Isso faz com que a API espere um JSON com a propriedade:

```text
question
```

---

# 🗃️ Conexão com o SQLite

A conexão com o banco está localizada em:

```text
app/database/connection.py
```

A aplicação utiliza o arquivo:

```text
lojas.db
```

O banco é criado caso ainda não exista.

A tabela também é criada utilizando:

```sql
CREATE TABLE IF NOT EXISTS produtos
```

Isso evita que a aplicação tente criar novamente uma tabela que já existe.

---

# ⚠️ Problemas comuns

## `ModuleNotFoundError: No module named 'app'`

Verifique se você está executando o comando na pasta principal:

```text
Projeto/
```

e não dentro da pasta `app`.

O comando correto é:

```powershell
uvicorn app.main:app --reload
```

---

## `uvicorn não é reconhecido`

Verifique se a virtual environment está ativada:

```powershell
.\.venv\Scripts\Activate.ps1
```

O terminal deve mostrar:

```text
(.venv)
```

Depois tente:

```powershell
uvicorn app.main:app --reload
```

---

## `table produtos already exists`

Não utilize:

```sql
CREATE TABLE produtos
```

Use:

```sql
CREATE TABLE IF NOT EXISTS produtos
```

Assim a tabela não será recriada quando o FastAPI for iniciado.

---

## API retorna `404 Not Found`

Se acessar:

```text
http://127.0.0.1:8000/
```

e receber:

```text
404 Not Found
```

isso não significa necessariamente que o FastAPI está com problema.

A aplicação pode simplesmente não possuir uma rota `/`.

Para testar a API, utilize:

```text
http://127.0.0.1:8000/docs
```

ou:

```text
http://127.0.0.1:8000/produtos/perguntar
```

---

## Erro `422 Unprocessable Entity`

Verifique se o JSON está correto:

```json
{
    "question": "qual o departamento do sabonete?"
}
```

Não envie somente:

```text
qual o departamento do sabonete?
```

O campo `question` é obrigatório.

---

## Erro ao conectar com o modelo

Verifique se o servidor local do modelo está funcionando na porta:

```text
1337
```

Teste:

```powershell
Test-NetConnection localhost -Port 1337
```

O resultado esperado:

```text
TcpTestSucceeded : True
```

---

# 🔐 Segurança

Caso o projeto utilize tokens ou chaves de API, **não coloque essas informações diretamente no código ou no GitHub**.

Utilize variáveis de ambiente e um arquivo `.env`.

Por exemplo:

```text
MODEL_API_URL=http://localhost:1337/v1
```

E adicione `.env` ao `.gitignore`:

```text
.env
.venv/
__pycache__/
```

---

# 🎤 Funcionalidade de voz

A versão original do projeto possuía integração com:

- Telegram Bot
- Whisper
- FFmpeg

Essas funcionalidades foram temporariamente deixadas de fora da versão atual.

O foco atual é:

```text
Texto
  ↓
FastAPI
  ↓
DSPy
  ↓
Gemma
  ↓
SQL
  ↓
SQLite
```

Posteriormente, o Whisper poderá ser integrado para permitir perguntas através de áudio:

```text
Áudio
  ↓
Whisper
  ↓
Texto
  ↓
DSPy
  ↓
SQL
  ↓
SQLite
```

---

# 🔄 Fluxo completo da aplicação

```text
┌───────────────────────┐
│       Usuário         │
│                       │
│ "Qual o departamento  │
│      do sabonete?"    │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│       FastAPI         │
│                       │
│ POST /produtos/       │
│ perguntar             │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│        Router         │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│        Service        │
│                       │
│ Recebe pergunta +     │
│ schema do banco       │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│         DSPy          │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│     Gemma local       │
│                       │
│ Gera SQL              │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│        SQLite         │
│                       │
│ Executa SQL           │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│       Resultado       │
│                       │
│ ["higiene"]           │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│       FastAPI         │
│                       │
│ Retorna JSON          │
└───────────────────────┘
```

---

# 🚀 Resumo rápido

Depois de clonar/baixar o projeto:

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

### 5. Inicie o servidor do modelo local

Certifique-se de que o modelo está disponível em:

```text
http://localhost:1337/v1
```

### 6. Inicie o FastAPI

```powershell
uvicorn app.main:app --reload
```

### 7. Abra a documentação

```text
http://127.0.0.1:8000/docs
```

### 8. Faça uma pergunta

```json
{
    "question": "qual o departamento do sabonete?"
}
```

---

# 👨‍💻 Projeto acadêmico

Projeto desenvolvido como parte das atividades acadêmicas de **Desenvolvimento de Software Multiplataforma / Interação Humano-Computador**.

O objetivo é estudar a integração entre:

- Linguagem natural
- Inteligência Artificial
- Geração automática de SQL
- APIs REST
- Banco de dados
- Modelos de linguagem locais