#!/usr/bin/env python
import sys, os, stat, glob, datetime, re, optparse, traceback, tarfile
from setuptools import setup, Extension
from tools import Configuration, opj, copy_if_newer


cfg    = Configuration()
PYTHON = sys.executable
WAF    = 'bin/waf-2.0.23'


#-------------------------------------------------------------------------------

def make_parser():
    usage_txt = """\
./zombie_build.py [command(s)] [options]

Commands:
  build    build everything needed to install"""
    OPTS = [('gtk2',  (False, 'On Linux build for gtk2 (default gtk3)')),
            ('cairo', (False, 'Allow Cairo use with wxGraphicsContext '
                              '(Windows only)'))]
    parser = optparse.OptionParser(usage_txt)
    for opt, info in OPTS:
        default, txt = info
        action = 'store'
        if type(default) == bool:
            action = 'store_true'
        if isinstance(opt, str):
            opts = ('--' + opt, )
            dest = opt
        else:
            opts = ('-' + opt[0], '--' + opt[1])
            dest = opt[1]
        parser.add_option(*opts, default = default, action = action,
                          dest = dest, help = txt)
    return parser

def main(args):
    args = ['--help'] if not args else args
    parser = make_parser()
    options, commands = parser.parse_args(args)
    cfg.finish_setup()
    while commands:
        os.chdir(cfg.ROOT_DIR)
        cmd = commands.pop(0)
        if 'cmd_' + cmd in globals():
            function = globals()['cmd_' + cmd]
            function(options)
        else:
            print('*** Unknown command: ' + cmd)
            parser.print_help()
            sys.exit()
    print('Done!')


#-------------------------------------------------------------------------------
# Helper functions
#-------------------------------------------------------------------------------

class CommandTimer(object):
    def __init__(self, name):
        self.name = name
        self.start_time = datetime.datetime.now()
        print('Running command: %s' % self.name)

    def __del__(self):
        delta = datetime.datetime.now() - self.start_time
        time = ''
        if delta.seconds / 60 > 0:
            time = '%dm' % (delta.seconds / 60)
        time += '%d.%ds' % (delta.seconds % 60, delta.microseconds / 1000)
        print('Finished command: %s (%s)' % (self.name, time))


class PushDir(object):
    def __init__(self, new_dir):
        self.cwd = os.getcwd()
        os.chdir(new_dir)

    def __del__(self):
        os.chdir(self.cwd)


def runcmd(cmd):
    print(cmd)
    exit_status = os.system(cmd)
    if exit_status:
        print("Command '%s' failed with exit code %d." % (cmd, exit_status))
        sys.exit(exit_status)

def msvc_build_wx_ext(wx_root_dir, opts):
    build_dir = opj(wx_root_dir, 'build', 'msw')
    print('creating wx/msw/setup.h from setup0.h')
    flags = {'wxUSE_UNICODE'              : '1',
             'wxDIALOG_UNIT_COMPATIBILITY': '0',
             'wxUSE_DEBUGREPORT'          : '0',
             'wxUSE_DIALUP_MANAGER'       : '0',
             'wxUSE_GRAPHICS_CONTEXT'     : '1',
             'wxUSE_DISPLAY'              : '1',
             'wxUSE_GLCANVAS'             : '1',
             'wxUSE_POSTSCRIPT'           : '1',
             'wxUSE_AFM_FOR_POSTSCRIPT'   : '0',
             'wxUSE_DATEPICKCTRL_GENERIC' : '1',
             'wxUSE_IFF'                  : '1',
             'wxUSE_ACCESSIBILITY'        : '1',
             'wxUSE_UIACTIONSIMULATOR'    : '1'}
    if 'cairo' in opts:
        flags['wxUSE_CAIRO'] = '1'
    msw_include_dir = opj(wx_root_dir, 'include', 'wx', 'msw')
    setup_0_file = opj(msw_include_dir, 'setup0.h')
    setup_text = open(setup_0_file, 'rb').read().decode()
    for key, value in flags.items():
        setup_text = re.subn(key + '\s+?\d', '%s %s' % (key, value),
                             setup_text)[0]
    open(opj(msw_include_dir, 'setup.h'), 'wb').write(setup_text.encode())
    options = ['-f makefile.vc', 'UNICODE=1', 'OFFICIAL_BUILD=1', 'SHARED=1',
               'MONOLITHIC=0', 'USE_OPENGL=1', 'USE_GDIPLUS=1', 'BUILD=release']
    options.append('COMPILER_VERSION=%s' % cfg.vcruntime_version)
    key = 'cairo'
    if key in opts:
        options.append('CPPFLAGS=/I%s' % opj(opts[key], 'include', key))
    print('Configure options: ' + repr(options))
    command = ' '.join(['nmake.exe'] + options)
    pwd = PushDir(build_dir)
    runcmd(command)
    dll_dir = opj(wx_root_dir, 'lib', cfg.VCDLL)
    arch = 'x64' if cfg.PYTHON_ARCH == '64bit' else 'x86'
    dlls = glob.glob(opj(dll_dir, 'wx*.dll'))
    if key in opts:
        dlls += glob.glob(opj(opts[key], arch, 'bin', '*.dll'))
    return dlls

