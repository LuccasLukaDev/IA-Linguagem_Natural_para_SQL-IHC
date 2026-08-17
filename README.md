# IA-Linguagem_Natural_para_SQL-IHC

## Conversão de Áudio e Texto em Linguagem Natural para SQL com modelo de IA

Projeto desenvolvido para a disciplina de **Interação Humano-Computador (IHC)** com o objetivo de permitir que o usuário faça perguntas utilizando **linguagem natural**, enquanto um modelo de Inteligência Artificial interpreta a pergunta e gera automaticamente uma consulta SQL para um banco de dados SQLite.

O projeto utiliza um **modelo de IA local**, executado através do **Jan.ai**, evitando a necessidade de utilizar uma API de IA hospedada externamente.

---

## 🎯 Objetivo

O objetivo principal do projeto é criar uma interface capaz de receber perguntas como:

> "Qual o departamento do sabonete?"

e transformá-las automaticamente em uma consulta SQL equivalente, por exemplo:

```sql
SELECT departamento FROM produtos WHERE nome = 'sabonete';
```

Depois disso, a consulta gerada pela IA é enviada para o banco de dados SQLite e o resultado é retornado para o usuário.

O fluxo principal do sistema é:

```text
Usuário
   │
   │ Pergunta em linguagem natural
   ▼
ReliableSQLGenerator
   │
   │ Modelo de IA local
   ▼
Jan.ai
   │
   │ SQL gerado
   ▼
SQLite
   │
   │ Resultado da consulta
   ▼
Usuário
```

---

## 🧠 Tecnologias utilizadas

* **Python**
* **DSPy**
* **SQLite**
* **Jan.ai**
* **Gemma**
* **OpenAI-compatible API**
* **Whisper** — utilizado para reconhecimento de áudio
* **PyTelegramBotAPI** — utilizado para integração com Telegram

---

## 📁 Estrutura do projeto

```text
IA-Linguagem_Natural_para_SQL-IHC/
│
├── IA/
│   └── ia.py
│
├── bd/
│   ├── banco.py
│   └── lojas.db
│
├── main.py
│
├── .gitignore
│
└── README.md
```

### `main.py`

É o arquivo responsável por executar o fluxo principal da aplicação.

Ele:

1. Define o schema do banco de dados.
2. Cria uma pergunta em linguagem natural.
3. Envia a pergunta e o schema para a IA.
4. Recebe a consulta SQL gerada.
5. Executa a consulta no SQLite.
6. Exibe o resultado.

---

### `IA/ia.py`

Contém a configuração do modelo de Inteligência Artificial e a implementação responsável por transformar linguagem natural em SQL.

O projeto utiliza o **DSPy** para definir a assinatura da tarefa:

```python
class TextToSQL(dspy.Signature):
```

A IA recebe:

* Schema do banco de dados
* Pergunta do usuário

e retorna:

* Consulta SQL

O `ReliableSQLGenerator` utiliza `ChainOfThought` para gerar a resposta:

```python
self.generate_sql = dspy.ChainOfThought(TextToSQL)
```

---

### `bd/banco.py`

Responsável pela comunicação com o banco de dados SQLite.

A função:

```python
executar_sql(sql)
```

recebe uma consulta SQL, executa no banco `lojas.db` e retorna os resultados.

---

## 🗄️ Banco de dados

O projeto utiliza SQLite.

A tabela utilizada atualmente é:

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

### Colunas

| Coluna         | Tipo        | Descrição                               |
| -------------- | ----------- | --------------------------------------- |
| `id`           | INTEGER     | Identificador único do produto          |
| `nome`         | VARCHAR(50) | Nome do produto                         |
| `departamento` | VARCHAR(50) | Departamento ao qual o produto pertence |
| `fabricante`   | TEXT        | Fabricante do produto                   |
| `data_venc`    | TEXT        | Data de vencimento                      |
| `data_fabri`   | TEXT        | Data de fabricação                      |
| `cod_barra`    | TEXT        | Código de barras                        |
| `origem`       | TEXT        | Origem do produto                       |
| `quantidade`   | INTEGER     | Quantidade disponível                   |

