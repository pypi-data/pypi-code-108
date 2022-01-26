class IfoodMercadoProduct:
    idLoja: int
    departamento: str
    categoria: str
    subCategoria: str
    marca: str
    unidade: str
    volume: str
    codigoBarra: str
    nome: str
    valor: int
    valorPromocao: int
    valorAtacado: int
    valorCompra: int
    quantidadeEstoqueAtual: int
    quantidadeEstoqueMinimo: int
    quantidadeAtacado: int
    descricao: str
    ativo: bool
    plu: str
    validade_proxima: bool
    image_url: str

    def __init__(self, idLoja: int, departamento: str, categoria: str, subCategoria: str, marca: str, unidade: str, volume: str, codigoBarra: str, nome: str, valor: int, valorPromocao: int, valorAtacado: int, valorCompra: int, quantidadeEstoqueAtual: int, quantidadeEstoqueMinimo: int, quantidadeAtacado: int, descricao: str, ativo: bool, plu: str, validadeProxima: bool, image_url: str) -> None:
        self.idLoja = idLoja
        self.departamento = departamento
        self.categoria = categoria
        self.subCategoria = subCategoria
        self.marca = marca
        self.unidade = unidade
        self.volume = volume
        self.codigoBarra = codigoBarra
        self.nome = nome
        self.valor = valor
        self.valorPromocao = valorPromocao
        self.valorAtacado = valorAtacado
        self.valorCompra = valorCompra
        self.quantidadeEstoqueAtual = quantidadeEstoqueAtual
        self.quantidadeEstoqueMinimo = quantidadeEstoqueMinimo
        self.quantidadeAtacado = quantidadeAtacado
        self.descricao = descricao
        self.ativo = ativo
        self.plu = plu
        self.validadeProxima = validadeProxima
        self.image_url = image_url
