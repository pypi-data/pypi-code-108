from time import sleep

from pybrary.func import todo

from setux.core.deployers import Enabler, Disabler, Starter, Stoper, Restarter
from setux.logger  import info, error

from .manage import Manager


# pylint: disable=assignment-from-no-return


class Service(Manager):
    def __init__(self, distro):
        super().__init__(distro)
        self.svcmap = distro.svcmap

    def status(self, name):
        svc = self.svcmap.get(name, name)
        up = self.do_status(svc)
        info(f'\tservice {name} {"." if up else "X"}')
        return up

    def wait(self, name, up=True):
        sleep(1)
        for _ in range(3):
            if self.status(name) is up: break
            sleep(3)

    def enable_svc(self, name):
        svc = self.svcmap.get(name, name)
        if not self.do_enabled(svc):
            info(f'\tenable {name}')
            self.do_enable(svc)
            enabled = self.do_enabled(svc)
            info(f'\t{name} enabled {"." if enabled else "X"}')

    def disable_svc(self, name):
        svc = self.svcmap.get(name, name)
        if self.do_enabled(svc):
            info(f'\tdisable {name}')
            self.do_disable(svc)
            enabled = self.do_enabled(svc)
            info(f'\t{name} disabled {"." if not enabled else "X"}')

    def start_svc(self, name):
        svc = self.svcmap.get(name, name)
        if not self.status(name):
            info(f'\tstart {name}')
            self.do_start(svc)
            self.wait(name)

    def stop_svc(self, name):
        svc = self.svcmap.get(name, name)
        if self.status(name):
            info(f'\tstop {name}')
            self.do_stop(svc)
            self.wait(name, up=False)

    def restart_svc(self, name):
        svc = self.svcmap.get(name, name)
        if self.status(name):
            info(f'\trestart {name}')
            self.do_restart(svc)
            self.wait(name)
        else:
            self.start(name)

    def enable(self, name, verbose=True):
        svc = self.svcmap.get(name, name)
        try:
            Enabler(self.target, servicer=self, name=svc)(verbose)
        except Exception as x:
            error(f'enable {name} ! {x}')
            return False
        return True

    def disable(self, name, verbose=True):
        svc = self.svcmap.get(name, name)
        try:
            Disabler(self.target, servicer=self, name=svc)(verbose)
        except Exception as x:
            error(f'disable {name} ! {x}')
            return False
        return True

    def start(self, name, verbose=True):
        svc = self.svcmap.get(name, name)
        try:
            Starter(self.target, servicer=self, name=svc)(verbose)
        except Exception as x:
            error(f'start {name} ! {x}')
            return False
        return True

    def stop(self, name, verbose=True):
        svc = self.svcmap.get(name, name)
        try:
            Stoper(self.target, servicer=self, name=svc)(verbose)
        except Exception as x:
            error(f'stop {name} ! {x}')
            return False
        return True

    def restart(self, name, verbose=True):
        svc = self.svcmap.get(name, name)
        try:
            Restarter(self.target, servicer=self, name=svc)(verbose)
        except Exception as x:
            error(f'restart {name} ! {x}')
            return False
        return True

    def do_enabled(self, svc): todo(self)
    def do_status(self, svc): todo(self)
    def do_enable(self, svc): todo(self)
    def do_disable(self, svc): todo(self)
    def do_start(self, svc): todo(self)
    def do_stop(self, svc): todo(self)
    def do_restart(self, svc): todo(self)
