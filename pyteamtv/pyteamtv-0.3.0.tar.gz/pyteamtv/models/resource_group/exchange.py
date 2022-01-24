from . import _ResourceGroup

from .capabilities import _HasSharingGroupResourceGroupsMixin


class ExchangeResourceGroup(_ResourceGroup, _HasSharingGroupResourceGroupsMixin):
    pass


