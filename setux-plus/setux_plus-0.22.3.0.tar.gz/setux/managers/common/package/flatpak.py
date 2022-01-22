from setux.core.package import CommonPackager
from setux.targets import Local
from setux.logger import info, error


# pylint: disable=no-member


class Distro(CommonPackager):
    '''Flatpaks managment
    '''
    manager = 'flatpak'
    pkgmap = dict()
    supported = 'Debian', 'Fedora', 'Arch', 'Artix'

    @staticmethod
    def is_supported(distro):
        return any(d in distro.lineage for d in Distro.supported)

    def add_flathub(self):
        ret, out, err = self.run(
            'flatpak remotes --columns=name',
            report = 'quiet',
        )
        if ret==0:
            remotes = out[1:]
            if 'flathub' not in remotes:
                self.run('''
                    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
                ''')

    def do_init(self):
        ret, out, err = self.run('flatpak --version')
        if ret==0:
            self.add_flathub()
            ret, out, err = self.run(
                'flatpak run com.github.tchx84.Flatseal -h',
                report = 'quiet',
            )
            if ret!=0:
                self.do_install('flatseal')
            return
        self.target.Package.install('flatpak')
        self.add_flathub()

    def do_install(self, pkg, ver=None):
        ret, out, err = self.run(f'flatpak install -y flathub {pkg}')
        return ret==0

    def do_installed(self, pattern=None):
        ret, out, err = self.run('flatpak list --columns=application,version')
        for line in out[1:]:
            try:
                n, v  = line.split()
                yield n.strip(), v.strip()
            except: pass

    def do_installable_cache(self):
        ret, out, err = self.run(
            'flatpak remote-ls --columns=application,version',
            report = 'quiet',
        )
        if ret!=0:
            error('\n'.join(out))
            return

        with open(self.cache_file, 'w') as cache:
            for line in out:
                try:
                    app, ver = line.split('\t')
                    cache.write(f'{app} {ver}\n')
                except ValueError: pass

    def do_remove(self, pkg):
        ret, out, err = self.run(f'flatpak uninstall -y {pkg}')
        return ret == 0

    def do_cleanup(self):
        raise NotImplemented

    def do_update(self):
        raise NotImplemented

