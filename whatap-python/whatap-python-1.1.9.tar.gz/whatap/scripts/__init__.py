import os
import re
from functools import wraps

import sys, threading

from whatap import check_whatap_home, ROOT_DIR, init_config, update_config, \
    batch_agent, AGENT_NAME, go, configPort


def whatap_command(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if len(sys.argv) == 1:
            print('WHATAP: INVALID ARGMENTS.')
            print(func.__doc__)
        else:
            if check_whatap_home():
                return func(*args, **kwargs)
    
    return wrapper

def start_agent_batch():
    batch_agent()

def stop_agent():
    try:
        os.system('killall {}'.format(AGENT_NAME))
    except Exception as e:
        print(
            'Try to execute command. \n  {}'.format(
                '`ps -ef | grep {}`'.format(AGENT_NAME)))
        print(
            'Next, `sudo killall {}`'.format(AGENT_NAME))
    finally:
        print('WHATAP: AGENT STOP.')
    
@whatap_command
def start_agent():
    """
    Usage:
         whatap-start-agent [YOUR_APPLICATION_START_COMMAND]
    """
    
    args = sys.argv[1:]
    root_directory = os.path.dirname(ROOT_DIR)
    boot_directory = os.path.join(root_directory, 'bootstrap')
    
    python_path = boot_directory
    
    if 'PYTHONPATH' in os.environ:
        path = os.environ['PYTHONPATH'].split(os.path.pathsep)
        if not boot_directory in path:
            python_path = "%s%s%s" % (boot_directory, os.path.pathsep,
                                      os.environ['PYTHONPATH'])
    
    os.environ['PYTHONPATH'] = python_path
    
    program_exe_path = args[0]
    if not os.path.dirname(program_exe_path):
        program_search_path = os.environ.get('PATH', '').split(os.path.pathsep)
        for path in program_search_path:
            path = os.path.join(path, program_exe_path)
            if os.path.exists(path) and os.access(path, os.X_OK):
                program_exe_path = path
                break
    
    try:
        port = configPort()
    except Exception as e:
        print('WHATAP: AGENT ERROR: {}'.format(e))
        print('WHATAP: continue to start user application')

    try:
        go(opts={'whatap.port': str(port)})
    except Exception as e:
        print('WHATAP: AGENT ERROR: {}'.format(e))
        print('WHATAP: continue to start user application')

    try:
        os.execl(program_exe_path, *args)
    except Exception as e:
        print('WHATAP: INVALID ARGMENTS.')
        print(start_agent.__doc__)


OPTIONS = ['--host', '--license', '--app_name', '--app_process_name']


@whatap_command
def setting_config():
    """
    Usage:
        whatap-setting-config [--host HOST_ADDR]
                              [--license LICENSE_KEY]
                              [--app_name APPLICATION_NAME]
                              [--app_process_name APPLICATION_PROCESS_NAME]
    """
    home = 'WHATAP_HOME'
    if init_config(home):
        print('WHATAP:')
        args = ' '.join(sys.argv[1:])
        is_success=False
        for opt in OPTIONS:
            key = opt.split('--')[1]
            m = re.match(r"[\s\w\-\_\.\/]*" + key + " (?P<key>[\w\-\_\.\/]*)", args)
            if m:
                if key == 'host':
                    key = 'whatap.server.{}'.format(key)
                update_config(home, key, m.group('key'))
                print('\t{}={}'.format(key, m.group('key')))
                is_success = True
        #update_config(home, "unix_socket_enabled", 'true')
                
        if is_success:
            print('SUCCESS!')
        else:
            print(setting_config.__doc__)
    
    
