import re
import logging
import sys
import os
import json
from typing import Optional
from datetime import datetime

from pathlib import Path
from patchwork import files, transfers
from invoke import runners
from invoke.exceptions import Exit
from fabric import Connection


logger = logging.Logger('fabric', level=logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))


class Tmux(object):
    """Tmux helper for fabric 2"""
    def __init__(self, runner, session_name='default'):
        self.session_name = session_name
        self.run_cmd = runner.run

        self.create_session()

    def create_session(self):
        test = self.run_cmd('tmux has-session -t %s' % self.session_name, warn=True)

        if test.failed:
            self.run_cmd('tmux new-session -d -s %s' % self.session_name)

        self.run_cmd(
            'tmux set-option -t %s -g allow-rename off' % self.session_name)

    def recreate(self):
        self.kill_session()
        self.create_session()

    def kill_session(self):
        self.run_cmd('tmux kill-session -t %s' % self.session_name)

    def command(self, command, pane=0):
        self.run_cmd('tmux send-keys -t %s:%s "%s" ENTER' % (
            self.session_name, pane, command))

    def new_window(self, name):
        self.run_cmd('tmux new-window -t %s -n %s' % (self.session_name, name))

    def find_window(self, name):
        test = self.run_cmd('tmux list-windows -t %s | grep \'%s\'' % (self.session_name, name), warn=True)

        return test.ok

    def rename_window(self, new_name, old_name=None):
        if old_name is None:
            self.run_cmd('tmux rename-window %s' % new_name)
        else:
            self.run_cmd('tmux rename-window -t %s %s' % (old_name, new_name))

    def wait_for(self, signal_name):
        self.run_cmd('tmux wait-for %s' % signal_name)

    def run_singleton(self, command, orig_name, wait=True):
        run_name = "run/%s" % orig_name
        done_name = "done/%s" % orig_name

        # If the program is running we wait to be finished.
        if self.find_window(run_name):
            self.wait_for(run_name)

        # If the program is not running we create a window with done_name
        if not self.find_window(done_name):
            self.new_window(done_name)

        self.rename_window(run_name, done_name)

        # Check that we can execute the commands in the correct window
        assert self.find_window(run_name)

        rename_window_cmd = 'tmux rename-window -t %s %s' % (
            run_name, done_name)
        signal_cmd = 'tmux wait-for -S %s' % run_name

        expanded_command = '%s ; %s ; %s' % (
            command, rename_window_cmd, signal_cmd)
        self.command(expanded_command, run_name)

        if wait:
            self.wait_for(run_name)


def merge(x, y):
    """ 仅支持一级嵌套
    gparam x:
    :param y:
    :return:
    """
    # logger.info('合并配置项，初始值: \n%s', x)
    # logger.warning('合并配置项，覆盖值：\n%s' % y)
    z = {}
    for xk, xv in x.items():
        if isinstance(xv, dict):
            new_xv = xv.copy()
            yv = y.get(xk)
            if yv is not None:
                new_xv.update(yv)
            z[xk] = new_xv
        else:
            yv = y.get(xk, None)
            z[xk] = xv if yv is None else yv
    for yk, yv in y.items():
        if x.get(yk) is None:
            z[yk] = yv
    # logger.info('合并配置项，最终值: \n%s', z)
    return z


class ConfigBuilder(object):

    def __init__(self, name: str, tplname: str, tpltarget: str, replaceobj: dict, basedir: Optional[Path]) -> None:
        """ 初始化
        :param tplname: 模版名称，不含扩展名
        :param dstname: 目测名称
        """
        self.name = name
        self.tplname = tplname
        self.tplfile = tplname + '.jinja2'
        self.tpltarget = tpltarget
        self.replaceobj = replaceobj
        self.basedir = basedir

    def create_from_jinja(self):
        """
        调用 jinja2 直接渲染
        """
        from jinja2 import Environment, FileSystemLoader
        tplenv = Environment(loader=FileSystemLoader(self.basedir))
        tpl = tplenv.get_template(self.tplfile)
        with open(self.tpltarget, 'w') as f:
            f.write(tpl.render(self.replaceobj))

    def write_config_file(self):
        # create_from_jinja 仅接受字符串
        if isinstance(self.tpltarget, Path):
            tpltarget = str(self.tpltarget.resolve())
        with open(self.tpltarget, 'w') as f:
            if self.tplname.endswith('_json'):
                json.dump(self.replaceobj, f, ensure_ascii=False, indent='  ')
            else:
                self.create_from_jinja()