def gcc_build_wx_ext(wx_root_dir, build_dir, opts):
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)
    pwd = PushDir(build_dir)
    options = ['--enable-unicode', '--enable-sound', '--enable-graphics_ctx',
               '--enable-display', '--enable-geometry', '--enable-debug_flag',
               '--enable-optimise', '--disable-debugreport',
               '--enable-uiactionsim', '--enable-autoidman', '--with-sdl']
    key = 'gtk'
    if key in opts:
        options.append('--with-gtk=%s' % opts[key])
    print('Configure options: ' + repr(options))
    configure_cmd = opj(wx_root_dir, 'configure')
    runcmd(' '.join([configure_cmd] + options))
    runcmd('make -j %d' % os.sysconf('SC_NPROCESSORS_ONLN'))
    wxlibdir = opj(build_dir, 'lib')
    dlls = glob.glob(wxlibdir + '/libwx_*.so')
    dlls += glob.glob(wxlibdir + '/libwx_*.so.[0-9]*')
    return dlls

#-------------------------------------------------------------------------------
# Command functions
#-------------------------------------------------------------------------------

def cmd_build(options):
    lib_nanosvg = opj(cfg.PKGDIR, 'svg', '_nanosvg' + cfg.EXT_SUFFIX)
    if os.path.exists('build') and os.path.exists(lib_nanosvg):
        print('Build present!')
    else:
        cmd_timer = CommandTimer('build')
        cmd_update_files(options)
        cmd_build_wx_ext(options)
        cmd_build_py_ext(options)
        cmd_build_siplib(options)
        cmd_build_others(options)
    print('\n------------ BUILD FINISHED ------------')
    print('To use wxPython from the build folder (without installing):')
    print(' - Set your PYTHONPATH variable to %s.\n' % cfg.ROOT_DIR)

def cmd_update_files(dummy):
    cmd_timer = CommandTimer('update_files')
    if cfg.IS_NT:
        copy_if_newer(cfg.c_plusplus_std_lib, cfg.PKGDIR, verbose = True)
    else:
        for file in ['zombie_build.py', opj(cfg.WXDIR, 'configure')]:
            st = os.stat(file)
            os.chmod(file, st.st_mode | stat.S_IEXEC)

def cmd_build_wx_ext(options):
    cmd_timer = CommandTimer('build_wx_ext')
    build_options = {}
    if cfg.IS_NT and options.cairo:
        cairo_root = opj(cfg.ROOT_DIR, 'packaging', 'msw-cairo')
        build_options['cairo'] = cairo_root
    elif not cfg.IS_NT:
        build_options['gtk'] = '2' if options.gtk2 else '3'
    print('wxWidgets build options: ' + repr(build_options))
    wx_root_dir = opj(cfg.ROOT_DIR, cfg.WXDIR)
    try:
        if cfg.IS_NT:
            dlls = msvc_build_wx_ext(wx_root_dir, build_options)
        else:
            dlls = gcc_build_wx_ext(wx_root_dir, cfg.BUILD_DIR, build_options)
    except Exception:
        print('ERROR: failed building wxWidgets')
        traceback.print_exc()
        sys.exit(1)
    for dll in dlls:
        copy_if_newer(dll, cfg.PKGDIR, verbose = True)

def cmd_build_py_ext(dummy):
    cmd_timer = CommandTimer('build_py_ext')
    build_option = '--out=%s' % opj('build', 'waf')
    cmd = '"%s" %s %s configure build' % (PYTHON, WAF, build_option)
    runcmd(cmd)

def cmd_build_siplib(dummy):
    cmd_timer = CommandTimer('build_siplib')
    pwd = PushDir(cfg.SIPINC)
    tar_file = glob.glob('*.tar.gz')[0]
    tarfile.open(tar_file).extractall()
    os.chdir(tar_file[:tar_file.rindex('.tar.gz')])
    cmd = '"%s" setup.py build_ext -b %s' % (PYTHON, cfg.ROOT_DIR)
    runcmd(cmd)

def cmd_build_others(dummy):
    cmd_timer = CommandTimer('build_others')
    module = Extension(name = 'wx.svg._nanosvg',
                       sources = ['wx/svg/_nanosvg.c'],
                       include_dirs = ['ext/nanosvg/src'],
                       define_macros = [('NANOSVG_IMPLEMENTATION', '1'),
                                        ('NANOSVGRAST_IMPLEMENTATION', '1'),
                                        ('NANOSVG_ALL_COLOR_KEYWORDS', '1')])
    setup(script_name = 'dummy',
          script_args = ['build_ext', '--inplace'],
          ext_modules = [module],
          options     = {'build': {'build_base': 'build/wxsvg'}})

#-------------------------------------------------------------------------------

if __name__ == '__main__':
    main(sys.argv[1:])
