def port_from_preset(p):
    pr = getattr(presets['ports'], p, None)
    if not pr:
        raise Exception('Did not find port for %s in presets' % p)
    return pr


# ----------------------------------------------------------------------------
from urllib.parse import urlsplit, parse_qsl


def parse_via(url, props=None, default_port=None, add_caps_str=False):
    """
    'mysql+pymysql://root@127.0.0.1:3306/diameap' to
    {'caps': ['mysql', 'pymysql'],
     'hostname': '127.0.0.1',
     'netloc': 'root@127.0.0.1:3306',
     'path': '/diameap',
     'port': 3306,
     'scheme': 'mysql+pymysql',
     'username': 'root'}

    dia:
    url = 'aaa://127.0.0.1:13868;transport=tcp;protocol=diameter'
    we treat like it would be: 'aaa+tcp+diameter://127.0.0.1:13868?transport=tcp&protocol=diameter'

    'aaa://127.0.0.1:13868;transport=tcp;protocol=diameter' ->
    {'caps': ['aaa', 'tcp', 'diameter'],
     'hostname': '127.0.0.1',
     'netloc': '127.0.0.1:13868',
     'port': 13868,
     'protocol': 'diameter',
     'scheme': 'aaa',
     'transport': 'tcp'}
    """
    from .__init__ import simple_props

    props = {} if props is None else props
    if isinstance(url, dict):
        if 'port' in url:
            url['port'] = port_from_preset(url['port'])
        return url
    if not url:
        url = 'ip://'
    if not '://' in url:
        url += '://'

    u = urlsplit(url)
    hostport = u.netloc
    semicolnfos = None
    if ';' in hostport:
        hostport, semicolnfos = hostport.split(';', 1)
        u = urlsplit(url.replace(';' + semicolnfos, ''))

    nl = u.netloc.split(':')
    if len(nl) == 2 and not nl[1].isdigit():
        nl[1] = default_port or str(port_from_preset(nl[1]))
        url = url.replace(u.netloc, ':'.join(nl))
        u = urlsplit(url)

    m = props
    m.update(dict([(k, v) for k, v in simple_props(u) if v]))
    if m.get('hostname') == '*':
        m['hostname'] = '0.0.0.0'
    if not m.get('scheme'):
        msg = 'Could not derive Scheme: %s' % url
        if '_' in url.split('://', 1)[0]:
            msg += '. Scheme may not contain underscores. Use minus'
        raise Exception(msg)
    s = m['scheme']
    c = m['caps'] = s.split('+')
    if 'https' in c:
        m['ssl'] = True
        m['caps'][c.index('https')] = 'http'
    elif 'aaas' in c:  # diameter
        m['ssl'] = True
        m['caps'][c.index('aaas')] = 'aaa'

    m.update(parse_qsl(m.pop('query', {})))

    # dia:
    if semicolnfos:
        s = parse_qsl(semicolnfos.replace(';', '&'))
        m.update(s)
        m['caps'].extend([i[1] for i in s])
    if add_caps_str:
        m['caps_str'] = '+'.join(m['caps'])
    return m


isconn = lambda c: getattr(c, '__isconn__', False)


class Conn:
    __isconn__ = True
    via, src, next, sink = None, None, None, None

    @classmethod
    def show(c, ind=2):
        if not hasattr(c, 'src'):
            return
        via = c.via['caps'][0]
        sink = c.sink.name if c.sink else '-'
        # print('foo' * 1000)
        print(
            '%s src: %s, via: %s, sink: %s, next: %s'
            % (' ' * ind, c.src.name, via, sink, c.next.src.name if c.next else '-',)
        )
        ind = ind + 2
        c.next.show(ind) if c.next else None

    @classmethod
    def to(cls, sink, via=None):
        if via is None:
            via = cls.end().via
        if cls.next:
            c = cls.next.to(sink, via)
            return cls
        else:
            if not cls.sink:
                # we build a new one with same source, was given as
                # connect(foo).to(bar) -> first one is irrelevant
                connection_classes.pop()
            c = connect(cls.sink or cls.src, to=sink, via=via)
            if not cls.sink:
                return c
            cls.next = c
            cls.sink = None
        return cls

    @classmethod
    def end(cls):
        return cls if cls.sink else cls.next.end() if cls.next else cls


connection_classes = []


def connect(frm, to=None, via=None, **props):
    end = frm.end() if isconn(frm) else None
    if end and via is None:
        via = end.via
    via = parse_via(via, props)

    class Connection(Conn):
        pass

    C = Connection
    C.src = end.sink if end else frm
    C.sink = to
    C.next = None
    C.via = via
    if isconn(to):
        C.next = to
        C.sink = None
    if isconn(frm):
        end.next = C
        end.sink = None
        return frm
    connection_classes.append(C)
    return C


all_clses_by_conn = {}
from time import time


def map_connections_to_all_classes(root):
    """
    "connect(Nginx, Auth)" could mean tons of specific connections - since
    src and sink can be parent classes for many specific ones. Here we build
    out the all_clses_by_conn map, mapping all conn. objs to their affected
    sources and sinks
    """

    t1 = time()

    def add(conn, to, attr):
        if not hasattr(to, '_hirarchy'):
            # just e.g. a string
            return
        setattr(to, attr, getattr(to, attr, ()) + (conn,))

    for c in connection_classes:
        all_clses_by_conn[c] = {'src': [], 'sink': []}
        # if c.src._id == 22:
        #    import pdb; pdb.set_trace()
        add(conn=c, to=c.src, attr='_src')
        add(conn=c, to=c.sink or c.next.src, attr='_sink')

    # now we need all SPECIFIC classes for a connection -> we walk the tree:
    def set_conn(cls):
        for t in 'src', 'sink':
            conns = getattr(cls, '_' + t, ())
            for c in conns:
                all_clses_by_conn[c][t].append(cls)

    def walk(cur):
        set_conn(cur)
        for c in cur._childs:
            walk(c)

    walk(root)
    # print time() - t1


