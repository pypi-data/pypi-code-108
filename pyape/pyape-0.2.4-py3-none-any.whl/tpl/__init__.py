from pathlib import Path
from jinja2 import Environment, FileSystemLoader

basedir = Path(__file__).parent

# 所有的模版文件配置
tplconfs = {
    'supervisord': {
        'tpl': 'supervisord.conf.jinja2',
        'target': 'supervisord.conf',
        'default': {
            'unix_http_server_file': '/var/run/supervisor.sock',
            'supervisorctl_serverurl':  'unix:///var/run/supervisor.sock',
            'include_files': '/etc/supervisor/conf.d/*.conf',
            'supervisord_logfile': '/var/log/supervisor/supervisord.log',
            'supervisord_pidfile': '/var/run/supervisord.pid',
            'supervisord_user': 'root',
            'supervisord_directory': '/tmp',
        }
    },
    'systemd': {
        'tpl': 'supervisord.service.jinja2',
        'target': 'supervisord.service',
        'default': {
            'supervisord_exec': '/usr/local/bin/supervisord',
            'supervisord_conf': '/etc/supervisor/supervisord.conf',
            'supervisorctl_exec': '/usr/local/bin/supervisorctl',
        }
    },
    'program': {
        'tpl': 'supervisor_program.conf.jinja2',
        'target': None,
        'default': {
            'priority': 999,
            'user': 'app',
        }
    },
}


def create_from_jinja(tplname, tpltarget=None, replaceobj={}):
    """ 调用 jinja2 渲染
    :param tplname: 模版文件的名称
    :param tpltarget: 如果不提供则返回渲染后的文本，若提供则必须是一个 Path 对象
    """
    tplconf = tplconfs.get(tplname)
    if tplconf is None:
        raise ValueError('没有找到名为 %s 的模版文件！' % tplname)
    robj = dict(tplconf['default'])
    robj.update(replaceobj)
    tplenv = Environment(loader=FileSystemLoader(basedir.resolve()))
    tpl = tplenv.get_template(tplconf['tpl'])
    text = tpl.render(robj)
    if isinstance(tpltarget, Path):
        target = tplconf['target']
        if tpltarget.is_dir() and target is not None:
            tpltarget = tpltarget.joinpath(target)
        tpltarget.write_text(text)
    return text

