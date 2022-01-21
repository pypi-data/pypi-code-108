"""
Parser for a Type / Class Tree

After a call to build_type_hirarchy, the types are put into a hirarchy, then
the class parsing starts.

The main features this thing provides is to detect type derived superclasses and
rearanges of them as new classes within the defining one.

        class Foo(Bar, Baz) ->
        class Foo(Bar):
                class Baz(Baz)

where in this not yet built when doing this,
we are in its metacls __new__ yet.

later Foo.Baz can be getting special settings without influencing the other
Baz classes.

This allows for very small definition specs.
"""

# TODO: Check this: https://www.stat.washington.edu/~hoytak/code/treedict/

# -------------------------------------------------------------- Build the Tree
# py 2 version. py2 syntax is compat with py3, so py3 can override
# cls_with_meta
import os
import sys

# from tree_builder.py2 import cls_with_meta
from collections import OrderedDict


def sys_path_insert(fn):
    """ helper, often required in SPECs, which does import us only"""
    sys.path.insert(0, os.path.abspath(os.path.dirname(fn)))


try:
    is_str = lambda s, t=str: isinstance(s, t)
except:
    is_str = lambda s: isinstance(s, (str, bytes))  # v3


try:
    # have?
    from theming.pretty_print import dict_to_txt

    class ODict(OrderedDict):
        def __repr__(self):
            return dict_to_txt(self)


except:
    import json

    ODict = OrderedDict
    dict_to_txt = lambda a, **kw: json.dumps(a, indent=4, default=str)


def pretty(o):
    from tree_builder.render import to_dict

    return dict_to_txt(to_dict(o), fmt={'ax': 1})


class ObjKeyDict(dict):
    set = dict.__setitem__


have_tty = lambda: sys.stdin.isatty() and sys.stdout.isatty()


class UserInput:
    """Avoids repeatedly asking same questions over repeated spec runs
    Stores answered questions in DA_DIR/.stored_input
    """

    fn = lambda: os.environ.get('DA_DIR', 'no_da_dir') + '/.stored_input'
    # when loaded (oncee from fn) then this keeps all previous user input:
    # inp e.g. = {'env': {'registration_token': 'foo'}}
    inp = None

    @classmethod
    def get_stored_if_build(ui, val_pth):
        """We do not want to prevent parsing of spec if env vars are missing.

        Only when its a spec build we return None, resulting in questions on the tty
        (or failures if non interactive)
        """

        if ui.inp is None:
            ui.load()
        m = ui.inp
        # val_pth e.g. ['env', 'reg_token']:
        while val_pth:
            m = m.get(val_pth.pop(0)) or {}
        if m != {}:
            return m

        # are we a spec build? If not return a placeholder:
        from devapp.app import app_func
        from devapp.spec.build import build

        if app_func(inner=True) != build:
            # placholder, this is not a spec build:
            return 'Input Value(%s)' % '.'.join(val_pth)

    @classmethod
    def load(ui):
        if not os.path.exists(ui.fn()):
            ui.inp = {}
            return
        with open(ui.fn()) as fd:
            ui.inp = json.loads(fd.read())

    @classmethod
    def store(ui):
        """called by successfull spec.build, storing last inputs"""
        if ui.inp:
            with open(ui.fn(), 'w') as fd:
                fd.write(json.dumps(ui.inp, indent=2))


def Env(key, dflt=None, suggest=None):
    """env access bridge for specs - here we can in a build process
    parametrize the constructor query session
    """
    import os

    res = os.environ.get(key, dflt)
    if res is None:
        res = UserInput.get_stored_if_build(['env', key])
        if res is None:
            if have_tty():
                print('Require value for: %s' % key)
                print(
                    'Note: Specifying a command (format: json) will delay value acquisition to process start time and prevent putting the value into process environ.'
                )
                print('Example: ["cat", "/tmp/mypw"]')
                if suggest:
                    print('Suggested (enter to confirm): %s' % suggest)
                res = UserInput.inp.setdefault('env', {})[key] = (
                    input('Value for %s: ' % key) or suggest
                )

            if not res:
                raise Exception('Required but not provided: $%s' % key)

    return res


def mro(c):
    return c.mro()


class Reg:
    """
    stores global registries,to allow isolated load of more specs in one
    process (clients could pass maps as 'env', then not using os.environ)
    """

    def __init__(self, env):
        self.env = env
        self.mixins = {}
        self.hirarchy = []
        self.cls_counter = 0
        self.hir_postconfigured = 2
        self.hirarchy_built = False
        self.classes = ObjKeyDict({})


