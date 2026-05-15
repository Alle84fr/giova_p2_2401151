from model import Produto, Pedido


class TestProduto:

    def test_criacao_atributos(self):

        # Novo produto
        p = Produto(id=1, nome="Camiseta Dick Vigarista & Mutle - M", preco=113.48, estoque=5)
        assert p.id      == 1
        assert p.nome    == "Camiseta Dick Vigarista & Mutle - M"
        assert p.preco   == 113.48
        assert p.estoque == 5

    def test_produto_sem_estoque(self):
        
        # estoque 0 o produto existe na loja mas não tem no momento
        p = Produto(id=2, nome="Cartucho Road Rash 2", preco=69.94, estoque=0)
        assert p.estoque == 0

    def test_igualdade_entre_produtos(self):

        p1 = Produto(id=1, nome="Camiseta Dick Vigarista & Mutle - M", preco=113.48, estoque=5)
        p2 = Produto(id=1, nome="Camiseta Dick Vigarista & Mutle - M", preco=113.48, estoque=5)
        assert p1 == p2

    def test_produtos_com_dados_diferentes_nao_sao_iguais(self):
        
        p1 = Produto(id=3, nome="Lego", preco=480.00, estoque=5)
        p2 = Produto(id=4, nome="Mangá", preco=36.89, estoque=10)
        assert p1 != p2

    def test_repr_contem_nome(self):

        p = Produto(id=5, nome="Hisoka", preco=977.00, estoque=3)
        assert "Hisoka" in repr(p)
        #gerar erro
        assert "977.0" in repr(p)


class TestPedido:

    def test_carrinho(self):
        pedido = Pedido(
            id=1,
            produto_id=5,
            quantidade=2,
            valor_total=960.00,
            cupom="GEEK20",
            nsu="Id_pG_GkSte_15052026_0001"
        )
        assert pedido.produto_id  == 5
        assert pedido.quantidade  == 2
        assert pedido.valor_total == 960.00
        assert pedido.nsu         == "Id_pG_GkSte_15052026_0001"

    def test_pedido_sem_cupom_e_nsu(self):

        pedido = Pedido(id=None, produto_id=4, quantidade=1, valor_total=36.89)
        assert pedido.cupom is None
        assert pedido.nsu   is None

    def test_pedido_id_igual_none(self):
        # id=None representa um pedido ainda não persistido no banco
        
        pedido = Pedido(id=None, produto_id=3, quantidade=1, valor_total=480.00)
        assert pedido.id is None

    def test_igualdade_entre_pedidos(self):
        
        p1 = Pedido(id=3, produto_id=1, quantidade=1, valor_total=480.00)
        p2 = Pedido(id=3, produto_id=1, quantidade=1, valor_total=480.00)
        assert p1 == p2