from komora_syncer.models.netbox.NetboxBase import NetboxBase
from slugify import slugify

import logging
logger = logging.getLogger(__name__)


class NbRegion(NetboxBase):
    # Types = region, district, municipality
    def __init__(self, komora_obj=None, type=None):
        # TODO:
        if type not in ['region', 'district', 'municipality']:
            raise Exception

        NetboxBase.__init__(self)
        self.api_object = None

        self.name = komora_obj.name
        self.slug = slugify(self.name)
        self.komora_id = komora_obj.id
        self.region_type = type

        if type == 'region':
            parent = "CZ"
            self.find_parent(parent, "state")
        elif type == 'district':
            parent = komora_obj.regionName
            self.find_parent(parent, "region")
        elif type == 'municipality':
            parent = komora_obj.districtName
            self.find_parent(parent, "district")

    def find_parent(self, parent, region_type):
        try:
            if parent:
                self.parent = self.netbox.connection.dcim.regions.get(
                    name=parent, cf_region_type=region_type, cf_komora_id__n=self.komora_id)

            else:
                self.parent = None
        except Exception as e:
            logger.exception(f"Parent region {parent} does not exists")
            self.parent = None

    def find_or_create(self):
        self.find()
        if not self.api_object():
            self.create()

        return self.api_object

    def find(self):
        if self.komora_id:
            try:
                netbox_region = self.netbox.connection.dcim.regions.get(
                    cf_komora_id=self.komora_id)

                if netbox_region:
                    self.api_object = netbox_region
                    return self.api_object
            except Exception as e:
                logger.exception(
                    f"Unable to find region by komora_id: {self.komora_id}")

    def create(self):
        try:
            netbox_region_param = self.get_params()
            netbox_region = self.netbox.connection.dcim.regions.create(
                netbox_region_param)

            logger.info("Region: %s created sucessfully", self.name)
            self.api_object = netbox_region
        except Exception as e:
            logger.exception("Unable to create netbox site: %s", self.name)
            raise e

        return self.api_object

    def update(self, nb_region):
        try:
            if nb_region.update(self.get_params()):
                self.api_object = nb_region
                logger.info(f"Region: {self.name} updated successfuly")
        except Exception as e:
            logger.exception(f"Unable to update region {self.name}")
            raise e

    def synchronize(self):
        region = self.find()

        if region:
            self.update(region)
        else:
            self.create()

    def get_params(self):
        params = {'name': self.name,
                  'slug': self.slug}

        if self.parent:
            params['parent'] = self.parent.id

        if self.komora_id:
            if type(params.get('custom_fields')) is dict:
                params['custom_fields']['komora_id'] = self.komora_id
            else:
                params['custom_fields'] = {"komora_id": self.komora_id}

        if self.region_type:
            if type(params.get('custom_fields')) is dict:
                params['custom_fields']['region_type'] = self.region_type
            else:
                params['custom_fields'] = {"region_type": self.region_type}
        return params
