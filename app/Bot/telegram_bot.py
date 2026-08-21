import telebot
import json
import whisper

from app.services.sql_service import generate
from app.services.listar_produto_service import listar_produtos
from app.Bot.env import API_TOKEN


bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=["start"])
def start(message):
    bot.reply_to(
        message,
        "Olá! 🤖\n"
        "Você pode me perguntar algo sobre os produtos."
    )


@bot.message_handler(commands=["listar"])
def listar(message):
    resultado = listar_produtos()

    bot.reply_to(
        message,
        json.dumps(resultado, ensure_ascii=False, indent=2)
    )


@bot.message_handler(content_types=["voice"])
def transcricao_mensagem_voz(message):

    file_id = message.voice.file_id

    file_path = bot.get_file_url(file_id)

    text = transcricao_whisper(file_path)

    print("Texto transcrito:", text)

    resultado = generate(text)

    if not resultado:
        resposta = "Nenhum resultado encontrado."

    elif isinstance(resultado, dict) and "erro" in resultado:
        resposta = f"❌ {resultado['erro']}"

    else:
        resposta = "\n".join(
            str(linha[0])
            for linha in resultado
        )

    bot.reply_to(message, resposta)


@bot.message_handler(content_types=["text"])
def responder_texto(message):

    resultado = generate(message.text)

    if not resultado:
        resposta = "Nenhum resultado encontrado. Examine a solicitação evite erros ortográficos / digitação"

    if isinstance(resultado, dict) and "erro" in resultado:
        resposta = f"❌ {resultado['erro']}"

    if isinstance(resultado, list) and resultado:
        resposta = "\n".join(
            str(linha[0])
            for linha in resultado
        )

    bot.reply_to(message, resposta)


def transcricao_whisper(filepath: str, model="base") -> str:

    whisper_model = whisper.load_model(model)

    result = whisper_model.transcribe(filepath)
    
    return result["text"]