# ==============================================================================
# IMPORTAÇÃO DE BIBLIOTECAS
# ==============================================================================
import sqlite3     # Banco de dados relacional embutido
import dspy        # Framework para programação e orquestração de LLMs
import os          # Manipulação de caminhos de arquivos e sistema operacional
import telebot     # API para criação de bots no Telegram (pyTelegramBotAPI)
import whisper     # Modelo de IA da OpenAI para transcrição de áudio (ASR)
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
          - produtos: nome, departamento
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
    



# ==============================================================================
# CONFIGURAÇÃO E HANDLERS DO BOT DO TELEGRAM
# ==============================================================================
# Token de autenticação do bot fornecido pelo @BotFather no Telegram
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(BASE_DIR, ".env"))

API_TOKEN = os.getenv('MEU_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

# Handler para qualquer mensagem de texto recebida
@bot.message_handler(func=lambda message: True)
def reply_hi(message):
  """Recebe mensagens de texto, gera a consulta SQL com DSPy, executa no banco
  e responde ao usuário com os resultados em formato JSON.
  """
  result = generate(message.text)
  bot.reply_to(message, json.dumps(result))

# Handler para mensagens de áudio/voz
@bot.message_handler(content_types=['voice'])
def transcribe_voice_message(message):
    """Recebe mensagens de voz, obtém o arquivo de áudio, transcreve com Whisper,
    processa a consulta no banco de dados e retorna o resultado.
    """
    file_id = message.voice.file_id
    # Obtém a URL do arquivo de áudio hospedado nos servidores do Telegram
    file_path = bot.get_file_url(file_id)

    # Transcreve o áudio para texto utilizando Whisper
    text = whisper_transcribe(file_path)

    # Consulta o banco a partir do texto transcrito da mensagem de voz
    result = generate(text)
    bot.reply_to(message, json.dumps(result))

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
    model = whisper.load_model(model)
    result = model.transcribe(filepath)

    return result["text"]

# Inicia a escuta contínua de novas mensagens enviadas ao bot (loop bloqueante)
bot.polling()