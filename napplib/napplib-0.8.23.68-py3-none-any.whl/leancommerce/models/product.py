class Categories:
    def __init__(self, Nome='', Descricao='', CategoriaPaiId=0, Codigo=''):
        self.Nome = Nome
        self.Descricao = Descricao
        self.CategoriaPaiId = CategoriaPaiId
        self.Codigo = Codigo

class GridValue:
    def __init__(self, Valor='', Codigo=''):
        self.Valor = Valor
        self.Codigo = Codigo

class Grid:
    def __init__(self, Nome='', NomeExibicao='', Codigo='', Valores=[]):
        self.Nome = Nome
        self.NomeExibicao = NomeExibicao
        self.Codigo = Codigo
        self.Valores = Valores

class ProductGrid:
    def __init__(self, Id=0, Principal=True):
        self.Id = Id
        self.Principal = Principal

class Inventory:
    def __init__(self, Estoques=[]):
        self.Estoques = Estoques

class ProductInventory:
    def __init__(self, Sku='', Quantidade=''):
        self.Sku = Sku
        self.Quantidade = Quantidade

class Prices:
    def __init__(self, Precos=[]):
        self.Precos = Precos

class ProductPrices:
    def __init__(self, Sku='', PrecoVenda=0, PrecoCusto=0, PrecoPromocional=0):
        self.Sku = Sku
        self.PrecoVenda = PrecoVenda
        self.PrecoCusto = PrecoCusto
        self.PrecoPromocional = PrecoPromocional

class Variations:
    def __init__(self, Ativo= False, Sku= '', Estoque= 0, Gtin= '', Mpn= '',
      Ncm= '', PrecoVenda= 0, PrecoCusto= 0, PrecoPromocional= 0, Peso= 0,
      Altura= 0, Largura= 0, Profundidade= 0, GradeValores= []
    ):
        self.Ativo = Ativo
        self.Sku = Sku
        self.Estoque = Estoque
        self.Gtin = Gtin
        self.Mpn = Mpn
        self.Ncm = Ncm
        self.PrecoVenda = PrecoVenda
        self.PrecoCusto = PrecoCusto
        self.PrecoPromocional = PrecoPromocional
        self.Peso = Peso
        self.Altura = Altura
        self.Largura = Largura
        self.Profundidade = Profundidade
        self.GradeValores = GradeValores

class ProductImages:
    def __init__(self, UrlImagem='', Principal=False, GradeValores=[]):
        self.UrlImagem = UrlImagem
        self.Principal = Principal
        self.GradeValores = GradeValores

class Product:
    def __init__(self, 
        Ativo=False, Nome='', DescricaoGeral='', Marca='', Peso=0, Altura=0, Largura=0, Profundidade=0, CategoriaId=0, Grades=[],
        Variacoes=[], Codigo=''
    ):
        self.Ativo = Ativo
        self.Nome = Nome
        self.DescricaoGeral = DescricaoGeral
        self.Marca = Marca
        self.Peso = Peso
        self.Altura = Altura
        self.Largura = Largura
        self.Profundidade = Profundidade
        self.CategoriaId = CategoriaId
        self.Grades = Grades
        self.Variacoes = Variacoes
        self.Codigo = Codigo