# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.

def _to_dict(obj):
    if isinstance(obj, str):
        return obj
    else:
        return obj.to_dict()


class SyExpr(object):
    @classmethod
    def name(cls):
        return cls.__name__.lower()


class SyType(SyExpr):
    def __str__(self):
        return '{}({})'.format(self.name(), self._arg)

    def to_dict(self):
        return (self.name(), _to_dict(self._arg))


class SyTypes(SyType):
    def __init__(self, sy_group):
        assert isinstance(sy_group, SyGroup)
        self._arg = sy_group

    def to_dict(self):
        return (self.name(), _to_dict(self._arg))


class SyGeneric(SyType):
    def __init__(self, name):
        assert any(isinstance(name, t) for t in (str, SyLetters))
        self._arg = name

    def __str__(self):
        if isinstance(self._arg, str):
            return 'sygeneric("{}")'.format(self._arg)
        else:
            return 'sygeneric({})'.format(self._arg)

    def to_dict(self):
        return (self.name(), _to_dict(self._arg))


class SyList(SyType):
    def __init__(self, elt_sytype):
        assert isinstance(elt_sytype, SyType)
        self._arg = elt_sytype


class SyTuple(SyType):
    def __init__(self, *elt_sytypes):
        for elt_type in elt_sytypes:
            assert isinstance(elt_type, SyType)

        self._arg = elt_sytypes

    def __str__(self):
        return 'sytuple({})'.format(
            ', '.join(str(a) for a in self._arg))

    def to_dict(self):
        return tuple(['sytuple'] + [_to_dict(elt) for elt in self._arg])


class SyIndex(SyExpr):
    def __str__(self):
        return 'syindex'

    def to_dict(self):
        return ('syindex',)


class SyLetters(SyExpr):
    def __init__(self, sy_index):
        assert isinstance(sy_index, SyIndex)
        self._arg = sy_index

    def to_dict(self):
        return (self.name(), _to_dict(self._arg))

    def __str__(self):
        return 'syletters({})'.format(str(self._arg))


class SyGroup(SyExpr):
    def __init__(self, name):
        assert isinstance(name, str)
        self._arg = name

    def to_dict(self):
        return (self.name(), _to_dict(self._arg))

    def __str__(self):
        return 'sygroup("{}")'.format(self._arg)


class SyIGroup(SyGroup):
    def __init__(self, name):
        assert isinstance(name, str)
        self._arg = name

    def to_dict(self):
        return (self.name(), _to_dict(self._arg))

    def __str__(self):
        return 'syigroup("{}")'.format(self._arg)


class SyOGroup(SyGroup):
    def __init__(self, name):
        assert isinstance(name, str)
        self._arg = name

    def to_dict(self):
        return (self.name(), _to_dict(self._arg))

    def __str__(self):
        return 'syogroup("{}")'.format(self._arg)


class SyUnlist(SyExpr):
    def to_dict(self):
        return ('syunlist',)

    def sycall(self, arg):
        return arg[1:-1]

    def __str__(self):
        return 'syunlist'


class SyMap(SyType):
    def __init__(self, expr, list_expr):
        self._arg = [expr, list_expr]

    def to_dict(self):
        return tuple([self.name()] + [_to_dict(elt) for elt in self._arg])

    def __str__(self):
        return 'symap({}, {})'.format(self._arg[0], self._arg[1])


sygeneric = SyGeneric
sytuple = SyTuple
sylist = SyList
sytypes = SyTypes
syletters = SyLetters
sygroup = SyGroup
syigroup = SyIGroup
syogroup = SyOGroup

syindex = SyIndex()
syunlist = SyUnlist()
symap = SyMap


_lookup = {
    syt.name(): syt for syt in
    [sygeneric, sytuple, sylist, sytypes, syletters,
     syigroup, syogroup, sygroup, syindex, syunlist, symap]}


class TemplateTypes(object):
    generic = sygeneric
    tuple = sytuple
    types = sytypes
    list = sylist
    letters = syletters
    group = sygroup
    igroup = syigroup
    ogroup = syogroup
    index = syindex
    unlist = syunlist
    map = symap


def _from_dict(obj):
    if isinstance(obj, tuple) or isinstance(obj, list):
        inst_or_cls = _lookup[obj[0]]
        if isinstance(inst_or_cls, SyExpr):
            return inst_or_cls
        elif issubclass(inst_or_cls, SyExpr):
            return inst_or_cls(*[_from_dict(arg) for arg in obj[1:]])
    elif isinstance(obj, str):
        return obj


def minno(no):
    if isinstance(no, int):
        return no
    elif no is None:
        return 1

    return minno(no[0])


def maxno(no):
    if isinstance(no, int):
        return no

    if len(no) == 1 or no[1] is None:
        return float('inf')

    return no[1] or no[0] or 1


def defno(no):
    if (isinstance(no, tuple) or isinstance(no, list)) and len(no) == 3:
        return no[2]
    return minno(no)


