from .base import BaseModel, ObjectListModel

class Klant(BaseModel):
    
    def __init__(self,
        klantennummer=None,
        aanspreektitel=None,
        voornaam=None,
        achternaam=None,
        straat=None,
        huisnummer=None,
        busnummer=None,
        postcode=None,
        plaats=None,
        land=None,
        geboortedatum=None,
        geboorteplaats=None,
        is_bedrijf=None,
        bedrijfsnaam=None,
        BTW_nummer=None,
        ondernemingsnummer=None
    ):

        super().__init__()

        self.klantennummer = klantennummer
        self.aanspreektitel = aanspreektitel
        self.voornaam = voornaam
        self.achternaam = achternaam
        self.straat = straat
        self.huisnummer = huisnummer
        self.busnummer = busnummer
        self.postcode = postcode
        self.plaats = plaats
        self.land = land
        self.geboortedatum = geboortedatum
        self.geboorteplaats = geboorteplaats
        self.is_bedrijf = is_bedrijf
        self.bedrijfsnaam = bedrijfsnaam
        self.BTW_nummer = BTW_nummer
        self.ondernemingsnummer = ondernemingsnummer

class Klanten(ObjectListModel):
    def __init__(self):
        super().__init__(list=[], listObject=Klant)
