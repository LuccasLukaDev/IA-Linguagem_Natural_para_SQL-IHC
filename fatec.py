import sqlite3
import dspy
import os
import telebot #pip install pytelegrambotapi
import whisper #pip install -U openai-whisper
### whisper requires ffmpeg: on windows: choco install ffmpeg
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "lojas.db")

def create_db():
  conn = sqlite3.connect(db_path)
  c = conn.cursor()

  # Create tables
  c.execute("""CREATE TABLE IF NOT EXISTS produtos (
                nome TEXT, 
                departamento TEXT
            )""")

  c.executemany("INSERT INTO produtos VALUES (?, ?)", [
    ("sabonete", "higiene"),
    ("agua", "bebidas"),
    ("coca", "bebidas"),
  ])

  conn.commit()
  conn.close()

create_db()

conn = sqlite3.connect(db_path)
results = conn.execute("SELECT * from produtos").fetchall()
print(results)

lm = dspy.LM('openai/gemma-4-E2B-it-IQ4_XS', api_base='http://localhost:1337/v1', api_key='not-needed')
dspy.configure(lm=lm)

class TextToSQL(dspy.Signature):
    """Generate SQL from natural language.

        Database schema:
          - produtos: nome, departamento
    """
    dbschema = dspy.InputField(desc="Databases schema")
    question = dspy.InputField(desc="Natural language question")

    sql_query = dspy.OutputField(desc="Valid SQL query")

class ReliableSQLGenerator(dspy.Module):
    def __init__(self):
        super().__init__()
        self.generate_sql = dspy.ChainOfThought(TextToSQL)

    def forward(self, schema, question):
        pred = self.generate_sql(schema=schema, question=question)
        return pred
    

question = "qual o departamento do sabonete?"

def generate(question):
    schema = """
    CREATE TABLE produtos (
      nome VARCHAR(50),
      departmento VARCHAR(50),
    );
    """
    generator = ReliableSQLGenerator()
    sql = generator.forward(schema, question)
    print(sql)
    conn = sqlite3.connect(db_path)
    print(sql.sql_query)
    results = conn.execute(sql.sql_query).fetchall()
    return results

API_TOKEN = '8739034781:AAG_gDvIGcJpvuN8ha0ewwgKp-8bPKO2gZQ'
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(func=lambda message: True)
def reply_hi(message):
  result = generate(message.text)
  bot.reply_to(message, json.dumps(result))

@bot.message_handler(content_types=['voice'])
def transcribe_voice_message(message):
    file_id = message.voice.file_id
    # Get url to audio file.
    file_path = bot.get_file_url(file_id)

    # Transcribe the audio using Whisper AI
    text = whisper_transcribe(file_path)

    result = generate(text)
    bot.reply_to(message, json.dumps(result))

def whisper_transcribe(filepath: str, model="tiny") -> str:
    """
    Function to perform ASR on a .mp3 file
    :param filepath: Path to the .mp3 audiofile.
    :param model: Set the model type for whisper
    ["tiny", "base", "small", "medium", "large"].
    Larger model means more parameters, higher memory requirements and
    slower speed.
    :return: transcribed audio.
    """
    # Choose tiny model for faster output.
    model = whisper.load_model(model)
    result = model.transcribe(filepath)

    return result["text"]

bot.polling()