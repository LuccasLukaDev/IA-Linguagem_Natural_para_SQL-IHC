import sqlite3
import os

from app.config.database import DB_SCHEMA

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "lojas.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(DB_SCHEMA)

    conn.commit()
    conn.close()