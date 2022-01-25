from komora_syncer.config import get_config
import requests
import traceback

from komora_syncer.models.komora.organization import Organization
from komora_syncer.models.komora.region import Region
from komora_syncer.models.komora.district import District
from komora_syncer.models.komora.municipality import Municipality
from komora_syncer.models.komora.site import Site
from komora_syncer.models.komora.device import Device
from komora_syncer.models.komora.contact import Contact

import hmac
import hashlib
import time
import base64
import urllib.parse
import json
import time


import logging
# Log Warnings and higher errors from imported modules
logging.getLogger(requests.__name__).setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class KomoraApi:
    def __init__(self):
        self.sites = []
        self.regions = []
        self.districts = []
        self.municipalities = []
        self.organizations = []
        self.contacts = []
        self.devices = []

    def checkout_url(model, params=""):
        private_key, sign_app = get_config()['komora']['PRIVATE_KEY'], get_config()[
            'komora']['SIGN_APP']
        komora_url = get_config()['komora']['KOMORA_API_URL']

        base_url = f"{komora_url}/{model}"
        signDate = str(int(time.time()))

        if params:
            params = f"?{params}&signApp={sign_app}&signDate={signDate}"
        else:
            params = f"?signApp={sign_app}&signDate={signDate}"

        digest = hmac.new(bytes(private_key, "utf-8"),
                          msg=str.encode(params), digestmod=hashlib.sha256).digest()
        signature = base64.b64encode(digest).decode()
        parsed_signature = urllib.parse.quote_plus(signature)

        result_url = f"{base_url}{params}&signHash={parsed_signature}"
        return result_url

    # TODO: catch errors
    def get_sites(self):
        if self.sites:
            return self.sites

        url = KomoraApi.checkout_url("Site", "")

        try:
            logger.info("Polling sites from Komora")
            response = requests.get(url)
            response.raise_for_status()
        except Exception as e:
            logger.error(f"Unable to poll sites from Komora\n{e}")
            logger.debug(f"URL: {url}")
            logger.debug(traceback.format_exc())
            raise e
        else:
            response = response.json()

        for site in response.get("data", []):
            self.sites.append(Site(**site))

        return self.sites

    def get_organizations(self):
        if self.organizations:
            return self.organizations

        filter = ''  # filter = 'filters.isCustomer=true'
        url = KomoraApi.checkout_url("Organization", filter)

        try:
            logger.info("Polling organizations from Komora")
            response = requests.get(url)
            response.raise_for_status()
        except Exception as e:
            logger.exception("Unable to poll organizations from Komora")
            logger.debug(f"URL: {url}")
            raise e
        else:
            response = response.json()

        for organization in response.get("data", []):
            self.organizations.append(Organization(**organization))

        return self.organizations

    def get_regions(self):
        if self.regions:
            return self.regions

        api = 'Ruian/region'

        try:
            logger.info("Polling regions from Komora")
            for reg in KomoraApi.__get_paged_records(api):
                self.regions.append(Region(**reg))
        except Exception as e:
            logger.error(f"Unable to poll regions from Komora\n{e}")
            logger.debug(traceback.format_exc())
            raise e
        return self.regions

    def get_districts(self):
        if self.districts:
            return self.districts

        api = 'Ruian/district'

        try:
            logger.info("Polling districts from Komora")
            for dis in KomoraApi.__get_paged_records(api):
                self.districts.append(District(**dis))
        except Exception as e:
            logger.exception("Unable to poll districts from Komora")
            raise e

        return self.districts

    def get_municipalities(self):
        if self.municipalities:
            return self.municipalities

        api = "Ruian/municipality"

        try:
            logger.info("Polling municipalities from Komora")
            for muni in KomoraApi.__get_paged_records(api):
                self.municipalities.append(Municipality(**muni))
        except Exception as e:
            logger.exception("Unable to poll municipalities from Komora")
            raise e

        return self.municipalities

    def get_devices(self):
        if self.devices:
            return self.devices

        api = "Device"

        try:
            logger.info("Polling devices from Komora")
            for dev in KomoraApi.__get_paged_records(api):
                self.devices.append(Device(**dev))
        except Exception as e:
            logger.exception("Unable to poll devices from Komora")
            raise e

        return self.devices

    def post_devices(self, nb_devices):
        api = "ServiceRecord/SendDeviceData"
        url = KomoraApi.checkout_url(api)

        # nb_devices save to file
        # TODO: filepath - move to config
        timestr = time.strftime("%Y%m%d-%H%M%S")
        filename = f"{timestr}_devices.json"
        filepath = get_config()['common']['DEVICES_DATA_PATH']
        file = filepath+filename

        with open(file, 'w') as outfile:
            json.dump(nb_devices, outfile)

        try:
            logger.info("Posting devices to Komora")
            requests.post(url, files={'dataFile': open(file, 'rb')})
        except Exception as e:
            logger.exception("Unable to post devices to Komora")
            raise e

    def get_contacts(self):
        if self.contacts:
            return self.contacts

        filter = ''  # filter = 'filters.isCustomer=true'
        url = KomoraApi.checkout_url("Contact", filter)

        try:
            logger.info("Polling contacts from Komora")
            response = requests.get(url)
            response.raise_for_status()
        except Exception as e:
            logger.exception("Unable to poll contacts from Komora")
            logger.debug(f"URL: {url}")
            raise e
        else:
            response = response.json()

        for contact in response.get("data", []):
            self.contacts.append(Contact(**contact))

        return self.contacts

    def __get_page(api, page, page_size):
        params = f"Page={page}&PageSize={page_size}"
        url = KomoraApi.checkout_url(api, params)

        try:
            response = requests.get(url)
            response.raise_for_status()
        except Exception as e:
            logger.exception("Unable to get page")
            logger.debug(f"URL {url}")
            raise e
        else:
            response = response.json()
            result = response.get('data', [])

            # Check number of all records
            total = response.get('total', 0)

            return result, int(total)

    def __get_paged_records(api):
        page_size = 100
        page = 0

        # load first page
        record_list, total = KomoraApi.__get_page(api, page, page_size)

        # if less records are returned than total number of records -> get rest of records
        if len(record_list) < total:
            last_page = int((total/page_size))

            for page in range(1, last_page + 1):
                next_data = KomoraApi.__get_page(api, page, page_size)[0]
                record_list.extend(next_data)

        if len(record_list) == total:
            return record_list
        # TODO: generate proper error
        else:
            raise Exception
