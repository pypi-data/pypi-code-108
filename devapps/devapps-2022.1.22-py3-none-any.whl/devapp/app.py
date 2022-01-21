import json
import os
import signal
import subprocess
import sys
import time
from functools import partial

from absl import app as abslapp
from absl import flags as flags_
from devapp import gevent_patched  # noqa
from devapp import load, tools
from devapp.lib import sh
from structlogging import sl
from theming.absl_color_help import call_doc, exit_at_help_flag
from theming.colorhilite import coljhighlight

FLG = flags_.FLAGS


env = os.environ
py_env = load.py_env

kvmsg = lambda kw: '  ' + '\n  '.join(['%s: %s' % (k, str(v)) for k, v in kw.items()])
kvprint = lambda l, msg, kw: print('[%s] %s\n%s' % (l, msg, kvmsg(kw)))

notifier = [None]


def notify(app, msg, **kw):
    app.info('NOTIF: %s' % msg, **kw)
    if notifier[0] == None:
        notifier[0] = False
        for n in 'dunstify', 'notify-send':
            if os.system('type %s 1>/dev/null 2>/dev/null' % n) == 0:
                notifier[0] = n
                break
    if not notifier[0]:
        return
    try:
        subprocess.Popen([notifier[0], msg, '\n' + kvmsg(kw)])
    except:
        pass


class App:
    """
    Placeholder for dirs and log and die function, when app is run without the framework
    e.g. in unit tests, where, in the same process later the run_app function will be
    called, for the tested code (e.g lc's test_node_red)

    Otherwise, better use init_app, when you never call run_app.
    """

    is_initted = False
    name = sys.argv[0]

    def die(self, msg, **kw):
        App().warn(msg, **kw)
        sys.exit(1)

    def info(self, msg, **kw):
        kvprint('NFO', msg, kw)

    def warn(self, msg, **kw):
        kvprint('WRN', msg, kw)

    def debug(self, msg, **kw):
        kvprint('DBG ', msg, kw)

    def error(self, msg, **kw):
        kvprint('ERR ', msg, kw)

    def notify(self, msg, **kw):
        notify(App, msg, **kw)

    def __repr__(self):
        return json.dumps({'DevApp': self.name})


App.dbg = App.debug

# def kvs(f):
#    d = [k for k in dir(self) if not k.startswith('_')]
#    return dict([(k, getattr(self, k)) for k in d if f(k)])

# return json.dumps(
#    {
#        'DevApp': self.name,
#        'dirs': kvs(lambda k: '_dir' in k),
#        'attrs': kvs(lambda k: not '_dir' in k),
#    },
#    indent=4,
#    default=str,
#    sort_keys=True,
# )


# this is only for being able to print it:
app = App()


def set_direct_log_methods(app):
    for k in dir(app.log):
        if k[0] != '_' and not k == 'log':
            setattr(app, k, getattr(app.log, k))
    app.dbg = app.debug
    app.log_level = app.log._logger.level


# # allowing from devapp import FLG, flag;  flag.def_str(..)
# class flag:
#     to_flags = tools.define_flags


# r = lambda k: k.replace('DEFINE_', '')
# [setattr(flag, r(k), getattr(flags, k)) for k in dir(flags) if 'DEFINE_' in k]


# --------------------------------------------------------------- Wrapping Apps
def set_dirs():
    """
    - sets PATH if project.root()/bin exists so that resources are found
    """
    from devapp.tools import project

    # no-fail returns None when not found
    db = project.root(no_fail=True)
    if not db:
        return
    db += '/bin'

    if db and os.path.exists(db):
        p = os.environ['PATH']
        if not db + ':' in p:
            os.environ['PATH'] = db + ':' + p
    # e = env.get
    # p = 'DA_DIR_'
    # d = dict(
    #    [
    #        ('%s_dir' % k.split(p, 1)[1].lower(), e(k) + '/' + app_name)
    #        for k in env
    #        if k.startswith(p)
    #    ]
    # )
    ## an app (like build may allow to set --da_dir, overruling env:
    # d['da_dir'] = getattr(FLG, 'da_dir', env.get('DA_DIR', '.'))
    # we are used e.g. at construct/prepare.sh w/o DA:
    # c = 'CONDA_PREFIX'
    # breakpoint()
    # d['pkgs_dir'] = env.get(c + '_1') or env.get(c) + '/pkgs'
    # return d


command_name = lambda: sys.argv[0].rsplit('/', 1)[-1].replace('.py', '')


