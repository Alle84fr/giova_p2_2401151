import pytest
from unittest.mock import MagicMock
from services import processar_pedido, ErrorEstoqueInsuficiente, ErrorProdutoNaoEncontrado, ErrorCupomInvalido, CUPONS_VALIDOS


def mock_gateway_aprovado(nsu="Id_pG_GkSte_TEST_001"):

    m = MagicMock()
    m.processar_pagamento.return_value = {"sucesso": True, "nsu": nsu}
    return m


class TestCompraComSucesso:
   
   # ok
    def test_compra_sucesso(self, db):
        gateway = mock_gateway_aprovado()
        resultado = processar_pedido(
            produto_id=1,
            quantidade=1,
            dados_cartao={},
            gateway=gateway
        )

        assert resultado["sucesso"] is True
        assert resultado["valor_total"] == 480.00
        assert resultado["nsu"] == "Id_pG_GkSte_TEST_001"
        assert "pedido_id" in resultado

    def test_gateway_analise_duplicata(self, db):

        gateway = mock_gateway_aprovado()

        processar_pedido(produto_id=3, quantidade=1,
                         dados_cartao={}, gateway=gateway)

        gateway.processar_pagamento.assert_called_once()

    def test_gateway_valor_correto(self, db):

        gateway = mock_gateway_aprovado()

        processar_pedido(produto_id=4, quantidade=2,
                         dados_cartao={}, gateway=gateway)

        args, _ = gateway.processar_pagamento.call_args
        # erro deve ser 1954.00 pois são dois produtos
        assert args[0] == pytest.approx(977.00, rel=1e-2)

    def test_compra_cupom_desconto10(self, db):

        gateway = mock_gateway_aprovado()

        resultado = processar_pedido(
            produto_id=3,           
            quantidade=1,
            dados_cartao={},
            cupom="DESCONTO10",
            gateway=gateway
        )

        assert resultado["sucesso"] is True
        # deve ser 36.89
        assert resultado["valor_total"] == pytest.approx(33.00, rel=1e-2)

    def test_compra_cupom_geek20(self, db):

        gateway = mock_gateway_aprovado()

        resultado = processar_pedido(
            produto_id=3,
            quantidade=1,
            dados_cartao={},
            cupom="GEEK20",
            gateway=gateway
        )

        # erro, deve ser 29.51
        assert resultado["valor_total"] == pytest.approx(36.89, rel=1e-2)

    def test_estoque_saida(self, db):

        gateway = mock_gateway_aprovado()

        processar_pedido(produto_id=4, quantidade=2,
                         dados_cartao={}, gateway=gateway)

        cursor = db.cursor()
        cursor.execute("SELECT estoque FROM produtos WHERE id = 4")
        assert cursor.fetchone()["estoque"] == 1

    def test_pedido_registrado_(self, db):

        gateway = mock_gateway_aprovado(nsu="NSU-DB-CHECK")

        processar_pedido(produto_id=3, quantidade=1,
                         dados_cartao={}, gateway=gateway)

        cursor = db.cursor()
        cursor.execute("SELECT * FROM pedidos WHERE nsu = 'NSU-DB-CHECK'")
        pedido = cursor.fetchone()
        assert pedido is not None
        assert pedido["produto_id"] == 3


class TestFluxosDeErro:

    # erro
    def test_estoque_insuficiente(self, db):

        gateway = mock_gateway_aprovado()

        with pytest.raises(ErrorEstoqueInsuficiente):
            processar_pedido(produto_id=2, quantidade=1,
                             dados_cartao={}, gateway=gateway)

        # O gateway não é chamado se não tiver estoque
        gateway.processar_pagamento.assert_not_called()

    def test_produto_inexistente(self, db):
  
        gateway = mock_gateway_aprovado()

        with pytest.raises(ErrorProdutoNaoEncontrado):
            processar_pedido(produto_id=7, quantidade=1,
                             dados_cartao={}, gateway=gateway)

        gateway.processar_pagamento.assert_not_called()

    def test_cupom_invalido(self, db):

        gateway = mock_gateway_aprovado()

        with pytest.raises(ErrorCupomInvalido):
            processar_pedido(produto_id=1, quantidade=1,
                             dados_cartao={}, cupom="CUPOM_FAke",
                             gateway=gateway)

        gateway.processar_pagamento.assert_not_called()

    def test_gateway_recusado(self, db):

        gateway = MagicMock()
        gateway.processar_pagamento.return_value = {
            "sucesso": False,
            "nsu": None
        }

        resultado = processar_pedido(
            produto_id=1, quantidade=1,
            dados_cartao={}, gateway=gateway
        )

        assert resultado["sucesso"] is False
        assert "recusado" in resultado["mensagem"].lower()

    def test_quantidade_acima_estoque(self, db):

        gateway = mock_gateway_aprovado()

        with pytest.raises(ErrorEstoqueInsuficiente):
            processar_pedido(produto_id=4, quantidade=7,
                             dados_cartao={}, gateway=gateway)


class TestCupons:

    def test_cupons_existem(self):
        assert "DESCONTO10" in CUPONS_VALIDOS
        assert "GEEK20"     in CUPONS_VALIDOS

    def test_desconto_corretos(self):
        assert CUPONS_VALIDOS["DESCONTO10"] == 0.10
        assert CUPONS_VALIDOS["GEEK20"]     == 0.20

    def test_cupom_inexistente(self):
        assert "CUPOM_FAke" not in CUPONS_VALIDOS