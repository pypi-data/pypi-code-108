from pybrary.func import memo


from .manage import Manager
from .module import Module
from .mapping import Mapping, Packages, Services
from .package import CommonPackager, SystemPackager
from .service import Service
from . import plugins
from setux.logger import logger, debug, info, error
import setux.managers
import setux.modules
import setux.mappings


# pylint: disable=bad-staticmethod-argument


class Distro:
    Package = None
    Service = None

    def __init_subclass__(cls, **k):
        super().__init_subclass__(**k)
        cls.pkgmap = dict()
        cls.svcmap = dict()

    def __init__(self, target):
        self.name = self.__class__.__name__
        self.target = target
        self.manager_plugins = plugins.Managers(self,
            Manager, setux.managers
        )
        self.modules = plugins.Modules(self,
            Module, setux.modules
        )
        self.mappings = plugins.Mappings(self,
            Mapping, setux.mappings
        )
        self.set_managers()
        self.reg_modules()
        self.set_mappings()

    def __str__(self):
        return f'Distro : {self.name}'

    def reg_modules(self):
        for module in self.modules:
            name = getattr(module, 'register', None)
            if name:
                self.target.register(module, name)

    def set_managers(self):
        for manager in self.manager_plugins:
            if issubclass(manager, SystemPackager):
                if manager.manager==self.Package:
                    self.Package = manager(self)
                    debug('%s Package %s', self.name, manager.manager)
            elif issubclass(manager, Service):
                if manager.manager==self.Service:
                    self.Service = manager(self)
                    debug('%s Service %s', self.name, manager.manager)
            else:
                if manager.is_supported(self):
                    setattr(self, manager.manager, manager(self))
                    debug('%s %s', self.name, manager.manager)

    def set_mappings(self):
        for mapping in self.mappings:
            if issubclass(mapping, Packages):
                dist = mapping.__name__
                if mapping.pkg:
                    debug('Mapping %s Packages', dist)
                    debug(' '.join(mapping.pkg.keys()))
                    self.pkgmap.update(mapping.pkg)
                for name, manager in self.managers.items():
                    if isinstance(manager, CommonPackager):
                        items = mapping.__dict__.get(name)
                        if items:
                            debug('Mapping %s %s', dist, name)
                            manager.pkgmap.update(items)
            elif issubclass(mapping, Services):
                debug('Mapping Services %s', mapping.__name__)
                self.svcmap.update(mapping.mapping)
            else:
                error('%s', mapping)

    @classmethod
    def release_default(cls, target):
        if target.release_infos is None:
            ret, out, err = target.run('cat /etc/*-release', report='quiet', shell=True)
            target.release_infos = dict(l.split('=') for l in out if '=' in l)
            debug('%s %s', target, target.release_infos)
        return target.release_infos

    @classmethod
    def release_name(cls, infos):
        did = infos['ID'].strip()
        ver = infos['VERSION_ID'].strip()
        return f'{did}_{ver}'

    @classmethod
    def release_check(cls, target, infos=None):
        if hasattr(cls, 'release_infos'):
            try:
                infos = cls.release_infos(target)
            except: pass
        if not infos:
            infos = cls.release_default(target)
        try:
            return cls.release_name(infos) == cls.__name__
        except: return False

    @staticmethod
    def distro_bases(cls):
        return list(reversed([
            base
            for base in cls.__mro__
            if issubclass(cls, Distro)
        ]))[1:]

    @memo
    def bases(self):
        return Distro.distro_bases(self.__class__)

    @staticmethod
    def distro_lineage(cls):
        return [b.__name__ for b in Distro.distro_bases(cls)]

    @memo
    def lineage(self):
        return [b.__name__ for b in self.bases]

    @memo
    def managers(self):
        items = {
            name : manager
            for name, manager in self.__dict__.items()
            if isinstance(manager, Manager)
        }
        return items

    def search_pkg(self, pattern):
        name = self.Package.manager
        for pkg, ver in self.Package.installable(pattern):
            yield name, pkg, ver

        for name, packager in self.managers.items():
            if isinstance(packager, CommonPackager):
                for pkg, ver in packager.installable(pattern):
                    yield name, pkg, ver

    def search(self, pattern, report='normal'):
        if report=='quiet':
            with logger.quiet():
                yield from self.search_pkg(pattern)
        else:
            yield from self.search_pkg(pattern)
