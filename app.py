# ==============================================================================
# 1. IMPORTAÇÕES E CONFIGURAÇÕES DE AMBIENTE
# ==============================================================================
import os          # Manipulação de caminhos e sistema operacional
import json        # Manipulação e formatação de JSON
import threading   # Execução em paralelo do bot do Telegram e da API FastAPI
import dspy        # Framework de orquestração de LLMs
import telebot     # API para o bot do Telegram
import whisper     # OpenAI Whisper para reconhecimento de fala (ASR)
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Define o diretório base e carrega variáveis de ambiente do .env
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Importa a instância do banco de dados encapsulado em server.py
from server import db


# ==============================================================================
# 2. CONFIGURAÇÃO DO MODELO DE LINGUAGEM (LLM LOCAL)
# ==============================================================================
# Conecta ao modelo local servido em endpoint compatível com OpenAI (ex: LM Studio, Ollama)
lm = dspy.LM('openai/gemma-4-E2B-it-IQ4_XS', api_base='http://localhost:1337/v1', api_key='not-needed')
dspy.configure(lm=lm)


# ==============================================================================
# 3. CAMADA DE INTELIGÊNCIA ARTIFICIAL (DSPY: SIGNATURES E MÓDULOS)
# ==============================================================================
class TextToSQL(dspy.Signature):
    """Gera uma consulta SQL a partir de uma pergunta em linguagem natural.

        Database schema:
          - produtos: id, nome, departamento, fabricante, data_venc, data_fabri, cod_barra, origem, quantidade
    """
    dbschema = dspy.InputField(desc="Databases schema")
    question = dspy.InputField(desc="Natural language question")
    sql_query = dspy.OutputField(desc="Valid SQL query")

class ReliableSQLGenerator(dspy.Module):
    """Módulo DSPy que utiliza ChainOfThought (raciocínio passo a passo) para gerar SQL confiável."""
    def __init__(self):
        super().__init__()
        self.generate_sql = dspy.ChainOfThought(TextToSQL)

    def forward(self, schema, question):
        return self.generate_sql(schema=schema, question=question)

class RespostaAmigavel(dspy.Signature):
    """Responda à pergunta do usuário de forma clara, educada e natural em português,
    baseando-se exclusivamente nos dados retornados do banco de dados.
    """
    question = dspy.InputField(desc="Pergunta feita pelo usuário")
    data = dspy.InputField(desc="Dados obtidos do banco de dados em formato JSON")
    answer = dspy.OutputField(desc="Resposta final amigável em linguagem natural para o usuário")

class NaturalLanguageResponder(dspy.Module):
    """Módulo DSPy que formula uma resposta em linguagem natural a partir dos dados obtidos."""
    def __init__(self):
        super().__init__()
        self.responder = dspy.ChainOfThought(RespostaAmigavel)

    def forward(self, question, data):
        return self.responder(question=question, data=data)

# Instanciação dos geradores de IA
sql_generator = ReliableSQLGenerator()
nl_responder = NaturalLanguageResponder()

DB_SCHEMA = "produtos (id, nome, departamento, fabricante, data_venc, data_fabri, cod_barra, origem, quantidade)"


# ==============================================================================
# 4. MOTOR DE PROCESSAMENTO (CORE PIPELINE)
# ==============================================================================
def process_question(text: str) -> dict:
    """Pipeline central: Pergunta -> Geração SQL -> Trava Segurança -> SQLite -> Resposta Amigável."""
    print(f"[INFO] Pergunta recebida: {text}")

    # 1. Gera o comando SQL com a IA
    pred = sql_generator(schema=DB_SCHEMA, question=text)

    # 2. Limpa formatações markdown caso a IA responda com ```sql ... ```
    sql = pred.sql_query.replace("```sql", "").replace("```", "").strip().rstrip(";")
    print(f"[INFO] SQL gerado: {sql}")

    # 3. Trava de segurança no app.py: aceita estritamente comandos SELECT
    if not sql.upper().startswith("SELECT"):
        print("[AVISO] Comando bloqueado no app.py: apenas consultas SELECT sao permitidas.")
        return {
            "sucesso": False,
            "sql": sql,
            "resposta": "Desculpe, só posso realizar consultas de busca e listagem no banco de dados.",
            "dados": []
        }

    # 4. Executa a consulta no banco encapsulado (server.py)
    try:
        resultados = db.execute_query(sql)
        print(f"[INFO] Consulta executada no SQLite. Registros encontrados: {len(resultados)}")
    except Exception as e:
        print(f"[ERRO] O SQLite rejeitou a consulta: {e}")
        return {
            "sucesso": False,
            "sql": sql,
            "resposta": f"Não foi possível consultar os dados. Motivo: {str(e)}",
            "dados": []
        }

    if not resultados:
        return {
            "sucesso": True,
            "sql": sql,
            "resposta": "Não encontrei nenhum produto correspondente à sua busca.",
            "dados": []
        }

    # 5. Gera a resposta em linguagem natural usando DSPy
    dados_json = json.dumps(resultados, ensure_ascii=False)
    try:
        pred_resposta = nl_responder(question=text, data=dados_json)
        resposta_final = pred_resposta.answer.strip()
    except Exception as err:
        print(f"[AVISO] Falha ao gerar resposta amigável via IA: {err}")
        resposta_final = f"Encontrei os seguintes dados: {dados_json}"

    print(f"[INFO] Resposta amigável gerada: {resposta_final}")
    return {
        "sucesso": True,
        "sql": sql,
        "resposta": resposta_final,
        "dados": resultados
    }

