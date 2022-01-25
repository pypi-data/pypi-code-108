import os
import sys

version = {}
with open('hw_wwj/__init__.py') as hw:
    exec(hw.read(), version)
__version__ = version['__version__']

try:
    import setuptools
except ImportError:
    pass
from numpy.distutils.core import setup, Extension
from numpy.distutils.system_info import get_info

# Fortran extension
fortran_t = Extension(name = 'hw_wwj.hw_fortran_t', 
						sources = ['hw_wwj/hwfortran.f90'])

description = '测试fortran编写的程序在python中调用'

this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name = 'hw_wwj',     # 包名
      packages=['hw_wwj'],
      ext_modules=[fortran_t],
      version=__version__,
      description=description,
      #long_description = '', # 这里的内容会显示在pypi包首页上
      long_description=long_description,    #包的详细介绍，一般在README.md文件内
      long_description_content_type="text/markdown",
      author = 'banshiliuli',
      author_email = '446601097@qq.com',
      url = 'https://github.com/pypa/sampleproject',
      install_requires=['numpy>=1.13'],
      python_requires=">=3.6")
#!/usr/bin/env python
