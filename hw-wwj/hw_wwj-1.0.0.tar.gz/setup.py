import setuptools
from distutils.core import setup
from setuptools import find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Fortran extension
from numpy.distutils.core import Extension 
from numpy.distutils.core import setup 
ext_for1 = Extension(name='hw',
                sources=['/home/wangwenjie/桌面/hw_wwj/src/hw_wwj/hw.f90'])
'''这是fortran需要的一部分安装文件
setup(
  ext_modules         = [ext_for1],
)        
'''        

setup(name = 'hw_wwj',     # 包名
      version = '1.0.0',  # 版本号
      description = '',
      #long_description = '', # 这里的内容会显示在pypi包首页上
      long_description=long_description,    #包的详细介绍，一般在README.md文件内
      long_description_content_type="text/markdown",
      author = 'banshiliuli',
      author_email = '446601097@qq.com',
      url = 'https://github.com/pypa/sampleproject',
      install_requires = [], # 申明依赖包，安装包时pip会自动安装：格式如下（我上面的setup.py没有这个参数，因为我这不依赖第三方包:)）
      classifiers = [
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities'
      ],
      keywords = '',
      packages = find_packages('src'),  # 必填，就是包的代码主目录
      package_dir = {'':'src'},         # 必填
      include_package_data = True,
    python_requires='>=3.6',    #对python的最低版本要求
    
    ext_modules         = [ext_for1],
)
#!/usr/bin/env python
