from typing import List
from datetime import datetime
from src.entities.product import Product
from src.entities.product import ItemBrinde
from src.entities.product import ItemPersonalizado
from src.entities.cliente import Cliente
from src.entities.pagamento import Pagamento


class Pedido:

    def __init__(self, id, pedido_venda_id, data_pedido, data_geracao,
                 codigo_referencia, valor_total, valor_forma_pagamento,
                 valor_desconto, valor_frete, status: str, quantidade_titulos,
                 previsao_entrega, codigo_rastreio, canal_id,
                 transportadora_id, transportadora,
                 servico_id, servico, codigo_carga,
                 transacao, usuario, pagamento: list[Pagamento],
                 itens, itens_brinde, itens_personalizados,
                 forma_pagamento_parceiro, forma_envio_parceiro,
                 pedido_nota_fiscal, protocolo, valor_adicional_forma_pagamento):
        self.id = id
        self.pedido_venda_id = pedido_venda_id
        self.data_pedido = data_pedido
        self.data_geracao = data_geracao
        self.codigo_referencia = codigo_referencia
        self.valor_total = valor_total
        self.valor_adicional_forma_pagamento = valor_adicional_forma_pagamento
        self.valor_forma_pagamento = valor_forma_pagamento
        self.valor_desconto = valor_desconto
        self.valor_frete = valor_frete
        self.status = status
        self.quantidade_titulos = quantidade_titulos
        self.previsao_entrega = previsao_entrega
        self.codigo_rastreio = codigo_rastreio
        self.canal_id = canal_id
        self.transportadora_id = transportadora_id
        self.transportadora = transportadora
        self.servico_id = servico_id
        self.servico = servico
        self.codigo_carga = codigo_carga
        self.transacao = transacao  # {Transacao}
        # {FormaPagamento}
        self.forma_pagamento_parceiro = forma_pagamento_parceiro
        self.forma_envio_parceiro = forma_envio_parceiro
        self.pedido_nota_fiscal = pedido_nota_fiscal  # [NotaFiscal]
        self.protocolo = protocolo
        self.novo_cliente = True

        if usuario is not None:
            self.usuario = Cliente(**usuario)

        self.pagamento: List[Pagamento]
        self.pagamento = []
        if pagamento is not None:
            for pag in pagamento:
                p = Pagamento(**pag)
                self.pagamento.append(p)

        self.itens: List[Product]
        self.itens = []
        if itens is not None:
            for item in itens:
                self.itens.append(OrderItem(**item))

        self.itens_brinde: List[ItemBrinde]
        self.itens_brinde = []
        if itens_brinde is not None:
            for item in itens_brinde:
                p = ItemBrinde(**item)
                self.itens_brinde.append(p)

        self.itens_personalizados: List[ItemPersonalizado]
        self.itens_personalizados = []
        if itens_personalizados is not None:
            for item in itens_personalizados:
                p = ItemPersonalizado(**item)
                self.itens_personalizados.append(p)

    def get_insert(self):
        sql = '''INSERT INTO lojasinfinity_openkuget.pedido_erp
                        (id, loja_id, client_id, processado,
                        datapedido, valor, valor_frete,
                        status_canal_id, status, canal_venda_id,
                        data_criacao, forma_envio)
                VALUES (null, 1, 147, 1, '''
        + self.data_pedido + ','
        + self.valor_total + ','
        + self.valor_frete + ','
        + self.status + ','
        + self.status + ','
        + self.canal_id + ','
        + self.data_geracao + ','
        + self.forma_envio_parceiro
        + ')'
        return sql

    def get_dados_cliente(self):
        # tes = stT.ljust(40, "N")
        # tes = stT.rjust(15, "0")
        tipo_endereco = 'RUA'
        documento = self.usuario.cpf if self.usuario.cpf is not None \
            else self.usuario.cnpj

        nome_cliente = self.usuario.nome
        if self.usuario.nome is None:
            nome_cliente = self.usuario.razao_social

        dados = '1;C;' + \
            documento.rjust(15, "0") + ';' + \
            nome_cliente.ljust(40, " ") + ';' + \
            tipo_endereco + ';' + \
            self.usuario.Endereco.logradouro.ljust(40, " ") + ';' + \
            self.usuario.Endereco.numero.ljust(5, " ") + ';' + \
            self.usuario.Endereco.cep + ';' + \
            self.usuario.Endereco.bairro.ljust(20, " ") + ';' + \
            self.usuario.email.ljust(40, " ") + ';' + \
            self.usuario.TelefoneCelular + ';' + \
            documento.rjust(15, "0") + ';\n'
        return dados

    def get_dados_pedido(self):
        forma_pagamento = ""
        if len(self.pagamento) > 0:
            forma_pagamento = self.pagamento[0].opcao_pagamento

        dt_pedido = ""
        if self.data_pedido is not None:
            data = datetime.strptime(self.data_pedido, "%Y-%m-%dT%H:%M:%S")
            dt_pedido = data.strftime("%d/%m/%Y")

        documento = self.usuario.cpf if self.usuario.cpf is not None \
            else self.usuario.cnpj

        nome_cliente = self.usuario.nome
        if self.usuario.nome is None:
            nome_cliente = self.usuario.razao_social

        dados = '1;P;' + \
            str(self.id).rjust(12, "0") + ';' + \
            documento.rjust(15, "0") + ';' + \
            nome_cliente.ljust(15, " ") + ';' + \
            dt_pedido + ';' + \
            str(self.valor_total).rjust(15, "0") + ';' + \
            str(self.valor_desconto).rjust(15, "0") + ';' + \
            forma_pagamento.ljust(100, " ") + ';\n'

        return dados

    def get_dados_lista_itens(self):
        d_itens = ''
        for it in self.itens:
            d_itens = d_itens + '1;I;' + \
                it.sku_principal.rjust(12, "0") + ';' + \
                str(it.valor_desconto).rjust(15, "0") + ';' + \
                str(it.value).rjust(15, "0") + ';' + \
                str(it.quantidade).rjust(15, "0") + ';' + \
                it.ean.ljust(13, " ") + ';' + \
                str(self.valor_frete).rjust(12, "0") + ';\n'

        return d_itens

    def get_insert_itens(self):
        sql = '''INSERT INTO lojasinfinity_openkuget.item_pedido_erp'''
        return sql

    def get_comando_proc(self):
        # STP_PROCESSA_PEDIDO3(P_TIPREG VARCHAR2,P_TEXTO VARCHAR2)
        sql = "call STP_PROCESSA_PEDIDO3 (" + \
            str(self.id) + "," + \
            " conteudo de ARQUIVO )"
        return sql

    def get_insert_cliente(self):
        sql = '''INSERT INTO lojasinfinity_openkuget.cliente
                        (id, loja_id, client_id, processado,
                        datapedido, valor, valor_frete,
                        status_canal_id, status, canal_venda_id,
                        data_criacao, forma_envio)
                VALUES (null, 1, 147, 1, '''
        + self.data_pedido + ','
        + self.valor_total + ','
        + self.valor_frete + ','
        + self.status + ','
        + self.status + ','
        + self.canal_id + ','
        + self.data_geracao + ','
        + self.forma_envio_parceiro
        + ')'
        return sql

    def get_insert_endereco(self):
        sql = '''INSERT INTO lojasinfinity_openkuget.endereco_cliente
                        (id, loja_id, client_id, processado,
                        datapedido, valor, valor_frete,
                        status_canal_id, status, canal_venda_id,
                        data_criacao, forma_envio)
                VALUES (null, 1, 147, 1, '''
        + self.data_pedido + ','
        + self.valor_total + ','
        + self.valor_frete + ','
        + self.status + ','
        + self.status + ','
        + self.canal_id + ','
        + self.data_geracao + ','
        + self.forma_envio_parceiro
        + ')'
        return sql





