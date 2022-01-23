from distutils import cmd
import glob
import os

from setuptools import setup, Command, Extension

import numpy as np

relief_ext = Extension('reliefcpp._c_relief',
                       sources=glob.glob(os.path.join(
                           'src', 'reliefcpp', '*.cpp')),
                       include_dirs=['include', np.get_include()],
                       extra_compile_args=['-std=c++17', '-O2'])


class CleanCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


cmdclass = {'clean': CleanCommand}

options = {
    'name': 'reliefcpp',
    'description': 'reliefcpp is a package for running the relief feature ranking algorithm.',
    'license': 'MIT',
    'version': '0.3',
    'author': 'Euxhen Hasanaj',
    'author_email': 'ehasanaj@cs.cmu.edu',
    'url': 'https://github.com/ferrocactus/reliefcpp',
    'provides': ['reliefcpp'],
    'package_dir': {'reliefcpp': os.path.join('src', 'reliefcpp')},
    'packages': ['reliefcpp'],
    'cmdclass': cmdclass,
    'ext_modules': [relief_ext],
    'platforms': 'ALL',
    'keywords': ['relief', 'reliefcpp'],
    'install_requires': ['numpy'],
    'setup_requires': ['numpy'],
    'python_requires': ">=3.7"
}

setup(**options)
