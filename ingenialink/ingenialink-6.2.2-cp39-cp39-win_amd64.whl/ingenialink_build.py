import sys
import re
import os
from os.path import join, exists
from distutils.spawn import find_executable
from subprocess import check_call, call, Popen, PIPE

from cffi import FFI


_SRC_DIR = '_deps'
_BUILD_DIR = '_build'
_INSTALL_DIR = '_install'

_INC_DIR = join(_INSTALL_DIR, 'include')
_LIB_DIR = join(_INSTALL_DIR, 'lib')

if 'INGENIALINK_DIR' in os.environ:
    _IL_URL = None
    _IL_SRC = os.environ['INGENIALINK_DIR']
else:
    _IL_URL = 'https://github.com/ingeniamc/ingenialink'
    _IL_VER = '6.2.2'
    _IL_SRC = join(_SRC_DIR, 'ingenialink')

_IL_BUILD = join(_BUILD_DIR, 'ingenialink')

if 'SERCOMM_DIR' in os.environ:
    _SER_SRC = os.environ['SERCOMM_DIR']
else:
    _SER_SRC = join(_IL_SRC, 'external', 'sercomm')

_SER_BUILD = join(_BUILD_DIR, 'sercomm')

if 'XML2_DIR' in os.environ:
    _XML2_SRC = os.environ['XML2_DIR']
else:
    _XML2_SRC = join(_IL_SRC, 'external', 'libxml2')

_XML2_BUILD = join(_BUILD_DIR, 'libxml2')

if 'SOEM_DIR' in os.environ:
    _SOEM_SRC = os.environ['SOEM_DIR']
else:
    _SOEM_SRC = join(_IL_SRC, 'external', 'soem')

_SOEM_BUILD = join(_BUILD_DIR, 'soem')

# SOEM dirname
# _SOEM_URL = 'https://github.com/OpenEtherCATsociety/SOEM'
# _SOEM_VER = 'master'
# _SOEM_SRC = join(_IL_SRC, 'external', 'SOEM')
# _SOEM_BUILD = join(_SOEM_SRC, _BUILD_DIR)

if sys.platform == 'win32':
    if sys.version_info >= (3, 5):
        _CMAKE_GENERATOR = 'Visual Studio 14 2015'
    else:
        raise ImportError('Unsupported Python version')

    if sys.maxsize > 2**32:
        _CMAKE_GENERATOR += ' Win64'
else:
    _CMAKE_GENERATOR = 'Unix Makefiles'


def _build_deps():
    """Obtains and build dependencies (sercomm and ingenialink)."""

    # Check for Git & CMake
    git = find_executable('git')
    if not git:
        raise FileNotFoundError('Git is not installed or in PATH')

    cmake = find_executable('cmake')
    if not cmake:
        raise FileNotFoundError('CMake is not installed or in PATH')

    # Clone
    if not exists(_IL_SRC) and _IL_URL:
        check_call([git, 'clone', '--recursive', '-b', _IL_VER, _IL_URL,
                    _IL_SRC])

        # check_call([git, 'clone', '-b', _SOEM_VER, _SOEM_URL, _SOEM_SRC])

    # Deps: libsercomm
    check_call([cmake, '-H' + _SER_SRC, '-B' + _SER_BUILD,
                '-G', _CMAKE_GENERATOR,
                '-DCMAKE_BUILD_TYPE=Release',
                '-DCMAKE_INSTALL_PREFIX=' + _INSTALL_DIR,
                '-DBUILD_SHARED_LIBS=OFF', '-DWITH_PIC=ON'])
    check_call([cmake, '--build', _SER_BUILD, '--config', 'Release',
                '--target', 'install'])

    # Deps: libxml2 (only on Windows)
    if sys.platform == 'win32':
        check_call([cmake, '-H' + _XML2_SRC, '-B' + _XML2_BUILD,
                    '-G', _CMAKE_GENERATOR,
                    '-DCMAKE_BUILD_TYPE=Release',
                    '-DCMAKE_INSTALL_PREFIX=' + _INSTALL_DIR,
                    '-DBUILD_SHARED_LIBS=OFF', '-DWITH_PIC=ON'])
        check_call([cmake, '--build', _XML2_BUILD, '--config', 'Release',
                    '--target', 'install'])

    if sys.platform == 'win32':
        check_call([cmake, '-H' + _SOEM_SRC, '-B' + _SOEM_BUILD,
                    '-G', _CMAKE_GENERATOR,
                    '-DCMAKE_BUILD_TYPE=Release',
                    '-DCMAKE_INSTALL_PREFIX=' + _INSTALL_DIR,
                    '-DBUILD_SHARED_LIBS=OFF', '-DWITH_PIC=ON'])
        check_call([cmake, '--build', _SOEM_BUILD, '--config', 'Release',
                    '--target', 'install'])

    print("[INFO] Ingenialink build")
    check_call([cmake, '-H' + _IL_SRC, '-B' + _IL_BUILD,
                '-G', _CMAKE_GENERATOR,
                '-DCMAKE_BUILD_TYPE=Release',
                '-DCMAKE_INSTALL_PREFIX=' + _INSTALL_DIR,
                '-DBUILD_SHARED_LIBS=OFF',
                '-DWITH_PROT_MCB=ON',
                '-DWITH_PROT_ECAT=ON',
                '-DWITH_PROT_VIRTUAL=ON',
                '-DWITH_PIC=ON'])
    check_call([cmake, '--build', _IL_BUILD, '--config', 'Release',
                '--target', 'install'])


