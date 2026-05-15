from flask import Flask
from database import init_db
from routes import rotas_blueprint 

app = Flask(__name__)


app.register_blueprint(rotas_blueprint)

if __name__ == "__main__":
    init_db()

    
    from database import connection_bd
    conn = connection_bd()
    # cursor() mensageiro entre .py e sql
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM produtos")
    # pesquisa da 1° linha em diante
    count = cursor.fetchone()[0]

    if count == 0:
        cursor.executemany(
            "INSERT INTO produtos (nome, preco, estoque) VALUES (?, ?, ?)",
            [
                ("Lego One Piece, Tenda Palhaço Buggy - Modelo 3D - 573 peças ",  480.00, 5),
                ("Cartucho Jogo Road Rash 2 - usado", 69.94, 0),
                ("Mangá DanDaDan, vol 1", 36.89, 10),   
                ("Boneco Colecionável, Hisoka Morow - 33cm, Hunter X Hunter", 977.00, 3),
            ]
        )
        conn.commit()
    conn.close()

    app.run(host="0.0.0.0", port=5000, debug=False)