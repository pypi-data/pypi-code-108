from pybrary.func import memo

from setux.core.manage import Manager


class Distro(Manager):
    '''Login User
    '''
    manager = 'login'

    @memo
    def name(self):
        ret, out, err = self.run('id -un')
        return out[0]

    @memo
    def id(self):
        ret, out, err = self.run('id -u')
        return int(out[0])
