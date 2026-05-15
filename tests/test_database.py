from services import listar_produtos, buscar_produto
from database import init_db, connection_bd


class TestEstruturaDoBanco:

    def test_tabela_produtos_existe(self, db):

        cursor = db.cursor()
        cursor.execute( "SELECT name FROM sqlite_master WHERE type='table' AND name='produtos'")
        assert cursor.fetchone() is not None, "Tabela 'produtos' não foi criada"

    def test_tabela_pedidos_existe(self, db):
        cursor = db.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='pedidos'")
        assert cursor.fetchone() is not None, "Tabela 'pedidos' não foi criada"

    def test_colunas_da_tabela_produtos(self, db):
        cursor = db.cursor()
        cursor.execute("PRAGMA table_info(produtos)")
        colunas = {row["name"] for row in cursor.fetchall()}
        assert {"id", "nome", "preco", "estoque"}.issubset(colunas)

    def test_colunas_da_tabela_pedidos(self, db):
        cursor = db.cursor()
        cursor.execute("PRAGMA table_info(pedidos)")
        colunas = {row["name"] for row in cursor.fetchall()}
        assert {"id", "produto_id", "quantidade", "valor_total", "cupom", "nsu"}.issubset(colunas)

#__________ dados ficticios

class TestSeeding:


    def test_banco_total_produtos(self, db):
        cursor = db.cursor()
        cursor.execute("SELECT COUNT(*) FROM produtos")
        assert cursor.fetchone()[0] == 4

    def test_produto_sem_estoque(self, db):
        cursor = db.cursor()
        cursor.execute("SELECT estoque FROM produtos WHERE nome LIKE '%Road Rash%'")
        row = cursor.fetchone()
        assert row is not None
        assert row["estoque"] == 0

#__________ crud

class TestOperacoesDeBanco:

    def test_listar_produtos(self, db):
        produtos = listar_produtos()
        assert isinstance(produtos, list)
        assert len(produtos) == 4

    def test_listar_produtos_id(self, db):
        produtos = listar_produtos()
        chaves_esperadas = {"id", "nome", "preco", "estoque"}
        for p in produtos:
            assert chaves_esperadas.issubset(p.keys()), \
                f"Produto com problema de chave: {p.keys()}"

    def test_buscar_produto_existente(self, db):
        produto = buscar_produto(1)
        assert produto is not None
        assert "Lego" in produto["nome"]
        assert produto["preco"] == 480.00

    def test_buscar_produto_inexistente(self, db):
        assert buscar_produto(7) is None

    def test_inserir_pedido(self, db):
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO pedidos (produto_id, quantidade, valor_total, cupom, nsu) "
            "VALUES (?, ?, ?, ?, ?)",
            (1, 1, 480.00, None, "NSU-MANUAL-TEST")
        )
        db.commit()

        cursor.execute("SELECT * FROM pedidos WHERE nsu = 'NSU-MANUAL-TEST'")
        pedido = cursor.fetchone()
        assert pedido is not None
        assert pedido["valor_total"] == 480.00
        assert pedido["produto_id"] == 1

    def test_update_estoque(self, db):
        cursor = db.cursor()
        cursor.execute("UPDATE produtos SET estoque = estoque - 2 WHERE id = 4")
        db.commit()

        cursor.execute("SELECT estoque FROM produtos WHERE id = 4")
        assert cursor.fetchone()["estoque"] == 1

    def test_row_acesso_por_nome(self, db):
        conn = connection_bd()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos WHERE id = 1")
        row = cursor.fetchone()
        conn.close()
        # Se row_factory não estivesse ativo, row["nome"] lançaria TypeError
        assert row["nome"] is not None