---

# 🤖 Configuração da Inteligência Artificial

O projeto utiliza o **Jan.ai** para executar o modelo de linguagem localmente.

O Jan.ai deve estar instalado e configurado para disponibilizar uma API compatível com a API da OpenAI.

Neste projeto, a API é acessada através de:

```text
http://localhost:1337/v1
```

O modelo utilizado atualmente é:

```text
gemma-4-E2B-it-IQ4_XS
```

A configuração utilizada no DSPy é:

```python
lm = dspy.LM(
    "openai/gemma-4-E2B-it-IQ4_XS",
    api_base="http://localhost:1337/v1",
    api_key="not-needed"
)

dspy.configure(lm=lm)
```

> O nome do modelo precisa ser exatamente igual ao identificador disponibilizado pelo servidor local do Jan.ai.

---

# 📦 Instalação

## 1. Clonar o repositório

```bash
git clone https://github.com/LuccasLukaDev/IA-Linguagem_Natural_para_SQL-IHC.git
```

Entre na pasta do projeto:

```bash
cd IA-Linguagem_Natural_para_SQL-IHC
```

---

## 2. Criar um ambiente virtual

No Windows:

```powershell
python -m venv .venv
```

Ative o ambiente:

```powershell
.venv\Scripts\activate
```

No Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Instalar as dependências

Instale o DSPy:

```bash
pip install dspy
```

Caso o projeto de reconhecimento de áudio seja utilizado:

```bash
pip install -U openai-whisper
```

Para a integração com Telegram:

```bash
pip install pytelegrambotapi
```

O SQLite já possui suporte através da biblioteca padrão `sqlite3` do Python.

---

# 🖥️ Configuração do Jan.ai

Depois de instalar o Jan.ai:

1. Abra o Jan.ai.
2. Instale um modelo compatível.
3. Inicie o servidor local da API.
4. Verifique se o servidor está disponível na porta `1337`.

A aplicação espera encontrar a API em:

```text
http://localhost:1337/v1
```

É possível verificar se o servidor está funcionando acessando:

```text
http://localhost:1337/v1/models
```

No PowerShell, por exemplo:

```powershell
Invoke-RestMethod http://localhost:1337/v1/models
```

Se o servidor estiver funcionando corretamente, deverá ser retornada a lista de modelos disponíveis.

---

# ▶️ Executando o projeto

Com o ambiente virtual ativado e o Jan.ai executando o modelo, execute:

```bash
python main.py
```

O programa irá:

1. Enviar o schema para a IA.
2. Enviar a pergunta.
3. Gerar a consulta SQL.
4. Executar a consulta no SQLite.
5. Exibir o resultado.

Exemplo de pergunta:

```python
question = "qual o departamento do sabonete?"
```

A IA poderá gerar uma consulta semelhante a:

```sql
SELECT departamento FROM produtos WHERE nome = 'sabonete';
```

O resultado será então obtido diretamente do banco de dados.

---

# 🔄 Fluxo de funcionamento

O funcionamento pode ser dividido em três etapas principais.

### 1. Linguagem natural

O usuário fornece uma pergunta:

```text
Qual o departamento do sabonete?
```

### 2. Geração do SQL

O `ReliableSQLGenerator` recebe:

```text
Schema do banco
+
Pergunta do usuário
```

e envia essas informações para o modelo de linguagem.

O modelo gera uma consulta SQL:

```sql
SELECT departamento
FROM produtos
WHERE nome = 'sabonete';
```

### 3. Execução

A consulta é enviada para:

```python
executar_sql(result.sql_query)
```

O SQLite executa a consulta e retorna o resultado:

```text
[("higiene",)]
```

---

# 🧩 DSPy e `Prediction`

