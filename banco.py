import sqlite3
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "lojas.db")


def executar_sql(sql):
    conn = sqlite3.connect(db_path)

    try:
        resultado = conn.execute(sql).fetchall()
        return resultado

    finally:
        conn.close()