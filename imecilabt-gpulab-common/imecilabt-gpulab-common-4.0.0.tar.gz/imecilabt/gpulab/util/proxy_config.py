from typing import Optional, Dict, Union

from imecilabt.gpulab.util.gpulab_config import BaseConfig
from imecilabt_utils.urn_util import URN, always_optional_urn


class ProxyConfig(BaseConfig):
    """
    Config of proxy username mapping
    Example:
         proxy_username_prefix:
            wall2.ilabt.iminds.be: ''  # old wall2.ilabt.iminds.be usernames are NOT prefixed. Example: 'wvdemeer'->'wvdemeer'
            ilabt.imec.be: 'fff'       # ilabt.imec.be usernames are prefixed with 'fff', example: 'wvdemeer'->'fffwvdemeer'
    """
    def __init__(self):
        super(ProxyConfig, self).__init__()

        self.proxy_username_prefix = {}

    def load_from_dict(self, cfg: Dict, *, backward_compatible=False):
        # super().load_from_dict(cfg, backward_compatible=backward_compatible)

        def mandatory(keys):
            raise Exception('Argument is required: {}   \n   Was not found in {}'.format(keys, cfg))

        self.proxy_username_prefix = BaseConfig._get_from_dict(cfg, mandatory, 'proxy_username_prefix')

    def save_to_dict(self) -> Dict:
        res = dict()
        BaseConfig._to_dict(res, self.proxy_username_prefix, 'proxy_username_prefix')
        return res

    def find_proxy_username(self, user_urn: Union[str, URN]) -> Optional[str]:
        u = always_optional_urn(user_urn)
        if u and u.name and u.authority:
            if u.authority in self.proxy_username_prefix:
                return "{}{}".format(self.proxy_username_prefix[u.authority], u.name)
            else:
                return None
        else:
            return None
