"""
Templating

"""
import json
import os
import re
import sys

from devapp import tools
from devapp.app import app
from tree_builder import full_id

# passed into rendering contexts:
r_objs_by_fid = {}

nil = '\x01'
fidstr = lambda r: r['___']  # stored here to show up top

postprocs = {'': lambda v: v, 'json.dumps': json.dumps}


class SmartAdapt:
    """processing the context render hits on cls.<key>"""

    def __init__(self, r, name=''):
        name = 'Template ' + name
        self.r, self.name = r, name
        self.log = app.log.bind(name=name, fid=fidstr(r))

    def __getitem__(self, k):
        'try proxy to class first'
        k, postproc = (k + '|>').split('|>')[:2]
        v = self.getitem(k)
        return postprocs[postproc](v)

    def getitem(self, k):
        if k == 'fid':  # often
            return self.r['spec']['fid']
        r, m = self.r, self.r
        k, dflt = (k + '|' + nil).split('|')[:2]
        ko = k
        if not '.' in k:
            if k.startswith('v:'):
                return Vault.get(r, k[2:])
            k = 'env.' + k
        elif k.startswith('.'):
            k = k[1:]
        parts = k.split('.')
        k = parts.pop()
        for part in parts:
            try:
                m = m[part]
            except:
                raise Exception(self.name, 'part not present', part, 'in', ko)
        # check env, alternatively:
        v = m.get(k, r['env'].get(ko, dflt))
        if v == nil:
            if sys.stdin.isatty():
                app.warn('Replacement Error', key=ko, r=r)
                self.log.warn('SmartAdapt: could not resolve', key=ko)
                breakpoint()
                print('Inspect the environ here')
            app.die('Could not resolve', key=ko, r=r)
        return v


def execfn(fn, r, smart=None):
    out = []
    # fmt:off
    # The rendering globals:
    m = {
        'r'        : r,
        'api'      : API,
        'R'        : smart,
        'out'      : out,
        # 'Vault'  : Vault,
        'classes'  : r_objs_by_fid,
    }
    # fmt:on
    # if template chdirs
    here = os.getcwd()
    try:
        # chdir to the hook file, to make live easy there:
        os.chdir(os.path.dirname(fn))
        app.info('Executing as python', template=fn)
        # better than exec when debugging:
        tools.exec_file(fn, m)
    finally:
        os.chdir(here)
    return out


single_percent_regex = re.compile(r'%(?!\()')  # perc. not followed by bracket


def exec_templ(fn, r):
    """we want to keep the name fixed, no matter if its plain or code
    (better for debugging)
    So we require a tag "axc-exec" somewhere within to exec it
    - execs are always execed using the current ctx
    - plains(simples) are loaded once, then mapped n times.
    """
    if not tools.exists(fn):
        raise Exception(fn, 'does not exist')
    smart = SmartAdapt(r, fn)
    out = tools.read_file(fn, '', bytes=100)
    first_line = out.split('\n', 1)[0]
    if first_line.startswith('#!') and 'python' in first_line:
        # if the template is python its result is a line array, 'out'
        out = '\n'.join(execfn(fn, r, smart))
    else:
        app.info('Reading', template=fn)
        out = tools.read_file(fn)
    try:
        try:
            return out % smart
        except TypeError as ex:
            pr = single_percent_regex.sub('%%', out)
            if pr != out:
                _ = 'You have single "%" in your template. '
                app.warn(_ + 'Trying with "%" escaped version.')
                return pr % smart
    except Exception as ex:
        app.warn(ex)
        breakpoint()
        _ = 0  # just to stay in local scope for ex


