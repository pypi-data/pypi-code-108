import json
from ast import Num


class Produto:
    def __init__(self, product_dict: dict):
        self.codigo_erp = product_dict['CODIGO_ERP']
        self.parceiro = 1 # parceiro 1 = ERP
        self.codigo_referencia = product_dict['CODIGO_REFERENCIA']
        self.agrupador = product_dict['AGRUPADOR']
        self.nome = product_dict['NOME']
        self.descricao = product_dict['DESCRICAO']
        self.quantidade_minima = product_dict['QUANTIDADE_MINIMA']
        self.quantidade_maxima_compra = product_dict['QUANTIDADE_CAIXA']
        self.multiplo = product_dict['MULTIPLO']
        self.metakeyword = product_dict['METAKEYWORD']
        self.metadescription = product_dict['METADESCRIPTION']
        self.meses_garantia = product_dict['MESES_GARANTIA']
        self.modelo = product_dict['MODELO']
        self.tempo_adicional_entrega = product_dict['TEMPO_ADICIONAL_ENTREGA']
        self.ativo = bool(product_dict['ATIVO'])
        self.dimensoes = Dimensao(product_dict['PESO'], product_dict['ALTURA'], product_dict['LARGURA'], product_dict['COMPRIMENTO'], product_dict['VOLUME'])
        self.unidade_medida = UnidadeMedida(product_dict['MEDIDA_SIGLA'], product_dict['MEDIDA_DESCRICAO'], product_dict['MEDIDA_CODIGO'])
        self.ipi = product_dict['IPI']
        
        self.hierarquias_categoria = []
        if product_dict['NOME_CATEGORIA_N1'] is not None:
            self.hierarquias_categoria.append(NivelCategoria(product_dict['NOME_CATEGORIA_N1'], product_dict['CODIGO_CATEGORIA_N1'], None))
        
        if product_dict['NOME_CATEGORIA_N2'] is not None:
            self.hierarquias_categoria.append(NivelCategoria(product_dict['NOME_CATEGORIA_N2'], product_dict['CODIGO_CATEGORIA_N2'], product_dict['CODIGO_CATEGORIA_N1']))
        
        if product_dict['NOME_CATEGORIA_N3'] is not None:
            self.hierarquias_categoria.append(NivelCategoria(product_dict['NOME_CATEGORIA_N3'], product_dict['CODIGO_CATEGORIA_N3'], product_dict['CODIGO_CATEGORIA_N2']))
        
        if product_dict['NOME_CATEGORIA_N4'] is not None:
            self.hierarquias_categoria.append(NivelCategoria(product_dict['NOME_CATEGORIA_N4'], product_dict['CODIGO_CATEGORIA_N4'], product_dict['CODIGO_CATEGORIA_N3']))

        self.fabricante = Fabricante(product_dict['FABRICANTE_DESCRICAO'], product_dict['FABRICANTE_LINK_IMAGEM'], product_dict['FABRICANTE_CODIGO'])
        self.marca = Marca(product_dict['MARCA_DESCRICAO'], product_dict['MARCA_LINK_IMAGEM'], product_dict['MARCA_CODIGO'])
        
        self.atributos_produto = []
        hierarquia_atributo = []
        attr = None
        if product_dict['VARIACAO_OPCAO_1'] is not None and product_dict['VARIACAO_OPCAO_VALOR_1'] is not None:
            if product_dict['VARIACAO_OPCAO_2'] is not None and product_dict['VARIACAO_OPCAO_VALOR_2'] is not None:
                if product_dict['VARIACAO_OPCAO_3'] is not None and product_dict['VARIACAO_OPCAO_VALOR_3'] is not None:
                    attr = Atributo(product_dict['VARIACAO_OPCAO_1'], product_dict['VARIACAO_OPCAO_1'], product_dict['VARIACAO_OPCAO_VALOR_1'], 
                                Atributo(product_dict['VARIACAO_OPCAO_2'], product_dict['VARIACAO_OPCAO_2'], product_dict['VARIACAO_OPCAO_VALOR_2'], 
                                    Atributo(product_dict['VARIACAO_OPCAO_3'], product_dict['VARIACAO_OPCAO_3'], product_dict['VARIACAO_OPCAO_VALOR_3'], None)))
                    # hierarquia_atributo.append(product_dict['VARIACAO_OPCAO_VALOR_3'])
                else:
                    attr = Atributo(product_dict['VARIACAO_OPCAO_1'], product_dict['VARIACAO_OPCAO_1'], product_dict['VARIACAO_OPCAO_VALOR_1'], 
                                Atributo(product_dict['VARIACAO_OPCAO_2'], product_dict['VARIACAO_OPCAO_2'], product_dict['VARIACAO_OPCAO_VALOR_2'], None))
                    # hierarquia_atributo.append(product_dict['VARIACAO_OPCAO_VALOR_2'])
            else:
                attr = Atributo(product_dict['VARIACAO_OPCAO_1'], product_dict['VARIACAO_OPCAO_1'], product_dict['VARIACAO_OPCAO_VALOR_1'], None)
                # hierarquia_atributo.append(product_dict['VARIACAO_OPCAO_VALOR_1'])
                    
            if attr is not None:
                self.atributos_produto.append(attr)

        self.preco_estoque = [PrecoEstoque(product_dict['CODIGO_ERP_VARIACAO'], product_dict['SKU_VARIACAO'],
                                            None, product_dict['EAN_13_VARIACAO'], product_dict['EAN_14_VARIACAO'],
                                            product_dict['PRECO_ATUAL'], product_dict['PRECO_LISTA'], product_dict['PRECO_CUSTO'],
                                            product_dict['QUANTIDADE'], self.dimensoes, hierarquia_atributo)]
        
        
        self.outras_descricoes = []
        if product_dict['ADICIONA_DESCRICAO_1'] is not None and product_dict['ADICIONA_CONTEUDO_1'] is not None:
            self.outras_descricoes.append(InfoDescricao(product_dict['ADICIONA_DESCRICAO_1'], product_dict['ADICIONA_CONTEUDO_1'], 1))


    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
        

    def __repr__(self):
        return "<Produto id:%s, codigo_sku:%s>" % (self.id, self.codigo_sku)

    def __str__(self):
        return 'Produto id : %s, ' \
            'SKU : %s' % (self.id, self.codigo_sku)

