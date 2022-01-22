from setux.core.package import CommonPackager
from setux.logger import debug, info, error


# pylint: disable=no-member


class Distro(CommonPackager):
    '''YAY Packages managment
    '''
    manager = 'yay'
    pkgmap = dict()

    @staticmethod
    def is_supported(distro):
        return distro.Package=='pacman'

    def aur(self, pkg):
        baz = '/data/aur'
        dst = f'{baz}/{pkg}'
        usr = grp = 'setux_yay' # must be sudoer nopasswd
        self.distro.user_(usr)
        self.target.script(f'''
            pacman -Sy
            pacman -R {pkg}
            pacman -S --needed --noconfirm git base-devel binutils
            rm -rf {dst}
            mkdir -p {baz}
            chown -R {usr}:{grp} /data
            cd {baz}
            sudo -u {usr} git clone https://aur.archlinux.org/{pkg}.git
            cd {dst}
            sudo -u {usr} makepkg -si --noconfirm
        ''', remove=False)

    def _run(self, cmd):
        user = 'setux_yay'
        if not hasattr(self, '_user_done_'):
            self.distro.user_.quiet = True
            self.distro.user_(user)  # sudoer nopasswd
            self._user_done_ = True
        ret, out, err = self.run(f'sudo -u {user} yay {cmd}')
        return ret, out, err

    def do_init(self):
        ret, out, err = self._run('--version')
        if ret!=0:
            self.aur(self.pkgmap['yay'])

    def do_install(self, pkg, ver=None):
        ret, out, err = self._run(f'-S --needed --noconfirm {pkg}')
        if err:
            msg = '\n'.join(err)
            debug(msg) if ret==0 else error(msg)
        return ret==0

    def do_remove(self, pkg):
        ret, out, err = self._run(f'-Rns --noconfirm {pkg}')
        return ret == 0

    def do_cleanup(self):
        self._run(f'-Yc')

    def do_update(self):
        self._run('-Syu --noconfirm')

    def do_installed(self, pattern=None):
        raise NotImplemented

    def do_installable(self, pattern):
        ret, out, err = self._run(f'-Ss {pattern}')
        for line in out[::2]:
            name, ver, *_ = line.split()
            yield name.strip(), ver.strip()


class Manjaro(Distro):
    def do_init(self):
        ret, out, err = self.run('yay --version')
        if ret!=0:
            self.run('pacman -Sq --noconfirm git base-devel binutils')
            self.run('pacman -Sq --noconfirm yay')


class Endeavour(Distro):
    def do_init(self):
        # installed out of the box
        ret, out, err = self.run('yay --version')
        if ret!=0:
            error('\n'.join(err))

