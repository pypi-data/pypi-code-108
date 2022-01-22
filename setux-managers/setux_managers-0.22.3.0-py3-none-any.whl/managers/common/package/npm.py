from json import load

from setux.core.package import CommonPackager
from setux.targets import Local


# pylint: disable=no-member


class Distro(CommonPackager):
    '''JavaScript Packages managment
    '''
    manager = 'npm'
    pkgmap = dict()

    def do_init(self):
        self.target.distro.Package.install('npm')

    def do_installed(self, pattern=None):
        ret, out, err = self.run('npm list -g --depth=0')
        for line in out[1:]:
            if len(line)<5: continue
            n, v = line[4:].split('@')
            yield n, v

    def _do_installable_cache(self):
        # very bad
        # better off using npm search
        # look for a better way
        local = Local(outdir=self.cache_dir)
        url = 'https://replicate.npmjs.com/_all_docs'
        org = f'{self.cache_dir}/npm_all_docs.json'
        local.download(url=url, dst=org)
        with open(self.cache_file, 'w') as out:
            for pkg in load(open(org))['rows']:
                name = pkg['id']
                out.write(f'{name} -\n')
        local.file(org).rm()

    def do_installable(self, pattern):
        ret, out, err = self.run(f'npm search {pattern}')
        for line in out[1:]:
            fields = line.split('|')
            name, ver = fields[0], fields[4]
            yield name.strip(), ver.strip()

    def do_remove(self, pkg):
        ret, out, err = self.run(f'npm uninstall {pkg}')
        return ret == 0

    def do_cleanup(self):
        raise NotImplemented

    def do_update(self):
        raise NotImplemented

    def do_install(self, pkg, ver=None):
        ret, out, err = self.run(f'npm install -g {pkg}')
        return ret==0
