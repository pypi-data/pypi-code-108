#!/usr/bin/env python3

import os
from distutils.core import setup
from distutils.command.build_py import build_py
from cinp.client import __CLIENT_VERSION__


class build( build_py ):
  def build_packages( self ):
    # get all the .py files, unless they end in _test.py
    # we don't need testing files in our published product
    for package in self.packages:
      package_dir = self.get_package_dir( package )
      modules = self.find_package_modules( package, package_dir )
      for ( package2, module, module_file ) in modules:
        assert package == package2
        if os.path.basename( module_file ).endswith( '_test.py' ) or os.path.basename( module_file ) == 'tests.py':
          continue
        self.build_module( module, module_file, package )


setup( name='cinp',
       version=__CLIENT_VERSION__,
       description='CInP, Concise Interaction Protocol',
       long_description="""A HTTP/JSON Protocol that brings some of the
flexability of REST, but extends beyond CRUD to support Metod Calling and
fully describing the enpoints and data sctuctures.  As well as enabeling
the Business Logic and permissions to be fully encapsulated on the Server.""",
       author='Peter Howe',
       author_email='pnhowe@gmail.com',
       url='https://github.com/cinp/python',
       python='~=3.6',
       license='Apache2',
       classifiers=[
           'Development Status :: 5 - Production/Stable',
           'Intended Audience :: Developers',
           'License :: OSI Approved :: Apache Software License',
           'Programming Language :: Python :: 3',
           'Programming Language :: Python :: 3.6'
       ],
       packages=[ 'cinp' ],
       cmdclass={ 'build_py': build }
       )
