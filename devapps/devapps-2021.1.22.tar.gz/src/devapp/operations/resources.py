from devapp.tools import offset_port, exists, project
import os
from devapp.app import app


class tool:
    conda_env = 'lctools'


def redis_server(**kw):
    return 'redis-server --port %s' % offset_port(6379)


def verify_tools(path, rsc, **kw):
    for p in rsc.provides:
        d = path + '/' + p
        if not exists(d):
            app.error('Not found', cmd=d)
            return False
    return True


def lc_tools(*a, **kw):
    cmd = kw['cmd']
    if cmd == 'tmux':
        d = project.root() + '/tmp/tmux'
        os.makedirs(d, exist_ok=True)
        return {'cmd_pre': 'export TMUX_TMPDIR="%s"; ' % d, 'cmd': 'tmux'}
    return cmd


class rsc:
    """For services we change dir to project."""

    class redis_server:
        cmd = 'redis-server'
        run = redis_server
        pkg = 'redis'
        port = 6379
        systemd = 'redis-server'

    class lc_tools:
        # httpd for rotatelogs
        provides = ['git', 'fzf', 'jq', 'rg', 'fd', 'http', 'htop', 'tmux']
        conda_chan = 'conda-forge'
        conda_pkg = (
            ' '.join(provides)
            .replace(' rg ', ' ripgrep ')
            .replace(' fd ', ' fd-find ')
            .replace(' http ', ' httpie ')
        )
        run = lc_tools
        verify_present = verify_tools

    class lc_tools_kf:
        # httpd for rotatelogs
        provides = ['rotatelogs']
        conda_chan = 'kalefranz'
        conda_pkg = 'httpd'
        verify_present = verify_tools
