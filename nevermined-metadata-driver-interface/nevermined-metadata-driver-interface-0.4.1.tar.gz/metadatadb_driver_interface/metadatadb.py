from metadatadb_driver_interface.constants import CONFIG_OPTION
from metadatadb_driver_interface.utils import start_plugin


class MetadataDb:
    """High-level, plugin-bound Metadata DB functions.
    Instantiated with an subclass implementing the ledger plugin
    interface (:class:`~.AbstractPlugin`) that will automatically be
    bound to all top-level functions:
        - :attr:`type` (as a read-only property)
        - :func:`write`
        - :func:`read`
        - :func:`update`
        - :func:`delete`
        - :func:`list`
    Attributes:
        plugin (Plugin): Bound persistence layer plugin.
    """

    def __init__(self, file_path=None, config_option=CONFIG_OPTION):
        self.plugin = start_plugin(file_path, config_option)