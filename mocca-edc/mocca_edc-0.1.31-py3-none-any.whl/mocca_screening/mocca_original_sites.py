from edc_sites import get_current_country


class Site:
    def __init__(self, name, title, site_id, enrolled, regex, country):
        self.name = name
        self.title = title
        self.site_id = site_id
        self.enrolled = enrolled
        self.regex = regex
        self.country = country

    def __repr__(self):
        return f"{self.__class__.__name__}(`{self.name}`)"

    def __str__(self):
        return self.name


sites = {
    "amana": Site("amana", "Amana", 1, 237, r"^060[0-9]{3}", "tanzania"),
    "bunju": Site("bunju", "Bunju", 2, 118, r"^080[0-9]{3}", "tanzania"),
    "hindu_mandal": Site("hindu_mandal", "Hindu Mandal", 3, 223, r"^070[0-9]{3}", "tanzania"),
    "mkuranga": Site("mkuranga", "Mkuranga", 4, 117, r"^100[0-9]{3}", "tanzania"),
    "mwananyamala": Site("mwananyamala", "Mwananyamala", 5, 117, r"^090[0-9]{3}", "tanzania"),
    "kisugu": Site("kisugu", "Kisugu", 6, 179, r"^04\-0[0-9]{3}", "uganda"),
    "kiswa": Site("kiswa", "Kiswa", 7, 191, r"^05\-0[0-9]{3}", "uganda"),
    "mulago": Site("mulago", "Mulago", 8, 257, r"^01\-0[0-9]{3}", "uganda"),
    "ndejje": Site("ndejje", "Ndejje", 9, 247, r"^03\-0[0-9]{3}", "uganda"),
    "wakiso": Site("wakiso", "Wakiso", 10, 225, r"^02\-0[0-9]{3}", "uganda"),
}


def get_mocca_sites_by_country(country=None):
    return {k: v for k, v in sites.items() if v.country == country}


def get_mocca_site_limited_to():
    return {
        "name__in": [
            site.name for site in sites.values() if site.country == get_current_country()
        ]
    }
