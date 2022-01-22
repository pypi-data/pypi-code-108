from setux.logger import debug
from setux.core.manage import SpecChecker


class Distro(SpecChecker):
    """User's Group managment
    """
    manager = 'group'

    def do_validate(self, specs):
        for k, v in specs.items():
            if k=='name':
                yield k, v
            elif k=='gid':
                yield k, int(v)
            else:
                debug(f'Invalid Spec for {self.manager} : {k}={v}')

    def get(self):
        group = self.key if self.key else self.spec['gid']
        Ret, out, err = self.run(f'grep ^{group}: /etc/group', shell=True)
        for line in out:
            name, x, gid, users = line.split(':')
            if self.key:
                if name != self.key: continue
            else:
                if int(gid) != self.spec['gid']: continue
            return dict(
                name = name,
                gid = int(gid),
                users = users.split(','),
            )

    @property
    def name(self):
        return self.get()['name']

    @property
    def gid(self):
        return self.get()['gid']

    def cre(self, check=True):
        debug(f'group create {self.key}')
        self.do_cre(group=self.key, check=check)

    def mod(self, key, val, check=True):
        debug(f'group {self.key} change {key} -> {val}')
        self.do_mod(key=key, val=val, group=self.key, check=check)

    def rm(self, check=True):
        debug(f'group delete {self.key}')
        self.do_rm(group=self.key, check=check)

    def do_cre(self, *, group, check):
        self.run(f'groupadd {group}', check=check)

    def do_mod(self, *, group, key, val, check):
        self.run(f'groupmod --{key} {val} {group}', check=check)

    def do_rm(self, *, group, check):
        self.run(f'groupdel {group}', check=check)


class FreeBSD(Distro):
    opts = dict(
        gid = 'g',
    )

    def do_cre(self, *, group, check):
        self.run(f'pw groupadd -n {group}', check=check)

    def do_mod(self, *, group, key, val, check):
        opt = self.opts[key]
        self.run(f'pw groupmod -n {group} -{opt} {val}', check=check)

    def do_rm(self, *, group, check):
        self.run(f'pw groupdel -n {group}', check=check)

