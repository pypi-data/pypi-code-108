
class Invoice:
    def __init__(self, pedido_id: int, chave_nf: str, num_serie: str, num_nf: str, valor_nf: float,
                 data_emissao: str, quantidade: int, link_nf: str, link_xml: str, xml: str):
        self.id: int = pedido_id
        self.chave_acesso: str = chave_nf
        self.numero_serie: str = num_serie
        self.numero_nota: str = num_nf
        self.valor_total_nota: float = valor_nf
        self.data_emissao: str = data_emissao
        self.quantidade_volume: int = quantidade
        self.link_danfe: str = link_nf
        self.link_xml: str = link_xml
        self.xml: str = xml