def set_app(name, log):
    app.log = log
    set_direct_log_methods(app)  # app.info, app.debug, ...
    app.notify = partial(notify, app)
    app.sh = sh
    # app.var_dir ...:
    set_dirs()
    # [setattr(app, k, v) for k, v in dirs(name).items()]
    # allows raise app.die(msg, **kw):
    app.die = app_die(app)
    app.name = name
    app.name_clean = tools.clean_env_key(name)
    app.is_initted = True
    if load.py_env:
        app.env = load.py_env
    if load.app_mod:
        app.mod = load.app_mod

    if FLG.redir_stderr and not os.environ.get('stderr_is_redirected'):
        # we leave it to the the system, can do better than python:
        os.environ['stderr_is_redirected'] = str(FLG.redir_stderr)
        cmd = ' '.join(['"%s"' % j for j in sys.argv])
        sys.exit(os.system(cmd + ' 2>%s' % FLG.redir_stderr))


def init_app_parse_flags(*args):
    """
    An app creator for situations when we do not call run_app - i.e. in pytest
    but still want e.g. logging

    Used in test.tools.build_flow for pytest.
    """
    if hasattr(app, 'log'):
        # not twice
        return
    name = args[0]
    # initializes flags - from argv; stores parsed flags into this FlagValues object.
    # we have no sys.argv in test situations, all will be default:
    l = list(args)
    # allows this: log_level=40 pytest -xs .
    l.extend(['--environ_flags'])
    # FLG = flags.FLAGS
    FLG(l)  # <----------- Flag parsing
    # now reset their values from env
    tools.set_flag_vals_from_env()
    kw_log = {}
    sl.setup_logging(**kw_log)
    log = sl.get_logger(name)
    set_app(name, log)


running = [0]


def run_app(
    main,
    kw_log=None,
    flags_parser=None,
    flags_validator=None,
    wrapper=None,
    flags=None,
    argv=None,
    call_main_when_already_running=False,
):
    """Starter for devapps' main functions

    Examples:
        run = lambda: run_app(build, {'log_dev_fmt_coljson': ['r']})

    flags: Optional flags class

    """

    if running[0]:
        # workaround:
        # certain tests require starting the app when already an app is running:
        if call_main_when_already_running:
            return main()
        app.die('Repeated call of app.run_app', hint='Should call only once per proc.')

    running[0] = True

    # some callers, like plugins, pass over their flags classes, do not call define in mod
    if flags:
        tools.define_flags(flags)
    tools.rm_absl_flags()
    # that's for flags: they only understand helpfull, we want -hf <match>
    argv = argv if argv else sys.argv
    exit_at_help_flag(main, argv)

    #     if '-hf' in argv or '--hf' in argv:
    #         av = list(argv)
    #         argv.clear()
    #         [argv.append('--helpfull' if a in ['-hf', '--hf'] else a) for a in av]

    # name of app (-> logging, var, log, ...folders):
    # n = env.get('DA_CLS') or command_name()
    n = command_name()
    if not flags_parser:
        #     # setup_colorized_help(main, argv)
        flags_parser = abslapp.parse_flags_with_usage
    define_action_flags_in_cli()
    # flags_parser = wrap_flag_parser_with_action_detector(flags_parser)

    try:
        abslapp.run(
            partial(
                run_phase_2,
                name=n,
                main=main,
                kw_log=kw_log,
                flags_validator=flags_validator,
                wrapper=wrapper,
            ),
            argv=argv,
            flags_parser=flags_parser,
        )
    except Exception as ex:
        sys.exit(1)


def define_action_flags_in_cli():
    args = sys.argv
    afs = tools.action_flags
    p = 0
    have = set()
    for a in args[1:]:
        p += 1
        if a == '--':
            return
        if not a in afs:
            continue
        if p > 1:
            pa = args[p - 1]
            pa = pa[2:] if pa.startswith('--') else pa[1:] if pa.startswith('-') else pa
            pf = FLG.__flags.get(pa)
            if pf and pf.flag_type() != 'bool':
                continue
        f = afs.get(a)
        key = f['key']
        if key in have:
            continue
        have.add(key)
        args[p] = '--' + f['key']
        tools.define_flags(f['flg_cls'], sub=key, parent_autoshort=f['autoshort'])
        action[0] = key


action = [0]
# def on_flag_parse_err_have_action_flag(key, af, parser):
#     p = sys.argv.index(key)
#     key = af['key']  # short to long
#     action[0] = key
#     args = list(sys.argv)
#     args[p] = '--' + key
#     tools.define_flags(af['flg_cls'], sub=key, parent_autoshort=af['autoshort'])
#     for arg in args[p + 1 :]:
#         p += 1
#         if arg.startswith('--'):
#             if arg == '--':
#                 break
#             args[p] = arg.replace('--', '--%s_' % key)
#     return parser(args)


