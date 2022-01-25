"""
Taktile Client
"""
from .config import arrow_available
from .config import version as __version__

if arrow_available:
    from taktile_client.arrow import ArrowClient

# pylint: disable-next=wrong-import-position, wrong-import-order
from taktile_client.rest import RestClient
