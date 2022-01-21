"""
from build/bin/<app run script>
- for out of process entry
- early load of app module, for gevent and other imports

"""
import importlib
import json
import os
import sys
import traceback

py_env = {}
app_mod = None
app_type = None  # 'subproc|module'
app_import_err = None
enter_path = os.environ['PATH']


def app_load(fn_env):
    if py_env:
        return
    with open(fn_env) as fd:
        e = json.loads(fd.read())
    py_env.update(e)
    for p in reversed(e.get('PYTHONPATH', '').split(':')):
        sys.path.insert(0, p)
    [sys.path.append(p) for p in e.get('sys_path_append', '').split(':')]
    # all subprocs need this:
    export_env()
    if_app_is_module_then_load_it()


def export_env():
    m = {}
    for k, v in py_env.items():
        if isinstance(v, str):
            m[k] = v
            continue
        m[k] = json.dumps(v)
    os.environ.update(m)


def if_app_is_module_then_load_it():
    """ we remember the finding in a var file app_type"""
    global app_type
    app = py_env.get('app')
    if not app:
        raise Exception('No $app')

    def try_load():
        global app_mod, app_type, app_import_err
        if '/' in app:
            app_type = 'subproc'
            return
        app_type = 'module'
        # probably... not sure.
        # but we see now - early import in any case (gevent..)
        try:
            app_mod = importlib.import_module(app)
        except ImportError as ex:
            r = traceback.extract_tb(sys.exc_info()[2])[4:]
            l = [l.filename for l in r if '/%s' % app in l.filename]
            if not l:
                # this not a module, which just has an import error
                app_type = 'subproc'
                return
            # will report when we have logging:
            app_import_err = ex
        except Exception as ex:
            print('wtf', ex)
            breakpoint()
            i = 1

    # Trying to remember the app type is too risky: One wrong config and it never works again:
    try_load()
    return

    # ft = py_env['var_dir'] + '/app_type'
    # if os.path.exists(ft):
    #    with open(ft) as fd:
    #        app_type = fd.read().strip()
    # if app_type == None:
    #    try_load()
    #    with open(ft, 'w') as fd:
    #        fd.write(app_type)
    # elif app_type == 'module':
    #    try_load()
