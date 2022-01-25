import zeep
import time
from loguru import logger


class DaData(object):
    def __init__(self, host: str):
        self._host = host

    def get_data(self, address: str, errors: int = 0, max_errors: int = 3, only_dadata: bool = False):
        while errors < max_errors:
            try:
                _client = zeep.Client(self._host)
                data = {"requestAddress": address, "onlyDadata": only_dadata}

                _response = _client.service.getAddress(input=data)
                return _response

            except Exception as ex:
                logger.error(ex)
                errors += 1
                time.sleep(2)