R = Reg(os.environ)


def reinit(env=os.environ):
    global R
    R = Reg(env)
    return R


def load_isolated(spec, env=None):
    """execing a spec file (as string), should not collide
    only problem I see is that T's _allowed childs could differ,
    have to make an exception for it

    Note: R
    """
    global R
    if env is None:
        env = os.environ
    R = Reg(env=env)
    R.hirarchy.append(T)
    exec(spec, globals())
    return R.Root


pystring = str


def out(*a):
    pass
    # print ' '.join([str(k) for k in a])


class MixinTypeMetaClass(type):
    def __new__(cls, name, bases, attrs):
        ncls = type.__new__(cls, name, bases, attrs)
        # ncls = super(MixinTypeMetaClass, cls).__new__(cls, name, bases, attrs)
        R.mixins.setdefault(ncls, [])
        return ncls


def out_clses(cs):
    r = ''
    for c in cs:
        r += ', name: ' + c.__name__
    return 'Classes: ' + r[1:]


class MT(object, metaclass=MixinTypeMetaClass):
    pass


def build_type_hirarchy(root):
    """ e.g. Project"""
    while 1:
        if R.hirarchy[0] != root:
            R.hirarchy.pop(0)
        else:
            break
    # that hack now is necessary since transcypt requires the base with the
    # metaclass as FIRST base. Our Py2/Py3 compliance hack (cls_with_meta)
    # inserts an intermediate class - with a constructor which would overwrite
    # the actual wanted one (and we don't have super in Transcrypt, so that we
    # could fix it in the intermediate's __init__).
    # In short: We have to bypass __init__ of the intermediate helper base class:
    pfh = globals().get('post_fix_hirarchy')
    pfh() if pfh else None
    out('have hirarchy', [n.__name__ for n in R.hirarchy])
    R.hirarchy_built = True  # close hirachy, following are specific classes


class HirarchyErr(Exception):
    pass


def check_allow_add(cls, sub):
    if cls.__name__ == 'xProject':
        import pdb

        pdb.set_trace()
    try:
        if not sub._hirarchy == cls._hirarchy + 1:
            for c in cls._allowed_childs:
                if sub.type == c.type:
                    return
            raise HirarchyErr("Can't add %s directly within %s" % (sub, cls))
    except Exception as ex:
        print(ex)
        import pdb

        pdb.set_trace()


# ----------------------------------------------------------------------------
def cast_str(v):
    for t in float, int:
        try:
            return t(v)
        except:
            pass
    if v.lower() == 'true':
        return True
    if v.lower() == 'false':
        return False
    return v


nil = '\x01'


class ItemGetterMetaType(type):
    """with env to attr mapping (for inheritance. => DONT do a dict here)"""

    def __getitem__(cls, k, dflt=None):
        if isinstance(k, str) and k.startswith('$'):
            'could be env var pointing to our var OR env var'
            # we have it directly?:
            k = k[1:]
            ck = getattr(cls, '_env_%s' % k, nil)
            if ck != nil:
                return ck
            k = R.env.get(k, nil)
            if k == nil:
                return dflt
        return getattr(cls, k, dflt)

    def __setitem__(cls, k, v):
        # support cls['foo,bar'] = 'bar', 'foo'
        if isinstance(k, str):
            if k.startswith('$'):
                setattr(cls, '_env_%s' % k[1:], v)
            else:
                setattr(cls, k, v)
        else:
            # n.Consul['is_server', 'port_http', 'port_dns'] = True, 8880, 53
            for k, v in zip(k, v):
                setattr(cls, k, v)

    def get(cls, k, dflt=None):
        return cls.__getitem__(k, dflt)

    def get_env(cls):
        r = ODict()
        for k in [i for i in dir(cls) if i.startswith('_env_')]:
            r[k[5:]] = getattr(cls, k)
        return r


class Group(object, metaclass=ItemGetterMetaType):
    pass


