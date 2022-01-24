# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import time
import redis

from threading import Lock
from urllib.parse import urlparse

from trytond.config import config

_client = None
_client_lock = Lock()


def get_client():
    global _client, _client_lock
    with _client_lock:
        if _client is None:
            redis_uri = config.get('session', 'redis_uri')
            assert redis_uri, 'redis uri not set'
            url = urlparse(redis_uri)
            assert url.scheme == 'redis', 'invalid redis url'
            host = url.hostname
            port = url.port
            db = url.path.strip('/')
            _client = redis.StrictRedis(host=host, port=port, db=db)
    return _client


def key(dbname, user, session):
    return 'session:%s:%d:%s' % (dbname, user, session)


# The current implementation only uses and checks for config:timeout
# To implement checking for config:max_age it will be needed
# to create two keys, one for max_age, one for timeout
def set_session(dbname, user, session, login):
    '''
    - Create a user session with expiry set to timeout
    - Return 'OK'
    '''
    k = key(dbname, user, session)
    timeout = config.getint('session', 'timeout')
    return get_client().setex(k, timeout, login)


def hit_session(dbname, user, session):
    '''
    - Search for a valid session
    - Reset the timeout on a valid session
    - Return the TTL of a found session or None
    '''
    k = key(dbname, user, session)
    timeout = config.getint('session', 'timeout')
    ttl = get_client().ttl(k)
    if ttl != -2:
        get_client().expire(k, timeout)
        return ttl


def get_session(dbname, user, session):
    '''
    - Get the value of a user session (currently the user name)
    - Return the value of a session or None
    '''
    k = key(dbname, user, session)
    return get_client().get(k)


def del_session(dbname, user, session):
    '''
    - Delete a user session
    - Return the number of deleted sessions
    '''
    k = key(dbname, user, session)
    return get_client().delete(k)


def count_sessions(dbname, user):
    '''
    - Count the sessions of a user
    - Return the number of active sessions
    '''
    c = get_client()
    ks = key(dbname, user, '*')
    return len(list(c.scan_iter(ks)))


def del_sessions(dbname, user):
    '''
    - Delete all sessions of a user
    '''
    c = get_client()
    ks = key(dbname, user, '*')
    for k in c.scan_iter(ks):
        c.delete(k)


def time_user(dbname, user, ttl):
    '''
    - Track the login time of a user per day
    - Return the login time today
    '''
    timeout = config.getint('session', 'timeout')
    get_client().incrby(
        'user:%s:%d:%s' % (dbname, user, time.strftime('%y:%m:%d')),
        timeout - ttl)