def eval_ports(ports):

    def eval_sygeneric(sytype, ctx):
        return '<{}>'.format(eval_sytype(sytype._arg, ctx))

    def eval_sytuple(sytype, ctx):
        args = [y for a in sytype._arg for y in eval_sytype(a, ctx)]
        return '({})'.format(','.join(args))

    def eval_sylist(sytype, ctx):
        return '[{}]'.format(eval_sytype(sytype._arg, ctx))

    def eval_syletters(sytype, ctx):
        i = eval_sytype(sytype._arg, ctx)
        oa = ord('a')
        assert i >= 0 and i <= ord('z') - oa
        return chr(oa + i)

    def eval_sytypes(group, ctx):
        return tuple([a for a in eval_sytype(group._arg, ctx)])

    def eval_sygroup(sygroup, ctx):
        return [eval_port(port)['type'] for port in groups[sygroup._arg]]

    def eval_syigroup(sygroup, ctx):
        return [eval_port(port)['type'] for port in igroups[sygroup._arg]]

    def eval_syogroup(sygroup, ctx):
        return [eval_port(port)['type'] for port in ogroups[sygroup._arg]]

    def eval_syindex(sytype, ctx):
        return ctx['index']

    def eval_symap(sytype, ctx):
        return tuple(map(sytype._arg[0].sycall,
                         eval_sytype(sytype._arg[1], ctx)))

    eval_lookup = {'sygeneric': eval_sygeneric,
                   'sytuple': eval_sytuple,
                   'sytypes': eval_sytypes,
                   'sylist': eval_sylist,
                   'syletters': eval_syletters,
                   'sygroup': eval_sygroup,
                   'syigroup': eval_syigroup,
                   'syogroup': eval_syogroup,
                   'syindex': eval_syindex,
                   'symap': eval_symap}

    def eval_sytype(sytype, ctx):
        return eval_lookup[sytype.name()](sytype, ctx)

    def eval_port(port):
        if port['eval']:
            index = port['group_index']
            ctx = {'index': index}
            sytype = _from_dict(port['type'])

            if isinstance(sytype, SyExpr):
                port['type'] = eval_sytype(sytype, ctx)

        port['eval'] = False
        return port

    groups = {}
    igroups = {}
    ogroups = {}

    for i, port in enumerate(ports):
        name = port['name']
        kind = port['kind']
        if kind == 'input':
            group_ports = igroups.setdefault(name, [])
        elif kind == 'output':
            group_ports = ogroups.setdefault(name, [])

        all_group_ports = groups.setdefault(name, [])

        port['group_index'] = len(group_ports)
        group_ports.append(port)
        all_group_ports.append(port)

    res = [eval_port(port) for port in ports]
    for port in res:
        del port['group_index']
    return res



class PortType(object):
    """Port is the interface for ports."""

    required_fields = ['description', 'type', 'scheme']
    optional_fields = ['name', 'requiresdata', 'n', 'preview']

    def __init__(self, description, port_type, scheme, **kwargs):
        self.description = description
        self.type = port_type
        self.scheme = scheme
        self.preview = False

        for key, value in kwargs.items():
            if key in self.optional_fields:
                setattr(self, key, value)

        if 'n' in kwargs:
            assert 'name' in kwargs, (
                "If argument n is provided then name must be also.")

    def to_dict(self):
        """
        Return dict contaning the required fields:
            'description'
            'type'
            'scheme'
        Optionally:
            'name'
            'n'
            'requiresdata'

        The values should all be of string type.
        """
        result = {}
        for key in self.required_fields + self.optional_fields:
            try:
                attr = getattr(self, key)
                if attr is not None:
                    result[key] = attr
            except Exception:
                pass

        if isinstance(self.type, SyExpr):
            result['type'] = self.type.to_dict()

        return result

    @staticmethod
    def from_dict(data):
        required = {key: data[key] for key in PortType.required_fields}
        optional = {}
        for key in PortType.optional_fields:
            if key in data:
                optional[key] = data[key]

        type_ = required.get('type')
        if isinstance(type_, dict):
            required['type'] = _from_dict(type_)

        return PortType(*required.values(), **optional)

    def __contains__(self, key):
        return (key in self.required_fields or
                key in self.optional_fields and hasattr(self, key))

    def __getitem__(self, key):
        if key in self:
            return getattr(self, key)

    def __str__(self):
        return '**{}** : {}\n    {}'.format(getattr(self, 'name', ''),
                                            self.type,
                                            self.description)


def instantiate(input_ports, output_ports, no=None):
    no = no or {}
    inputs = []
    outputs = []
    for kind, ports, res in [('input', input_ports, inputs),
                             ('output', output_ports, outputs)]:
        for i, port in enumerate(ports):
            port = dict(port)
            port['kind'] = kind
            port['def_index'] = i
            res.append(port)

    ports = []
    for kind, group in [('input', inputs), ('output', outputs)]:
        for p in group:
            n = no.get(kind, {}).get(p.get('name'))
            if n is None:
                n = defno(p.get('n', 1))
            for i in range(n):
                ports.append(dict(p))

    for i, port in enumerate(ports):
        if not port.get('name'):
            port['name'] = i

        port['eval'] = True

    ports = eval_ports(ports)
    inputs = []
    outputs = []

    for port in ports:
        if port['kind'] == 'input':
            inputs.append(port)
        elif port['kind'] == 'output':
            outputs.append(port)
        else:
            assert False, 'Unknown port kind.'

        port.pop('kind')
        if isinstance(port['name'], int):
            del port['name']

        # Fields to keep.
        fields = PortType.required_fields + PortType.optional_fields
        fields.remove('n')
        fields.append('def_index')

        for key in list(port.keys()):
            if key not in fields:
                port.pop(key)

    for ports in [inputs, outputs]:
        for i, port in enumerate(ports):
            port['index'] = i

    return inputs, outputs