class Deploy(object):
    def __init__(self, name, envs, conn, basedir=None, deploy_root_dir='/srv/app', pye='python3'):
        """ 初始化
        """
        self.name = name
        self.envs = envs
        self.conn = conn
        self.basedir = Path(basedir)
        self.deploy_root_dir = Path(deploy_root_dir)
        self.pye = pye

    def check_remote_conn(self):
        """ 确保当前提供的 conn 是远程版本
        """
        if not isinstance(self.conn, Connection):
            raise Exit('Use -H to provide a host!')

    def get_remote_path(self, *args):
        deploy_dir = self.get_env_value('deploy_dir')
        if deploy_dir is None:
            raise Exit('配置中必须包含 deploy_dir！')
        deploy_path = Path(deploy_dir)
        # logger.info('get_remote_path deploy_path: %s, deploy_root_dir: %s', deploy_path, self.deploy_root_dir)
        if deploy_path.is_absolute():
            return str(deploy_path.joinpath(*args).resolve())
        return str(self.deploy_root_dir.joinpath(deploy_path, *args))

    def check_env_name(self):
        if self.name is None:
            raise Exit('请使用 --env 参数指定一个环境名称！')
        keys = self.envs.keys()
        if not self.name in self.envs: 
            raise Exit('--env 参数值范围： \n\n%s' % '\n'.join(keys))

    def get_env_value(self, key=None, default_value=None):
        self.check_env_name()
        value = self.envs.get(self.name)
        if value and key is not None:
            return value.get(key, default_value)
        return value

    def remote_exists(self, file):
        """ 是否存在远程文件 file
        """
        self.check_remote_conn()
        # files.exists 仅接受字符串
        if isinstance(file, Path):
            file = str(file.resolve())
        return files.exists(self.conn, file)

    def make_remote_dir(self, *args):
        """ 创建部署文件夹
        """
        self.check_remote_conn()
        remotedir = self.get_remote_path(*args)
        if not self.remote_exists(remotedir):
            command = 'mkdir %s' % remotedir
            logger.info('创建远程文件夹 %s', command)
            self.conn.run(command)

    def cat_remote_file(self, *args):
        """ 使用 cat 命令获取远程文件的内容
        """
        f = self.get_remote_path(*args)
        logger.info('cat_remote_file %s', f)
        if not self.remote_exists(f):
            return None
        result = self.conn.run('cat ' + f, warn=False, hide=True)
        return result.stdout

    def get_remote_pid(self, host=None, port=None):
        """ 利用命令行查找某个端口运行进程的 pid
        :param host: IP 地址
        :param port: 端口号
        """
        self.check_remote_conn()
        address = None
        if host:
            address = host
        if port:
            p = ':' + str(port)
            if address:
                address += '@' + p
            else:
                address = p
        if not address:
            raise Exit('需要 host 或 port 配置。')
        # command = 'lsof -i :2004 | tail -1'
        command_fmt = 'lsof -i {} | tail -1'
        command = command_fmt.format(address)
        result = self.conn.run(command, warn=False, hide=True)
        if result.stdout == '':
            return None
        return re.split(r'\s+', result.stdout)[1]

    def init_remote_dir(self, deploy_dir):
        """ 创建远程服务器的运行环境
        """
        deploy_dir_path = Path(deploy_dir)
        for d in [ self.deploy_root_dir,
            deploy_dir,
            deploy_dir_path.joinpath('logs'),
            deploy_dir_path.joinpath('output') ]:
            self.make_remote_dir(d)

    def source_venv(self):
        remote_venv_dir = self.get_remote_path('venv')
        if not self.remote_exists(remote_venv_dir):
            raise Exit('venv 还没有创建！请先执行 init_remote_venv')
        return 'source {}/bin/activate'.format(remote_venv_dir)

    def init_remote_venv(self):
        """ 创建虚拟环境
        """
        remote_venv_dir = self.get_remote_path('venv')
        if not self.remote_exists(remote_venv_dir):
            self.conn.run('{} -m venv {}'.format(self.pye, remote_venv_dir))
        with self.conn.prefix('source {}/bin/activate'.format(remote_venv_dir)):
            self.conn.run('pip install -U pip')
            self.conn.run('pip install -r {}'.format(self.get_remote_path('requirements.txt')))

    def piplist(self, format='columns'):
        """ 获取虚拟环境中的所有安装的 python 模块
        :@param format: columns (default), freeze, or json
        """
        with self.conn.prefix(self.source_venv()):
            result = self.conn.run('pip list --format ' + format)
            return result.stdout

    def pipoutdated(self, format='columns'):
        """ 查看过期的 python 模块
        :@param format: columns (default), freeze, or json
        """
        with self.conn.prefix(self.source_venv()):
            result = self.conn.run('pip list --outdated --format ' + format)
            return result.stdout

    def pipupgrade(self, names=None, all=False):
        """ 更新一个 python 模块
        """
        with self.conn.prefix(self.source_venv()):
            mod_names = []
            if all:
                result = self.conn.run('pip list --outdated --format json')
                if result.ok:
                    mod_names = [item['name'] for item in json.loads(result.stdout)]
            elif names:
                mod_names = [name for name in names]
            if mod_names:
                self.conn.run('pip install -U ' + ' '.join(mod_names))

    def _get_replaceobj(self, baseobj, tplname, wrapkey=None):
        replobj = baseobj.copy()
        updateobj = self.get_env_value(tplname)
        if updateobj is not None:
            replobj = merge(replobj, updateobj)
        return {wrapkey: replobj} if wrapkey else replobj

    def _put_tpl_remote(self, cb, tpltarget_remote, force):
        self.make_remote_dir()
        # 删除远程文件
        tpltarget_remote_exists = self.remote_exists(tpltarget_remote)
        if force and tpltarget_remote_exists:
            logger.warning('delete %s', tpltarget_remote)
            remoter = self.conn.run('rm -f ' + tpltarget_remote)
            if remoter.ok:
                logger.warning('删除远程配置文件 %s', tpltarget_remote)
            tpltarget_remote_exists = False
        
        # 本地创建临时文件后上传
        if force or not tpltarget_remote_exists:
            cb.write_config_file()
            self.conn.put(cb.tpltarget, tpltarget_remote)
            logger.warning('覆盖远程配置文件 %s', tpltarget_remote)
            localrunner = runners.Local(self.conn)
            # 删除本地的临时配置文件
            localr = localrunner.run('rm -f ' + cb.tpltarget)
            if localr.ok:
                logger.warning('删除本地临时文件 %s', cb.tpltarget)

    def _replace_environ_values(self, obj, key, value) -> None:
        """ 执行具体的替换操作，支持递归
        """
        if isinstance(value, dict):
            for k, v in value.items():
                self._replace_environ_values(obj[key], k, v)
        else:
            environ_key = value.format(self.name.upper())
            environ_value = os.environ.get(environ_key)
            obj[key] = environ_value
            logger.info(f'替换 {key} 环境变量：{environ_key}， 值：{environ_value}')

    def _replace_values_from_environ(self, tplname, replaceobj: dict) -> None:
        """ 从环境变量中替换值
        例如，指定配置

        env_prod: {
            'config_json_value_environ_replacer': {
                'FLASK': {
                    'SQLALCHEMY_DATABASE_URI': 'AID_{}_SQLALCHEMY_DATABASE_URI',
                    'SECRET_KEY': 'AID_{}_SECRET_KEY',
                }
            }
        }
        
        在生成 prod 的配置文件时，会自动在环境变量中寻找 AID_PROD_SECRET_KEY 来替换 SECRET_KEY 的值
        """
        # 找到配置中是否有相应的配置
        replacer_name = f'{tplname}_value_environ_replacer'
        value_environ_replacer = self.get_env_value(replacer_name)

        if value_environ_replacer is None:
            return
        logger.info(f'找到了 {replacer_name}： {value_environ_replacer}')
        for k, v in value_environ_replacer.items():
            self._replace_environ_values(replaceobj, k, v)

    def put_tpl(self, tplname, baseobj, dstname=None, wrapkey=None, force=False, local=False):
        """ 基于 jinja2 模板生成配置文件
        :param wrapkey: 嵌套 dict 的键名。若提供，则将获取到的 replace 对象嵌套进入一个 dict  中，以 wrapkey 为键名
        :param dstname: 若提供，则使用 dstname 作为目标文件名，不提供则使用 tplname
        """
        if dstname is None:
            dstname = tplname
        replaceobj = self._get_replaceobj(baseobj, tplname, wrapkey)
        self._replace_values_from_environ(tplname, replaceobj)

        if self.name.startswith('local') or local:
            tpltarget = self.basedir.joinpath(dstname)
            logger.warning('tpltarget %s', tpltarget)
            if force or not tpltarget.exists():
                cb = ConfigBuilder(self.name, tplname, str(tpltarget.resolve()), replaceobj, self.basedir)
                cb.write_config_file()
                logger.warning('覆盖本地配置文件 %s', tpltarget)
        else:
            # 需要创建一个临时文件用于上传
            tpltarget_local = str(self.basedir.joinpath(tplname + '.temp').resolve())
            cb = ConfigBuilder(self.name, tplname, tpltarget_local, replaceobj, self.basedir)
            self._put_tpl_remote(cb, self.get_remote_path(dstname), force)

    def rsync(self, exclude=[], is_windows=False):
        """ 部署最新程序到远程服务器
        """
        if is_windows:
            # 因为 windows 下面的 rsync 不支持 windows 风格的绝对路径，转换成相对路径
            pdir = str(self.basedir.relative_to('.').resolve())
        else:
            pdir = str(self.basedir.resolve())
        if not pdir.endswith('/'):
            pdir += '/'
        deploy_dir = self.get_remote_path()
        self.init_remote_dir(deploy_dir)
        transfers.rsync(self.conn, pdir, deploy_dir, exclude=exclude)
        logger.warn('RSYNC [%s] to [%s]', pdir, deploy_dir)

    def get_logs(self, extras=[]):
        """ 下载远程 logs 到本地
        """
        log_files = ['app.log', 'error.log', 'access.log']
        time_string = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        for f in log_files + extras:
            logf = self.get_remote_path('logs/{}'.format(f))
            if not self.remote_exists(logf):
                logger.warning('找不到远程 log 文件 %s', logf)
                continue
            logp = Path(logf)
            local_file = self.basedir.joinpath('logs', '{name}_{basename}_{times}{extname}'.format(name=self.name, times=time_string, basename=logp.name, extname=logp.suffix))
            self.conn.get(logf, local=local_file)


