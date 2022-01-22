from pybrary.func import memo

from setux.core.manage import Manager


class Distro(Manager):
    '''Net Infos
    '''
    manager = 'net'

    @memo
    def addr(self):
        self.target.pip.install('pybrary', verbose=False)
        ret, out, err = self.run('get_ip_adr')
        return out[0]

