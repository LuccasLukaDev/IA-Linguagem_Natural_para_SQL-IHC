# ==============================================================================
# IMPORTAÇÃO DE BIBLIOTECAS
# ==============================================================================
import sqlite3     # Banco de dados relacional embutido
import dspy        # Framework para programação e orquestração de LLMs
import os          # Manipulação de caminhos de arquivos e sistema operacional
import telebot     # API para criação de bots no Telegram (pyTelegramBotAPI)
import whisper     # Modelo de IA da OpenAI para transcrição de áudio (ASR) 
# pip install openai-whisper
### Whisper requer ffmpeg instalado no sistema:
### No Windows: choco install ffmpeg | No Linux: sudo apt install ffmpeg
import json        # Manipulação e formatação de dados JSON
import os 
from dotenv import load_dotenv


# ==============================================================================
# CONFIGURAÇÃO DO MODELO DE LINGUAGEM (LLM) VIA DSPY
# ==============================================================================
# Conecta a um modelo local servido em um endpoint compatível com OpenAI (ex: Ollama, LM Studio, vLLM)
lm = dspy.LM('openai/gemma-4-E2B-it-IQ4_XS', api_base='http://localhost:1337/v1', api_key='not-needed')
dspy.configure(lm=lm)

# ==============================================================================
# DEFINIÇÃO DO DSPY: SIGNATURE E MÓDULO (TEXT-TO-SQL)
# ==============================================================================
class TextToSQL(dspy.Signature):
    """Gera uma consulta SQL a partir de uma pergunta em linguagem natural.

        Database schema:
          - produtos: id, nome, departamento, fabricante, data_venc, data_fabri, cod_barra, origem, quantidade
    """
    # Campos de entrada fornecidos ao modelo:
    dbschema = dspy.InputField(desc="Databases schema")
    question = dspy.InputField(desc="Natural language question")

    # Campo de saída esperado do modelo:
    sql_query = dspy.OutputField(desc="Valid SQL query")

class ReliableSQLGenerator(dspy.Module):
    """Módulo DSPy que utiliza ChainOfThought (raciocínio passo a passo) para gerar SQL confiável."""
    def __init__(self):
        super().__init__()
        # ChainOfThought instrui o modelo a raciocinar antes de produzir a resposta final
        self.generate_sql = dspy.ChainOfThought(TextToSQL)

    def forward(self, schema, question):
        # Executa a geração passando o schema e a pergunta do usuário
        pred = self.generate_sql(schema=schema, question=question)
        return pred

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


# ==============================================================================
# CONFIGURAÇÃO DO BANCO E GERAÇÃO/VALIDAÇÃO DE SQL
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "lojas.db")

# Instancia os módulos DSPy
sql_generator = ReliableSQLGenerator()
nl_responder = NaturalLanguageResponder()

DB_SCHEMA = "produtos (id, nome, departamento, fabricante, data_venc, data_fabri, cod_barra, origem, quantidade)"

def generate(text: str) -> str:
    """Gera a query SQL a partir de texto, valida, executa no SQLite e responde em linguagem natural."""
    print(f"[INFO] Pergunta recebida: {text}")

    # 1. Gera o comando SQL com a IA
    pred = sql_generator(schema=DB_SCHEMA, question=text)

    # 2. Limpa formatações markdown caso a IA responda com ```sql ... ```
    sql = pred.sql_query.replace("```sql", "").replace("```", "").strip().rstrip(";")
    print(f"[INFO] SQL gerado: {sql}")

    # 3. Trava de segurança: aceita estritamente comandos SELECT
    if not sql.upper().startswith("SELECT"):
        print("[AVISO] Comando bloqueado: apenas consultas SELECT sao permitidas.")
        return "Desculpe, só posso realizar consultas de busca e listagem no banco de dados."

    # 4. Testa e executa no SQLite
    try:
        conn = sqlite3.connect(db_path)

        # TESTA a query usando o método nativo do SQLite (não lê nem mexe nos dados)
        conn.execute(f"EXPLAIN {sql}")

        # Se passou no teste acima, executa a busca real
        cursor = conn.cursor()
        cursor.execute(sql)
        colunas = [desc[0] for desc in cursor.description] if cursor.description else []
        linhas = cursor.fetchall()
        conn.close()

        print(f"[INFO] Consulta executada com sucesso. Registros encontrados: {len(linhas)}")
        resultados = [dict(zip(colunas, linha)) for linha in linhas]

        if not resultados:
            return "Não encontrei nenhum produto correspondente à sua busca."

        # 5. Gera a resposta em linguagem natural usando DSPy
        dados_json = json.dumps(resultados, ensure_ascii=False)
        try:
            pred_resposta = nl_responder(question=text, data=dados_json)
            resposta_final = pred_resposta.answer.strip()
        except Exception as err:
            print(f"[AVISO] Falha ao gerar resposta amigável via IA: {err}")
            resposta_final = f"Encontrei os seguintes dados: {dados_json}"

        print(f"[INFO] Resposta amigável gerada: {resposta_final}")
        return resposta_final

    except sqlite3.Error as e:
        print(f"[ERRO] O SQLite rejeitou a consulta: {e}")
        return {"erro": f"O SQLite rejeitou a consulta: {e}", "query": sql}


