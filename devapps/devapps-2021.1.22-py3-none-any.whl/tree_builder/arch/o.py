"""
Parser for a Type / Class Tree

After a call to build_type_hirarchy, the types are put into a hirarchy, then
the class parsing starts.

The main features this thing provides is to detect type derived superclasses and
rearanges of them as new classes within the defining one.

        class Foo(Bar, Baz) ->
        class Foo(Bar)
                class Baz(Baz)

where in this not yet built when doing this,
we are in its metacls __new__ yet.

later Foo.Baz can be getting special settings without influencing the other
Baz classes.

This allows for very small definition specs.

"""

# -------------------------------------------------------------- Build the Tree
hirarchy = []
hirarchy_built = False
# non interesting bases, up to the first type:
mixins = {}
classes = {}
cls_counter = 0


def out(*msg):
    try:
        console.log(' '.join([str(m) for m in msg]))
    except:
        print(*msg)


class MixinTypeMetaClass(type):
    """ outside the hirarchy but still a type.
    not in use currently, was e.g. for Label types like ServiceGroup=foo
    (later we added svc group into the hirarchy)
    """

    def __new__(cls, name, bases, attrs):
        ncls = type.__new__(cls, name, bases, attrs)
        mixins.setdefault(ncls, [])
        return ncls


class MT(object):
    __metaclass__ = MixinTypeMetaClass


def build_type_hirarchy(root):
    """ e.g. Project"""
    out(hirarchy, 'fooo')
    if root not in hirarchy:
        raise Exception(root, 'not in hirarchy')
    while 1:
        if hirarchy[0] != root:
            hirarchy.pop(0)
        else:
            break
    out('have hirarchy', [n.__name__ for n in hirarchy])
    global hirarchy_built
    hirarchy_built = True  # close hirachy, following are specific classes


def add_to(*dests, **kw):
    'convenience wrapper for add_cls - from spec'
    dests = _list(dests)
    for parent in dests:
        for k, childs in kw.items():
            for child in _list(childs):
                if not child.type == k:
                    raise Exception("Can't add: %s is no %s" % (child, k))
                add_cls(parent, child)


def add_cls(parent, child):
    """ called from the spec """
    check_allow_add(parent, child)
    out('    adding %s to %s' % (child, parent))
    new_sub = type(child.__name__, (child,), {'_parent': parent})
    setattr(parent, child.__name__, new_sub)
    return new_sub


class HirarchyErr(Exception):
    pass


def check_allow_add(cls, sub):
    if not sub._hirarchy == cls._hirarchy + 1:
        for c in cls._allowed_childs:
            if sub.type == c.type:
                return
        raise HirarchyErr("Can't add %s directly within %s" % (sub, cls))


# ----------------------------------------------------------------------------


class TypeMetaClass(type):
    def __new__(cls, name, bases, attrs):
        attrs = dict(attrs)
        b0, orig_bases = bases[0], None
        if b0 in mixins and not hirarchy_built:
            raise Exception("First Base Class can't be a mixin", b0)
        if hirarchy_built:
            if not '_parent' in attrs:
                while not b0 in hirarchy:
                    # a helper class (like class Node(Node, Role.Foo) and inner Node is
                    # hirarchy type -> act as if we'd defined all:
                    inh = classes[b0]
                    b0, bases = inh[0], inh + bases[1:]
                attrs['type'] = b0.__name__
                attrs['cls'] = name
                out('adding %s(%s)' % (name, b0.__name__))

                bases, orig_bases, mxins, attrs = set_bases_as_attrs(
                    name, b0, bases, attrs
                )

        else:
            out('registring type', name)
            attrs['type'] = name
            attrs.setdefault('_allowed_childs', [])

        global cls_counter
        cls_counter += 1
        attrs['_nr'] = cls_counter
        ncls = type.__new__(cls, name, bases, attrs)
        if hirarchy_built:
            if '_parent' in attrs:
                return ncls
        if orig_bases:
            classes[ncls] = orig_bases
            for m in mxins:
                if hasattr(m, '__code__'):
                    m(ncls)
                else:
                    out(
                        'Adding %s to %s %s'
                        % (name, mixins[m]['orig'].__name__, m.__name__)
                    )
                    mixins[m]['members'].append(ncls)
            return ncls
        if not hirarchy_built and len(hirarchy):
            hirarchy[-1:][0]._allowed_childs.append(ncls)
            ncls._hirarchy = len(hirarchy)
        hirarchy.append(ncls)
        return ncls

    def __repr__(cls):
        g = getattr
        p = g(cls, '_parent', None)
        if isinstance(p, str):
            p = 'prebound(%s)' % p
        elif p == None:
            p = 'type'
        else:
            if not g(p, '_parent', None):
                p = ''
            else:
                p = ' [%s]' % p
        return '%s.%s.%s%s' % (cls.type, g(cls, 'cls', ''), g(cls, '_nr', 0), p)


# import sys
# if sys.version_info.major == 3:
#    exec ('class T(object, metaclass=TypeMetaClass): descr=None')
# else:
class T(object, metaclass=TypeMetaClass):
    descr = None


# class T(object):
#    __metaclass__ = TypeMetaClass
#    descr = None


simple_types = (float, int, bool, str, type(None), tuple, list, dict)


def is_sub_cls(c):
    if is_simple_type(c):
        return
    if not getattr(c, '__class__', None):
        return
    return False
    out(isinstance(3, simple_types))
    out(isinstance(c, simple_types))
    return isinstance(c, simple_types) and not isinstance(c, property)

    # return getattr(c, '_parent', None)


