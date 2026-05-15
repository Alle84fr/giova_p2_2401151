from database import connection_bd
from gateway import GatewayPagamento


CUPONS_VALIDOS = {
    "DESCONTO10": 0.10,   
    "GEEK20":     0.20
}


class ErrorEstoqueInsuficiente(Exception):
    
    """ Estoque insuficiente """
    
    pass


class ErrorProdutoNaoEncontrado(Exception):
    
    """Id do produto não encontrado"""
    pass


class ErrorCupomInvalido(Exception):
    
    """Cupom invalido"""
    
    pass


def processar_pedido(
    produto_id: int,
    quantidade: int,
    dados_cartao: dict,
    cupom: str = None,
    gateway: GatewayPagamento = None
    ) -> dict:
    
    if gateway is None:
        gateway = GatewayPagamento()
    
    #___________ validar cumpom
    
    if cupom and cupom not in CUPONS_VALIDOS:
        raise ErrorCupomInvalido (F"Cupom {cupom} inválido")    


    conn = connection_bd()
    cursor = conn.cursor()

    #___________ pesquisa produto
    
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    produto_row = cursor.fetchone()

    if produto_row is None:
        conn.close()
        raise ErrorProdutoNaoEncontrado(f"Produto {produto_id} não encontrado.")

    preco    = produto_row["preco"]
    estoque  = produto_row["estoque"]
    nome     = produto_row["nome"]

    #___________ valida estoque
    
    if estoque < quantidade:
        conn.close()
        raise ErrorEstoqueInsuficiente(
            f"Estoque insuficiente. Disponível: {estoque}, solicitado: {quantidade}."
        )

    #___________ calcula valor + cupom
    
    desconto = CUPONS_VALIDOS.get(cupom, 0.0) if cupom else 0.0
    valor_total = preco * quantidade * (1 - desconto)

    #___________ pagamento
    
    resultado_pagamento = gateway.processar_pagamento(valor_total, dados_cartao)

    if not resultado_pagamento.get("sucesso"):
        conn.close()
        return {"sucesso": False, "mensagem": "Pagamento recusado pelo gateway."}

    nsu = resultado_pagamento["nsu"]

    # Atualiza estoque
    cursor.execute(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
        (quantidade, produto_id)
    )

    # Registra pedido
    cursor.execute(
        """INSERT INTO pedidos (produto_id, quantidade, valor_total, cupom, nsu)
           VALUES (?, ?, ?, ?, ?)""",
        (produto_id, quantidade, valor_total, cupom, nsu)
    )

    conn.commit()
    pedido_id = cursor.lastrowid
    conn.close()

    return {
        "sucesso": True,
        "pedido_id": pedido_id,
        "produto": nome,
        "valor_total": round(valor_total, 2),
        "nsu": nsu,
        "mensagem": "Compra efetuada"
    }


def listar_produtos() -> list:
    
    """Retorna todos os produtos disponíveis no catálogo"""
    
    conn = connection_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def buscar_produto(produto_id: int) -> dict:
    
    """Retorna produto pelo ID """
    
    conn = connection_bd()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None