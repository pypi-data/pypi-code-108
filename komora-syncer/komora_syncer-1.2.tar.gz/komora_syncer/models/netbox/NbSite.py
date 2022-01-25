from komora_syncer.models.netbox.NbLocation import NbLocation
from komora_syncer.models.netbox.NetboxBase import NetboxBase
from komora_syncer.config import get_config

from slugify import slugify

import logging
logger = logging.getLogger(__name__)


class NbSite(NetboxBase):
    def __init__(self, komora_obj):
        NetboxBase.__init__(self)
        # Locations are already flatten via Komora site obj
        self.site_locations = komora_obj.flatten_locations

        self.name = komora_obj.name
        self.slug = slugify(self.name)

        # netbox site description max length is 200
        self.description = ""
        self.comments = ""

        if len(komora_obj.description or "") > 200:
            self.comments = komora_obj.description
        else:
            self.description = str(
                komora_obj.description or "").replace("\n", " ").strip()

        self.physical_address = komora_obj.address.text if komora_obj.address else ""
        self.shipping_address = ""
        self.latitude = float(
            komora_obj.latitude) if komora_obj.latitude else None
        self.longitude = float(
            komora_obj.longitude) if komora_obj.longitude else None

        self.komora_id = komora_obj.id
        self.komora_url = f"{get_config()['komora']['KOMORA_URL']}/app/site/{self.komora_id}"

        # site id
        self.code = komora_obj.code
        # Types: Připojný bod, virtuální bod, etc
        self.type_name = komora_obj.typeName
        self.type_id = komora_obj.typeId

        self.api_object = None
        self.region = None
        self.tenant = None

        try:
            if komora_obj.address:
                municipality_komora_id = komora_obj.address.municipalityId

                if municipality_komora_id:
                    self.region = self.netbox.connection.dcim.regions.get(
                        cf_komora_id=municipality_komora_id)
        except Exception as e:
            logger.exception(
                f"Unable to find region {komora_obj.address} for site {self.name}")

        try:
            komora_org_id = komora_obj.organizationId

            if komora_org_id:
                self.tenant = self.netbox.connection.tenancy.tenants.get(
                    cf_komora_id=komora_org_id)
        except Exception as e:
            logger.exception(
                f"Unable to find tenant {komora_obj.organization} for site {self.name}")

    def find(self):
        # 1. lookup by KOMORA_ID
        if self.komora_id:
            try:
                netbox_site = self.netbox.connection.dcim.sites.get(
                    cf_komora_id=self.komora_id)
                if netbox_site:
                    self.api_object = netbox_site
                    return self.api_object
            except Exception as e:
                logger.exception(
                    f"Unable to get site by komora_id: {self.komora_id}")

        # 2. Lookup by name, if komora id is not preseted
            # - log a problem, when the name exists, but komora_id was not found
        try:
            netbox_site = self.netbox.connection.dcim.sites.get(
                name__ie=self.name)
            if netbox_site:
                logger.warning(
                    f"komora_id: {str(self.komora_id)} was not found, but Site {self.name} already exists")
                self.api_object = netbox_site
                return self.api_object

        except Exception as e:
            logger.exception(f"Unable to get site by name: {self.name}")

        return self.api_object

    def create(self):
        try:
            params = self.get_params()
            netbox_site = self.netbox.connection.dcim.sites.create(params)

            logger.info("Site: %s created sucessfully", self.name)
            self.api_object = netbox_site
        except Exception as e:
            logger.exception("Unable to create netbox site: %s", self.name)
            raise e

        return self.api_object

    def update(self, nb_site):
        try:
            if nb_site.update(self.get_params()):
                self.api_object = nb_site
                logger.info(f"Site: {self.name} updated successfuly")
        except Exception as e:
            logger.exception(f"Unable to update site {self.name}")

    def find_or_create(self):
        self.find()
        if not self.api_object():
            self.create()

        return self.api_object

    def synchronize(self):
        site = self.find()

        if site:
            self.update(site)
        else:
            self.create()

        # sync location of site
        for location in self.site_locations:
            parent = next((parent for parent in self.site_locations if parent.id ==
                          location.parentId), None) if location.parentId else None

            nb_location = NbLocation(location, parent, self.api_object)
            nb_location.synchronize()

    def get_params(self):
        params = {
            "name": self.name.strip(),
            "slug": self.slug,
            "description": self.description,
            "physical_address": self.physical_address,
            "shipping_address": self.shipping_address,
            "latitude": self.latitude,
            "longitude": self.longitude,
        }

        if self.komora_id:
            if type(params.get('custom_fields')) is dict:
                params['custom_fields']['komora_id'] = self.komora_id
                params['custom_fields']['komora_url'] = self.komora_url

                params['custom_fields']['code'] = self.code
                params['custom_fields']['type'] = self.type_name
            else:
                params['custom_fields'] = {"komora_id": self.komora_id,
                                           "komora_url": self.komora_url,
                                           "code": self.code,
                                           "type": self.type_name}

        if self.region:
            params['region'] = self.region.id

        if self.tenant:
            params['tenant'] = self.tenant.id

        return params
