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

# ==============================================================================
# CONFIGURAÇÃO DO BANCO DE DADOS LOCAL
# ==============================================================================
# Define o diretório base do script atual e o caminho completo para o banco de dados
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "lojas.db")

def create_db():
  """Cria a tabela 'produtos' no SQLite e insere registros iniciais de exemplo."""
  conn = sqlite3.connect(db_path)
  c = conn.cursor()

  # Criação da tabela de produtos com as colunas 'nome' e 'departamento'
  c.execute("""CREATE TABLE IF NOT EXISTS produtos (
                nome TEXT, 
                departamento TEXT
            )""")

  # Inserção de dados de teste (mock data)
  c.executemany("INSERT INTO produtos VALUES (?, ?)", [
    ("sabonete", "higiene"),
    ("agua", "bebidas"),
    ("coca", "bebidas"),
  ])

  conn.commit()  # Salva as alterações
  conn.close()   # Fecha a conexão

# Executa a função para garantir que o banco e os dados existam
create_db()

# Teste simples de leitura para verificar se os dados foram inseridos corretamente
conn = sqlite3.connect(db_path)
results = conn.execute("SELECT * from produtos").fetchall()
print(results)