class TypeMetaClass(ItemGetterMetaType):
    def __new__(cls, name, bases, attrs):
        try:
            attrs = dict(attrs)  # 0
        except:
            pass
        attrs['name'] = name
        if not bases:
            bases = (object,)
        b0, orig_bases = bases[0], None
        if b0 in R.mixins and not R.hirarchy_built:
            raise Exception("First Base Class can't be a mixin", b0)

        if R.hirarchy_built:
            out('adding a class', name, bases)
            if not '_parent' in attrs and not hasattr(b0, '_parent'):
                while not b0 in R.hirarchy:
                    # a helper class (like class Node(Node, Role.Foo) and inner
                    # Node is
                    # R.hirarchy type -> act as if we'd defined all:
                    inh = R.classes.get(b0)
                    b0, bases = inh[0], inh + bases[1:]
                attrs['type'] = b0.__name__
                attrs['_cls'] = name
                attrs['_hir'] = R.hirarchy.index(b0)
                out('adding {0}({1})'.format(name, b0.__name__))
                bases, orig_bases, mxins, attrs = set_bases_as_attrs(
                    name, b0, bases, attrs
                )
        else:
            # out ('Registering type', name)
            attrs['type'] = name
            attrs.setdefault('_allowed_childs', [])

        R.cls_counter += 1
        attrs['_id'] = R.cls_counter
        # ncls = super(TypeMetaClass, cls).__new__(cls, name, bases, attrs)
        ncls = type.__new__(cls, name, bases, attrs)
        if orig_bases:
            out(ncls.__name__, 'orig_bases', out_clses(orig_bases))
        if R.hirarchy_built:
            # if name == 'NB':
            #    import pdb; pdb.set_trace()
            if '_parent' in attrs:
                out('returning', ncls.__name__)
                return ncls
        if orig_bases:
            R.classes.set(ncls, orig_bases)
            for m in mxins:
                if hasattr(m, 'func_name'):
                    m(ncls)
                else:
                    out(
                        'Adding %s to %s %s'
                        % (name, R.mixins[m]['orig'].__name__, m.__name__)
                    )
                    R.mixins[m]['members'].append(ncls)
            out('built class', ncls.__name__, out_clses(R.classes.get(ncls)))
            return ncls
        if not R.hirarchy_built:  # and len(R.hirarchy):
            if R.hirarchy:
                R.hirarchy[-1:][0]._allowed_childs.append(ncls)
            ncls._hirarchy = len(R.hirarchy)
        R.hirarchy.append(ncls)
        return ncls

    def __repr__(cls):
        p = getattr(cls, '_parent', None)
        if p:
            # an object within an exploded tree:
            return fidstr(cls)

        if isinstance(p, pystring):
            p = 'prebound(%s)' % p
        elif isinstance(p, type(None)):
            p = 'type'
        else:
            if not getattr(p, '_parent', None):
                p = ''
            else:
                p = ' [%s]' % p
        return '%s.%s.%s%s' % (
            cls.type,
            getattr(cls, 'name', ''),
            getattr(cls, '_id', 0),
            p,
        )


class T(object, metaclass=TypeMetaClass):
    descr = None

    @classmethod
    def all(cls, type, **kw):
        def filter(o, kw):
            for k, v in kw:
                if getattr(o, k, None) == v:
                    return True

        # depends on root._all_<type>s to be set in build time:
        res = [
            o for o in getattr(cls._parents[0], '_all_%ss' % type) if cls in o._parents
        ]
        if not kw:
            return res
        kw = list(kw.items())
        return [o for o in res if list(filter(o, kw))]


class AXCTreeObj(T):
    pass


# T = cls_with_meta(TypeMetaClass, {'descr': None})


def has_parent(c):
    return getattr(c, '_parent', None)


def descr(c):
    'up the mro to find any descr or __doc__'
    d = []
    for b in mro(c):
        if b in R.hirarchy:  # this is a type not a class
            break
        dd = getattr(b, 'descr', None)
        if dd and not dd in d:
            d.append(dd)
        else:
            dd = b.__doc__
            if dd and not dd in d:
                d.append(dd)
    return '.'.join(d)


def has_typ(c):
    try:
        return hasattr(c, 'type')
    except:
        pass


def add_to(*dests, **kw):
    'convenience wrapper for add_cls - from spec'
    dests = _list(dests)
    for parent in dests:
        for k, childs in list(kw.items()):
            for child in _list(childs):
                if not child.type == k:
                    raise Exception("Can't add: %s is no %s" % (child, k))
                add_cls(parent, child)


def add_cls(parent, child):
    """ called from the spec """
    check_allow_add(parent, child)
    out('    adding %s to %s' % (child, parent))
    # R.cls_counter += 1
    new_sub = type.__new__(
        TypeMetaClass,
        child.__name__,
        (child,),
        {'_parent': parent, '_id': R.cls_counter},
    )
    # new_sub = type(child.__name__, (child,), {'_parent': parent})
    setattr(parent, child.__name__, new_sub)
    return new_sub


