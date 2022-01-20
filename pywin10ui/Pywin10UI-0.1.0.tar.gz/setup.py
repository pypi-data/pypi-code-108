#coding:utf-8
from setuptools import setup

setup(name='PyWin10UI',
      version='0.1.0',
      description='基于Pygame的UI模块,支持模块以外的pygame组件',
      url='https://github.com/bytfr/pywin10ui',
      author='bytfr 啃竹子',
      author_email='2678509244@qq.com',
      license='MIT',
      packages=['pywin10ui'],
      install_requires=['pygame>=2.0.1','easygui>=0.98.2']
      )