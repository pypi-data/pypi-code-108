from setux.logger import error, debug
from setux.core.package import SystemPackager


# pylint: disable=expression-not-assigned


class Distro(SystemPackager):
    '''PACMAN Packages management
    '''
    manager = 'pacman'

    def do_init(self):
        # self.do_cleanup()
        self.do_update()
        self.run(f'pacman -Sq --noconfirm expac')

    def do_installed(self, pattern=None):
        ret, out, err = self.run(
            'expac -Qs "%n %v"',
        report='quiet')
        for line in out:
            name, ver = line.strip("'").split()
            yield name, ver

    def do_bigs(self):
        ret, out, err = self.run(
            'expac -Qs "%m %n" | sort -n | tail -n 22',
        report='quiet')
        yield from out

    def do_upgradable(self):
        ret, out, err = self.run('pacman -Qu', report='quiet')
        for line in out:
            try:
                name, ver = line.split(' ', 1)
                yield name, ver
            except Exception as x:
                debug(line)

    def do_installable(self, pattern=None):
        ret, out, err = self.run(
            'expac -Ss "%n %v"',
        )
        for line in out:
            name, ver = line.strip("'").split()
            yield name, ver

    def do_remove(self, pkg):
        ret, out, err = self.run(f'pacman --noconfirm -Rc {pkg}')
        return ret == 0

    def do_cleanup(self):
        self.run('pacman --noconfirm -Rcsun $(pacman -Qdtq)')
        self.run('pacman --noconfirm -Scc')

    def do_update(self):
        self.run('pacman -Sy')

    def do_upgrade(self):
        self.run('pacman --noconfirm -Su')

    def do_install(self, pkg, ver=None):
        ret, out, err = self.run(f'pacman --noconfirm -Sq {pkg}')
        if ret:
            error('\n'.join(err))
            return False
        else:
            return True

