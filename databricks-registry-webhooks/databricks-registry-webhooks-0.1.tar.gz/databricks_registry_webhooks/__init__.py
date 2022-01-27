from databricks_registry_webhooks.client import RegistryWebhooksClient
from databricks_registry_webhooks.entities import *
from databricks_registry_webhooks.utils.logging_utils import _configure_loggers
# Define a __version__ attribute for easy / conventional version checking
from databricks_registry_webhooks.version import VERSION as __version__

_configure_loggers(root_module_name=__name__)
