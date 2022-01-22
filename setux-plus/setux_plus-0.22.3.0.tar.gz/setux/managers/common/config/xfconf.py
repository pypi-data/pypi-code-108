from re import compile, IGNORECASE

from setux.logger import debug
from setux.core.manage import Manager


class Prop:
    types = dict(
        s = ('string', str),
        i = ('int', int),
        u = ('uint', int),
        f = ('float', float),
        b = ('bool', bool),
    )

    def __init__(self, manager, channel, name, val=None):
        self.query = manager.query
        self.channel = channel
        self.name = name.strip()
        self._val = val.strip() if val else None

    @property
    def full(self):
        return f'{self.channel}/{self.name}'

    def guess_typ(self, val):
        if val in ('true', 'false'):
            return 'b', val
        try:
            return 'i', int(val)
        except: pass
        try:
            return 'f', float(val)
        except: pass
        return 's', val

    def parse_typ(self, val):
        if ':' in val:
            t, v = val.split(':')
        else:
            t, v = self.guess_typ(val)
        name, conv = self.types[t]
        return name, conv(v)

    def parse_val(self, value):
        return [
            self.parse_typ(val)
            for val in value.split(',')
        ]

    @property
    def val(self):
        if self._val: return self._val
        v = self.query(f'-c {self.channel} -p {self.name}')
        v = v or ['???']
        v = ','.join(v[1:]) if len(v)>1 else v[0]
        return v

    @val.setter
    def val(self, value):
        self._val = None
        if value:
            values = self.parse_val(value)
            args = ' '.join(f"-t {t} -s '{v}'" for t, v in values)
            debug(f'{self.channel}/{self.name} = {", ".join(str(v[1]) for v in values)}')
            self.query(f'-c {self.channel} -p {self.name} -n {args}')
        else:
            debug(f'reset {self.channel}/{self.name}')
            self.query(f'-c {self.channel} -p {self.name} -r')

    def __str__(self):
        return f'{self.full}={self.val}'


class Channel:
    def __init__(self, manager, name):
        self.manager = manager
        self.query = manager.query
        self.name = name

    @property
    def props(self):
        pv = [
            line.split(maxsplit=1)
            for line in self.query(f'-lcv {self.name}', report='quiet')
        ]
        pv = [i for i in pv if len(i)==2]
        return [
            Prop(self.manager, self.name, name, val=val)
            for name, val in pv
        ]


class Distro(Manager):
    '''XFCE Config managment
    '''
    manager = 'xfconf'

    def query(self, args, report='normal'):
        ret, out, err = self.run(f'xfconf-query {args}', shell=True, report=report)
        return out if ret==0 else []

    @property
    def channels(self):
        return  {
            name : Channel(self, name)
            for name in self.query('-l', report='quiet')[1:]
        }

    @property
    def props(self):
        return [p
            for c in self.channels.values()
            for p in c.props
        ]

    def select(self, spec):
        pat, _, val = spec.partition('=')
        match = compile(pat, flags=IGNORECASE).match
        for prop in (str(p) for p in self.props):
            if match(prop):
                yield prop

    def dump(self, spec=r'.*', path=None):
        if path:
            with open(path, 'w') as out:
                for p in self.select(spec):
                    out.write(f'{p}\n')
        else:
            for p in self.select(spec):
                debug(p)
                print(p)

    def set(self, spec):
        c, _, pv = spec.partition('/')
        p, _, val = pv.partition('=')
        prop = Prop(self, c, p)
        old = prop.val
        if old!=val:
            print(f'{prop} => {val}')
            prop.val = val

    def set_re(self, spec):
        for prop in self.select(spec):
            seld.set(prop)

    def load(self, path):
        for line in open(path):
            if line.startswith('*'):
                self.set_re(line.strip()[1:])
            else:
                self.set(line.strip())