O DSPy retorna o resultado da execução do módulo como um objeto `Prediction`.

Por exemplo:

```text
Prediction(
    reasoning="Para encontrar o departamento do sabonete...",
    sql_query="SELECT departamento FROM produtos WHERE nome = 'sabonete'"
)
```

Esse objeto contém os campos produzidos pelo modelo.

Neste projeto, o campo principal utilizado é:

```python
result.sql_query
```

que contém a consulta SQL gerada pela IA.

O `reasoning` contém a justificativa produzida pelo `ChainOfThought`.

---

# 🛡️ Separação entre IA e banco de dados

Uma das características importantes do projeto é a separação entre o modelo de linguagem e o banco de dados.

A IA **não acessa diretamente o SQLite**.

O fluxo é:

```text
                    ┌───────────────┐
                    │      IA       │
                    │               │
Pergunta ──────────►│ Gera SQL      │
                    └───────┬───────┘
                            │
                            │ SQL
                            ▼
                    ┌───────────────┐
                    │    SQLite     │
                    │               │
                    │ Executa SQL   │
                    └───────┬───────┘
                            │
                            │ Resultado
                            ▼
                         Usuário
```

Dessa forma, o modelo de linguagem é responsável apenas por **interpretar a linguagem natural e gerar SQL**, enquanto o módulo de banco de dados é responsável pela execução da consulta.

---

# 🎙️ Conversão de áudio

O projeto também possui suporte para trabalhar com perguntas recebidas através de áudio.

Para isso, é utilizado o **Whisper**, responsável por converter o áudio em texto.

O fluxo pode ser expandido para:

```text
Áudio
  │
  ▼
Whisper
  │
  │ Texto
  ▼
Modelo de IA
  │
  │ SQL
  ▼
SQLite
  │
  │ Resultado
  ▼
Usuário
```

Assim, o usuário pode fazer uma pergunta por voz e o sistema pode utilizar o texto transcrito como entrada para o gerador de SQL.

---

# ⚠️ Observações

## O Jan.ai precisa estar executando

A aplicação depende do servidor local do Jan.ai.

Caso ele não esteja funcionando na porta `1337`, o programa não conseguirá enviar as solicitações para o modelo.

Verifique:

```text
http://localhost:1337/v1/models
```

---

## O modelo precisa estar disponível

O nome configurado em `ia.py`:

```python
openai/gemma-4-E2B-it-IQ4_XS
```

deve corresponder ao modelo disponibilizado pelo servidor local.

Caso o nome seja diferente, altere:

```python
lm = dspy.LM(
    "openai/NOME_DO_MODELO",
    api_base="http://localhost:1337/v1",
    api_key="not-needed"
)
```

---

## O SQL gerado deve ser validado

Como o SQL é gerado por um modelo de linguagem, é importante validar a consulta antes de executá-la em aplicações reais.

Atualmente, o projeto executa diretamente:

```python
resultado = executar_sql(result.sql_query)
```

Em uma versão futura, pode ser implementada uma camada de validação para permitir apenas operações seguras, como:

```sql
SELECT
```

e bloquear comandos como:

```sql
DROP
DELETE
UPDATE
INSERT
ALTER
```

---

# 🚀 Possíveis melhorias futuras

* Interface gráfica para o usuário.
* Conversão de áudio para texto.
* Suporte a múltiplas tabelas.
* Validação automática do SQL gerado.
* Histórico de perguntas.
* Tratamento de erros do banco de dados.
* Identificação automática de tabelas e colunas.
* Sistema de confirmação antes de executar consultas.
* Suporte a outros modelos de linguagem.
* Integração com Telegram.
* Retorno dos resultados em formato de tabela.
* Sistema de autenticação.
* Melhor tratamento de perguntas ambíguas.

---

# 👨‍💻 Autores

Projeto acadêmico desenvolvido para a disciplina de **Interação Humano-Computador (IHC)**.

**Lucas da Silva Alves**

---

# 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos e educacionais.
