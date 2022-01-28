from json import JSONDecodeError
import etl

logger = etl.LOGGER


def check_if_response_is_ok(response):
    if 200 < response.status_code >= 300:
        logger.error("Request failed with code %d.", response.status_code)
        try:
            logger.error(response.json().get("message"), stack_info=True)
            logger.debug(response.text)
        except JSONDecodeError:
            logger.error(response.text, stack_info=True)
        finally:
            raise(ConnectionError("Failed to get valid response"))
    return True
