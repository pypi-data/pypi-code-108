from datetime import datetime

from pybrary.ascii import oct_mod

from setux.logger import debug, error
from setux.core.manage import SpecChecker


ignore = 'verbose',

class Distro(SpecChecker):
    '''Files managment
    '''
    manager = 'file'

    def do_validate(self, specs):
        for k, v in specs.items():
            if k=='name':
                yield k, v
            elif k=='mode':
                yield k, str(v)
            elif k=='user':
                yield k, v
            elif k=='group':
                yield k, v
            elif k=='size':
                yield k, int(v)
            else:
                if k not in ignore:
                    debug(f'Invalid Spec for {self.manager} : {k}={v}')

    def get(self):
        ret, out, err = self.run(f'ls -l --color=never {self.key}', report='quiet')
        if ret: return
        try:
            mod, ln, usr, grp, size, month, day, time, path = out[0].split()
            typ, mod = mod[0], mod[1:10]
            assert typ=='-', f'FILE {self.key} : {typ} !'
            return dict(
                name  = path,
                mode  = oct_mod(mod),
                user  = usr,
                group = grp,
                size  = size,
            )
        except Exception as x:
            error('file %s !\n%s : %s', self.key, type(x), x)

    def __str__(self):
        data = self.get()
        if data:
            return f'File {self.key} {data["size"]} {data["mod"]} {data["usr"]}:{data["grp"]}'
        else:
            return f'File {self.key} not found'

    def cre(self):
        debug(f'file create {self.key}')
        self.run(f'touch {self.key}')

    def mod(self, key, val):
        debug(f'file {self.key} change {key} -> {val}')
        if key=='mode':
            self.run(f'chmod {val} {self.key}')
        elif (
            key in ('user', 'group')
            and 'user' in self.spec
            and 'group' in self.spec
        ):
            usr = self.spec["user"]
            grp = self.spec["group"]
            self.run(f'chown {usr}:{grp} {self.key}')
        elif key=='user':
            self.run(f'chown {val} {self.key}')
        elif key=='group':
            self.run(f'chgrp {val} {self.key}')
        else:
            raise KeyError(f' ! {key} !')

    def rm(self):
        debug(f'file delete {self.key}')
        self.run(f'rm {self.key}')

    @property
    def size(self):
        data = self.get()
        if data:
            size = data.get('size')
            if size:
                return int(size)

    @property
    def mtime(self):
        ret, out, err = self.run(f'stat -c "%Y" {self.key}')
        if ret == 0:
            ts = int(out[0])
            dt = datetime.fromtimestamp(ts)
            return dt

    @property
    def age(self):
        mtime = self.mtime
        if mtime:
            delta = datetime.now() - mtime
            return delta.days

    def read(self):
        content = self.target.read(self.key)
        assert self.size==len(content), f'\n size ! {self.size} ! {len(content)} !'
        return content

    def write(self, content):
        self.target.write(self.key, content)
        assert self.size==len(content), f'\n size ! {self.size} ! {len(content)} !'

    @property
    def hash(self):
        hasher = 'sha256sum -b'
        ret, out, err =  self.run(f'{hasher} {self.key}', report='quiet')
        if ret:
            debug(f'hash {self.key} ! {" ".join(out)} ! {" ".join(err)}')
            return None
        h, _p = out[0].split()
        return h

