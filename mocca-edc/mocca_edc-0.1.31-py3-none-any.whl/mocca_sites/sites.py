from django.core.management import color_style
from edc_sites.single_site import SingleSite as BaseSingleSite

style = color_style()

fqdn = "mocca.clinicedc.org"


class SingleSite(BaseSingleSite):
    def __init__(self, *args, orig_site_id=None, **kwargs):
        self.orig_site_id = orig_site_id
        super().__init__(*args, **kwargs)


# site_id, name, **kwargs
all_sites = {
    "uganda": (
        SingleSite(
            119,
            "kisugu",
            title="Kisugu Hospital",
            orig_site_id=6,
            country_code="ug",
            country="uganda",
            domain=f"kisugu.ug.{fqdn}",
        ),
        SingleSite(
            120,
            "kiswa",
            title="Kiswa Hospital",
            orig_site_id=7,
            country_code="ug",
            country="uganda",
            domain=f"kiswa.ug.{fqdn}",
        ),
        SingleSite(
            121,
            "mulago",
            title="Mulago Hospital",
            country_code="ug",
            orig_site_id=8,
            country="uganda",
            domain=f"mulago.ug.{fqdn}",
        ),
        SingleSite(
            122,
            "ndejje",
            title="Ndejje Hospital",
            orig_site_id=9,
            country_code="ug",
            country="uganda",
            domain=f"ndejje.ug.{fqdn}",
        ),
        SingleSite(
            123,
            "wakiso",
            title="Wakiso Hospital",
            orig_site_id=10,
            country_code="ug",
            country="uganda",
            domain=f"wakiso.ug.{fqdn}",
        ),
    ),
    "tanzania": (
        SingleSite(
            220,
            "amana",
            title="Amana Hospital",
            orig_site_id=1,
            country="tanzania",
            country_code="tz",
            domain=f"amana.tz.{fqdn}",
        ),
        SingleSite(
            250,
            "bunju",
            title="Bunju Hospital",
            orig_site_id=2,
            country="tanzania",
            country_code="tz",
            domain=f"bunju.tz.{fqdn}",
        ),
        SingleSite(
            221,
            "hindu_mandal",
            title="Hindu Mandal Hospital",
            orig_site_id=3,
            country="tanzania",
            country_code="tz",
            domain=f"hindu-mandal.tz.{fqdn}",
        ),
        SingleSite(
            222,
            "mkuranga",
            title="Mkuranga Hospital",
            orig_site_id=4,
            country="tanzania",
            country_code="tz",
            domain=f"mkuranga.tz.{fqdn}",
        ),
        SingleSite(
            240,
            "mwananyamala",
            title="Mwananyamala Hospital",
            orig_site_id=5,
            country="tanzania",
            country_code="tz",
            domain=f"mwananyamala.tz.{fqdn}",
        ),
    ),
}
