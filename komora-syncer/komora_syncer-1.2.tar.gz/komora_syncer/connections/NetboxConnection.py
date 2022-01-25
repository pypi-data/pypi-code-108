from komora_syncer.config import get_config
import pynetbox
import logging
logger = logging.getLogger(__name__)


class NetboxConnection:
    def __init__(self):
        self.netbox_url = get_config()['netbox']['NETBOX_INSTANCE_URL']
        self.api_token = get_config()['netbox']['NETBOX_API_TOKEN']
        self.connection = None

    # https://pynetbox.readthedocs.io/en/latest/endpoint.html
    def open(self):
        try:
            # private_key_file='/path/to/private-key.pem',
            self.connection = pynetbox.api(
                self.netbox_url, token=self.api_token)
        except Exception as e:
            logger.exception("Could not establish connection to pynetbox")
            raise e
