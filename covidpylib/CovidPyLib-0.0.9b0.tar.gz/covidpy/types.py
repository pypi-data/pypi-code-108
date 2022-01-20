# Copyright (c) 2022, CovidPyLib
# This file is part of CovidPy v0.0.9.
#
# The project has been distributed in the hope it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# You can use it and/or modify it under the terms of the GNU General Public License v3.0 or later.
# You should have received a copy of the GNU General Public License along with the project.

import io
from qrcode.image.pil import PilImage


pfizer_recc = """Comirnaty 30 micrograms/dose concentrate for dispersion for injection is indicated for active immunisation to prevent COVID-19 caused by SARS-CoV-2 virus, in individuals 12 years of age and older.

Comirnaty 30 micrograms/dose dispersion for injection is indicated for active immunisation to prevent COVID-19 caused by SARS-CoV-2 virus, in individuals 12 years of age and older.

Comirnaty 10 micrograms/dose concentrate for dispersion for injection is indicated for active immunisation to prevent COVID-19 caused by SARS-CoV-2 virus, in children aged 5 to 11 years.

The use of this vaccine should be in accordance with official recommendations."""

janssen_recc = """COVID-19 Vaccine Janssen is indicated for active immunisation to prevent COVID-19 caused by SARS-CoV-2 in individuals 18 years of age and older.

The use of this vaccine should be in accordance with official recommendations."""

novavax_recc = """Nuvaxovid is indicated for active immunisation to prevent COVID-19 caused by SARS-CoV-2 in individuals 18 years of age and older.

The use of this vaccine should be in accordance with official recommendations."""

moderna_recc = """Spikevax is indicated for active immunisation to prevent COVID-19 caused by SARS-CoV-2 in individuals 12 years of age and older.

The use of this vaccine should be in accordance with official recommendations."""

az_recc = """Vaxzevria is indicated for active immunisation to prevent COVID 19 caused by SARS CoV 2, in individuals 18 years of age and older.
The use of this vaccine should be in accordance with official recommendations."""

class QRCode:
    def __init__(
        self, img: PilImage, rawdata: dict, in_blacklist: bool, instance
    ) -> None:
        super().__init__()
        self.raw_data = rawdata
        self.pil_img = img
        self.in_blacklist = in_blacklist
        self.__cpyinstance = instance

    def save(self, path: str):
        self.pil_img.save(path)

    def to_bytesio(self) -> io.BytesIO:
        bio = io.BytesIO()
        self.pil_img.save(bio)
        return bio

    def decode(self):
        self.__cpyinstance.decode(self)

    def verify(self):
        self.__cpyinstance.verify(self)
class VerifyResult:
    def __init__(self, is_valid: bool, is_revoked: bool):
        self.valid = is_valid
        self.revoked = is_revoked

class Person:
    def __init__(self, jsonp, date) -> None:
        self.raw_data = [jsonp, date]
        self.first_name = jsonp["fn"]
        self.last_name = jsonp["gn"]
        self.date_of_birth = jsonp["dob"]
        self.formatted_first_name = jsonp["fnt"]
        self.formatted_last_name = jsonp["gnt"]
    def __str__(self):
        return {
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth,
            'formatted_first_name': self.formatted_first_name,
            'formatted_last_name': self.formatted_last_name
        }
    
class VaccinationCertificateInfo:
    def __init__(self, jsoni) -> None:
        raise NotImplementedError("VaccineCertificateInfo is not implemented yet")

class RecoveryCertificateInfo:
    def __init__(self, jsoni) -> None:
        raise NotImplementedError("RecoveryCertificateInfo is not implemented yet")

class TestCertificateInfo:
    def __init__(self, jsoni) -> None:
        raise NotImplementedError("TestCertificateInfo is not implemented yet")

class VaccineInfo:
    def __init__(self, codename=None,knownas=None,name=None,productor=None,indications=None,substance=None,emalink=None) -> None:
        self.eu_codename = codename
        self.known_as = knownas
        self.vaccine_name = name
        self.productor_name = productor
        self.eu_indications = indications
        self.active_substance = substance
        self.ema_link = emalink

eu_codenames:dict = {
        'EU/1/20/1528': VaccineInfo('EU/1/20/1528', 'Pfizer', 'Comirnaty', 'BioNTech Manufacturing GmbH', pfizer_recc, 'tozinameran, COVID-19 mRNA vaccine (nucleoside-modified)', 'https://www.ema.europa.eu/en/medicines/human/summaries-opinion/comirnaty'),
        'EU/1/20/1525': VaccineInfo('EU/1/20/1525', 'Janssen', 'COVID-19 Vaccine Janssen', 'Janssen-Cilag International NV', janssen_recc, 'COVID-19 vaccine (Ad26.COV2-S [recombinant])', 'https://www.ema.europa.eu/en/medicines/human/EPAR/covid-19-vaccine-janssen'),
        'EU/1/21/1618': VaccineInfo('EU/1/21/1618', 'Novavax', 'Nuvaxovid', 'Novavax CZ, a.s.', novavax_recc, 'COVID-19 Vaccine (recombinant, adjuvanted)', None),
        'EU/1/20/1507': VaccineInfo('EU/1/20/1507', 'Moderna', 'Spikevax', 'MODERNA BIOTECH SPAIN, S.L.', moderna_recc, 'COVID-19 mRNA Vaccine (nucleoside modified)', 'https://www.ema.europa.eu/en/medicines/human/summaries-opinion/covid-19-vaccine-moderna'),
        'EU/1/21/1529': VaccineInfo('EU/1/21/1529', 'AstraZeneca', 'Vaxzevria', 'AstraZeneca AB', az_recc, 'COVID-19 Vaccine (ChAdOx1-S [recombinant])', 'https://www.ema.europa.eu/en/medicines/human/EPAR/vaxzevria-previously-covid-19-vaccine-astrazeneca')
}

class Certificate:
    def __init__(self, jsoncert:dict) -> None:
        self.raw_data = jsoncert
        self.country_code = jsoncert[1]
        self.owner = Person(jsoncert[-261][1]['nam'], jsoncert[-261][1]['dob'])
        self.version = jsoncert[-261][1]['ver']
        self.ceritificate_type = None
        self.vaccination_info = None
        self.recovery_info = None
        self.test_info = None
        if self.jsoncert.get('v', None):
            self.ceritificate_type = 'vaccine'
            self.vaccination_info = [VaccinationCertificateInfo(x) for x in self.jsoncert['v']]
        elif self.jsoncert.get('r', None):
            self.ceritificate_type = 'recovery'
            self.recovery_info = [RecoveryCertificateInfo(x) for x in self.jsoncert['r']]
        elif self.jsoncert.get('t', None):
            self.ceritificate_type = 'test'
            self.test_info = [TestCertificateInfo(x) for x in self.jsoncert['t']]
