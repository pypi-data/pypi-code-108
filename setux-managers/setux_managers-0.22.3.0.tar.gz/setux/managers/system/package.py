from pybrary.ascii import rm_ansi_codes

from setux.logger import debug, info, error
from setux.core.package import SystemPackager
from setux.targets.local import Local


class Debian(SystemPackager):
    '''APT packages manangment
    '''
    manager = 'apt'

    def do_init(self):
        self.do_cleanup()
        self.do_update()

    def do_installed(self, pattern=None):
        ret, out, err = self.run('apt list --installed', report='quiet')
        decolor = rm_ansi_codes
        for line in out:
            if '/' not in line: continue
            name, ver, *_ = line.split()
            name = decolor(name.split('/')[0])
            yield name, ver

    def do_bigs(self):
        ret, out, err = self.target.script('''#!/bin/bash
            dpkg-query -Wf '${Installed-Size;9} ${Package}\n' | sort -n | tail -n 22
        ''', report='quiet')
        yield from out

    def do_upgradable(self):
        ret, out, err = self.run('''
            apt list --upgradable
        ''', report='quiet')
        decolor = rm_ansi_codes
        for line in out:
            if not line.strip(): continue
            try:
                line = decolor(line)
                name_ver = line.split()[0]
                name, ver = name_ver.split('/')
                yield name, ver
            except:
                debug(line)

    def do_installable(self, pattern=None):
        ret, out, err = self.run('apt list', report='quiet')
        decolor = rm_ansi_codes
        for line in out:
            if '/' in line and '[install' not in line:
                name, ver, *_ = line.split()
                name = decolor(name.split('/')[0])
                yield name, ver

    def do_remove(self, pkg):
        ret, out, err = self.run(f'apt-get -y purge {pkg}')
        return ret == 0

    def do_cleanup(self):
        self.run('apt-get autoclean -y')
        self.run('apt-get autoremove -y')
        self.run('apt-get clean -y')

    def do_update(self):
        self.run('apt-get update')

    def do_upgrade(self):
        self.run('apt-get upgrade -y')

    def do_install(self, pkg, ver=None):
        cmd = 'DEBIAN_FRONTEND=noninteractive apt-get -o Dpkg::Options::="--force-confdef" -o Dpkg::Options::="--force-confnew" --yes install'
        ver = f'={ver}' if ver else ''
        shell = isinstance(self.target, Local)
        ret, out, err = self.run(f'{cmd} {pkg}{ver}', shell=shell)
        for line in out:
            if line==pkg:
                info(f'\t++> {pkg} {ver or ""}')
                break

        err = [
            x
            for x in err
            if (
                x.strip()
                and not x.startswith('Extracting templates')
                and x != 'Connection to xyz closed.'
            )
        ]
        if err: error('\n'.join(err))

        return ret==0


class FreeBSD(SystemPackager):
    '''PKG packages managment
    '''
    manager = 'pkg'

    def do_init(self):
        self.do_cleanup()

    def do_installed(self, pattern=None):
        ret, out, err = self.run(
            'pkg query "%n %v"',
            report = 'quiet',
        )
        for line in out:
            name, ver = line.strip("'").split()
            yield name, ver

    def do_bigs(self):
        ret, out, err = self.run(
            'pkg query "%sb %n" | sort -n | tail -n 22',
            report = 'quiet',
        )
        yield from out

    def do_upgradable(self):
        yield None, None

    def do_installable(self, pattern=None):
        ret, out, err = self.run(
            'pkg search -x ".*"',
            report = 'quiet',
        )
        for line in out:
            name_ver, *_desc = line.split()
            name, ver = name_ver.rsplit('-', 1)
            yield name, ver

    def do_remove(self, pkg):
        ret, out, err = self.run(f'pkg delete -y {pkg}')
        return ret == 0

    def do_cleanup(self):
        self.run('pkg autoremove -y')
        self.run('pkg clean -y')

    def do_update(self):
        pass

    def do_upgrade(self):
        self.run('pkg upgrade -y')

    def do_install(self, pkg, ver=None):
        ret, out, err = self.run(f'pkg install -y {pkg}')
        for line in out:
            name, *_ = line.partition(':')
            if name==pkg:
                info('\t++> %s %s', pkg, ver or '')
                break
        return ret==0

