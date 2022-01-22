from setux.logger import error, info
from setux.core.package import CommonPackager

from setux.managers.common.package.pypi import Pypi


# pylint: disable=no-member


class Distro(CommonPackager):
    '''Python Packages managment
    '''
    manager = 'pip'
    pkgmap = dict()

    def do_init(self):
        if self.target.login.name!='root': return
        self.target.distro.Package.install('setuptools', verbose=False)
        pip = self.target.distro.pkgmap.get('pip')
        if pip:
            self.target.distro.Package.install_pkg(pip)
        else:
            self.run(f'python3 -m ensurepip --upgrade')
        venv = self.target.distro.pkgmap.get('venv')
        if venv:
            self.target.distro.Package.install_pkg(venv)

    def do_install(self, pkg, ver=None):
        ret, out, err = self.run(f'pip3 install -qU {pkg}')
        if ret == 0:
            return True

        for o in out:
            if 'already satisfied' in o:
                return True
            if 'Successfully installed' in o:
                info('\t++> %s %s', pkg, ver or '')
                return True
        else:
            if any(line.strip() for line in out):
                error('\n'.join(out))
        return False

    def do_installed(self, pattern=None):
        ret, out, err = self.run('pip3 list')
        for line in out[2:]:
            try:
                n, v, *_ = line.split()
                v = v.replace('(', '')
                v = v.replace(')', '')
            except:
                error(line)
            else:
                yield n, v

    def do_installable_cache(self):
        Pypi(self).cache()

    def do_installable(self, pattern):
        yield from Pypi(self).search(pattern)

    def do_remove(self, pkg):
        ret, out, err = self.run(f'pip3 uninstall -y {pkg}')
        return ret == 0

    def do_cleanup(self):
        raise NotImplemented

    def do_update(self):
        raise NotImplemented

