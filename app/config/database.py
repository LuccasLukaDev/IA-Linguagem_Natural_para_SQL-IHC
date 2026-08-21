DB_SCHEMA = """
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
"""