class API:
    """
    Template API.
    TODO:Global "api" in hooks.
    For reliabilty compared to uncontrollable
    imports of anything, this we can guarantee stable.
    => Never remove stuff here!'
    """

    class links:
        def get_via(r, io, *caps, min=1, max=1000):
            """
            conn = lambda io, w: api.links.get_via(r, io, w, min=1)[0]
            httpapi = conn('in', 'api')
            """
            from devapp.spec.links import get_via_by_r

            return get_via_by_r(r, io, *caps, min=1, max=1000)

        def get_vias(links):
            """for simple svcs easier to handle"""
            all_vias, add = {}, False
            for d in 'in', 'out':
                vias = all_vias[d] = []
                conns = links[d]
                for c in conns:
                    v = {'cls': ['.'.join(full_id(co)) for co in c['cls']]}
                    v.update(c['via'])
                    vias.append(v)
                    add = True
            return all_vias

    class inventory:
        pass

    class opsys:
        pass  # don't collide with import os after _into

    class fs:
        pass

    @staticmethod
    def create_token(r, secret_at=None, **kw):
        """TODO: support central token stores, Vault
        secret at is ignored, too shaky with spec dependent hub names
        """
        import jwt, time, uuid

        # independent of hub name:
        s = r['env']['DA_DIR'] + '/secure/token_secret'
        fn = r['env'].get('DA_FILE_TOKEN_SECRET', s)
        if not os.path.exists(fn):
            app.warn('Creating token secret', secret_file=fn)
            tools.write_file(fn, str(uuid.uuid4()))
        s = tools.read_file(fn)

        kw['iat'] = int(time.time())
        kw['exp'] = kw.get('exp', kw['iat'] + 86400 * 360 * 5)
        kw['why'] = kw.get('why', 'build')
        return jwt.encode(kw, s, algorithm='HS256').decode('utf-8')

    # links = Links
    @staticmethod
    def lazy(*a, **kw):
        'provide a cache for user funcs, e.g. the ssh key read'
        # not overwrite our own stuff:
        # TODO: take from old axc2:
        return c_lazy('user_api_' + a[0], *a[1:], **kw)

    @classmethod
    def _into(cls, g):
        """convenience, hooks *can* call this to have api funcs in globals
        api.write_file -> write_file..."""
        [
            operator.setitem(g, k, getattr(cls, k))
            for k in dir(cls)
            if not k.startswith('_')
        ]


'These we pass into custom funcs to make live simpler there'
# we do these one by one not by module
# to avoid accidential changes of function names in modules, breaking hooks

# api_funcs = (full_id, say, warn, l, die, call_func, dict_to_txt)
# [setattr(API, k.__name__, staticmethod(k)) for k in api_funcs]

# opsys api:
# os_api_funcs = (app.sh,)
# [setattr(API.opsys, k.__name__, staticmethod(k)) for k in os_api_funcs]

# fs api, pub funcs marked with 'API:' there:
# for k in dir(fs):
#    f = getattr(fs, k)
#    if (getattr(f, '__doc__', 0) or '').startswith('API:'):
#        setattr(API.fs, k, staticmethod(f))


def align_by_eq(lines):
    """make a nice aligned unit file """
    max_len, out, kvs = 0, [], []

    def add_kvs(out, kvs, m=0):
        if not kvs:
            return
        kls = [len(kv[0]) for kv in kvs if isinstance(kv, tuple)]
        if kls:
            m = max(kls)
        ind = ' ' * (m + 3)
        for kv in kvs:
            if not isinstance(kv, tuple):
                out.append(ind + kv)
            else:
                out.append('%s = %s' % (kv[0].ljust(m), kv[1]))

    while lines:
        line = lines.pop(0)
        if not line:
            kvs.append(line)
        elif line[0] == '[':
            add_kvs(out, kvs)
            out.append(line)
            kvs = []
        else:
            kv = line.split('=', 1)
            if len(kv) != 2:
                kvs.append(line)
            else:
                kvs.append((kv[0].rstrip(), kv[1].lstrip()))
                while lines:
                    if not line.endswith('\\'):
                        break
                    line = lines.pop(0)
                    kvs.append(line)
    if kvs:
        add_kvs(out, kvs)
    return '\n'.join(out)
