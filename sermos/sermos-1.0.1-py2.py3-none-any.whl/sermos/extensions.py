""" Initialize most extensions used throughout application
"""
import logging

logger = logging.getLogger(__name__)

try:
    # Client packages *should* provide a `sermos.yaml` file. This
    # loads the configuration file with the provided name ofthe client
    # package (e.g. sermos_demo_client)
    from sermos.sermos_yaml import load_client_config_and_version
    sermos_config, sermos_client_version = load_client_config_and_version()
except Exception as e:
    sermos_config = None
    sermos_client_version = None
    logger.warning("Unable to load client Sermos config ... {}".format(e))
