from inspect import cleandoc, getsource
from ast import parse, walk, Call
from textwrap import dedent

from pybrary.func import todo

from setux.logger import error, debug


def inst(installer, installables):
    if installables:
        installables = installables.strip()
        if ' ' in installables:
            installables = installables.split()
        else:
            installables = [installables]
        for installable in installables:
            installer(installable)


class Module:
    def __init__(self, distro):
        self.distro = distro

    def __getattr__(self, attr):
        return getattr(self.distro.target, attr)

    def deploy(self, target, **kw):
        for mod in (
            c
            for c in reversed(self.__class__.mro())
            if issubclass(c, Module)
        ):
            try:
                ret = mod.do_deploy(self, target, **kw)
            except Exception as x:
                error(x)
                return False
            if not ret: return False
        return True

    def do_deploy(self, target, **kw):
        '''to be overridden
        '''
        return True

    @property
    def submodules(self):
        subs = list()
        modules = set(self.modules.items.keys())
        for meth in (self.deploy, self.do_deploy):
            tree = parse(dedent(getsource(meth)))
            for node in walk(tree):
                if isinstance(node, Call):
                    try:
                        f = node.func.attr
                        if f in ('deploy', 'do_deploy'):
                            m = node.args[0].s
                            if m in modules:
                                subs.append(m)
                    except: pass
        return subs

    def install(self, target, *, pre=None, dep=None, pkg=None, **specs):
        inst(target.Package.install, pre)
        inst(target.deploy, dep)
        inst(target.Package.install, pkg)
        for name, packages in specs.items():
            try:
                packager = getattr(self, name)
            except Exception as x:
                debug(f'install ! {x}')
                error(f'invalid packager : {name}')
            else:
                inst(packager.install, packages)
        return True

    @classmethod
    def help(cls):
        for klass in (
            c
            for c in cls.mro()
            if issubclass(c, Module)
        ):
            try:
                return cleandoc(klass.__doc__)
            except: pass
        return '?'
