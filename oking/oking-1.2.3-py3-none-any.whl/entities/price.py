
class Price:
    def __init__(self, CODIGO_ERP, PRECO_ATUAL, PRECO_CUSTO, PRECO_LISTA, CODIGO_EXTERNO_CAMPANHA):
        self.codigo_erp = CODIGO_ERP
        self.preco_atual = PRECO_ATUAL
        self.preco_lista = PRECO_LISTA
        self.preco_custo = PRECO_CUSTO
        self.parceiro = 1
        self.codigo_externo_campanha = CODIGO_EXTERNO_CAMPANHA