def set_bases_as_attrs(name, b0, orig_bases, attrs):
    """ type hirarchy is built at this point
    Our job now is to pop those bases (and add them as subclasses which
    registered already).
    If registered as mixin then we create new R.mixins or resolve - see below
    """

    def add_local(b0, name, sub, parent_attrs, lms=None):
        """
        """
        msg = 'Error trying to add %s(%s) to %s: ' % (sub, name, b0)
        try:
            check_allow_add(b0, sub)
        except HirarchyErr:
            if not lms:
                raise Exception(msg + ' no mro based sub')
            for i in range(len(lms), 0, -1):
                l = lms[i - 1]
                try:
                    t = add_cls(l, sub)
                    return t
                except HirarchyErr:
                    lms.pop(i - 1)
            raise Exception(msg + 'check_allow_add failed')
        bn = sub.__name__
        out('    adding {0} to {1}'.format(sub.__name__, name))
        # parent_attrs[bn] = t = type(bn, (sub,), {'_parent': name})
        # won't work with R.mixins, is basically creating a class also for python=0:
        parent_attrs[bn] = t = type.__new__(
            TypeMetaClass, bn, (sub,), {'_parent': name}
        )
        parent_attrs.setdefault('_from_mro', []).append(t)
        out('parent_attrs', len(parent_attrs), list(parent_attrs.keys()))
        return t

    mxins = []

    def new_mixin(ncls, b0, orig_mixin):
        if ncls in R.mixins:
            raise Exception('mixin %s already defined' % ncls)
        R.mixins[ncls] = {'members_cls': b0, 'members': [], 'orig': orig_mixin}

    mx = R.mixins.get(b0)
    if mx:
        # class NBI(AXESS) where AXESS is a group
        # -> we set group='AXESS' and b0 to Service
        mxins.append(b0)  # this will add this new cls to b0's members,
        # we don't have it yet
        attrs[mx['orig'].__name__] = b0.__name__
        b0 = mx['members_cls']
        attrs['type'] = b0.type

    new_bases = [b0]
    lms = []  # last added mro based sub
    out('orig_bases', out_clses(orig_bases))
    out('orig_bases1', out_clses(orig_bases[1:]))
    for b in orig_bases[1:]:
        out('base', b.__name__)
        if b in R.mixins:
            # a mixin type in the bases: class AXESS(Service, Group)
            # -> we'll create a NEW mixin, but with a members_type,
            # e.g. Service
            # if such a members_cls is alredy set, then we resolve
            # e.g. class Foo(Role, AXESS), AXESS is such a mx-> resolve
            mx = R.mixins[b]
            if 'members_cls' in mx:
                out('    resolving all members of %s' % b.__name__)
                for m in mx['members']:
                    # lms = [add_local(b0, name, sub=m, parent_attrs=attrs)]
                    lms = [add_local(b0, name, m, attrs)]
            else:
                # create new
                mxins.append(lambda ncls: new_mixin(ncls, b0, b))
        elif b in R.hirarchy:
            out(
                'you should instantiate your inner classes from R.hirarchy type classes'
            )
            import pdb

            pdb.set_trace()
        elif R.classes.get(b):
            # lms.append(add_local(b0, name, sub=b, parent_attrs=attrs, lms=lms))
            lms.append(add_local(b0, name, b, attrs, lms))
        else:
            # normal superclass:
            new_bases.append(b)
    return tuple(new_bases), orig_bases, mxins, attrs


def allow(*what, **on):
    # def allow(what):
    # 'allow((this, that), (onthis, onthat))'
    # what, on = what[0], what[1]
    on = on['on'] if isinstance(on['on'], (list, tuple)) else (on['on'],)
    for o in on:
        for w in what:
            o._allowed_childs.append(w)


def _list(s):
    if s and isinstance(s, tuple) and isinstance(s[0], (tuple, list)):
        s = s[0]
    return list(s) if isinstance(s, (list, tuple)) else [s]


# ------------------------------------------------------------ Tools
def lazy(d, key, func_if_missing, args):
    """ a lazy setdefault effectively. Often useful"""
    if key in d:
        return d[key]
    d[key] = func_if_missing(*args)
    return d[key]


# ------------------------------------------------------------ Explore the Tree
def props(c):
    # keys = [k for k in dir(c) if not k.startswith('_')]
    l = [(k, getattr(c, k)) for k in dir(c) if not k.startswith('_')]
    return [i for i in l if not hasattr(i[1], 'func_name') and not i[0] == 'all']


simple_types = (float, int, bool, pystring)


def simple_props(c):
    res = [(k, v) for k, v in props(c) if isinstance(v, simple_types)]
    return res


struct_types = (float, int, bool, pystring, dict, list, tuple)


def struct_props(c):
    'still serializable but with dicts and lists'
    res = [(k, v) for k, v in props(c) if isinstance(v, struct_types)]
    return res


