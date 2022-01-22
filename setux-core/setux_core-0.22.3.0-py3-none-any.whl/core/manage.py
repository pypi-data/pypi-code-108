from inspect import cleandoc

from pybrary.func import todo

from setux.logger import silent
from .deploy import Deployer


# pylint: disable=no-member,not-callable,not-an-iterable


class Manager:
    def __init__(self, distro, quiet=False):
        self.distro = distro
        self.target = distro.target
        self.run = self.target.run
        self.key = None
        self.quiet = quiet
        self.context = dict()

    @staticmethod
    def is_supported(distro):
        return True

    @classmethod
    def help(cls):
        for klass in (
            c
            for c in cls.mro()
            if issubclass(c, Manager)
        ):
            try:
                return cleandoc(klass.__doc__)
            except Exception: pass
        return '?'

    def __str__(self):
        base = self.__class__.__bases__[0].__name__
        return f'{base}.{self.manager}'


class Checker(Manager, Deployer):
    def fetch(self, key, *args, **spec):
        self.key = key
        self.args = args
        self.spec = self.validate(spec)
        return self

    @property
    def labeler(self):
        return silent

    @property
    def label(self):
        return f'{self.manager} {self.key}'

    def __call__(self, key, *args, **spec):
        self.fetch(key, *args, **spec)
        verbose = spec.pop('verbose', True)
        super().__call__(verbose=verbose)
        return self

    def validate(self, specs):
        return {
            k: v
            for k, v in self.do_validate(specs)
        }

    def do_validate(self, specs): todo(self)

    def __str__(self):
        fields = ', '.join(f'{k}={v}' for k, v in self.get().items())
        return f'{self.manager}({fields})'


class SpecChecker(Checker):
    def chk(self, name, value, spec):
        return value == spec

    def check(self):
        found = self.get()
        if found:
            for k, v in self.spec.items():
                # if found.get(k) != v:
                if not self.chk(k, found.get(k), v):
                    return False       # mismatch
            return True                # conform
        return None                    # absent

    def deploy(self):
        found = self.get()
        if not found:
            self.cre()
            found = self.get()
            if not found: return False
        for k, v in self.spec.items():
            if not self.chk(k, found.get(k), v):
                self.mod(k, v)
                found = self.get()
                if not self.chk(k, found.get(k), v):
                    return False
        return True


class ArgsChecker(Checker):
    def check(self):
        found = self.get()
        if found:
            for arg in self.args:
                if arg not in found:
                    return False       # mismatch
            return True                # conform
        return None                    # absent

    def remove(self, args=None, found=None):
        args = args or self.args
        found = found or self.get()
        ok = True
        for arg in found:
            if arg in args:
                ok = ok and self.rm(arg)
        return ok

    def extend(self, args=None, found=None):
        args = args or self.args
        found = found or self.get()
        ok = True
        for arg in args:
            if arg not in found:
                ok = ok and self.add(arg)
        return ok

    def deploy(self):
        args = self.args
        found = self.get()
        return self.remove(args, found) and self.extend(args, found)
