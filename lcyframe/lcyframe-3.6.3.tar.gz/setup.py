# -*- coding:utf-8 -*-
import os
from setuptools import setup, find_packages

name = "lcyframe"
version = "3.6.3"

setup(name=name,
      version=version,
      description="A Fast ApiServer Frame for python3",
      long_description="",
      classifiers=[],
      keywords=name,
      author="lcylln",
      author_email="123220663@qq.com",
      url='',
      license='',
      platforms='any',
      packages=find_packages(),
      zip_safe=False,
      include_package_data=True,
      entry_points={
                'console_scripts': [
                    '%s = %s.__main__:main' % (name, name),
                ]
            },
      install_requires=[
          'tornado==5.0',
          'tornado-redis',
          'sphinx==1.6.3',
          'sphinx-rtd-theme==0.2.4',
          'mistune==0.8.4',     # 与m2r配合，生成文档 md
          'm2r>=0.1.12',
          'ruamel.yaml>=0.12.5',
          'normalize',
          'pyjwt>=1.5.3',
          'pyssdb>=0.4.2',
          'redis>=2.10.6',
          'celery>=4.4.7',
          'pynsq>=0.8.1',
          'mongoengine>=0.23.1',
          'pymongo>=3.11.4',
          'pymysql>=1.0.2',
          'DBUtils>=2.0.1',
          'pyaml>=17.10.0',
          'falcon>=1.3.0',
          'paho-mqtt>=1.3.1',
          'jinja2>=3.0.1',
          'xlrd>=2.0.1',
          'rsa>=4.7.2',
          # 'Crypto>=1.4.1',
          'pycryptodome'
      ],

)

