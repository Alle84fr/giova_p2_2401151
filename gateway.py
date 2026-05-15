class GatewayPagamento:

    def processar_pagamento(self, valor: float, dados_cartao: dict) -> dict:
        
        return {
            "sucesso": True,
            "nsu": "Id_pG_GkSte_15052026_0001"
        }