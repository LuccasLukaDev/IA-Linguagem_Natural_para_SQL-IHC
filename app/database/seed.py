from app.database.connection import get_connection


produtos = [
    (
        "sabonete",
        "higiene",
        "Nivea",
        "2027-05-10",
        "2026-05-10",
        "7891234567890",
        "Brasil",
        50
    ),
    (
        "agua",
        "bebidas",
        "Crystal",
        "2027-08-20",
        "2026-08-20",
        "7899876543210",
        "Brasil",
        100
    ),
    (
        "coca",
        "bebidas",
        "Coca-Cola",
        "2027-10-15",
        "2026-10-15",
        "7891112223334",
        "Brasil",
        80
    ),
    (
        "arroz",
        "alimentos",
        "Tio João",
        "2027-12-01",
        "2026-06-01",
        "7895556667778",
        "Brasil",
        30
    )
]


def inserir_produtos():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.executemany("""
        INSERT INTO produtos (
            nome,
            departamento,
            fabricante,
            data_venc,
            data_fabri,
            cod_barra,
            origem,
            quantidade
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, produtos)

    conn.commit()
    conn.close()

    print(f"{len(produtos)} produtos inseridos com sucesso!")


if __name__ == "__main__":
    inserir_produtos()