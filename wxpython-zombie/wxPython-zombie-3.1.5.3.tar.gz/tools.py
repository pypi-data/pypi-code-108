import _imp, sys, os, re, platform, shutil, traceback
import pkg_info
from stat import ST_MTIME
from setuptools import msvc


def opj(*args):
    path = os.path.join(*args)
    return os.path.normpath(path)
#-------------------------------------------------------------------------------

class Configuration(object):

    IS_NT       = os.name == 'nt'
    PYTHON_ARCH = platform.architecture()[0]
    EXT_SUFFIX  = _imp.extension_suffixes()[0]
    ROOT_DIR    = os.path.dirname(__file__)
    SIPINC      = 'sip/siplib'
    SIPOUT      = 'sip/cpp'
    WXDIR       = 'ext/wxWidgets'
    PKGDIR      = pkg_info.TOP_LEVEL

    def __init__(self):
        self.get_wx_version()

    def finish_setup(self):
        if self.IS_NT:
            (self.c_plusplus_std_lib,
             self.vcruntime_version) = activate_vc_env(self.PYTHON_ARCH)
            if self.PYTHON_ARCH == '64bit':
                self.VCDLL = 'vc%s_x64_dll' % self.vcruntime_version
            else:
                self.VCDLL = 'vc%s_dll' % self.vcruntime_version
        else:
            os.environ['LD_RUN_PATH'] = '$ORIGIN'
            self.BUILD_DIR = opj(self.ROOT_DIR, 'build', 'wxbld')
            self.WX_CONFIG = opj(self.BUILD_DIR, 'wx-config')


    # --------------------------------------------------------------------------
    # Helper functions
    # --------------------------------------------------------------------------

    def get_wx_version(self):
        wx_version_file = opj(self.WXDIR, 'include', 'wx', 'version.h')
        try:
            txt = open(wx_version_file, 'rb').read().decode()
            s = re.search(r'^#define\s+wxMAJOR_VERSION\s+(\d+)\n', txt, re.M)
            wxVER_MAJOR = int(s.group(1))
            s = re.search(r'^#define\s+wxMINOR_VERSION\s+(\d+)\n', txt, re.M)
            wxVER_MINOR = int(s.group(1))
            self.WXDLLVER = '%d%du' % (wxVER_MAJOR, wxVER_MINOR)
        except Exception:
            print('ERROR: wxWidgets version not found.')
            traceback.print_exc()
            sys.exit(1)

    def get_wx_config_value(self, flag):
        cmd = '%s %s' % (self.WX_CONFIG, flag)
        value = os.popen(cmd).read()[:-1]
        return value

    def make_lib_name(self, name, is_msw_base = False):
        basename = 'base' if is_msw_base else 'msw'
        if name:
            libname = 'wx%s%s_%s' % (basename, self.WXDLLVER, name)
        else:
            libname = 'wx%s%s' % (basename, self.WXDLLVER)
        return [libname]

    def find_wx_setup_h(self):
        output = self.get_wx_config_value('--cflags')
        wx_setup_h = output.split()[0]
        assert wx_setup_h.startswith('-I')
        return wx_setup_h[2:]

    def check_setup(self, wx_setup_h, flag):
        name = 'setup.h'
        try:
            setup = [opj(root, name)
                     for root, dirs, files in os.walk(wx_setup_h)
                     if name in files][0]
            txt = open(setup, 'rb').read().decode()
            s = re.search(r'^#define\s+%s\s+(\d+)\n' % flag, txt, re.M)
            check = bool(int(s.group(1)))
        except:
            print('WARNING: Unable to find setup.h in {}, assuming {} is not '
                  'available.'.format(wx_setup_h, flag))
            check = False
        return check


#-------------------------------------------------------------------------------
# other helpers
#-------------------------------------------------------------------------------

def _newer(src, dst):
    newer = not (os.path.exists(src) and os.path.exists(dst))
    if not newer:
        mtime1 = os.stat(src)[ST_MTIME]
        mtime2 = os.stat(dst)[ST_MTIME]
        newer = mtime1 > mtime2
    return newer

def _copy_file(src, dst, verbose = False):
    if verbose:
        print('copying %s --> %s' % (src, dst))
    if os.path.islink(src):
        if os.path.exists(dst):
            os.unlink(dst)
        linkto = os.readlink(src)
        os.symlink(linkto, dst)
    else:
        shutil.copy2(src, dst)

def copy_if_newer(src, dst, verbose = False):
    if os.path.isdir(dst):
        dst = opj(dst, os.path.basename(src))
    if _newer(src, dst):
        _copy_file(src, dst, verbose)

def activate_vc_env(arch):
    plat_spec = ['x86', 'amd64'][arch == '64bit']
    env = msvc.msvc14_get_vc_env(plat_spec)
    os.environ['CPU'] = plat_spec.upper()
    os.environ['PATH'] = env['path']
    os.environ['INCLUDE'] = env['include']
    os.environ['LIB'] = env['lib']
    os.environ['LIBPATH'] = env['libpath']
    crt_dir, vcruntime = os.path.split(env['py_vcruntime_redist'])
    s = re.search(r'vcruntime(\d+)\.dll', vcruntime)
    vcruntime_version = s.group(1)
    c_plusplus_std_lib = opj(crt_dir, 'msvcp%s.dll' % vcruntime_version)
    return c_plusplus_std_lib, vcruntime_version
