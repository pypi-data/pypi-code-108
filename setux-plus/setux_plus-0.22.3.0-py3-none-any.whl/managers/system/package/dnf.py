from pybrary.ascii import rm_ansi_codes

from setux.logger import error, debug
from setux.core.package import SystemPackager


class Fedora(SystemPackager):
    '''DNF Packages managment
    '''
    manager = 'dnf'

    def parse(self, line):
        line = rm_ansi_codes(line)
        name, ver, _ = line.split()
        name = name.split('.')[0]
        return name, ver

    def do_init(self):
        self.do_update()

    def do_installed(self, pattern=None):
        ret, out, err = self.run('dnf list --installed', report='quiet')
        for line in out:
            try:
                yield self.parse(line)
            except: pass

    def do_bigs(self):
        ret, out, err = self.target.script('''#!/bin/bash
            dnf repoquery --installed --queryformat '%9{size} %{name}' | sort -n | tail -n 22
        ''', report='quiet')
        yield from out

    def do_upgradable(self):
        ret, out, err = self.run('''
            dnf list --upgrades
        ''', report='quiet')
        for line in out:
            try:
                yield self.parse(line)
            except Exception as x:
                debug(line)

    def do_installable(self, pattern=None):
        ret, out, err = self.run('dnf list --available', report='quiet')
        for line in out:
            try:
                yield self.parse(line)
            except: pass

    def do_remove(self, pkg):
        ret, out, err = self.run(f'dnf -y remove {pkg}')
        return ret == 0

    def do_cleanup(self):
        self.run('dnf clean all')

    def do_update(self):
        self.run('dnf check-update -y')

    def do_upgrade(self):
        self.run('dnf upgrade -y')

    def do_install(self, pkg, ver=None):
        ver = f' ={ver}' if ver else ''
        ret, out, err = self.run(f'dnf -y -C install {pkg}{ver}')
        if ret==1:
            ret, out, err = self.run(f'dnf -y install {pkg}{ver}')
        if err:
            error('\n'.join(err))
            return False
        else:
            return True
