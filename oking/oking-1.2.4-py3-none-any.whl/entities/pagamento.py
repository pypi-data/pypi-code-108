
class Pagamento:

    def __init__(self, opcao_pagamento, parcelas, bandeira,
                 condicao_pagamento_erp, tabela_financiamento_rsvarejo,
                 tipo_venda_rsvarejo, canal_venda_id, canal_venda,
                 numero_cupom, valor_cupom, codigo_compra, codigo_pedido_canal,
                 data_movimento, codigo_mercado, titulos):
        self.opcao_pagamento = opcao_pagamento
        self.parcelas = parcelas
        self.bandeira = bandeira
        self.condicao_pagamento_erp = condicao_pagamento_erp
        self.tabela_financiamento_rsvarejo = tabela_financiamento_rsvarejo
        self.tipo_venda_rsvarejo = tipo_venda_rsvarejo
        self.canal_venda_id = canal_venda_id
        self.canal_venda = canal_venda
        self.numero_cupom = numero_cupom
        self.valor_cupom = valor_cupom
        self.codigo_compra = codigo_compra
        self.codigo_pedido_canal = codigo_pedido_canal
        self.data_movimento = data_movimento
        self.codigo_mercado = codigo_mercado
        self.titulos = titulos  # [TituloPagamento]


class TituloPagamento:

    def __init__(self, parcela, valor, data_vencimento, data_baixa,
                 data_pago, codigo_retorno, descricao_retorno,
                 valor_abatimento_concebido, desconto_concebido,
                 valor_iof_recolhido, valor_creditado,
                 valor_sacado, outros_valores, outros_creditos):
        self.parcela = parcela
        self.valor = valor
        self.data_vencimento = data_vencimento
        self.data_baixa = data_baixa
        self.data_pago = data_pago
        self.codigo_retorno = codigo_retorno
        self.descricao_retorno = descricao_retorno
        self.valor_abatimento_concebido = valor_abatimento_concebido
        self.desconto_concebido = desconto_concebido
        self.valor_iof_recolhido = valor_iof_recolhido
        self.valor_creditado = valor_creditado
        self.valor_sacado = valor_sacado
        self.outros_valores = outros_valores
        self.outros_creditos = outros_creditos


class FormaPagamento:

    def __init__(self, tipo_pagamento, bandeira, codigo_autorizacao,
                 codigo_status, codigo_transacao, data_criacao,
                 data_aprovacao, detalhe_status, status,
                 valor_frete, valor_parcela, valor_pedido,
                 valor_total_pago, parcelas):
        self.tipo_pagamento = tipo_pagamento
        self.bandeira = bandeira
        self.codigo_autorizacao = codigo_autorizacao
        self.codigo_status = codigo_status
        self.codigo_transacao = codigo_transacao
        self.data_criacao = data_criacao
        self.data_aprovacao = data_aprovacao
        self.detalhe_status = detalhe_status
        self.status = status
        self.valor_frete = valor_frete
        self.valor_parcela = valor_parcela
        self.valor_pedido = valor_pedido
        self.valor_total_pago = valor_total_pago
        self.parcelas = parcelas
