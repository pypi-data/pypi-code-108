from typing import NamedTuple, Any, Optional, Type, List
from .scpi_transport_base import ScpiTransports, ScpiTransportBase
import logging

_logger = logging.getLogger(__name__)


class ScpiResource(NamedTuple):
    """A SCPI resource object"""
    transport: Type[ScpiTransports]
    """Transport of the SCPI resource"""
    address: Any
    """address (e.g. TCP/IP hostname/port) of resource"""
    location: Optional[str] = None
    """Location (e.g. USB bus hierarchy) of resource"""
    name: Optional[str] = None
    """Descriptive name of resource"""
    manufacturer: Optional[str] = None
    """Descriptive manufacturer string of resource"""
    model: Optional[str] = None
    """Model description of resource"""
    serialnum: Optional[str] = None
    """Serial number of resource"""
    info: Optional[Any] = None

    @classmethod
    def discover(cls, transports: Optional[List[Type[ScpiTransports]]] = None, **kwargs) -> List['ScpiResource']:
        """Find SCPI devices connected to system.

        By default lists all available possible SCPI devices. However behaviour can be controlled using
        kwargs supported by the transport classes.
        """
        if transports is None: transports = ScpiTransportBase.__subclasses__()

        resources = []

        for transport in transports:
            # filter keyword arguments accepted by transport and call transport's find_devices method
            args = {k:v for k, v in kwargs.items() if k in transport.discover.__code__.co_varnames}
            argstr = ", ".join(["{}={}".format(k, v) for k,v in args.items()])

            try:
                new = transport.discover(**args)
                resources += new
                _logger.debug(
                    f'Running discover({argstr}) on {transport._transport_class}: {len(new)} resources found')
            except Exception as e:
                _logger.warning(
                    f'Exception during discover({argstr}) on {transport._transport_class}: {str(e)}')

        return resources

    @classmethod
    def from_resource_name(cls, resource_name: str, transports: Optional[List[Type[ScpiTransports]]] = None) -> 'ScpiResource':
        """Create resource object for a device using a VISA resource name"""
        if transports is None: transports = ScpiTransportBase.__subclasses__()

        for transport in transports:
            # Find a transport that accepts resource name
            try:
                resource = transport.from_resource_name(resource_name)
                if resource is not None:
                    _logger.debug(f"Resource name '{resource_name}' accepted by {transport._transport_class}")
                    break
            except Exception as e:
                # Some transports may not implement this method
                _logger.warning(
                    f"Exception during parsing of resource name '{resource_name}' by {transport._transport_class}: {str(e)}"
                )
        else:
            # No transport found that accepts resource name
            _logger.error(
                f"No transport found accepting resource name '{resource_name}'"
            )
            raise ValueError

        return resource

    @property
    def resource_class(self) -> str:
        return 'ScpiResource'

    @property
    def resource_type(self) -> str:
        return 'SCPI'

    @property
    def resource_info(self) -> str:
        return 'SCPI Resource'

    @property
    def resource_name(self) -> str:
        """Returns the VISA resource string identifying the device"""
        return self.transport.to_resource_name(self)