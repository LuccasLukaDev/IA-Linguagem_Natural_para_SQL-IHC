# IA Linguagem Natural para SQL

Projeto de uma aplicação capaz de receber perguntas em linguagem natural através de um Bot do Telegram, transformar essas perguntas em consultas SQL utilizando inteligência artificial e consultar um banco de dados SQLite através de uma API REST desenvolvida com FastAPI.

## Arquitetura

O projeto é dividido em três responsabilidades principais:

```text
┌──────────────┐
│     BOT      │
│              │
│ Telegram     │
│ Whisper      │
│ DSPy + Gemma │
│              │
│ Gera SQL     │
└──────┬───────┘
       │
       │ HTTP
       │ { "sql_query": "SELECT ..." }
       ▼
┌──────────────┐
│     HTTP     │
│              │
│   FastAPI    │
│              │
│ Recebe SQL   │
│ Encaminha    │
└──────┬───────┘
       │
       │ SQL
       ▼
┌──────────────┐
│    BANCO     │
│              │
│    SQLite    │
│              │
│ Executa SQL  │
│ Retorna dado │
└──────┬───────┘
       │
       │ Resultado
       ▼
┌──────────────┐
│     HTTP     │
└──────┬───────┘
       │
       │ JSON
       ▼
┌──────────────┐
│     BOT      │
│              │
│ Exibe para   │
│ o usuário    │
└──────────────┘
```

### Responsabilidades

#### Bot

O Bot é responsável por:

* Receber mensagens do Telegram.
* Receber mensagens de texto e áudio.
* Utilizar o Whisper para transcrever mensagens de voz.
* Processar a pergunta utilizando o `ReliableSQLGenerator`.
* Gerar a consulta SQL.
* Enviar a SQL para a API através de uma requisição HTTP.
* Receber o resultado retornado pela API.
* Apresentar a resposta ao usuário.

O Bot **não acessa diretamente o banco de dados**.

#### HTTP / FastAPI

A API é responsável por:

* Receber requisições HTTP do Bot.
* Receber a consulta através do campo `sql_query`.
* Encaminhar a consulta para o serviço responsável pelo banco.
* Retornar o resultado do banco em formato JSON.

Exemplo de requisição:

```json
{
    "sql_query": "SELECT nome FROM produtos WHERE departamento = 'bebidas'"
}
```

Exemplo de resposta:

```json
{
    "resultado": [
        ["agua"],
        ["coca"]
    ]
}
```

#### Banco de dados

O banco é responsável por:

* Receber a consulta SQL através do serviço da aplicação.
* Validar a consulta.
* Executar a consulta no SQLite.
* Retornar os resultados para a API.

Atualmente, somente consultas `SELECT` são permitidas.

---

## Fluxo da aplicação

Uma pergunta enviada pelo usuário segue o seguinte fluxo:

```text
Usuário
   │
   │ "Quais produtos são bebidas?"
   ▼
Telegram
   │
   ▼
Bot
   │
   │ DSPy + Gemma
   ▼
SQL
   │
   │ HTTP POST
   ▼
FastAPI
   │
   ▼
SQL Service
   │
   ▼
SQLite
   │
   │ Resultado
   ▼
FastAPI
   │
   │ JSON
   ▼
Bot
   │
   ▼
Telegram
   │
   ▼
Usuário
```

O objetivo dessa separação é impedir que o Bot tenha acesso direto ao banco. A comunicação entre o Bot e o banco acontece exclusivamente através da API HTTP.

---

## Tecnologias utilizadas

| Tecnologia       | Utilização                             |
| ---------------- | -------------------------------------- |
| Python           | Linguagem principal                    |
| FastAPI          | Desenvolvimento da API REST            |
| Uvicorn          | Servidor da API                        |
| DSPy             | Geração de SQL utilizando IA           |
| Gemma            | Modelo de inteligência artificial      |
| SQLite           | Banco de dados                         |
| PyTelegramBotAPI | Desenvolvimento do Bot do Telegram     |
| OpenAI Whisper   | Transcrição de mensagens de voz        |
| Requests         | Comunicação HTTP entre Bot e API       |
| Pydantic         | Validação dos dados recebidos pela API |
| python-dotenv    | Gerenciamento de variáveis de ambiente |

---

## Estrutura do projeto

```text
app/
│
├── Bot/
│   ├── config_bot.py
│   ├── env.py
│   └── telegram_bot.py
│
├── config/
│   └── database.py
│
├── database/
│   ├── connection.py
│   └── seed.py
│
├── routers/
│   └── routes.py
│
├── schemas/
│   └── sqlQuery.py
│
├── services/
│   ├── sql_service.py
│   └── listar_produto_service.py
│
├── server/
│   └── bd.py
│
└── main.py
```

