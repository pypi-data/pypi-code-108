""" Primary CLI group entrypoint
"""
import logging
import click
from sermos.logging_config import setup_logging

setup_logging(default_level='INFO', establish_logging_config=False)
logger = logging.getLogger(__name__)

# Not all CLI tools will be functional / available depending on which extras
# are installed. For example, the config server won't work if the `workers`
# extra isn't available, which installs celery and networkx.
collection = []

warning_msg = "{} CLI tools are not available. This is most "\
               "likely due to a missing import. Verify you have the correct "\
               "Sermos extras installed."
try:
    from sermos.cli.deploy import deployment
    collection.append(deployment)
except ImportError as e:
    logger.warning(warning_msg.format("Deployment"))
    logger.warning(f"{e}")

try:
    from sermos.cli.config_server import config_server
    collection.append(config_server)
except ImportError as e:
    logger.warning(warning_msg.format("Configuration Server"))
    logger.warning(f"{e}")

try:
    from sermos.cli.proxy import sermos_proxy
    collection.append(sermos_proxy)
except ImportError as e:
    logger.warning(warning_msg.format("Proxy Service"))
    logger.warning(f"{e}")

sermos = click.CommandCollection(sources=collection)
