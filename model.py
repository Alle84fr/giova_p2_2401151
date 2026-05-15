from dataclasses import dataclass
from typing import Optional

# @dataclass gera __init__ - cria  
# @dataclass gera __repr__ - gera texto para "output"
# @dataclass gera __eq__ - para ver se os dados são iguais "=="
@dataclass
class Produto:

    """Produtos da loja"""
    
    id: int
    nome: str
    preco: float
    estoque: int


@dataclass
class Pedido:
 
    id: Optional[int]
    produto_id: int
    quantidade: int
    valor_total: float
    # ou é none ou uma string
    cupom: Optional[str] = None
    nsu: Optional[str] = None