### Descrição das principais pastas

**`Bot/`**

Contém a implementação do Bot do Telegram, geração de SQL utilizando DSPy/Gemma e comunicação HTTP com a API.

**`routers/`**

Contém as rotas HTTP disponibilizadas pela aplicação FastAPI.

**`schemas/`**

Contém os modelos Pydantic utilizados para validar os dados recebidos pelas requisições HTTP.

**`services/`**

Contém as regras responsáveis pela execução das consultas no banco.

**`config/`**

Contém as configurações do banco e o schema utilizado para validação das consultas.

**`database/`**

Contém funcionalidades relacionadas à criação/conexão e população inicial do banco.

---

## Endpoint principal

### `POST /produtos/perguntar`

Responsável por receber uma consulta SQL gerada pelo Bot.

### Request

```json
{
    "sql_query": "SELECT nome FROM produtos"
}
```

### Response

```json
{
    "resultado": [
        ["sabonete"],
        ["agua"],
        ["coca"],
        ["arroz"]
    ]
}
```

A API não gera a SQL. A SQL é gerada anteriormente pelo Bot utilizando o modelo de IA.

---

## Endpoint de listagem

### `GET /produtos/listar`

Retorna os produtos cadastrados no banco.

---

## Banco de dados

O projeto utiliza SQLite.

### Schema

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

### Dados iniciais

O banco possui dados de exemplo, como:

* Sabonete
* Água
* Coca-Cola
* Arroz

---

## Validação das consultas SQL

Antes de executar a consulta no banco real, a aplicação realiza uma validação utilizando um banco SQLite em memória.

O processo é:

```text
SQL recebida
     │
     ▼
Verifica se começa com SELECT
     │
     ▼
Executa em SQLite :memory:
     │
     ├── Inválida → retorna erro
     │
     └── Válida
          │
          ▼
      Banco real
          │
          ▼
       Resultado
```

Consultas que não sejam `SELECT` são rejeitadas.

Exemplo:

```sql
DELETE FROM produtos;
```

Resultado:

```text
Apenas consultas SELECT são permitidas.
```

---

## Instalação

Crie um ambiente virtual:

```bash
python -m venv venv
```

Ative o ambiente virtual.

### Windows

```bash
venv\Scripts\activate
```

### Linux

```bash
source venv/bin/activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## Configuração

Crie um arquivo `.env` para armazenar as configurações necessárias, incluindo o token do Bot do Telegram.

Exemplo:

```env
API_TOKEN=seu_token_aqui
```

Não compartilhe o token do Bot e não o envie para o repositório.

---

## Executando a API

Execute o FastAPI utilizando o Uvicorn:

```bash
uvicorn app.server.main:app --reload
```

A API estará disponível localmente em:

```text
http://localhost:8000
```

A documentação interativa do FastAPI pode ser acessada em:

```text
http://localhost:8000/docs
```

---

## Executando o Bot

Com a API em execução, execute o Bot:

```bash
python -m app.Bot.telegram_bot
```

O Bot deverá estar configurado com o token do Telegram.

O Bot utiliza a API HTTP para enviar as consultas SQL e receber os resultados.

---

## Dependências

```text
fastapi
uvicorn
dspy
pyTelegramBotAPI
openai-whisper
python-dotenv
requests
```

### Responsabilidades das dependências

| Pacote             | Uso                                   |
| ------------------ | ------------------------------------- |
| `fastapi`          | API REST                              |
| `uvicorn`          | Servidor da API                       |
| `dspy`             | Geração de SQL com o Gemma            |
| `pyTelegramBotAPI` | Bot do Telegram                       |
| `openai-whisper`   | Transcrição dos áudios                |
| `python-dotenv`    | Carregamento de configurações e token |
| `requests`         | Comunicação HTTP entre o Bot e a API  |

---

## Objetivo da arquitetura

A arquitetura foi definida para manter as responsabilidades separadas:

```text
BOT
 │
 │ HTTP
 ▼
FASTAPI
 │
 ▼
BANCO
```

Dessa forma:

* O **Bot** é responsável pela interação com o usuário e geração da SQL.
* O **HTTP/FastAPI** é responsável pela comunicação entre as partes.
* O **Banco** é responsável pela execução e retorno dos dados.
* O **Bot não acessa diretamente o banco**.
* O **Banco não depende do Bot**.
* A comunicação entre Bot e Banco ocorre através da API.
