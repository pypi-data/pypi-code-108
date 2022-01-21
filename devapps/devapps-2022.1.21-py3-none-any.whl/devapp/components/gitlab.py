#!/usr/bin/env python
import json
import os
import sys
from configparser import ConfigParser
from functools import partial

import requests
from devapp.app import FLG, app
from devapp.cli_flags import oauth
from devapp.spec.os_tools import confirm
from devapp.spec.os_tools import env_get_interactive_write as envget
from theming.colorhilite import coljhighlight

get_endpoint = oauth()

env = os.environ
exists = os.path.exists
fn_cfg = lambda: env['DA_DIR'] + '/secure/python-gitlab.cfg'


def cfg(c=[], all=None):
    """returns parsed config for section <endpoint_name> - if not exists, builds it
    When interactive auth is requred we do not write - i.e. only valid for cur.
    session.
    To avoid frequent password queries, call GL.setup function.
    """
    try:
        return c[0][FLG.endpoint_name]
    except:
        pass
    c.append(ConfigParser())
    fn = fn_cfg()
    if exists(fn):
        app.info('Reading', fn=fn)
        c[0].read(fn)
    else:
        c[0]['global'] = {
            'default': FLG.endpoint_name,
            'ssl_verify': 'true',
            'timeout': 1,
        }
    if not FLG.endpoint_name in c[0]:
        t = GitLab.authenticate()
        c[0][FLG.endpoint_name] = t
    if all:
        return c[0]
    return c[0][FLG.endpoint_name]


def req(meth, pth, **kw):
    t = cfg()
    u = t['url'] + '/api/v4' + pth
    kw['access_token'] = t['access_token']
    app.info('API request', url=u, **kw)
    d = kw.get('data')
    m = partial(meth, json=d) if d else partial(meth, params=kw)
    res = m(u, headers={'ContentType': 'application/json'})
    if res.status_code < 300:
        try:
            return json.loads(res.text)
        except:
            return {'status': res.status_code, 'response': res.text}
    app.die('Error', status_code=res.status_code)


def get(pth, **kw):
    return req(requests.get, pth, **kw)


def delete(pth, **kw):
    return req(requests.delete, pth, **kw)


def post(pth, data):
    return req(requests.post, pth, data=data)


class GitLab:
    """Interacting with the Gitlab Server"""

    def authenticate(user=None, password=None, gl_endpoint=None):
        """User Password Auth to get oauth2 token"""
        user = user or FLG.username or envget('user')
        password = password or envget('password')
        h = gl_endpoint or get_endpoint()
        app.info('Getting tokens', endpoint=h, user=user, pw=password[:2] + '..')
        d = {'grant_type': 'password', 'username': user, 'password': password}
        r = requests.post(h + '/oauth/token', json=d)
        if not r.status_code == 200:
            app.die('Sorry', status=r.status_code)
        t = json.loads(r.text)
        t['url'] = h
        return t

    def setup():
        """write oauth token from authenticate into config file"""
        c = cfg(all=True)
        with open(fn_cfg(), 'w') as fd:
            c.write(fd)
        return app.info('Written', **cfg())

    class Projects:
        pth = '/projects'

        @classmethod
        def list(cls, id=None, search=None, owned=True, simple=True, **filters):
            """
            - gitl proj    # all
            - gitl proj 68 # details
            - gitl proj wifi # match
            """
            if str(id).isdigit():
                return cls.get(id)
            if id and not search:
                search = id

            l, kw = locals(), filters
            if search:
                kw['search'] = search
            for k in 'owned', 'simple':
                kw[k] = l[k]
            return get('/projects', **kw)

        def get(id):
            return get('/projects/%s' % id)

        default = list

    class Runners:
        @classmethod
        def add(
            cls,
            token,
            tag_list,
            description='',
            active=True,
            locked=True,
            run_untagged=False,
            protected=True,
        ):
            """
            token from <repourl>/settings/ci_cd
            - gi ru add xxasdfauYsaz-iuzo_K8G 'foo,bar'
            """
            kw = {'token': token, 'tag_list': tag_list}
            res = post('/runners', data=kw)
            return cls.get(res['id'])

        @classmethod
        def list(cls, id=None, type='a', **filters):
            """
            types: p -> project_type, i->instance_type, g->group_type
            - gi run li
            - gi run li p  # project type only
            - gi run li 42 # details
            """
            if str(id).isdigit():
                return cls.get(id)

            f = filters
            typs = {
                'p': 'project_type',
                'i': 'instance_type',
                'g': 'group_type',
                'a': 'all',
            }
            if id in typs:
                type = id
            t = typs.get(type, type)
            if t == 'all':
                r = {}
                for k in typs:
                    if k != 'a':
                        r[typs[k]] = cls.list(type=k, **filters)
                return r
            f['type'] = t
            all = filters.get('all', '')
            all = '/all' if all else ''
            return get('/runners' + all, **f)

        def all(type='i', **filters):
            """all: List all runners (requires admin)"""
            filters['all'] = True
            return GitLab.Runners.list(type=type, **filters)

        def get(id):
            return get('/runners/%s' % id)

        @classmethod
        def delete(cls, id, force=False):
            if sys.stdin.isatty() and not force:
                res = cls.get(id)
                if not res:
                    app.die('No runner found', id=id)
                print(coljhighlight(res))
                if not confirm('Delete', False):
                    return
            elif not force:
                app.die('Set to true when run non interactively')
            return delete('/runners/%s' % id)

        default = list