def descr(c):
    """up the mro to find any descr or __doc__
    a manually set descr interrupts the process.
    """
    return 'decscr'
    d = ()
    alert(type(c))
    for b in c.mro()[:-2]:
        dd = getattr(b, 'descr', None)
        if dd and not dd in d:
            d += (dd,)
            break
        else:
            dd = b.__doc__
            if dd and not dd in d:
                d += (dd,)
    return '.'.join(d)


def build_tree(ncls):
    """ configure all prebound classes, add tree attrs to the others (_parent) """
    global hirarchy_built

    def pre(c, r, hir, cfg):
        c.descr = descr(c)
        childs = unordered_childs(c, is_sub_cls)
        for cc in childs:
            cc._parent = c
            for k in '_nr', '_hirarchy':
                cc._nr = getattr(cc, k, 0)
            cc.type = getattr(cc, 'type', '%s.%s' % (c.mro()[1].__name__, cc.__name__))
            cc.cls = getattr(cc, 'cls', cc.__name__)

    walk_tree(ncls, pre, None, is_sub_cls)
    hirarchy_built = 2


oltens = []


def set_bases_as_attrs(name, b0, orig_bases, attrs):
    """ type hirarchy is built at this point
    Our job now is to pop those bases (and add them as subclasses which
    registered already).
    If registered as mixin then we create new mixins or resolve - see below
    """

    def add_local(b0, name, sub, parent_attrs, lms=None):
        """
        """
        try:
            check_allow_add(b0, sub)
        except HirarchyErr as ex:
            if not lms:
                raise Exception('Hirarchy error %s %s' % (b0, sub))

            for i in range(len(lms), 0, -1):
                l = lms[i - 1]
                try:
                    t = add_cls(l, sub)
                    return t
                except HirarchyErr:
                    lms.pop(i - 1)
            raise Exception('Cannot add local %s %s' % (b0, sub))
        bn = sub.__name__
        out('    adding %s to %s' % (sub, name))
        parent_attrs[bn] = t = type(bn, (sub,), {'_parent': name})
        parent_attrs.setdefault('_from_mro', []).append(t)
        return t

    mxins = []

    def new_mixin(ncls, b0, orig_mixin):
        if ncls in mixins:
            raise Exception('mixin %s already defined' % ncls)
        mixins[ncls] = {'members_cls': b0, 'members': [], 'orig': orig_mixin}

    mx = mixins.get(b0)
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
    for b in orig_bases[1:]:
        if b in mixins:
            # a mixin type in the bases: class AXESS(Service, Group)
            # -> we'll create a NEW mixin, but with a members_type,
            # e.g. Service
            # if such a members_cls is alredy set, then we resolve
            # e.g. class Foo(Role, AXESS), AXESS is such a mx-> resolve
            mx = mixins[b]
            if 'members_cls' in mx:
                out('    resolving all members of %s' % b.__name__)
                for m in mx['members']:
                    lms = [add_local(b0, name, sub=m, parent_attrs=attrs)]
            else:
                # create new
                mxins.append(lambda ncls: new_mixin(ncls, b0, b))
        elif b in hirarchy:
            import pdb

            pdb.set_trace()
        elif b in classes:
            lms.append(add_local(b0, name, sub=b, parent_attrs=attrs, lms=lms))
        else:
            # normal superclass:
            new_bases.append(b)
    return tuple(new_bases), orig_bases, mxins, attrs


def allow(*what, **on):
    import pdb

    pdb.set_trace()
    # if exec_env == 'server':
    #    [k._allowed_childs.append(v) for k in _list(on.pop('on')) \
    #                                for v in _list(what)]


def _list(s):
    if s and isinstance(s, tuple) and isinstance(s[0], (tuple, list)):
        s = s[0]
    return list(s) if isinstance(s, (list, tuple)) else [s]


# ------------------------------------------------------------ Explore the Tree


def props(c):
    l = [(k, getattr(c, k)) for k in dir(c) if not k.startswith('_')]
    return [(k, v) for k, v in l if not is_function(v)]


def is_function(v):
    return typeof(v) == 'function'


def is_simple_type(v):
    if v is None:
        return True


__pragma__('ifdef', 'onserver')


def is_function(v):
    return hasattr(v, '__code__')


def is_simple_type(v):
    return isinstance(v, simple_types)


__pragma__('endif')


def walk_tree(cur, pre=None, post=None, match=None, res=None, cfg=None, hir=0):
    """
    Recursing the class tree, starting from a given root node (cur).
    the result is mutated
    pre, post, match = callables
    """
    if res is None:
        res = []
    hir += 1
    if pre:
        pre(cur, res, hir, cfg)
    if not cfg or cfg.get('stop_recursion') != cur.type:
        for k in ordered_childs(cur, match):
            walk_tree(k, pre, post, match, res, cfg, hir=hir)
    if post:
        post(cur, res, hir, cfg)
    return res


def unordered_childs(parent, match):
    c = getattr(parent, '_childs', None)
    if c:
        return c
    childs = []
    for k, v in props(parent):
        if match(v):
            childs.append(v)
    parent._childs = childs
    parent._childs_ordered = False
    return childs


def ordered_childs(parent, match):
    childs = unordered_childs(parent, match)
    if getattr(parent, '_childs_ordered', 0):
        return childs
    childs.sort(key=lambda x: getattr(x, '_nr', 0))
    parent._childs_ordered = True
    return childs
