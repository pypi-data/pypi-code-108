from .base import BaseModel, ObjectListModel

class Artikel(BaseModel):
    
    def __init__(self,
        naam=None,
        beschrijving=None,
        SKU=None,
        voorraad_bijhouden=None,
        op_voorraad=None,
        product_url=None,
        verkoopprijs_excl=None,
        verkoopprijs_incl=None,
        inkoopprijs_excl=None,
        inkoopprijs_incl=None,
        bestellingtype=None,
        units_per_bestelling=None,
        BTW=None,
        status=None
    ):

        super().__init__()

        self.naam = naam
        self.beschrijving = beschrijving
        self.SKU = SKU
        self.voorraad_bijhouden = voorraad_bijhouden
        self.op_voorraad = op_voorraad
        self.product_url = product_url
        self.verkoopprijs_excl = verkoopprijs_excl
        self.verkoopprijs_incl = verkoopprijs_incl
        self.inkoopprijs_excl = inkoopprijs_excl
        self.inkoopprijs_incl = inkoopprijs_incl
        self.bestellingtype = bestellingtype
        self.units_per_bestelling = units_per_bestelling
        self.BTW = BTW
        self.status = status

class Artikels(ObjectListModel):
    def __init__(self):
        super().__init__(list=[], listObject=Artikel)