#     for k in sys.argv[1:]:
#         if k == '--':
#             break
#         af = afg(k)
#         if k[0] != '-' and af:
#             return on_flag_parse_err_have_action_flag(k, af, parser=parser)
#     # No AF. Let crash - or leave alone, e.g. a app -a1 -- foo -a1 construct
#     sys.stderr.write(err)
#     return sys.exit(1)


class DieNow(Exception):
    # required since sys.exit will be catched - halting the app, not stopping it
    ''


class dev_app_exc_handler(abslapp.ExceptionHandler):
    wants = lambda self, exc: True

    def handle(self, exc):
        if type(exc) == DieNow:
            # app.die was called, we logged already:
            return  # -> silent exit, we logged already
        # Trying to return after json logging as below
        # seems to halt the app with geven sometimes:
        #    48 Sep 10 18:34:55 qtwesacs01 Expert[29848]:   File "src/gevent/greenlet.py", line 716, in gevent._greenlet.Greenlet.run
        #        (...)
        #    Sep 10 18:34:55 qtwesacs01 Expert[29848]:   File "/opt/axwifi_prod/envs/wi
        #    65 Sep 10 18:34:55 qtwesacs01 Expert[29848]:     item: T1 = heapq.heappop(sel
        #    66 Sep 10 18:34:55 qtwesacs01 Expert[29848]: IndexError: index out of range
        #    67 Sep 10 18:34:55 qtwesacs01 Expert[29848]: 2019-09-10T16:34:55Z <Greenlet "
        # so better play save and not invoke app.log when a greenlet crashes:
        raise exc
        # sentry here
        if app.is_initted:
            app.log.error('Exception. Dying now', exc=exc)
        else:
            raise exc


abslapp.install_exception_handler(dev_app_exc_handler())


class Reloaded(Exception):
    pass


def reload_handler(signum, frame):
    raise Reloaded('signal')


from io import StringIO


# def wrap_flag_parser_with_action_detector(flags_parser):
#     def parser(args, p=flags_parser):
#         try:
#             breakpoint()  # FIXME BREAKPOINT
#             e = sys.stderr
#             sys.stderr = StringIO()
#             r = p(args)
#             sys.stderr = e
#             return r
#         except SystemExit as ex:
#             sys.stderr, e = e, sys.stderr.getvalue()
#             return on_flag_parse_err_try_action_flags(args, err=e, parser=p)

#     return parser


# def on_flag_parse_err_try_action_flags(args, err, parser):
#     afg = tools.action_flags.get

#     for k in sys.argv[1:]:
#         if k == '--':
#             break
#         af = afg(k)
#         if k[0] != '-' and af:
#             return on_flag_parse_err_have_action_flag(k, af, parser=parser)
#     # No AF. Let crash - or leave alone, e.g. a app -a1 -- foo -a1 construct
#     sys.stderr.write(err)
#     return sys.exit(1)


# def on_flag_parse_err_have_action_flag(key, af, parser):
#     p = sys.argv.index(key)
#     key = af['key']  # short to long
#     action[0] = key
#     args = list(sys.argv)
#     args[p] = '--' + key
#     tools.define_flags(af['flg_cls'], sub=key, parent_autoshort=af['autoshort'])
#     for arg in args[p + 1 :]:
#         p += 1
#         if arg.startswith('--'):
#             if arg == '--':
#                 break
#             args[p] = arg.replace('--', '--%s_' % key)
#     return parser(args)


# action = ['']


