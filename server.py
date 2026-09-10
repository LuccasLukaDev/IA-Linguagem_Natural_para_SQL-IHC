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

  c.execute("DROP TABLE IF EXISTS produtos")

  # Criação da tabela de produtos com o novo esquema
  c.execute("""CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY,
                nome VARCHAR(50),
                departamento VARCHAR(50),
                fabricante TEXT,
                data_venc TEXT,
                data_fabri TEXT,
                cod_barra TEXT,
                origem TEXT,
                quantidade INTEGER
            )""")

  # Inserção de dados de teste (mock data)
  c.executemany("""INSERT INTO produtos (id, nome, departamento, fabricante, data_venc, data_fabri, cod_barra, origem, quantidade) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", [
    (1, "sabonete", "higiene", "Natura", "2025-12-31", "2023-01-15", "789100010001", "Nacional", 50),
    (2, "agua", "bebidas", "Crystal", "2024-10-20", "2024-04-20", "789100010002", "Nacional", 100),
    (3, "coca", "bebidas", "Coca-Cola", "2025-06-15", "2024-06-15", "789100010003", "Nacional", 80),
    (4, "arroz", "alimentos", "Camil", "2026-01-10", "2024-01-10", "789100010004", "Nacional", 40),
    (5, "feijao", "alimentos", "Tio Joao", "2025-11-20", "2024-02-15", "789100010005", "Nacional", 60),
    (6, "detergente", "limpeza", "Ype", "2026-05-30", "2024-05-30", "789100010006", "Nacional", 120),
    (7, "cafe", "alimentos", "Pilao", "2025-08-15", "2024-03-10", "789100010007", "Nacional", 35),
    (8, "pasta de dente", "higiene", "Colgate", "2026-12-01", "2024-01-05", "789100010008", "Nacional", 90),
    (9, "desinfetante", "limpeza", "Pinho Sol", "2026-08-20", "2024-08-20", "789100010009", "Nacional", 45),
    (10, "chocolate", "doces", "Nestle", "2025-09-30", "2024-07-01", "789100010010", "Importado", 70),
  ])

  conn.commit()  # Salva as alterações
  conn.close()   # Fecha a conexão

# Executa a função para garantir que o banco e os dados existam
create_db()

# Teste simples de leitura para verificar se os dados foram inseridos corretamente
conn = sqlite3.connect(db_path)
results = conn.execute("SELECT * from produtos").fetchall()
print(results)