import logging
import os

from botocore.client import Config

logger = logging.getLogger()
FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)
logger.setLevel(os.environ.get("logLevel", "INFO"))


REGION_NAME = os.environ.get("AWS_REGION")

# Default boto3 config, will prevent long timeouts
BOTO3_CONFIG = Config(connect_timeout=5, retries={"max_attempts": 10})
