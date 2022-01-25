#from pynetbox import RequestError
from komora_syncer.models.netbox.NetboxBase import NetboxBase
from slugify import slugify
from komora_syncer.helpers.utils import build_tenant_name

import traceback
import logging
logger = logging.getLogger(__name__)


class NbTenant(NetboxBase):
    def __init__(self, komora_obj=None):
        NetboxBase.__init__(self)

        self.name = build_tenant_name(komora_obj.clientId, komora_obj.name)
        self.slug = slugify(self.name)
        self.description = komora_obj.vipNote

        # Komora returns description as space
        if self.description.isspace():
            self.description = ""
        self.custom_fields = {
            "client_id": komora_obj.clientId,
            "komora_id": komora_obj.id,
            "client_name": komora_obj.name
        }

        # TODO: Remove
        if komora_obj.isCustomer == True:
            self.description += ";isCustomer;"

        self.description = self.description.strip()
        self.api_object = None

    def find_or_create(self):
        self.find()
        if not self.api_object():
            self.create()

        return self.api_object

    def find(self):
        # 1. lookup by KOMORA_ID
        # 2. Lookup by name, if komora id is not preseted
        # - log a problem, when the name exists, but komora_id was not found

        komora_id = self.custom_fields.get("komora_id", None)

        if komora_id:
            try:
                netbox_tenant = self.netbox.connection.tenancy.tenants.get(
                    cf_komora_id=komora_id)
                if netbox_tenant:
                    self.api_object = netbox_tenant
            # TODO:
            #except RequestError as e:
            #    logger.error(f"Unable to complete request - {e}")
            #    logger.debug(e)
            #    raise(e)
            except Exception as e:
                logger.exception(f"Unable to find tenant by komora_id: {komora_id}")
                raise(e)
        else:
            try:
                netbox_tenant = self.netbox.connection.tenancy.tenants.get(
                    name__ie=self.name)

                if netbox_tenant:
                    logger.warning(
                        f"komora_id: {str(komora_id)} was not found, but Tenant {self.name} already exists")
                    self.api_object = netbox_tenant
            except Exception as e:
                logger.exception(f"Unable to find tenant by name: {self.name}")
                raise(e)

        return self.api_object

    def create(self):
        try:
            params = self.get_params()
            netbox_tenant = self.netbox.connection.tenancy.tenants.create(
                params)

            logger.info("Region: %s created sucessfully", self.name)
            self.api_object = netbox_tenant
        except Exception as e:
            # TODO: Univerzita Tomáše Bati ve Zlíně, Fakulta aplikované informatiky - exists multiple times
            logger.error(f"Unable to create netbox tenant: {self.name}\n{e}")
            logger.debug(f"{traceback.format_exc()}")


        return self.api_object

    def update(self, nb_tenant):
        try:
            if nb_tenant.update(self.get_params()):
                self.api_object = nb_tenant
                logger.info(f"Tenant: {self.name} updated successfuly")
        except Exception as e:
            logger.error(e)
            raise e

    def synchronize(self):
        tenant = self.find()

        if tenant:
            self.update(tenant)
        else:
            self.create()

    def get_params(self):
        params = {'name': self.name,
                  'slug': self.slug,
                  'description': self.description,
                  'custom_fields': self.custom_fields}

        return params
