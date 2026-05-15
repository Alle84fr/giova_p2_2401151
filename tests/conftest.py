# conftest.py — carregada automaticamente as fixtures compartilhadas entre os arquivos de teste.

import os
import pytest

os.environ["DATABASE_URL"] = "test.db"

from database import init_db, connection_bd
from app import app as flask_app


#___________ fixture banco de dados

# yield divide a fixture em 2 pontos 
# lembrando que fixture (fix) "Parte fixa", código feita antes do test que o .py usará como parâmetro no teste
@pytest.fixture(scope="function")
def db():
    
    #___________ Setup (crindo/preparando tabela para teste)
    init_db() 

    conn = connection_bd()
    cursor = conn.cursor()

    #___________ Reset/ clean state (estado do bd sempre limpo)
    cursor.execute("DELETE FROM pedidos")
    cursor.execute("DELETE FROM produtos")
    # reseta o id, "zera" o id
    cursor.execute("DELETE FROM sqlite_sequence")

    #___________ Seeding/ povoamento (insere vários dados fictícios no teste)
    cursor.executemany(
        "INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)",
        [
                ("Lego One Piece, Tenda Palhaço Buggy - Modelo 3D - 573 peças ",  480.00, 5),
                ("Cartucho Jogo Road Rash 2 - usado", 69.94, 0),
                ("Mangá DanDaDan, vol 1", 36.89, 10),   
                ("Boneco Colecionável, Hisoka Morow - 33cm, Hunter X Hunter", 977.00, 3)
        ]
    )
    
    conn.commit()

    # faz a conexão com teste
    yield conn

     #___________ Teardown (limpeza), após teste
    conn.close()
    if os.path.exists("test.db"):
        os.remove("test.db")


#___________ fixture cliente

@pytest.fixture(scope="function")
def client(db):

    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client