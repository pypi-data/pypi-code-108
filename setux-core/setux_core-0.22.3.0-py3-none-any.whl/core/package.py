from pybrary.func import todo

from setux.core.deployers import Installer, Remover
from setux.logger import error, info

from .manage import Manager


class _Packager(Manager):
    def __init__(self, distro):
        super().__init__(distro)
        self.done = set()
        self.ready = False

    def _get_ready_(self):
        if self.ready: return
        self.do_init()
        self.mapkg = {v:k for k,v in self.pkgmap.items()}
        self.ready = True

    def filter(self, do_fetch, pattern=None):
        self._get_ready_()
        chk_name = self.mapkg.get
        for name, ver in do_fetch(pattern):
            name = chk_name(name, name)
            if pattern:
                if pattern in name.lower():
                    yield name, ver
            else:
                yield name, ver


    def installed(self, pattern=None):
        yield from self.filter(self.do_installed, pattern)

    def installable(self, pattern=None):
        yield from self.filter(self.do_installable, pattern)

    def bigs(self):
        self._get_ready_()
        info('\tbigs')
        for line in self.do_bigs():
            size, pkg = line.split()
            size = int(size)
            while size>1000:
                size = size//1000
            yield f'{size:>7} {pkg}'

    def upgradable(self):
        self._get_ready_()
        info('\tupgradable')
        yield from self.do_upgradable()

    def update(self):
        self._get_ready_()
        info('\tupdate')
        self.do_update()
        for name, ver in self.upgradable():
            info(f'\t\t{name}')

    def upgrade(self):
        self._get_ready_()
        info('\tupgrade')
        self.do_upgrade()

    def install_pkg(self, name, ver=None):
        if name in self.done: return
        self._get_ready_()
        info('\t--> %s', name)
        self.done.add(name)
        pkg = self.pkgmap.get(name, name)
        return self.do_install(pkg, ver)

    def install(self, name, ver=None, verbose=True):
        try:
            Installer(self.target, packager=self, name=name, ver=ver)(verbose)
        except Exception as x:
            error(f'install {name} ! {x}')
            return False
        return True

    def remove_pkg(self, name):
        self._get_ready_()
        info('\t<-- %s', name)
        self.done.discard(name)
        pkg = self.pkgmap.get(name, name)
        return self.do_remove(pkg)

    def remove(self, name, verbose=True):
        try:
            Remover(self.target, packager=self, name=name)(verbose)
        except Exception as x:
            error(f'remove {name} ! {x}')
            return False
        return True

    def cleanup(self):
        self._get_ready_()
        info('\tcleanup')
        self.do_cleanup()

    def do_init(self): todo(self)
    def do_update(self): todo(self)
    def do_upgradable(self): todo(self)
    def do_upgrade(self): todo(self)
    def do_install(self, pkg, ver=None): todo(self)
    def do_bigs(self): todo(self)
    def do_remove(self, pkg): todo(self)
    def do_cleanup(self): todo(self)
    def do_installed(self, pattern): todo(self)
    def do_installable(self, pattern): todo(self)


class SystemPackager(_Packager):
    def __init__(self, distro):
        super().__init__(distro)
        self.pkgmap = distro.pkgmap


class CommonPackager(_Packager):
    def __init__(self, distro):
        super().__init__(distro)
        self.cache_dir = '/tmp/setux/cache'
        self.cache_file = f'{self.cache_dir}/{self.manager}'
        self.cache_days = 10

    def do_installable(self, pattern):
        from setux.targets import Local
        local = Local(outdir=self.cache_dir)
        cache = local.file(self.cache_file)
        if cache.age is None or cache.size==0 or cache.age > self.cache_days:
            self.do_installable_cache()

        for line in open(self.cache_file):
            yield line.strip().split(maxsplit=1)

    def do_installable_cache(self): todo(self)

