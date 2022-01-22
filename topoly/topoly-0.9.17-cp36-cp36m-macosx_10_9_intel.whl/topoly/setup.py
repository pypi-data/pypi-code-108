#!/usr/bin/python3

from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

import os
import platform

dir_path = os.path.dirname(os.path.realpath(__file__))

def gcc_version():
    return int(os.popen('gcc -dumpversion').read().strip().split(".")[0])

if platform.system()=='Linux':
    rdirs = ['$ORIGIN/../../../../lib', '$ORIGIN/../../../lib', '$ORIGIN/../../lib', '/usr/local/lib', '$ORIGIN']
    linkerdirs = ['-std=c++11'] if gcc_version() > 5 else []
elif platform.system()=='Darwin':
    rdirs = ['@loader_path/../../../../lib', '@loader_path/../../../lib', '@loader_path/../../lib', '/usr/local/lib', '@loader_path', '@loader_path/../build']
    linkerdirs = ['-std=c++11', '-Wl,-rpath,'+'@loader_path/', '-Wl,-rpath,'+'@loader_path/../../../../lib', '-Wl,-rpath,'+'@loader_path/../../../lib', '-Wl,-rpath,'+'@loader_path/../../lib', '-Wl,-rpath,'+'/usr/local/lib', '-Wl,-rpath,'+'@loader_path/../build']
else:
    print('Unsupported platform!')

setup(
    ext_modules=cythonize([
        Extension("topoly.topoly_knot", ["topoly_knot.pyx"],
                  include_dirs=["preprocess", "knot_net"],
                  libraries=["knotfinder"],
                  extra_link_args=linkerdirs,
                  runtime_library_dirs=rdirs),
        Extension("topoly.topoly_preprocess", ["topoly_preprocess.pyx"],
                  include_dirs=["preprocess"],
                  libraries=["preprocess"],
                  extra_link_args=linkerdirs,
                  runtime_library_dirs=rdirs),
        Extension("topoly.topoly_lmpoly", ["topoly_lmpoly.pyx"],
                  include_dirs=["homfly/lmpoly/Wandy"],
                  libraries=["lmpoly"],
                  extra_link_args=linkerdirs,
                  runtime_library_dirs=linkerdirs),
        Extension("topoly.topoly_homfly", ["topoly_homfly.pyx"],
                  include_dirs=["homfly/homflylink","/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/include/c++/v1"],
                  libraries=["homfly"],
                  extra_compile_args=["-std=c++11"],
                  extra_link_args=linkerdirs,
                  runtime_library_dirs=rdirs
                  ),
        Extension("topoly.topoly_surfaces", ["topoly_surfaces.pyx"],
                  include_dirs=["preprocess", "surfaces"],
                  libraries=["surfaces"],
                  extra_link_args=linkerdirs,
                  runtime_library_dirs=rdirs),
        Extension("topoly.topoly_gln", ["topoly_gln.pyx"],
                  include_dirs=["preprocess", "glns"],
                  libraries=["glnfinder"],
                  extra_link_args=linkerdirs,
                  runtime_library_dirs=rdirs),
    ], compiler_directives={'language_level': "3"})
)