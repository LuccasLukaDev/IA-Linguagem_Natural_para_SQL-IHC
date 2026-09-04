import requests
import telebot
import whisper

from app.Bot.config_bot import ReliableSQLGenerator
from app.Bot.env import API_TOKEN
from app.config.database import DB_SCHEMA


bot = telebot.TeleBot(API_TOKEN)

API_URL = "http://localhost:8000/produtos/perguntar"
API_LISTAR_URL = "http://localhost:8000/produtos/listar"


def gerar_sql(question: str):

    generator = ReliableSQLGenerator()

    prediction = generator(
        schema=DB_SCHEMA,
        question=question
    )

    return prediction.sql_query.strip()


def consultar_api(sql_query: str):

    try:

        response = requests.post(
            API_URL,
            json={
                "sql_query": sql_query
            }
        )

        if response.status_code != 200:
            return {
                "erro": f"Erro HTTP: {response.status_code}"
            }

        return response.json()

    except Exception as e:

        return {
            "erro": f"Não foi possível acessar a API: {str(e)}"
        }


def consultar_lista_api():

    try:

        response = requests.get(API_LISTAR_URL)

        if response.status_code != 200:
            return {
                "erro": f"Erro HTTP: {response.status_code}"
            }

        return response.json()

    except Exception as e:

        return {
            "erro": f"Não foi possível acessar a API: {str(e)}"
        }


@bot.message_handler(commands=["start"])
def start(message):

    bot.reply_to(
        message,
        "Olá! 🤖\n"
        "Você pode me perguntar algo sobre os produtos."
    )


@bot.message_handler(commands=["listar"])
def listar(message):

    resposta_api = consultar_lista_api()

    if isinstance(resposta_api, dict) and "erro" in resposta_api:
        bot.reply_to(
            message,
            f"❌ {resposta_api['erro']}"
        )
        return

    produtos = resposta_api.get("resultado", [])

    if not produtos:
        bot.reply_to(
            message,
            "Nenhum produto encontrado."
        )
        return

    resposta = ""

    for produto in produtos:

        id_produto = produto[0]
        nome = produto[1]
        departamento = produto[2]
        fabricante = produto[3]
        data_venc = produto[4]
        data_fabri = produto[5]
        origem = produto[7]
        quantidade = produto[8]

        resposta += (
            f"🆔 ID: {id_produto}\n"
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

    sql = gerar_sql(text)

    print("SQL gerada:", sql)

    resposta_api = consultar_api(sql)

    if isinstance(resposta_api, dict) and "erro" in resposta_api:

        resposta = f"❌ {resposta_api['erro']}"

    else:

        resultado = resposta_api.get("resultado", [])

        if not resultado:

            resposta = "Nenhum resultado encontrado."

        else:

            resposta = "\n".join(
                str(linha[0])
                for linha in resultado
            )

    bot.reply_to(message, resposta)


@bot.message_handler(content_types=["text"])
def responder_texto(message):

    sql = gerar_sql(message.text)

    print("SQL gerada:", sql)

    resposta_api = consultar_api(sql)

    if isinstance(resposta_api, dict) and "erro" in resposta_api:

        resposta = f"❌ {resposta_api['erro']}"

    else:

        resultado = resposta_api.get("resultado", [])

        if not resultado:

            resposta = (
                "Nenhum resultado encontrado. "
                "Examine a solicitação e evite erros ortográficos/digitação."
            )

        else:

            resposta = "\n".join(
                str(linha[0])
                for linha in resultado
            )

    bot.reply_to(message, resposta)


def transcricao_whisper(filepath: str, model="base") -> str:

    whisper_model = whisper.load_model(model)

    result = whisper_model.transcribe(filepath)

    return result["text"]