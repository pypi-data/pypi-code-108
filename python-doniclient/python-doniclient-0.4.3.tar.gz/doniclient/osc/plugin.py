"""Module for OpenStackClient Integration."""
import logging

from keystoneauth1 import adapter
from osc_lib import utils

LOG = logging.getLogger(__name__)  # Get the logger of this module

DEFAULT_API_VERSION = "1"

# Required by the OSC plugin interface
API_NAME = "inventory"
API_VERSION_OPTION = "os_inventory_api_version"

# Maps api version from service catalog to class path
API_VERSIONS = {
    "1": "doniclient.v1.client.Client",
}
# Required by the OSC plugin interface
def make_client(instance):
    """Returns a client to the ClientManager.

    Called to instantiate the requested client version.  instance has
    any available auth info that may be required to prepare the client.

    :param ClientManager instance: The ClientManager that owns the new client
    """
    version = instance._api_version[API_NAME]
    inventory_client = utils.get_client_class(
        api_name=API_NAME,
        version=version,
        version_map=API_VERSIONS,
    )

    LOG.debug("Instantiating inventory client: %s", inventory_client)

    ksa_adapter = adapter.Adapter(
        session=instance.session, service_type="inventory", interface="public"
    )

    client = inventory_client(adapter=ksa_adapter)

    return client


# Required by the OSC plugin interface
def build_option_parser(parser):
    """Hook to add global options.

    Called from openstackclient.shell.OpenStackShell.__init__()
    after the builtin parser has been initialized.  This is
    where a plugin can add global options such as an API version setting.

    :param argparse.ArgumentParser parser: The parser object that has been
        initialized by OpenStackShell.
    """
    parser.add_argument(
        "--os-oscplugin-api-version",
        metavar="<oscplugin-api-version>",
        help="OSC Plugin API version, default="
        + DEFAULT_API_VERSION
        + " (Env: OS_OSCPLUGIN_API_VERSION)",
    )
    return parser
