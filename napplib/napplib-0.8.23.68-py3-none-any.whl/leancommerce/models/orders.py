class OrderTracking:
    def __init__(self, PedidoStatus=3, CodigoRastreio='', LinkRastreio=''):
        self.PedidoStatus = PedidoStatus
        self.CodigoRastreio = CodigoRastreio
        self.LinkRastreio = LinkRastreio

class OrderStatus:
    def __init__(self, PedidoStatus=0):
        self.PedidoStatus = PedidoStatus

class Invoice:    
    def __init__(self, Numero='', Serie='', Danfe='', Tipo='', Situacao='', Link='', Xml='', DataEmissao=''):
        self.Numero = Numero
        self.Serie = Serie
        self.Danfe = Danfe
        self.Tipo = Tipo
        self.Situacao = Situacao
        self.Link = Link
        self.Xml = Xml
        self.DataEmissao = DataEmissao