import logging as logging_module
import os
import platform
import sys
import subprocess, signal
import time
from whatap import build
from whatap.util.date_util import DateUtil
import threading

__version__ = build.version

LOGGING_MSG_FORMAT = '[%(asctime)s] : - %(message)s'
LOGGING_DATE_FORMAT = '%Y-%m-%d  %H:%M:%S'

logging = logging_module.getLogger(__name__)

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] == 3

ROOT_DIR = __file__


class ContextFilter(logging_module.Filter):
    def __init__(self):
        super(ContextFilter, self).__init__()
        self.last_id = None
    
    def filter(self, record):
        try:
            if record.id:
                if self.last_id == record.id:
                    return False
                
                self.last_id = record.id
                return True
        
        except Exception as e:
            record.id = ''
            return True


from whatap.conf.configure import Configure as conf

CONFIG_FILE_NAME = 'whatap.conf'
LOG_FILE_NAME = 'whatap-hook.log'


class Logger(object):
    def __init__(self):
        self.logger = logging
        self.logger.addFilter(ContextFilter())
        self.handler = None
        
        self.create_log()
    
    def create_log(self):
        os.environ['WHATAP_LOGS'] = os.path.join(os.environ['WHATAP_HOME'],
                                                 'logs')
        if not os.path.exists(os.environ['WHATAP_LOGS']):
            try:
                os.mkdir(os.environ['WHATAP_LOGS'])
            
            except Exception as e:
                print('WHATAP: LOG FILE WRITE ERROR.')
                print(
                    'WHATAP: Try to execute command. \n  {}'.format(
                        'sudo mkdir -m 777 -p $WHATAP_HOME/logs`'))
        
        self.print_log()
    
    def print_log(self):
        try:
            if self.handler:
                self.logger.removeHandler(self.handler)
            
            temp_logging_msg_format = '[%(asctime)s] : %(id)s - %(message)s'
            logging_format = logging_module.Formatter(
                fmt=temp_logging_msg_format, datefmt=LOGGING_DATE_FORMAT)
            
            fh = logging_module.FileHandler(
                os.path.join(os.environ['WHATAP_LOGS'], LOG_FILE_NAME))
            fh.setFormatter(logging_format)
            self.logger.addHandler(fh)
            self.handler = fh
            
            self.logger.setLevel(logging_module.DEBUG)
        except Exception as e:
            print('WHATAP: LOGGING ERROR: {}'.format(e))
        else:
            self.print_whatap()
    
    def print_whatap(self):
        str = '\n' + \
              ' _      ____       ______' + build.app + '-AGENT  \n' + \
              '| | /| / / /  ___ /_  __/__ ____' + '\n' + \
              '| |/ |/ / _ \\/ _ `// / / _ `/ _ \\' + '\n' + \
              '|__/|__/_//_/\\_,_//_/  \\_,_/ .__/' + '\n' + \
              '                          /_/' + '\n' + \
              'Just Tap, Always Monitoring' + '\n' + \
              'WhaTap ' + build.app + ' Agent version ' + build.version + ', ' + build.release_date + '\n\n'
        
        str += '{0}: {1}\n'.format('WHATAP_HOME', os.environ['WHATAP_HOME'])
        str += '{0}: {1}\n'.format('Config', os.path.join(os.environ['WHATAP_HOME'],
                                                os.environ['WHATAP_CONFIG']))
        str += '{0}: {1}\n\n'.format('Logs', os.environ['WHATAP_LOGS'])
        
        print(str)
        logging.debug(str)


def read_file(home, file_name):
    data = ''
    try:
        f = open(os.path.join(os.environ.get(home), file_name), 'r+')
        data = str(f.readline()).strip()
        f.close()
    finally:
        return data


def write_file(home, file_name, value):
    try:
        f = open(os.path.join(os.environ.get(home), file_name), 'w+')
        f.write(value)
        f.close()
    except Exception as e:
        print('WHATAP: WHATAP HOME ERROR. (path: {})'.format(os.path.join(os.environ.get(home))))
        print(
            'WHATAP: Try to execute command. \n  {}'.format(
                '`sudo chmod -R 777 $WHATAP_HOME`'))
        return False
    else:
        return True


