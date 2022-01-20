from distutils.core import setup, Extension
from Cython.Build import cythonize
from numpy import get_include


# python cython_setup.py build_ext --inplace
# import os
# from pathlib import Path
# f_path = Path(os.path.abspath(__file__))
# path = str(f_path.parent.absolute()) + "/SPMUtil/cython_files/cython_pyx_code.pyx"


ext1 = Extension("cython_code", sources=["cython_pyx_code.pyx"], include_dirs=['.', get_include()])
sourcefiles = ['cython_template_matching_code.pyx', 'template_matching.c']
ext2 = Extension("cython_tm_code", sourcefiles, include_dirs=[get_include()])
setup(name="ext_cy_module", ext_modules=cythonize([ext1, ext2]))


