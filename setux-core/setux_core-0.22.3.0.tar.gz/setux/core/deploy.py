from pybrary.func import todo

from setux.logger import logger, error, green, yellow, red

# pylint: disable=no-member,not-an-iterable


class Deployer:
    def __init__(self, target, **context):
        self.target = target
        self.context = context

    def __getattr__(self, attr):
        try:
            return self.context[attr]
        except KeyError:
            try:
                return self.target.context[attr]
            except KeyError:
                # debug(f'{attr} not in context ({self.label})')
                if attr=='local': return self.target.set_local()
                raise AttributeError

    @property
    def labeler(self):
        return yellow

    @property
    def label(self):
        todo(self)

    def __enter__(self):
        self.backup = dict(self.target.context)
        self.target.context.update(self.context)

    def _call_(self, verbose):
        with logger.quiet():
            try:
                ok = self.check()
            except Exception as x:
                error(x)
                red(f'!! {self.label}')
                return False
            if ok:
                if verbose: green(f'== {self.label}')
                return True

            with self.labeler(f'<> {self.label}'):
                try:
                    ok = self.deploy()
                except Exception as x:
                    error(x)
                    red(f'!! {self.label}')
                    return False

            if ok:
                try:
                    ok = self.check()
                except Exception as x:
                    error(x)
                    red(f'!! {self.label}')
                    return False
                if ok:
                    green(f'>> {self.label}')
                    return True

            red(f'XX {self.label}')
            return False

    def __call__(self, verbose=True):
        with self:
            return self._call_(verbose)

    def __exit__(self, typ, val, tb):
        self.target.context = self.backup


class Runner(Deployer):
    def _call_(self, verbose):
        with logger.quiet():
            with self.labeler(f'<> {self.label}'):
                try:
                    ok = self.deploy()
                except Exception as x:
                    error(x)
                    ok = False
            if ok:
                if verbose: green(f'.. {self.label}')
                return True
            else:
                if verbose: red(f'!! {self.label}')
                return False


class Deployers(Deployer):
    @property
    def ignore(self):
        return getattr(self, '_continue_', False)

    @ignore.setter
    def ignore(self, val):
        setattr(self, '_continue_', val)

    @property
    def deployers(self):
        todo(self)

    def get_deployer(self, dpl):
        if isinstance(dpl, Deployer):
            deployer = dpl
        else:
            deployer = dpl(self.target, **self.context)
        return deployer

    def check_deployer(self, deployer):
        if hasattr(deployer, 'check'):
            try:
                ok = deployer.check()
            except Exception as x:
                error(x)
                ok =  False
        else:
            try:
                ok = deployer(verbose=False)
            except Exception as x:
                error(x)
                ok =  False
        return ok

    def deploy_deployer(self, deployer):
        err = None
        with yellow(f'<> {deployer.label}'):
            try:
                ok = deployer.deploy()
            except Exception as x:
                err = str(x)
                error(err)
                ok =  False
        if err:
            red(f'!! {deployer.label}')
        return ok

    def check(self):
        all_ok = True
        for dpl in self.deployers:
            checker = self.get_deployer(dpl)
            ok = self.check_deployer(checker)
            if not ok:
                if self.ignore:
                    all_ok = False
                else:
                    raise RuntimeError
        return all_ok

    def deploy(self):
        all_ok = True
        for dpl in self.deployers:
            deployer = self.get_deployer(dpl)
            ok = self.deploy_deployer(deployer)
            if not ok:
                if self.ignore:
                    all_ok = False
                else:
                    raise RuntimeError
        return all_ok

    def _call_(self, verbose):
        with logger.quiet():
            with yellow(f'<> {self.label}'):
                all_ok = True
                for dpl in self.deployers:
                    deployer = self.get_deployer(dpl)
                    if isinstance(deployer, (Deployers, Runner)):
                        ok = deployer()
                    else:
                        ok = self.check_deployer(deployer)
                        if ok:
                            green(f'== {deployer.label}')
                        else:
                            ok = self.deploy_deployer(deployer)
                            if ok:
                                ok = self.check_deployer(deployer)
                                if ok:
                                    green(f'>> {deployer.label}')
                                else:
                                    red(f'XX {deployer.label}')
                    all_ok = all_ok and ok
            if all_ok:
                green(f'.. {self.label}')
                return True
            else:
                red(f'!! {self.label}')
                return False
