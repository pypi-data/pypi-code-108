# -*- coding: utf-8 -*-

import os
import sys
from distutils.core import setup, Extension
from distutils import sysconfig

with open('README.md') as readme:
    long_description = readme.read()


install_path = '/opt/swcdb'
include_dirs = [install_path+'/include',
                sysconfig.get_python_inc(plat_specific=True),
                '/usr/local/include', '/usr/include'] + \
                ''.split(';') + \
                ''.split(';') + \
                '/usr/local/include'.split(';')
include_dirs = list(set(include_dirs))

extra_compile_args = [a for a in set([a.strip() 
                      for a in " -D_LARGEFILE_SOURCE -m64 -D_FILE_OFFSET_BITS=64 -O3 -flto -fuse-linker-plugin -ffat-lto-objects -fdevirtualize-at-ltrans -Wall -Werror -Wextra -Wpedantic -Wformat-security -Wformat-nonliteral -Wcast-align -Wnon-virtual-dtor -Wzero-as-null-pointer-constant -Wno-error=zero-as-null-pointer-constant -Wold-style-cast -Wno-error=old-style-cast -Wnull-dereference -Wno-error=null-dereference -Wformat-signedness -Wnoexcept -Wno-error=noexcept -Wsuggest-override -Wno-error=suggest-override -Wuseless-cast -Wno-error=useless-cast -Wstrict-null-sentinel -Wno-error=strict-null-sentinel -Wduplicated-cond -Wno-error=duplicated-cond -Wduplicated-branches -Wno-error=duplicated-branches -Wlogical-op -Wno-error=logical-op -Wshadow=compatible-local -Wshadow=local -Wshadow=global -Wshadow -Wno-error=shadow=compatible-local -Wno-error=shadow=local -Wno-error=shadow=global -Wno-error=shadow -Wstack-usage=16384 -Wno-error=stack-usage=16384 -Wtrampolines -Wsuggest-attribute=const -Wno-error=suggest-attribute=const -Wsuggest-attribute=pure -Wno-error=suggest-attribute=pure -Wsuggest-attribute=malloc -Wno-error=suggest-attribute=malloc -Wsuggest-attribute=cold -Wno-error=suggest-attribute=cold -Wtsan -DASIO_STANDALONE -DASIO_NO_DEPRECATED -DOPENSSL_NO_SSL2 -DOPENSSL_NO_SSL3  -D_LARGEFILE_SOURCE -m64 -D_FILE_OFFSET_BITS=64 -O3 -flto -fuse-linker-plugin -ffat-lto-objects -Wall -Werror -Wformat-security".split(' ')]) if a]

libraries=[l.split('/')[-1].split('.')[0][3:] 
           for l in '/usr/local/lib/libtcmalloc_minimal.so.4.5.9'.split(';') 
           if '/' in l]

extensions = []


setup(
    name='swcdb',
    version='0.5.7.0',
    description='The SWC-DB Python Package',
    long_description=long_description,

    # long_description_content_type='text/markdown',
    # install_requires=['thrift==0.15.0'],

    url='https://github.com/kashirin-alex/swc-db',
    license='GPLv3',
    package_dir={'swcdb': 'swcdb'},
    packages=[
        'swcdb',
        'swcdb.thrift',
        'swcdb.thrift.native',
        'swcdb.thrift.tornado',
        'swcdb.thrift.twisted',
        'swcdb.thrift.zopeif'
    ],
    maintainer='Kashirin Alex',
    maintainer_email='kashirin.alex@gmail.com',
    ext_modules=extensions,
    
    classifiers=(
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Environment :: Console",
        "Framework :: Twisted",
        "Framework :: Zope",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Programming Language :: Zope",
        
        "Topic :: Database",
        "Topic :: Database :: Database Engines/Servers",
        "Topic :: Database :: Front-Ends",
        "Topic :: Scientific/Engineering",
    ),
    platforms=['any'],
)


# /
# setup.py
# swcdb/
#    __init__.py
#    thrift/
#         __init__.py
#         service.py
#         pool.py
#         native/
#         tornado/
#         twisted/
#         zopeif/
#
