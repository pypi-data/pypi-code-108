from setux.core.deploy import Deployer


class Directory(Deployer):
    @property
    def label(self):
        return f'dir {self.path}'

    def check(self):
        directory = self.target.dir.fetch(
            self.path,
            **self.spec,
        )
        return directory.check() is True

    def deploy(self):
        directory = self.target.dir.fetch(
            self.path,
            **self.spec,
        )
        return directory.deploy() is True
