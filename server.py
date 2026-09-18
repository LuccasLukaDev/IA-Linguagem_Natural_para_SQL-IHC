# ==============================================================================
# SERVIDOR BACKEND DO BANCO DE DADOS (FASTAPI + SQLITE)
# ==============================================================================
import os
import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Define o caminho do banco de dados local
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "lojas.db")


# ==============================================================================
# GERENCIADOR DO BANCO DE DADOS SQLITE
# ==============================================================================
class DatabaseManager:
    """Gerencia a conexão, validação e execução segura no SQLite."""
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Cria a tabela 'produtos' no SQLite e insere registros de teste se não existirem."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

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

        # Se a tabela estiver vazia, popula com os 10 registros de teste
        count = c.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]
        if count == 0:
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
            conn.commit()

        conn.close()

    def execute_query(self, sql: str) -> list[dict]:
        """Valida a query usando EXPLAIN e executa a busca no SQLite, retornando dicionários."""
        sql = sql.strip().rstrip(";")
        conn = sqlite3.connect(self.db_path)

        # Validação de sintaxe e nomes de colunas com o EXPLAIN nativo do SQLite
        conn.execute(f"EXPLAIN {sql}")

        cursor = conn.cursor()
        cursor.execute(sql)
        colunas = [desc[0] for desc in cursor.description] if cursor.description else []
        linhas = cursor.fetchall()
        conn.close()

        return [dict(zip(colunas, linha)) for linha in linhas]

db = DatabaseManager()


# ==============================================================================
# CONFIGURAÇÃO DA API FASTAPI DO BANCO DE DADOS
# ==============================================================================
api = FastAPI(
    title="Servidor de Banco de Dados - IHC",
    description="API REST para encapsulamento e execução segura de consultas SQLite.",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    sql: str

@api.post("/")
def execute_query(req: QueryRequest):
    """Recebe um comando SQL, valida e executa apenas consultas SELECT."""
    sql = req.sql.strip().rstrip(";")
    print(f"[INFO] SQL recebido no servidor: {sql}")

    # 1. Trava de segurança: apenas consultas SELECT
    if not sql.upper().startswith("SELECT"):
        print("[AVISO] Comando bloqueado no servidor: apenas consultas SELECT sao permitidas.")
        raise HTTPException(
            status_code=400,
            detail="Comando bloqueado: apenas consultas SELECT são permitidas."
        )

    # 2. Validação e Execução no SQLite
    try:
        resultados = db.execute_query(sql)
        print(f"[INFO] Consulta executada no SQLite. Registros retornados: {len(resultados)}")
        return {
            "sucesso": True,
            "query": sql,
            "total": len(resultados),
            "dados": resultados
        }
    except sqlite3.Error as e:
        print(f"[ERRO] Falha no SQLite: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Erro na consulta SQLite: {str(e)}"
        )


# ==============================================================================
# INICIALIZAÇÃO DO SERVIDOR (UVICORN)
# ==============================================================================
if __name__ == "__main__":
    db.init_db()
    uvicorn.run(api, host="127.0.0.1", port=8000)
