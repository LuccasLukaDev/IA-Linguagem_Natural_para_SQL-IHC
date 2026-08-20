from app.database.connection import get_connection


def listar_produtos():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            nome,
            departamento,
            fabricante,
            data_venc,
            data_fabri,
            cod_barra,
            origem,
            quantidade
        FROM produtos
    """)

    produtos = cursor.fetchall()

    conn.close()

    return produtos