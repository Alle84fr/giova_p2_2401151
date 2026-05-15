import sqlite3
import os

# lembrando que a seta (Type Hints) repersenta o tipo do retorno, que no caso é string
def path_bd() -> str:
    
    """Função mostra caminho do bd"""
    
    return os.environ.get("DATABASE_URL", "geekstore.db")

def connection_bd() -> sqlite3.Connection:

    """Conexão do bd"""
    
    caminho = path_bd()
    # conn = conection = conexão - palavra padrão
    conn = sqlite3.connect(caminho, check_same_thread=False)
    # sqlite3.Row permite que acesse por código e não indice
    conn.row_factory = sqlite3.Row   
    return conn


def init_db():

    conn = connection_bd()
    cursor = conn.cursor()

    #___________ tabela produtos
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            nome    TEXT    NOT NULL,
            preco   REAL    NOT NULL,
            estoque INTEGER NOT NULL DEFAULT 0
        )
    """)

    #___________ tabela pedidos
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pedidos (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id       INTEGER NOT NULL,
            quantidade       INTEGER NOT NULL DEFAULT 1,
            valor_total      REAL    NOT NULL,
            cupom            TEXT,
            nsu              TEXT,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
    """)

    conn.commit()
    conn.close()