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
    produtos = listar_produtos()

    if not produtos:
        bot.reply_to(message, "Nenhum produto encontrado.")
        return

    resposta = ""

    for produto in produtos:
        id = produto[0]
        nome = produto[1]
        departamento = produto[2]
        fabricante = produto[3]
        data_venc = produto[4]
        data_fabri = produto[5]
        origem = produto[7]
        quantidade = produto[8]
    
        resposta += (
            f"🆔 ID: {id}\n"
            f"📦 Produto: {nome}\n"
            f"🏢 Departamento: {departamento}\n"
            f"🏭 Fabricante: {fabricante}\n"
            f"📅 Data de vencimento: {data_venc}\n"
            f"📅 Data de fabricação: {data_fabri}\n"
            f"🌎 Origem: {origem}\n"
            f"🔢 Quantidade: {quantidade}\n"
            f"\n"
        )

    bot.reply_to(message, resposta)


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