fullid = lambda cls: [c.name for c in cls._parents]


def conns_by_cls_dependent(cls):
    """We go through all conns to us (is_sink)
    and pop their resulting src conns
    A daemon like nginx should then have no more source conns, since outgoing
    are resulting from incomming.
    """
    outs = list(getattr(cls, '_src', ()))
    ins = list(getattr(cls, '_sink', ()))
    d_ins = []
    for c in ins:
        m = {'cls': all_clses_by_conn[c]['src'], 'via': c.via}
        n = c.next
        if n:
            outs.remove(n)
            m['sink'] = sink(n)
        d_ins.append(m)
    r = {'out': [sink(s) for s in outs], 'in': d_ins, 'cls': cls}
    return r


def sink(n):
    return {'via': n.via, 'cls': all_clses_by_conn[n]['sink']}


def find_connected_classes(cls, into):
    outs = list(getattr(cls, '_src', ()))
    ins = list(getattr(cls, '_sink', ()))
    if not outs and not ins:
        return
    for conns, t in (outs, 'sink'), (ins, 'src'):
        for c in conns:
            all = all_clses_by_conn[c][t]
            [into.append(a) for a in all if not a in into]


is_str = lambda s: isinstance(s, str)
is_ext_src = lambda s: s in ('*',)
is_end_sink = lambda s: is_str(s)
is_start_source = lambda s: len(s.split('.')) == 4 or is_ext_src(s)


def link(*what, **kw):
    'first arg may be name, else name is ""'
    name = ''
    if len(what) > 0:
        if is_str(what[0]) and not is_start_source(what[0]):
            name = what[0]
            what = what[1:]
    if len(what) == 0:
        raise Exception(kw, 'You did not specificy what to link (i.e. a client)')
    sinks = kw.pop('sink', 0)
    if sinks == 0:
        raise Exception('Link: "sink" is a required argument', what, kw)
    if not isinstance(sinks, (tuple, list)):
        sinks = (sinks,)
    root = what[0]._root if is_end_sink(sinks[0]) else sinks[0]._root

    links = root._links = getattr(root, '_links', [])

    # populate:
    [setattr(s, '_srcs', getattr(s, '_srcs', [])) for s in sinks if not is_end_sink(s)]
    for c in what:  # src -> sink
        # c could be e.g. '0.0.0.0', for a standalone sink
        standalone_sink = True
        cid = c
        if hasattr(c, '_parent'):
            c['_sinks'] = getattr(c, '_sinks', [])
            standalone_sink = False
            cid = c._id
        via = kw.pop('via')
        for s in sinks:
            link = {'src': c, 'sink': s, 'name': name}
            if via:
                link.update(parse_via(via))
            link['id'] = (cid, s._id if not is_end_sink(s) else s)
            link.update(kw)
            links.append(link)
            if not standalone_sink:
                c._sinks.append(link)
            if not is_end_sink(s):
                s._srcs.append(link)


def set_connections(spec, fid, attr='connections'):
    root = getattr(spec, fid.split('.', 1)[0])
    n = '_have_%s' % attr
    if getattr(root, n, None):
        return
    conns = [(c, getattr(root, c)) for c in dir(root)]
    conns = [c for c in conns if getattr(c[1], '__isconn__', False)]
    [set_links(root, conn[0], conn[1], attr) for conn in conns]
    setattr(root, n, 1)


no_conn = lambda: {'is_sink': [], 'is_src': []}


def get_conns(c, type, attr):
    conns = getattr(c, attr, None)
    if not conns:
        conns = no_conn()
        setattr(c, attr, conns)
    return conns[type]


def set_links(root, name, conn, attr):
    while True:
        conn.name = name
        src, sink, via = conn.src, conn.sink or conn.next.src, conn.via
        src_conns, sink_conns = (
            get_conns(src, 'is_src', attr),
            get_conns(sink, 'is_sink', attr),
        )
        cm = {
            'via': conn.via,
            'name': name,
            'src': src.name,
            'sink': sink.name,
            'obj': conn,
        }
        src_conns.append(cm)
        sink_conns.append(cm)
        if conn.sink:
            return
        conn = conn.next


presets = {}


def add_link(ports=None):
    # In Specs: L = add_link(ports=Ports) -> allows to use strings for ports
    presets['ports'] = ports or {}
    if not ports:
        return connect
    offs = getattr(ports, '_offset_', None) or 0
    if not str(offs).isdigit():
        raise Exception('No numeric port offset: %s' % off)
    offs = int(offs)
    s = lambda k, m: k.startswith(m)
    for k in dir(ports):
        if not s(k, 'ext_') and not s(k, '_'):
            p = int(getattr(ports, k))
            if p + offs > 655535 or p + offs < 10:
                raise Exception(
                    'Port must be 10 < port < 655535. have  %s' % (p + port)
                )
            setattr(ports, k, p + offs)
    return connect


def dump_all(root, fmt=None):
    map_connections_to_all_classes(root)
    r = {}
    for s in root._all_services:
        r[str(s)] = conns_by_cls_dependent(s)
    if fmt == 'json':
        import json

        r = json.dumps(r, indent=2, sort_keys=True, default=str)
    return r
