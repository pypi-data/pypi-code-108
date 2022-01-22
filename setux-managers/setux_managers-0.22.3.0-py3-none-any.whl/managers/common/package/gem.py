from setux.core.package import CommonPackager
from setux.targets import Local
from setux.logger import error, info


# pylint: disable=no-member


class Distro(CommonPackager):
    '''Ruby Packages managment
    '''
    manager = 'gem'
    pkgmap = dict()

    def do_init(self):
        self.target.distro.Package.install('ruby-dev')
        self.target.distro.Package.install('rubygems')

    def do_installed(self, pattern=None):
        ret, out, err = self.run('gem list')
        for line in out:
            line = line.replace('(', '')
            line = line.replace(')', '')
            n, *_, v = line.split()
            yield n, v

    def do_installable_cache(self):
        local = Local(outdir=self.cache_dir)
        ret, out, err = self.run('gem search .*')
        try:
            with open(self.cache_file, 'w') as cache:
                for line in out:
                    name, ver = line.split(maxsplit=1)
                    ver = ver.strip('( )')
                    cache.write(f'{name} {ver}\n')
        except Exception as x:
            error(f'{x}')

    def do_remove(self, pkg):
        ret, out, err = self.run(f'gem uninstall {pkg}')
        return ret == 0

    def do_cleanup(self):
        raise NotImplemented

    def do_update(self):
        raise NotImplemented

    def do_install(self, pkg, ver=None):
        ret, out, err = self.run(f'gem install {pkg}')
        return ret==0