class PrecoEstoque:
    def __init__(self, codigo_erp_atributo: str, codigo_referencia_atributo: str, codigo_erp_restock: str,
                 codigo_ean: str, codigo_ean14: str, preco: float, preco_lista: float, preco_custo: float, 
                 estoque: int, dimensoes, hierarquia_codigo_atributo):
        self.codigo_erp_atributo = codigo_erp_atributo
        self.codigo_referencia_atributo = codigo_referencia_atributo
        self.codigo_erp_restock = codigo_erp_restock
        self.codigo_ean = codigo_ean
        self.codigo_ean14 = codigo_ean14
        self.preco = preco
        self.preco_lista = preco_lista
        self.preco_custo = preco_custo
        self.estoque = estoque
        self.dimensoes = dimensoes
        self.hierarquia_codigo_atributo = hierarquia_codigo_atributo


class Dimensao:
    def __init__(self, peso, altura, largura, comprimento, volume):
        self.peso = peso
        self.altura = altura
        self.largura = largura
        self.comprimento = comprimento
        self.volume = volume
        

class ItemBrinde:
    def __init__(self, preco_atual, quantidade, desconto, produto_id,
                 codigo_externo, identificador_produto, codigo_referencia,
                 nome_produto, unidade_produto, identificador_atributo,
                 identificador_opcao_atributo, filial_expedicao,
                 filial_faturamento):
        self.preco_atual = preco_atual
        self.quantidade = quantidade
        self.desconto = desconto
        self.produto_id = produto_id
        self.codigo_externo = codigo_externo
        self.identificador_produto = identificador_produto
        self.codigo_referencia = codigo_referencia
        self.nome_produto = nome_produto
        self.unidade_produto = unidade_produto
        self.identificador_atributo = identificador_atributo
        self.identificador_opcao_atributo = identificador_opcao_atributo
        self.filial_expedicao = filial_expedicao
        self.filial_faturamento = filial_faturamento


class ItemPersonalizado:
    def __init__(self, id, preco_liquido, preco_bruto, texto):
        self.id = id
        self.preco_liquido = preco_liquido
        self.preco_bruto = preco_bruto
        self.texto = texto


def customProdutoDecoder(produtoDict):
    return Produto(**produtoDict)


class Medida:
    def __init__(self, volume, peso, altura, largura, comprimento):
        self.volume = volume
        self.peso = peso
        self.altura = altura
        self.largura = largura
        self.comprimento = comprimento


class UnidadeMedida:
    def __init__(self, sigla, descricao, codigo):
        self.sigla = sigla
        self.descricao = descricao
        self.codigo = codigo


class NivelCategoria:
    def __init__(self, nome, codigo, codigo_categoria_pai):
        self.nome = nome
        self.codigo = codigo
        self.codigo_categoria_pai = codigo_categoria_pai


class Fabricante:
    def __init__(self, nome, link_imagem, codigo):
        self.nome = nome
        self.link_imagem = link_imagem
        self.codigo = codigo


class Marca:
    def __init__(self, nome, link_imagem, codigo):
        self.nome = nome
        self.link_imagem = link_imagem
        self.codigo = codigo


class Atributo:
    def __init__(self, classificacao, opcao_descricao, opcao_codigo, atributo_pai):
        self.classificacao = classificacao
        self.opcao_descricao = opcao_descricao
        self.opcao_codigo = opcao_codigo
        self.atributo_pai = atributo_pai


class InfoDescricao:
    def __init__(self, descricao, conteudo, ordem):
        self.descricao = descricao
        self.conteudo = conteudo
        self.ordem = ordem


class InfoCaracteristica:
    def __init__(self, nome, valor):
        self.nome = nome
        self.valor = valor


class Estoque:
    def __init__(self, codigo_erp, quantidade):
        self.codigo_erp = codigo_erp
        self.quantidade = quantidade


class EstoqueUnidadeDistribuicao:
    def __init__(self, u_distribuicao, codigo_erp, produto_id,
                 total, reserva, protocolo, parceiro):
        self.unidade_distribuicao = u_distribuicao
        self.codigo_erp = codigo_erp
        self.produto_id = produto_id
        self.quantidade_total = total
        self.quantidade_reserva = reserva
        self.protocolo = protocolo
        self.parceiro = parceiro


class Preco:
    def __init__(self, codigo_erp_atributo, codigo_referencia_atributo,
                 codigo_erp_restock, codigo_ean, codigo_ean14, ativo,
                 preco, preco_lista, preco_custo, estoque):
        self.codigo_erp_atributo = codigo_erp_atributo
        self.codigo_referencia_atributo = codigo_referencia_atributo
        self.codigo_erp_restock = codigo_erp_restock
        self.codigo_ean = codigo_ean
        self.codigo_ean14 = codigo_ean14
        self.ativo = ativo
        self.preco = preco
        self.preco_lista = preco_lista
        self.preco_custo = preco_custo
        self.estoque = estoque
        self.dimensoes = None  # {Medida}
        self.hierarquia_codigo_atributo = []  # "string"