class UwsgiDeploy(Deploy):
    """ 使用 uWSGI 来部署服务
    """
    def __init__(self, name, envs, conn, basedir=None, deploy_root_dir='/srv/app', pye='python3'):
        super().__init__(name, envs, conn, basedir, deploy_root_dir, pye)

    def get_fifo_file(self):
        """ 使用 master-fifo 来管理进程
        http://uwsgi-docs-zh.readthedocs.io/zh_CN/latest/MasterFIFO.html
        """
        fifofile = self.get_remote_path('uwsgi.fifo')
        if self.remote_exists(fifofile):
            return fifofile
        return None

    def get_pid_file(self):
        """ 使用 pidfile 来判断进程是否启动
        """
        pidfile = self.get_remote_path('uwsgi.pid')
        if self.remote_exists(pidfile):
            return pidfile
        return None

    def get_uwsgi_exe(self):
        """ 获取 venv 中 uwsgi 的可执行文件绝对路径
        """
        uwsgi_exe = self.get_remote_path('venv/bin/uwsgi')
        if not self.remote_exists(uwsgi_exe):
            raise Exit('没有找到 uwsgi 可执行文件！请先执行 init_remote_venv')
        return uwsgi_exe

    def start(self):
        """ 启动服务进程
        """
        pidfile = self.get_pid_file()
        if pidfile is not None:
            raise Exit('进程不能重复启动！')
        self.conn.run(self.get_uwsgi_exe() + ' ' + self.get_remote_path('uwsgi.ini'))

    def stop(self):
        """ 停止 API 进程
        """
        fifofile = self.get_fifo_file()
        if fifofile is not None:
            self.conn.run('echo q > %s' % fifofile)
        pidfile = self.get_pid_file()
        # 删除 pidfile 以便下次启动
        if pidfile is not None:
            self.conn.run('rm %s' % pidfile)

    def reload(self):
        """ 优雅重载 API 进程
        """
        fifofile = self.get_fifo_file()
        if fifofile is None:
            raise Exit('进程还没有启动！')
        self.conn.run('echo r > %s' % fifofile)


