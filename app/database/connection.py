import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "lojas.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
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
    """)

    conn.commit()
    conn.close()