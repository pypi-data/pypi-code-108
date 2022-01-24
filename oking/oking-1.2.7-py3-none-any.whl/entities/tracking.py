
class Tracking:
    def __init__(self, pedido_id: int, codigo_rastreio: str, link_rastreio: str, data_previsao_entrega: str, codigo_erp_rastreio: str, codigo_sku: str,
                 cnpj_transportadora: str, transportadora: str, codigo_transportadora: str, tipo_servico: str, quantidade: int):
        self.id: int = pedido_id
        self.codigoRastreio: str = codigo_rastreio
        self.linkRastreio: str = link_rastreio
        self.data_previsao_entrega: str = data_previsao_entrega
        self.observacao: str = 'Pedido atualizado via Oking - Api Okvendas'
        self.codigo_erp: str = codigo_erp_rastreio
        self.codigo_sku: str = codigo_sku
        self.cnpj_transportadora: str = cnpj_transportadora
        self.transportadora: str = transportadora
        self.codigo_transportadora: str = codigo_transportadora
        self.tipo_servico: str = tipo_servico
        self.quantidade: int = quantidade