def check_whatap_home(target='WHATAP_HOME'):
    whatap_home = os.environ.get(target)
    if not whatap_home:
        print('WHATAP: ${} is empty'.format(target))
    
    return whatap_home


def init_config(home):
    whatap_home = os.environ.get(home)
    if not whatap_home:
        whatap_home = read_file(home, home.lower())
        if not whatap_home:
            whatap_home = os.getcwd()
            os.environ[home] = whatap_home
            
            print('WHATAP: WHATAP_HOME is empty')
            print(
                'WHATAP: WHATAP_HOME set default CURRENT_WORKING_DIRECTORY value')
            print('CURRENT_WORKING_DIRECTORY is {}\n'.format(whatap_home))
    
    if not write_file(home, home.lower(), whatap_home):
        return False
    
    os.environ[home] = whatap_home
    config_file = os.path.join(os.environ[home],
                               CONFIG_FILE_NAME)
    
    if not os.path.exists(config_file):
        with open(
                os.path.join(os.path.dirname(__file__),
                             CONFIG_FILE_NAME),
                'r') as f:
            content = f.read()
            try:
                with open(config_file, 'w+') as new_f:
                    new_f.write(content)
            except Exception as e:
                print('WHATAP: PERMISSION ERROR: {}'.format(e))
                print(
                    'WHATAP: Try to execute command. \n  {}'.format(
                        '`sudo chmod -R 777 $WHATAP_HOME`'))
                return False
    
    return True


def update_config(home, opt_key, opt_value):
    config_file = os.path.join(os.environ[home],
                               CONFIG_FILE_NAME)
    
    try:
        with open(config_file, 'r+') as f:
            is_update = False
            content = ''
            for line in f:
                if line:
                    key = line.split('=')[0].strip()
                    if key == opt_key:
                        is_update = True
                        line = '{0}={1}\n'.format(key, opt_value)
                    
                    content += line
            if not is_update:
                content += '{0}={1}\n'.format(opt_key, opt_value)
            open(config_file, 'w+').write(content)
    
    except Exception as e:
        print('WHATAP: OPTION ERROR: {}'.format(e))


def config(home):
    os.environ['WHATAP_CONFIG'] = CONFIG_FILE_NAME
    
    from whatap.conf.configure import Configure as conf
    if conf.init():
        from whatap.net.packet_enum import PacketEnum
        PacketEnum.PORT = int(conf.net_udp_port)

        from whatap.conf.license import License
        conf.PCODE = License.getProjectCode(conf.license)

        hooks(home)


from whatap.trace.trace_import import ImportFinder
from whatap.trace.trace_module_definition import DEFINITION, IMPORT_HOOKS, \
    PLUGIN


def hooks(home):
    try:
        for key, value_list in DEFINITION.items():
            for value in value_list:
                if len(value) == 3 and not value[2]:
                    continue
                
                IMPORT_HOOKS[value[0]] = {'def': value[1],
                                          'module': '{0}.{1}.{2}.{3}'.format(
                                              'whatap',
                                              'trace',
                                              'mod',
                                              key)}
    except Exception as e:
        logging.debug(e, extra={'id': 'MODULE ERROR'})
    finally:
        try:
            if conf.hook_method_patterns:
                from whatap.trace.mod.plugin import instrument_plugin
            
                patterns = conf.hook_method_patterns.split(',')
                for pattern in patterns:
                    pattern=pattern.strip()
                
                    module_name, class_def = pattern.split(':')
                    if not PLUGIN.get(module_name):
                        PLUGIN[module_name] = []
                    PLUGIN[module_name].append(class_def)
                    
                    DEFINITION["plugin"].append(
                        (module_name, 'instrument_plugin'))
                    
                    key = 'plugin'
                    for value in DEFINITION[key]:
                        IMPORT_HOOKS[value[0]] = {'def': value[1],
                                                  'module': '{0}.{1}.{2}.{3}'.format(
                                                      'whatap',
                                                      'trace',
                                                      'mod',
                                                      key)}
        
        except Exception as e:
            logging.debug(e, extra={'id': 'PLUGIN ERROR'})
        finally:
            sys.meta_path.insert(0, ImportFinder())
            logging.debug('WHATAP AGENT START!', extra={'id': 'WA000'})


