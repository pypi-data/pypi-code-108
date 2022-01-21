import os
import uuid
from fnmatch import fnmatch
from functools import partial

import jwt
from absl import flags

FLAGS = flags.FLAGS

flags.DEFINE_string('token_name', 'X-AX-API-TOKEN', 'Token name')
flags.DEFINE_boolean('no_token_check', False, 'Omit token checks (for dev mode)')
flags.DEFINE_string(
    'token_secret',
    '%(DA_DIR_SECURE)s/%(name)s/.token_secret',
    'filename, $.. or direct',
)


def read_token(realm, raw_token=None, get_app=None, secret=None, unauth=None):
    app = get_app()
    app_server = app['app_server']
    raw_token = (
        app_server.request.headers.get(FLAGS.token_name, 'x')
        if raw_token is None
        else raw_token
    )
    app_server.response.headers['Cache-Control'] = 'no-store'
    app_server.response.headers['Server'] = '%(name)s/%(version)s' % app
    if FLAGS.no_token_check:
        token = {'realms': '*', 'roles': 'publ_*'}
        raw_token = str(uuid.uuid4())
    else:
        try:
            token = jwt.decode(raw_token, secret, algorithms=['HS256'])
            realms = token['realms']
            # token = {'token': t}
        except:
            unauth('Require valid %s' % FLAGS.token_name)

    realms = token['realms']
    if not fnmatch(realm, realms + '*'):
        return unauth('Token invalid (realm)')

    return token, raw_token


# ------------------------------------------------------------------- app setup
def read_secret(get_app, unauth):
    if FLAGS.no_token_check:
        secret = ''
    else:
        s = FLAGS.token_secret
        m = dict(os.environ)
        m['name'] = get_app()['name']
        if '%(' in s:
            s = s % m
        if os.path.exists(s):
            s = 'file://' + s
        if not s.startswith('file://'):
            if s.startswith('$'):
                secret = os.environ[s[1:]]
            else:
                secret = s
        else:
            # for now:
            fn = s.split('file://', 1)[1]
            if not os.path.exists(fn):
                log.warn('token secret file not found', filename=fn)
                sys.exit(1)
            with open(fn) as fd:
                secret = fd.read().strip()
    return partial(read_token, get_app=get_app, unauth=unauth, secret=secret)
