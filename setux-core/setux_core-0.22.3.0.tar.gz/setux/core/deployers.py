from setux.logger import silent
from .deploy import Runner, Deployer, Deployers


class Pinger(Runner):
    @property
    def labeler(self):
        return silent

    @property
    def label(self):
        return 'ping'

    def deploy(self):
        return self.target.ping()


class Downloader(Deployer):
    @property
    def label(self):
        return f'<- {self.name}'

    def check(self):
        dst = self.target.file.fetch(self.dst)
        return dst.size and dst.size > 0

    def deploy(self):
        return self.target.download(
            url = self.url,
            dst = self.dst,
        )


class Sender(Deployer):
    @property
    def labeler(self):
        return silent

    @property
    def label(self):
        dst = f' -> {self.dst}' if self.dst != self.src else ''
        return f'send {self.src}{dst}'

    def check(self):
        lhash = self.local.file(self.src, verbose=False).hash
        rhash = self.target.file(self.dst, verbose=False).hash
        return rhash == lhash

    def deploy(self):
        return self.target.do_send(self.src, self.dst)


class Syncer(Deployer):
    @property
    def label(self):
        dst = self.dst if hasattr(self, 'dst') else self.src
        dst = f' -> {dst}' if dst != self.src else ''
        return f'sync {self.src}{dst}'

    def check(self):
        dst = self.dst if hasattr(self, 'dst') else self.src
        lhash = self.local.dir(self.src, verbose=False).hash
        rhash = self.target.dir(dst, verbose=False).hash
        return rhash == lhash

    def deploy(self):
        dst = self.dst if hasattr(self, 'dst') else self.src
        return self.target.do_sync(self.src, dst)


class Moduler(Runner):
    @property
    def label(self):
        return self.module

    def deploy(self):
        return self.target.deploy(self.module)


class Modules(Deployers):
    @property
    def label(self):
        return f'Modules {self.name}'

    @property
    def deployers(self):
        return [
            Moduler(self.target, module=module)
            for module in self.modules
        ]


class Installer(Deployer):
    @property
    def label(self):
        return f'install {self.name}'

    def check(self):
        return self.name in [n.lower() for n,v in self.packager.installed(self.name)]

    def deploy(self):
        return self.packager.install_pkg(self.name, self.ver)


class Remover(Deployer):
    @property
    def label(self):
        return f'remove {self.name}'

    def check(self):
        return self.name not in [n.lower() for n,v in self.packager.installed(self.name)]

    def deploy(self):
        return self.packager.remove_pkg(self.name)


class Enabler(Deployer):
    @property
    def label(self):
        return f'enable {self.name}'

    def check(self):
        return self.servicer.do_enabled(self.name)

    def deploy(self):
        return self.servicer.do_enable(self.name)


class Disabler(Deployer):
    @property
    def label(self):
        return f'disable {self.name}'

    def check(self):
        return not self.servicer.do_enabled(self.name)

    def deploy(self):
        return self.servicer.do_disable(self.name)


class Starter(Deployer):
    @property
    def label(self):
        return f'start {self.name}'

    def check(self):
        return self.servicer.status(self.name)

    def deploy(self):
        ok = self.servicer.do_start(self.name)
        if ok: self.servicer.wait(self.name)
        return ok


class Stoper(Deployer):
    @property
    def label(self):
        return f'stop {self.name}'

    def check(self):
        return not self.servicer.status(self.name)

    def deploy(self):
        ok = self.servicer.do_stop(self.name)
        if ok: self.servicer.wait(self.name, up=False)
        return ok


class Restarter(Runner):
    @property
    def label(self):
        return f'restart {self.name}'

    def deploy(self):
        ok = True
        if self.servicer.status(self.name):
            ok = self.servicer.do_stop(self.name)
            if ok: self.servicer.wait(self.name, up=False)
        if ok:
            ok = self.servicer.do_start(self.name)
            if ok: self.servicer.wait(self.name)
        return ok