def agent():
    home = 'WHATAP_HOME'
    whatap_home = os.environ.get(home)
    if not whatap_home:
        whatap_home = read_file(home, home.lower())
        if not whatap_home:
            whatap_home = os.getcwd()
            os.environ[home] = whatap_home
            
            print('WHATAP: WHATAP_HOME is empty')
            print(
                'WHATAP: WHATAP_HOME set default CURRENT_WORKING_DIRECTORY value')
            print('CURRENT_WORKING_DIRECTORY is {}\n'.format(whatap_home))
    
    if write_file(home, home.lower(), whatap_home):
        os.environ['WHATAP_HOME'] = whatap_home
        
        # t = threading.Thread(target=go)
        # t.setDaemon(True)
        # t.start()
        config(home)

ARCH = {
    'x86_64': 'amd64',
    'x86': '386',
    'x86_32': '386',
    'ARM': 'arm',
    'AArch64': 'arm64',
}

AGENT_NAME = 'whatap_python'



def go(batch=False, opts={}):
    newenv=os.environ.copy()
    newenv['WHATAP_VERSION'] = build.version
    newenv['whatap.start'] = str(DateUtil.now())
    newenv['python.uptime'] = str(DateUtil.datetime())
    newenv['python.version'] = sys.version
    newenv['python.tzname'] = time.tzname[0]
    newenv['os.release'] = platform.release()
    newenv['sys.version_info'] = str(sys.version_info)
    newenv['sys.executable'] = sys.executable
    newenv['sys.path'] = str(sys.path)
    newenv.update(opts)

    if not batch:
        home = 'WHATAP_HOME'
        file_name = AGENT_NAME + '.pid'
    else:
        home = 'WHATAP_HOME_BATCH'
        file_name = AGENT_NAME + '.pid.batch'

    def get_pname(pid):
        cmdlinepath = os.path.join('/proc', str(pid), 'cmdline')
        if os.path.exists(cmdlinepath):
            with open(cmdlinepath) as f:
                content = f.read()
                if content:
                    return content.strip()
        return ''
    pid = read_file(home, file_name)
    if pid and get_pname(pid).find('whatap_python') >= 0:
        os.kill(int(pid), signal.SIGKILL)
        
    try:
        home_path= os.environ.get(home)
        if os.path.exists(os.path.join(home_path, AGENT_NAME)):
            os.remove(os.path.join(home_path, AGENT_NAME))

        source_cwd = os.path.join(os.path.join(os.path.dirname(__file__), 'agent'), platform.system().lower(),
                                  ARCH[platform.machine()])

        os.symlink(os.path.join(source_cwd, AGENT_NAME),
                   os.path.join(home_path, AGENT_NAME))

        sockfile_path = os.path.join(home_path, 'run')
        if not os.path.exists(sockfile_path):
            os.mkdir(sockfile_path)
        newenv['whatap.enabled'] = 'True'
        newenv['WHATAP_PID_FILE'] = file_name
        process = subprocess.Popen(['./{0}'.format(AGENT_NAME), '-t', '3', '-d', '1'],
                                   cwd=home_path,env=newenv, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdouts, errs = process.communicate()
        print("executed golang module ", stdouts, errs)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print('WHATAP: AGENT ERROR: {}'.format(e))
    else:
        print('WHATAP: AGENT UP! (process name: {})\n'.format(AGENT_NAME))

import signal

from whatap.trace.mod.application_wsgi import interceptor, start_interceptor, \
    end_interceptor, trace_handler

from whatap.trace.trace_context import TraceContext

def register_app(fn):
    @trace_handler(fn, True)
    def trace(*args, **kwargs):
        callback = None
        try:
            environ = args[0]
            callback = interceptor((fn, environ), *args, **kwargs)
        except Exception as e:
            logging.debug('WHATAP(@register_app): ' + str(e),
                          extra={'id': 'WA777'}, exc_info=True)
        finally:
            return callback if callback else fn(*args, **kwargs)
    
    if not os.environ.get('whatap.enabled'):
        agent()
    
    return trace


def method_profiling(fn):
    def trace(*args, **kwargs):
        callback = None
        try:
            ctx = TraceContext()
            ctx.service_name=fn.__name__
            ctx = start_interceptor(ctx)
            callback = fn(*args, **kwargs)
            end_interceptor(thread_id= ctx.thread_id)
        except Exception as e:
            logging.debug('WHATAP(@method_profiling): ' + str(e),
                          extra={'id': 'WA776'}, exc_info=True)
        finally:
            return callback if callback else fn(*args, **kwargs)
    
    if not os.environ.get('whatap.enabled'):
        agent()
    
    return trace


def batch_agent():
    home = 'WHATAP_HOME_BATCH'
    batch_home = os.environ.get(home)
    if not batch_home:
        if not read_file(home, home.lower()):
            print('WHATAP: WHATAP_HOME_BATCH is empty')
            return
    
    if write_file(home, home.lower(), batch_home):
        os.environ['WHATAP_HOME_BATCH'] = batch_home
        os.environ['WHATAP_HOME'] = batch_home
        go(batch=True)


def batch_profiling(fn):
    import inspect
    frame = inspect.stack()[1]
    module = inspect.getmodule(frame[0])
    
    def trace(*args, **kwargs):
        if not os.environ.get('whatap.batch.enabled'):
            home = 'WHATAP_HOME_BATCH'
            batch_home = read_file(home, home.lower())
            if not batch_home:
                print(
                    'WHATAP(@batch_profiling): try, whatap-start-batch')
                return fn(*args, **kwargs)
            else:
                os.environ['whatap.batch.enabled'] = 'True'
                os.environ['WHATAP_HOME_BATCH'] = batch_home
                os.environ['WHATAP_HOME'] = batch_home
                config(home)
        
        callback = None
        try:
            ctx = TraceContext()
            ctx.service_name=module.__file__.split('/').pop()
            ctx = start_interceptor(ctx)
            
            callback = fn(*args, **kwargs)
            end_interceptor(thread_id=ctx.thread_id)
        except Exception as e:
            logging.debug('WHATAP(@batch_profiling): ' + str(e),
                          extra={'id': 'WA777'}, exc_info=True)
        finally:
            return callback if callback else fn(*args, **kwargs)
    
    return trace


import fcntl, os, time
import errno
def openPortFile(filepath=os.environ.get('WHATAP_LOCK_FILE', '/tmp/whatap-python.lock')):
    f = None
    i=0
    while f == None and i < 100:
        try:
            f = open(filepath, 'r+')
        except IOError as e:
            if e.errno == 2:
                prefix = os.path.split(filepath)[0]
                try:
                    if not os.path.exists(prefix):
                        os.makedirs(prefix)
                    f = open(filepath, 'w+')
                except:
                    pass
        i += 1

    if f:
        try:
            fcntl.lockf(f, fcntl.LOCK_EX)
            return f
        except Exception as e:
            print(e)
            try:
                f.close()
            except:
                pass

def get_port_number(port=6600, home=os.environ.get('WHATAP_HOME')):
    if not home:
        return None

    for i in range(100):
        f = openPortFile()
        if not f:
            if i > 50:
                time.sleep(0.1)
            continue
    if f:
        lastPortFound = None
        for l in f.readlines():
            l = l.strip()
            try:
                (portFound, portHome) = l.split()
                portFound = int(portFound)
            except:
                continue
            if home == portHome:
                return portFound
            if not lastPortFound or lastPortFound < portFound:
                lastPortFound = int(portFound)
        if not lastPortFound:
            lastPortFound = port
        else:
            lastPortFound += 1
        f.write(str(lastPortFound))
        f.write('\t')    
        f.write(home)
        f.write('\n')    
        fcntl.lockf(f, fcntl.LOCK_UN)
        f.close()
        return lastPortFound
            
    return port


def configPort():
    port = get_port_number()
    if port:
        update_config('WHATAP_HOME', 'net_udp_port', str(port))
        return port