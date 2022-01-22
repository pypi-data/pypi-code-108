from setux.logger import debug
from setux.core.manage import SpecChecker


class Distro(SpecChecker):
    ''' No Login User
    '''
    manager = 'user_'

    def do_validate(self, specs):
        yield 'home', f'/home/{self.key}' # useradd -M doesn't work
        yield 'shell', '/bin/false'
        for k, v in specs.items():
            if k=='uid':
                yield k, int(v)
            elif k=='gid':
                yield k, int(v)
            elif k=='home':
                debug('No Home for System User')
            elif k=='shell':
                debug('No Shell for System User')
            else:
                debug(f'Invalid Spec : {k}={v}')

    def get(self):
        user = self.key if self.key else self.spec['uid']
        ret, out, err = self.run(f'grep ^{user}: /etc/passwd', shell=True)
        for line in out:
            name, x, uid, gid, rem, home, shell = line.split(':')
            if self.key:
                if name != self.key: continue
            else:
                if int(uid) != self.spec['uid']: continue
            return dict(
                name = name,
                uid = int(uid),
                gid = int(gid),
                home = home,
                shell = shell,
            )

    @property
    def group(self):
        return self.distro.group(
            self.key,
            gid = self.spec.get('gid')
        )

    def cre(self, check=True):
        debug(f'user create {self.key}')
        self.do_cre(user=self.key, check=check)

    def mod(self, key, val, check=True):
        debug(f'NO MOD for System User {self.key} ({key} : {val})')

    def rm(self, check=True):
        debug(f'user delete {self.key}')
        self.do_rm(user=self.key, check=check)

    def do_cre(self, *, user, check):
        self.run(f'useradd -M {user}', check=check) # M doesn't work
        self.run(f'usermod -L {user}', check=check)
        self.run(f'usermod -s /bin/false {user}', check=check)
        self.target.deploy('sudoers', user=user)

    def do_rm(self, *, user, check):
        self.run(f'userdel -r {user}', check=check)


#__to__do__
class FreeBSD(Distro):
    opts = dict(
        uid   = 'u',
        gid   = 'g',
        shell = 's',
        home  = 'd',
    )

    def do_cre(self, *, user, check):
        self.run(f'pw useradd -n {user}', check=check)

    def do_mod(self, *, user, key, val, check):
        opt = self.opts[key]
        self.run(f'pw usermod -n {user} -{opt} {val}', check=check)

    def do_rm(self, *, user, check):
        self.run(f'pw userdel -n {user} -r', check=check)