def walk_tree(cur, pre=None, post=None, match=None, res=None, cfg=None, level=0):
    """
    Recursing the class tree, starting from a given root node (cur).
    the result is mutated
    pre, post, match = callables
    """
    if not match:
        match = has_typ
    if res is None:
        res = []
    level += 1
    if pre:
        pre(cur, res, level, cfg)
    if not cfg or cfg.get('stop_recursion') != cur.type:
        for k in ordered_childs(cur, match):
            walk_tree(k, pre, post, match, res, cfg, level=level)
    if post:
        post(cur, res, level, cfg)
    return res


def setup(root):
    """ configure all prebound classes """
    cfg = {'hashes': [], 'root': root}
    out('walking tree', root.__name__)
    root._level = root._hir = 0
    root._parents = [root]

    # register (API): _all_<type>s, e.g. _all_clusters
    def type_list_n(c):
        return '_all_' + c.type.lower() + 's'

    for h in R.hirarchy:
        setattr(root, type_list_n(h), [])

    def pre(cur, res, level, cfg):
        root = cur._root = cfg['root']
        getattr(root, type_list_n(cur)).append(cur)
        if cur != root:
            cur._parents = list(cur._parent._parents)
            # c._cluster -> Cluster.foo
            for c in cur._parents:
                setattr(cur, '_%s' % c.type.lower(), c)

            cur._parents.append(cur)

        return unordered_childs(cur, has_typ, level)

    walk_tree(root, pre=pre, post=None, match=has_typ, cfg=cfg)
    R.hirarchy_built = R.hir_postconfigured
    root.descr = descr(root)
    R.Root = root
    root._hirarchy_list = R.hirarchy
    return root


create_tree = setup


def scale(c, into, n):
    for i0 in range(n):
        i = i0 + 1
        name = c.name + str(i)
        t = type(name, (c,), {})
        t.__doc__ = c.__doc__
        into[name] = t


def unordered_childs(parent, match, level=None):

    # if parent.name == 'NB':
    #    import pdb; pdb.set_trace()
    c = getattr(parent, '_childs', None)
    if c:
        return c
    childs = [(k, v) for k, v in props(parent) if match(v)]
    if not childs:
        _childs = childs
    else:
        # we sort class childs by mro order, e.g. NB(N, A, B, C) ->
        # _childs = [A, B, C] even if C._id < A._id since defined earlier:
        try:
            pmro = parent._from_mro
            childs.sort(key=lambda x: pmro.index(x[1]))
        except Exception as ex:
            # some parents have no _from_mro
            childs.sort(key=lambda x: x[1]._id)

        _childs = []
        for k, v in childs:
            # v = TypeMetaClass.__new__(TypeMetaClass, v.__name__, (v,), {})
            R.cls_counter += 1
            # v = TypeMetaClass.__new__(TypeMetaClass, v.__name__, (v,), {'_id': R.cls_counter})
            # if not isinstance(v._parent, basestring):
            #    import pdb; pdb.set_trace()
            #    v = v.__bases__[0]
            v = type.__new__(
                TypeMetaClass,
                v.__name__,
                (v,),
                {'_id': R.cls_counter, '_level': level, '_parent': parent},
            )
            setattr(parent, k, v)
            v.descr = descr(v)
            _childs.append(v)
    parent._childs = _childs
    # parent._childs_ordered = False
    return _childs


# spec API Functions:
def ordered_childs(parent, match):
    # match is always the same,thats why we can store the result:
    return unordered_childs(parent, match)


def full_id(c, sep=None):
    res = [o.name for o in c._parents]
    return sep.join(res) if sep else res


def assign(key, objs, vals):
    [setattr(_[0], key, _[1]) for _ in zip(objs, vals)]


def setter(key):
    def set(key, v, *o):
        for obj in o:
            setattr(obj, key, v)

    return lambda v, *o: set(key, v, *o)


# full id as string:
fidstr = lambda cls: '.'.join([c.name for c in cls._parents])


def get_spec_root(spec):
    for k in dir(spec):
        root = getattr(getattr(spec, k), '_root', None)
        if root:
            return root
    die('Could not determine spec root', spec)


if __name__ == '__main__':

    class Project(T):
        ''

    class Cluster(T):
        ''

    build_type_hirarchy(root=Project)

    class cluster(Group):
        class A(Cluster):
            'A cluster'

        class B(Cluster):
            'B cluster'

    class MyP(Project, cluster['A'], cluster.B):
        'Pro'

    setup(MyP)
    print(('have ', dir(MyP)))