def generate(text: str) -> str:
    """Função utilitária que retorna apenas o texto da resposta para o Telegram."""
    resultado = process_question(text)
    return resultado["resposta"]


# ==============================================================================
# 5. PROCESSAMENTO DE ÁUDIO (OPENAI WHISPER)
# ==============================================================================
def whisper_transcribe(filepath: str, model="tiny") -> str:
    """Realiza o reconhecimento de fala (ASR) a partir de um arquivo de áudio."""
    model = whisper.load_model('tiny')
    result = model.transcribe(filepath, language='pt')
    return result["text"]


# ==============================================================================
# 6. INTERFACES DE INTERAÇÃO HUMANO-COMPUTADOR (IHC)
# ==============================================================================

# ------------------------------------------------------------------------------
# 6.1. INTERFACE REST (FASTAPI & SWAGGER)
# ------------------------------------------------------------------------------
api = FastAPI(
    title="API de Linguagem Natural para SQL - IHC",
    description="Interface REST com documentação Swagger para o sistema de Text-to-SQL.",
    version="1.0.0"
)

class PerguntaRequest(BaseModel):
    pergunta: str

@api.get("/")
def health_check():
    """Verifica a saúde da API e indica o link da documentação interativa."""
    return {
        "status": "online",
        "mensagem": "API e Bot de Linguagem Natural para SQL ativos.",
        "docs": "http://127.0.0.1:8000/docs"
    }

@api.post("/perguntar")
def api_perguntar(req: PerguntaRequest):
    """Recebe uma pergunta em linguagem natural via HTTP e retorna resposta completa."""
    if not req.pergunta.strip():
        raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")
    
    return process_question(req.pergunta)

# ------------------------------------------------------------------------------
# 6.2. INTERFACE TELEGRAM (TEXTO E VOZ)
# ------------------------------------------------------------------------------
API_TOKEN = os.getenv('MEU_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(func=lambda message: True)
def reply_hi(message):
    """Recebe mensagens de texto no Telegram, processa e responde ao usuário."""
    print(f"[INFO] Mensagem de texto recebida no Telegram: '{message.text}'")
    result = generate(message.text)
    bot.reply_to(message, result)
    print("[INFO] Resposta enviada ao usuario.")

@bot.message_handler(content_types=['voice'])
def transcribe_voice_message(message):
    """Recebe mensagens de voz no Telegram, transcreve com Whisper e responde ao usuário."""
    print("[INFO] Mensagem de voz recebida. Baixando e transcrevendo via Whisper...")
    file_id = message.voice.file_id
    file_path = bot.get_file_url(file_id)

    text = whisper_transcribe(file_path)
    print(f"[INFO] Texto transcrito da voz: '{text}'")

    result = generate(text)
    bot.reply_to(message, result)
    print("[INFO] Resposta enviada ao usuario.")

def run_telegram_bot():
    """Executa o polling do Telegram em uma thread paralela."""
    try:
        bot_info = bot.get_me()
        print(f"[INFO] Bot do Telegram conectado: @{bot_info.username} (ID: {bot_info.id})")
    except Exception:
        print("[INFO] Bot do Telegram inicializado.")

    print("[INFO] Bot do Telegram aguardando mensagens...")
    bot.infinity_polling()


# ==============================================================================
# 7. PONTO DE ENTRADA E INICIALIZAÇÃO DO SISTEMA
# ==============================================================================
if __name__ == "__main__":
    # 1. Inicia o Bot do Telegram em segundo plano (thread daemon)
    thread_bot = threading.Thread(target=run_telegram_bot, daemon=True)
    thread_bot.start()

    # 2. Inicia o servidor FastAPI na thread principal
    print("[INFO] Servidor FastAPI iniciando em http://127.0.0.1:8000")
    print("[INFO] Documentação Swagger acessível em http://127.0.0.1:8000/docs")
    uvicorn.run(api, host="127.0.0.1", port=8000)