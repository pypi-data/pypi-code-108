#!/usr/bin/env python
import os

from datetime import date

from setuptools import setup, find_packages

from whatap import build
build.release_date = date.today().strftime('%Y%m%d')

readme_file = os.path.join(os.getcwd(), 'whatap', 'README.rst')

setup(name=build.name,
      version=build.version,
      description='Monitoring and Profiling Service',
      long_description=open(readme_file).read(),
      author='whatap',
      author_email='admin@whatap.io',
      license='Whatap License',
      url='https://www.whatap.io',
      packages=find_packages(exclude=('whatap_dev', 'whatap_dev.*')),
      package_data={
          'whatap': ['LICENSE', '*.rst', '*.conf', '*.json', 'agent/*/*/whatap_python']
      },
      entry_points={
          'console_scripts': [
              'whatap-start-agent=whatap.scripts:start_agent',
              'whatap-stop-agent=whatap.scripts:stop_agent',
              'whatap-setting-config=whatap.scripts:setting_config',
              
              
              'whatap-start-batch-agent=whatap:start_batch_agent',
          ],
      },
      zip_safe=False,
      )

