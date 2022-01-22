from pybrary.net import get_ip_adr
from pybrary.func import memo

from setux.core.manage import Manager
from setux.logger import logger, error, info
from setux.managers.common.host.deployers import Hostname


class Distro(Manager):
    '''System Infos
    '''
    manager = 'system'

    @property
    def hostname(self):
        attr = '_hostname_'
        try:
            val = getattr(self, attr)
        except AttributeError:
            ret, out, err = self.run('hostname')
            val = out[0]
            setattr(self, attr,  val)
        return val

    @hostname.setter
    def hostname(self, val):
        attr = '_hostname_'
        if hasattr(self, attr):
            delattr(self, attr)
        new_val = val.replace('_', '-')

        try:
            Hostname(target=self.target, name=new_val)()
        except Exception as x:
            error(f'hostname -> {new_val} ! {x}')
            return False
        return True

    @memo
    def fqdn(self):
        ret, out, err = self.run('hostname -f')
        return out[0]