class GunicornDeploy(Deploy):
    """ 使用 Gunicorn 来部署服务
    """
    def __init__(self, name, envs, conn, basedir=None, deploy_root_dir='/srv/app', pye='python3'):
        super().__init__(name, envs, conn, basedir, deploy_root_dir, pye)

    def get_pid_file(self):
        """ 使用 pidfile 来判断进程是否启动
        """
        pidfile = self.get_remote_path('gunicorn.pid')
        if self.remote_exists(pidfile):
            return pidfile
        return None

    def get_pid_value(self, *args):
        """ 获取远程 pid 文件中的 pid 值
        """
        pid_value = self.cat_remote_file('gunicorn.pid')
        if pid_value is None:
            raise Exit('gunicorn.pid 没有值！')
        return pid_value.strip()

    def get_gunicorn_exe(self):
        """ 获取 venv 中 uwsgi 的可执行文件绝对路径
        """
        gunicorn_exe = self.get_remote_path('venv/bin/gunicorn')
        if not self.remote_exists(gunicorn_exe):
            raise Exit('没有找到 gunicorn 可执行文件！请先执行 init_remote_venv')
        return gunicorn_exe

    def start(self, wsgi_app=None, daemon=None):
        """ 启动服务进程
        :@param wsgi_app: 传递 wsgi_app 名称
        :@param daemon: 若值为 True，则强制加上 -D 参数
        """
        pidfile = self.get_pid_file()
        if pidfile is not None:
            raise Exit('进程不能重复启动！')
        conf = self.get_remote_path('gunicorn.conf.py')
        cmd = self.get_gunicorn_exe() + ' --config ' + conf
        if daemon == True:
            cmd += ' -D'
        if wsgi_app is not None:
            cmd += ' ' + wsgi_app
        self.conn.run(cmd)

    def stop(self):
        """ 停止 API 进程
        """
        pidvalue = self.get_pid_value()
        killr = self.conn.run('kill -s TERM ' + pidvalue)
        if killr.ok:
            logger.warning('优雅关闭 %s', pidvalue)
            # 删除 pidfile 以便下次启动
            self.conn.run('rm %s' % self.get_pid_file())
        else:
            logger.warning('关闭 %s 失败', pidvalue)

    def reload(self):
        """ 优雅重载 API 进程
        """
        pidvalue = self.get_pid_value()
        killr = self.conn.run('kill -s HUP ' + pidvalue)
        if killr.ok:
            logger.warning('优雅重载 %s', pidvalue)
        else:
            logger.warning('重载 %s 失败', pidvalue)


class SupervisorGunicornDeploy(Deploy):
    """ 使用 Supervisor + Gunicorn(非 daemon 模式) 来部署服务
    """
    def __init__(self, name, envs, conn, basedir=None, deploy_root_dir='/srv/app', pye='python3'):
        super().__init__(name, envs, conn, basedir, deploy_root_dir, pye)

    def get_pid_file(self):
        """ 使用 pidfile 来判断进程是否启动
        """
        pidfile = self.get_remote_path('gunicorn.pid')
        if self.remote_exists(pidfile):
            return pidfile
        return None

    def start(self):
        """ 启动服务进程
        """
        pidfile = self.get_pid_file()
        if pidfile is not None:
            raise Exit('进程不能重复启动！')
        pass
        # self.conn.run('uwsgi ' + self.get_remote_path('uwsgi.ini'))

    def stop(self):
        """ 停止 API 进程
        """
        pidfile = self.get_pid_file()
        # 删除 pidfile 以便下次启动
        if pidfile is not None:
            self.conn.run('rm %s' % pidfile)

    def reload(self):
        """ 优雅重载 API 进程
        """
        pass