# ==============================================================================
# CONFIGURAÇÃO E HANDLERS DO BOT DO TELEGRAM
# ==============================================================================
# Token de autenticação do bot fornecido pelo @BotFather no Telegram
load_dotenv(os.path.join(BASE_DIR, ".env"))

API_TOKEN = os.getenv('MEU_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

# Handler para qualquer mensagem de texto recebida
@bot.message_handler(func=lambda message: True)
def reply_hi(message):
  """Recebe mensagens de texto, gera a consulta SQL com DSPy, executa no banco
  e responde ao usuário em linguagem natural.
  """
  print(f"[INFO] Mensagem de texto recebida no Telegram: '{message.text}'")
  result = generate(message.text)
  bot.reply_to(message, result)
  print("[INFO] Resposta enviada ao usuario.")

# Handler para mensagens de áudio/voz
@bot.message_handler(content_types=['voice'])
def transcribe_voice_message(message):
    """Recebe mensagens de voz, obtém o arquivo de áudio, transcreve com Whisper,
    processa a consulta no banco de dados e retorna o resultado.
    """
    print("[INFO] Mensagem de voz recebida. Baixando e transcrevendo via Whisper...")
    file_id = message.voice.file_id
    # Obtém a URL do arquivo de áudio hospedado nos servidores do Telegram
    file_path = bot.get_file_url(file_id)

    # Transcreve o áudio para texto utilizando Whisper
    text = whisper_transcribe(file_path)
    print(f"[INFO] Texto transcrito da voz: '{text}'")

    # Consulta o banco a partir do texto transcrito da mensagem de voz
    result = generate(text)
    bot.reply_to(message, result)
    print("[INFO] Resposta enviada ao usuario.")

# ==============================================================================
# TRANSCRIÇÃO DE ÁUDIO COM OPENAI WHISPER
# ==============================================================================
def whisper_transcribe(filepath: str, model="tiny") -> str:
    """Realiza o reconhecimento de fala (ASR) a partir de um arquivo de áudio.

    :param filepath: Caminho ou URL para o arquivo de áudio.
    :param model: Tamanho do modelo Whisper a carregar
           ["tiny", "base", "small", "medium", "large"].
           Modelos maiores exigem mais memória e tempo, mas entregam maior precisão.
    :return: Texto transcrito do áudio.
    """
    # Carrega o modelo selecionado (o modelo 'tiny' é o mais leve e rápido)
    model = whisper.load_model('tiny')
    result = model.transcribe(filepath, language='pt')

    return result["text"]

# Inicia a escuta contínua de novas mensagens enviadas ao bot (loop bloqueante)
try:
    bot_info = bot.get_me()
    print(f"[INFO] Bot conectado com sucesso: @{bot_info.username} (ID: {bot_info.id})")
except Exception:
    print("[INFO] Bot conectado com sucesso.")

print("[INFO] Aguardando mensagens no Telegram... (Pressione Ctrl+C para encerrar)")
bot.polling(none_stop=True)