class Transacao:

    def __init__(self, transacao_id, numero_autorizacao,
                 nsu, mensagem_retorno):
        self.transacao_id = transacao_id
        self.numero_autorizacao = numero_autorizacao
        self.nsu = nsu
        self.mensagem_retorno = mensagem_retorno


class FormaEnvio:

    def __init__(self, codigo_rastreio, forma_envio,
                 tipo_envio, status_envio, data_previsao_postagem,
                 modo_envio, plp, rota, mega_rota):
        self.codigo_rastreio = codigo_rastreio
        self.forma_envio = forma_envio
        self.tipo_envio = tipo_envio
        self.status_envio = status_envio
        self.data_previsao_postagem = data_previsao_postagem
        self.modo_envio = modo_envio
        self.plp = plp
        self.rota = rota
        self.mega_rota = mega_rota


class NotaFiscal:

    def __init__(self, nota_fiscal_id, pedido_id,
                 num_fiscal, num_serie, access_key,
                 valor_total_nota, data_emissao, dt_cadastro,
                 xml, link_danfe, link_xml, quantidade_volume):
        self.nota_fiscal_id = nota_fiscal_id
        self.pedido_id = pedido_id
        self.num_fiscal = num_fiscal
        self.num_serie = num_serie
        self.access_key = access_key
        self.valor_total_nota = valor_total_nota
        self.data_emissao = data_emissao
        self.dt_cadastro = dt_cadastro
        self.xml = xml
        self.link_danfe = link_danfe
        self.link_xml = link_xml
        self.quantidade_volume = quantidade_volume


class Fila:
    def __init__(self, pedido_id, data_pedido,
                 status, protocolo, data_fila,
                 observacao, valor_total):
        self.pedido_id = pedido_id
        self.data_pedido = data_pedido
        self.status = status
        self.protocolo = protocolo
        self.data_fila = data_fila
        self.observacao = observacao
        self.valor_total = valor_total


def toListFilaDecoder(fila):
    lista = []
    for item in fila:
        lista.append(Fila(**item))

    return lista


# Serializing
# data = json.dumps(pedido, default=lambda o: o.__dict__,
#                   sort_keys=True, indent=4)
# Deserializing
# decoded_data = Pedido.from_json(json.loads(data))