def run_phase_2(args, name, main, kw_log, flags_validator, wrapper):

    tools.set_flag_vals_from_env()  # 0.0001sec

    if FLG.help_call:
        # -h shows level 1:
        call_doc(main, level=2, render=True)
        return

    if FLG.help_call_detailed:
        call_doc(main, level=3, render=True)
        return

    kw_log = {} if kw_log == None else kw_log
    if flags_validator:
        try:
            err = flags_validator()
        except Exception as ex:
            err = str(ex)
        if err:
            print('Flags validation error: %s' % err, file=sys.stderr)
            sys.exit(1)
    sl.setup_logging(**kw_log)
    log = sl.get_logger(name)
    set_app(name, log)
    watcher_pid = None
    if FLG.dirwatch:
        # test if tools present:
        pass

        d, match, rec = (FLG.dirwatch + '::').split(':')[:3]
        d = os.path.abspath(d)
        if not os.path.isdir(d):
            app.die('No directory:', d=d, nfo='Use <dir>:<match>:[r]')
        w = os.path.dirname(os.path.abspath(__file__)) + '/utils/watch_dog.py'
        cmd = [w, ':'.join([d, str(os.getpid()), match, rec])]
        # print(' '.join(cmd))
        watcher_pid = subprocess.Popen(cmd).pid

    # An Action class - use it:
    post = None
    if isinstance(main, type):
        action_cls = main
        if not action[0]:
            for af in tools.action_flags.values():
                if af['flg_cls'].d:
                    action[0] = af['key']
                    app.debug('Running default action', action=af['key'])
                    break
        main = getattr(action_cls, action[0], None)
        if not main:
            app.die('Require action')
        pre = getattr(action_cls, '_pre', 0)
        if pre:
            # app.debug('Prepare hook')
            pre()
            # app.debug(action[0])
        post = getattr(action_cls, '_post', 0)

    res = None
    while True:
        try:
            # so that everybody knows what is running. informational
            app._app_func = main
            # main = lambda: run_app(Action, flags=Flags, wrapper=cleanup)
            res = wrapper(main) if wrapper else main()
            if FLG.dirwatch:
                app.info('Keep running, dirwatch is set')
                signal.signal(1, reload_handler)
                while 1:
                    time.sleep(10)
        except Reloaded as ex:
            continue
        except SystemExit as ex:
            return ex.args[0]
        except KeyboardInterrupt:
            if watcher_pid:
                os.kill(watcher_pid, 9)
            print('Keyboard Interrupt - Bye.')
            sys.exit(1)
            return
        finally:
            if post:
                # app.debug(
                #     'Post app hook', running=[p.__name__ for p in tools.to_list(post)]
                # )

                [p() for p in post] if isinstance(post, list) else post()
        break
    if not isinstance(res, (list, dict, tuple)):
        if not res is None:
            print(res)
        return res
    # exit phase. postprocessing, pretty to stdout, plain to | jq .:
    if FLG.flat:
        res = tools.flatten(res, sep='.')
    if not sys.stdout.isatty():
        jres = json.dumps(res, default=str)
        print(jres)
    else:
        # return res
        print(coljhighlight(res))
    # abseil would print it again:
    # return res


class Die(Exception):
    log = None

    def __init__(self, msg, log=None, **kw):
        log = log or self.log
        if log:
            log.error(msg, **kw)
        else:
            print(
                msg, json.dumps(kw, sort_keys=True, default=str, indent=4)[1:-1],
            )
        raise DieNow()


def app_func(inner=False):
    if not inner:
        return app._app_func
    f = app._app_func
    while hasattr(f, 'func'):
        f = f.func
    return f


def do(func, *a, _step=[0], titelize='', log_level=None, ll=None, fl=None, **kw):
    """When fl (full log level) is set to e.g. 10 we log only the message at higher levels"""

    if ll is not None:
        log_level = {10: 'debug', 20: 'info', 30: 'warn'}.get(ll, 'info')
    fn = func.__qualname__  # .rsplit('.', 1)[-1]
    if titelize:
        _step[0] += 1
        fn = 'STEP %s: %s' % (_step[0], fn)
    log = app.debug if func == system else app.info
    if log_level:
        log = getattr(app, log_level)

    if func == system:
        cmd, args = (a[0] + ' ').split(' ', 1)
        kwl = {} if not args else {'args': args}
        log('sh: ' + cmd, **kwl)
    else:
        if fl is not None and fl < app.log_level:
            log(fn)
        else:
            if a:
                ar = a[0] if len(a) == 1 else a
                log(fn, args=ar, **kw)
            else:
                log(fn, **kw)
    return func(*a, **kw)


def system(cmd, no_fail=False):
    # print('\x1b[38;5;240m', end='')
    d = ' 1>&2'
    # cat -> colors off
    fnf = '/tmp/failed_system_cmd'
    rcmd = 'echo -ne "\x1b[38;5;240m"%s; %s%s || touch "%s"; echo -ne "\x1b[0m"%s'
    rcmd = rcmd % (d, cmd, d, fnf, d)
    os.system(rcmd)
    err = False
    if os.path.exists(fnf):
        os.unlink(fnf)
        err = True
    # print('\x1b[0m', end='')
    if err:
        f = app.warn if no_fail else app.die
        f('Failed', cmd=cmd)
        return 1
    else:
        return 0


# is set into app as .die:
# allows raise app.die(msg, **kw) with correct error logging:
# we want to raise for --pdb_post_mortem
app_die = lambda app: type('Die', (Die,), {'log': app.log})
