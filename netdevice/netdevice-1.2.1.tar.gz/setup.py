#!/usr/bin/env python

from setuptools import setup

setup(name='netdevice',
      version='1.2.1',
      author='Yongping Guo',
      author_email='guoyoooping@163.com',
      description='Python modules to execute command on remote network device based on pexpect.',
      long_description=open('README.rst').read(),
      install_requires = ["ipaddress", "pexpect", "lxml", "IPy", "xmltodict", "dpkt", "simplejson"],
      url='https://github.com/guoyoooping/networkdevice',
      license="GPLv3",
      scripts=['demo/demo.py'],
      packages=['netdevice']
      )
