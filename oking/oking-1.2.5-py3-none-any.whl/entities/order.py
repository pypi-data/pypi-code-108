class Queue:
    def __init__(self, pedido_id, data_pedido, status, protocolo, data_fila, observacao, valor_total=0.0, numero_pedido_externo=''):
        self.order_id = pedido_id
        self.date = data_pedido
        self.status = status
        self.protocol = protocolo


class Order:
    def __init__(self, id: int, pedido_venda_id: str, data_pedido: str, data_geracao: str, codigo_referencia: str,
                 valor_total: float, valor_forma_pagamento: float, valor_desconto: float, valor_frete: float,
                 status: str, quantidade_titulos: int, previsao_entrega: str, codigo_rastreio: str,
                 canal_id: int, transportadora_id: str, transportadora: str, servico_id: int, servico: str,
                 codigo_carga: str, protocolo: str, transacao, usuario: dict, pagamento: list, itens: list,
                 itens_brinde, itens_personalizados, forma_pagamento_parceiro, forma_envio_parceiro: dict,
                 pedido_nota_fiscal, cnpj_intermediador='', cnpj_instituicao_pagamento='', canal_site: str = '',
                 valor_adicional_forma_pagamento: float = 0.0, codigo_pedido_canal_alternativo: str = ''):
        self.order_id: int = id
        self.order_code: str = pedido_venda_id
        self.date: str = data_pedido
        self.erp_code: str = codigo_referencia
        self.total_amount: float = valor_total
        self.total_discount: float = valor_desconto
        self.freight_amount: float = valor_frete
        self.status: str = status
        self.delivery_forecast = previsao_entrega
        self.tracking_code = codigo_rastreio
        self.carrier: str = transportadora
        self.user: User = User(**usuario)
        self.additional_payment_amount: float = valor_adicional_forma_pagamento
        self.items: list[OrderItem] = [OrderItem(**i) for i in itens]
        self.channel_id = canal_id

        payments: list[Payment] = [Payment(**p) for p in pagamento]
        if len(payments) > 0:
            self.paid_date = payments[0].paid_date
            self.flag = payments[0].flag
            self.erp_payment_condition = payments[0].erp_payment_condition
            self.parcels = payments[0].parcels
            self.payment_type = payments[0].type

        partner_shipping_methods: list[PartnerShippingMethod] = [PartnerShippingMethod(**forma_envio_parceiro)]
        if len(partner_shipping_methods) > 0:
            self.shipping_mode = partner_shipping_methods[0].shipping_mode


class PartnerShippingMethod:
    def __init__(self, codigo_rastreio: str, forma_envio: str, tipo_envio: str, status_envio: str, data_previsao_postagem: str, modo_envio: str,
                 plp: str, rota: str, mega_rota: str):
        self.shipping_mode: str = modo_envio


class Payment:
    def __init__(self, opcao_pagamento: str, parcelas: int, bandeira: str, condicao_pagamento_erp: str, tabela_financiamento_rsvarejo: str,
                 tipo_venda_rsvarejo: str, canal_venda_id: str, canal_venda: str, numero_cupom: str, valor_cupom: float, codigo_compra: str,
                 codigo_pedido_canal: str, data_movimento: str, codigo_mercado: str, titulos):
        self.type: str = opcao_pagamento
        self.erp_payment_condition: str = condicao_pagamento_erp
        self.parcels: int = parcelas
        self.flag: str = bandeira
        self.paid_date: str = titulos[0]['data_pago']


class User:
    def __init__(self, codigo_referencia: str, nome: str, razao_social: str, cpf: str, rg: str, data_nascimento: str,
                 sexo: str, email: str, orgao: str, RegistroEstadual: str, TelefoneResidencial: str, TelefoneCelular: str,
                 Endereco: dict, EnderecoEntrega: dict, cpnj: str = '', cnpj: str = ''):
        # adicionado cpnj acima para adaptar a api b2c da Jade
        self.erp_code: str = codigo_referencia
        self.name: str = nome
        self.company_name: str = razao_social
        self.cpf: str = cpf
        self.cnpj: str = cnpj
        self.email: str = email
        self.residential_phone: str = TelefoneResidencial
        self.mobile_phone: str = TelefoneCelular
        self.address: Address = Address(**EnderecoEntrega)
        self.cnpj: str = cnpj


class Address:
    def __init__(self, cep: str, logradouro: str, numero: str, complemento: str, bairro: str, cidade: str,
                 estado: str, pais: str, referencia: str, descricao: str, tipo_logradouro: str):
        self.zipcode: str = cep
        self.address_line: str = logradouro
        self.number: str = numero
        self.complement: str = complemento
        self.neighbourhood: str = bairro
        self.city: str = cidade
        self.state: str = estado
        self.reference: str = referencia
        self.address_type: str = tipo_logradouro or 'Rua'


class OrderItem:
    def __init__(self, sku_principal: str, sku_variacao: str, sku_reference: str, hierarquia_variacao: str, is_restock: bool, codigo_externo_restock: str,
                 ean: str, quantidade: int, value: float, valor_desconto: float, altura: float, comprimento: float, largura: float, peso: float, volume: float,
                 filial_expedicao: str, filial_faturamento: str, cnpj_filial_venda: str, valor_comissao_frete: float = 0.0, valor_frete: float = 0.0,
                 percentual_comissao: float = 0.0, valor_comissao: float = 0.0):
        self.sku: str = sku_reference
        self.erp_code: str = sku_variacao
        self.quantity: int = quantidade
        self.ean: str = ean
        self.value: float = value
        self.discount: float = valor_desconto
        self.freight_value: float = valor_frete