def _gen_cffi_header():
    """Generates cffi header.

    All ingenialink headers are joined into a single one, and, all
    cffi non-compatibe portions removed.

    Returns:
        str: cffi header.

    """
    remove = ['IL_EXPORT',
              'IL_BEGIN_DECL',
              'IL_END_DECL',
              '#ifdef.*',
              '#ifndef.*',
              '#endif.*',
              '#define PUBLIC.*',
              '#include.*',
              '.+foreach.+\n.*']

    headers = [join(_INC_DIR, 'ingenialink', 'const.h'),
               join(_INC_DIR, 'ingenialink', 'err.h'),
               join(_INC_DIR, 'ingenialink', 'dict_labels.h'),
               join(_INC_DIR, 'ingenialink', 'registers.h'),
               join(_INC_DIR, 'ingenialink', 'dict.h'),
               join(_INC_DIR, 'ingenialink', 'net.h'),
               join(_INC_DIR, 'ingenialink', 'servo.h'),
               join(_INC_DIR, 'ingenialink', 'poller.h'),
               join(_INC_DIR, 'ingenialink', 'monitor.h'),
               join(_INC_DIR, 'ingenialink', 'version.h')]

    h_stripped = ''

    for header in headers:
        with open(header) as h:
            h_stripped += re.sub('|'.join(remove), '', h.read())

    return h_stripped


def _get_libs():
    """Obtain the list of libraries to link against based on platform.

    Returns:
        list: List of libraries.

    """
    libs = ['ingenialink', 'sercomm', 'xml2', 'soem']

    if sys.platform.startswith('linux'):
        libs.extend(['udev', 'rt', 'pthread'])
    elif sys.platform == 'darwin':
        libs.extend(['pthread'])
    elif sys.platform == 'win32':
        libs.extend(['user32', 'setupapi', 'advapi32', 'wpcap', 'ws2_32',
                     'winmm', 'gdi32', 'dxguid'])

    return libs


def _get_link_args():
    """Obtain the list of extra linker arguments based on platform.

    Returns:
        list: List of extra linker arguments.

    """
    if sys.platform == 'darwin':
        return ['-framework', 'IOKit', '-framework', 'Foundation']

    return []


# build dependencies first
_build_deps()

# cffi builder
ffibuilder = FFI()

ffibuilder.cdef(
    _gen_cffi_header() + '''
    /* callbacks */
    extern "Python" void _on_found_cb(void *ctx, uint8_t node_id);
    extern "Python" void _on_evt_cb(void *ctx, il_net_dev_evt_t on_evt,
                                    const char *port);
    extern "Python" void _on_state_change_cb(void *ctx,
                                             il_servo_state_t state,
                                             int flags, uint8_t subnode);
    extern "Python" void _on_emcy_cb(void *ctx, uint32_t code);
''')

ffibuilder.set_source('ingenialink._ingenialink',
                      r'#include <ingenialink/ingenialink.h>',
                      include_dirs=[_INC_DIR],
                      library_dirs=[_LIB_DIR],
                      libraries=_get_libs(),
                      extra_link_args=_get_link_args())


if __name__ == '__main__':
    ffibuilder.compile(verbose=True)
