from flask import Blueprint, request, jsonify, render_template
from services import listar_produtos, buscar_produto, processar_pedido, ErrorCupomInvalido, ErrorEstoqueInsuficiente, ErrorProdutoNaoEncontrado


rotas_blueprint = Blueprint("rotas", __name__)

#___________ criando

@rotas_blueprint.route("/")
def index():
    produtos = listar_produtos()
    return render_template("index.html", produtos=produtos)

#___________ listar produtos

@rotas_blueprint.route("/produtos", methods=["GET"])
def rt_listar_produtos():
    produtos = listar_produtos()
    return jsonify(produtos), 200

#___________ pesquisar produto id

@rotas_blueprint.route("/produtos/<int:produto_id>", methods=["GET"])
def rt_pesquisar_produto(produto_id):
    produto = buscar_produto(produto_id)
    if produto is None:
        return jsonify({"erro": "Produto não encontrado"}), 404
    return jsonify(produto), 200

#___________ envio de compra do produto

@rotas_blueprint.route("/comprar", methods=["POST"])
def rota_comprar():
    dados = request.get_json()

    produto_id = dados.get("produto_id")
    quantidade = dados.get("quantidade", 1)
    cupom = dados.get("cupom")
    dados_pagamento = dados.get("dados_pagamento", {}) 

    try:
        resultado = processar_pedido(
            produto_id = produto_id,
            quantidade = quantidade,
            dados_pagamento = dados_pagamento, 
            cupom = cupom
        )
        return jsonify(resultado), 200
    

    except ErrorProdutoNaoEncontrado as e:
        return jsonify({"sucesso": False, "mensagem": str(e)}), 404
    
    except ErrorEstoqueInsuficiente as e:
        return jsonify({"sucesso": False, "mensagem": str(e)}), 400
    
    except ErrorCupomInvalido as e:
        return jsonify({"sucesso": False, "mensagem": str(e)}), 400
    
    except Exception as e:
        return jsonify({"sucesso": False, "mensagem": f"Erro interno: {str(e)}"}), 500