from setux.logger import debug
from setux.core.manage import SpecChecker
from setux.logger import debug, info, error


class Distro(SpecChecker):
    '''User managment
    '''
    manager = 'user'

    def do_validate(self, specs):
        for k, v in specs.items():
            if k=='name':
                yield k, v
            elif k=='uid':
                yield k, int(v)
            elif k=='gid':
                yield k, int(v)
            elif k=='home':
                yield k, v
            elif k=='shell':
                yield k, v
            else:
                debug(f'Invalid Spec for {self.manager} : {k}={v}')

    def get(self, attr=None):
        user = self.key if self.key else self.spec['uid']
        ret, out, err = self.run(f'grep ^{user}: /etc/passwd', shell=True)
        for line in out:
            name, x, uid, gid, rem, home, shell = line.split(':')
            if self.key:
                if name != self.key: continue
            else:
                if int(uid) != self.spec['uid']: continue
            attrs = dict(
                name = name,
                uid = int(uid),
                gid = int(gid),
                home = home,
                shell = shell,
            )
            return attrs[attr] if attr else attrs

    @property
    def group(self):
        group = self.distro.group.fetch(
            self.key,
            gid = self.get('gid')
        )
        return group

    @property
    def home(self):
        spec = self.get()
        home = self.distro.dir.fetch(
            spec['home'],
            user = spec['name'],
            group = self.group.name,
        )
        return home

    def chk(self, name, value, spec):
        if name=='home':
            return self.home.check()
        return value == spec

    def cre(self, check=True):
        if self.get():
            debug(f'user {self.key} exists')
        else:
            debug(f'user create {self.key}')
            self.do_cre(user=self.key, check=check)
            self.home.deploy()

    def mod(self, key, val, check=True):
        debug(f'user {self.key} change {key} -> {val}')
        if key=='gid':
            self.distro.group(self.key, gid=val).deploy()
        if key=='home':
            self.home.deploy()
        self.do_mod(user=self.key, key=key, val=val, check=check)

    def rm(self, check=True):
        if self.get():
            debug(f'user delete {self.key}')
            self.do_rm(user=self.key, check=check)
        else:
            debug(f'user {self.key} not found')

    def do_cre(self, *, user, check):
        self.run(f'useradd {user}', check=check)

    def do_mod(self, *, user, key, val, check):
        self.run(f'usermod --{key} {val} {user}', check=check)

    def do_rm(self, *, user, check):
        self.run(f'userdel -r {user}', check=check)


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

