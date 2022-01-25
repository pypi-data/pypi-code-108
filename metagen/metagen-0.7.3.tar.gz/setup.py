"""
NAME:
    setup.py
  
SYNOPSIS:
    python3 setup.py [options] [command]
    
DESCRIPTION:
    Using setuptools "setup", build, install, or make tarball of the package.
    
OPTIONS:
    See Distutils documentation for details on options and commands.
    Common commands:
    build               build the package, in preparation for install
    install             install module(s)/package(s) [runs build if needed]
    install_data        install datafiles (e.g., in a share dir)   
    install_scripts     install executable scripts (e.g., in a bin dir)   
    sdist               make a source distribution
    bdist               make a binary distribution
    clean               remove build temporaries

EXAMPLES:
    cd mydir
    (cp myfile-0.1.tar.gz here)
    gzip -cd myfile-0.1.tar.gz | tar xvf -
    cd myfile-0.1
    python3 setup.py build
    python3 setup.py install
    python3 setup.py sdist
"""

import glob
from setuptools import setup
from metagen.version import __version__

pkgname='metagen'
version = __version__
description = "Metadata.xml Generator for Ebuilds"
author = "Rob Cakebread"
author_email = "pythonhead@gentoo.org"
url = "https://gitweb.gentoo.org/proj/metagen.git/"
license = "GPL-2"

packages=['metagen']
package_data={"metagen" : ["test_cli"]}
data_files=[("share/doc/%s-%s" % ("metagen", version), glob.glob("docs/*"))]


def main():
    setup(
        name = pkgname,
        version = version,
        description = description,
        long_description = open('README.md').read(),
        long_description_content_type = 'text/markdown',
        author = author,
        author_email = author_email,
        url=url,
        license = license,

        setup_requires = [
            'setuptools>=38.6.0',  # for long_description_content_type
        ],
        install_requires = [
            'lxml',
        ],

        packages = packages,
        data_files = data_files,
        package_data = package_data,

        entry_points = {
            'console_scripts': [
                "metagen = metagen.__main__:main",
            ],
        },

        classifiers = [
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
            'Natural Language :: English',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Programming Language :: Python :: 3 :: Only',
            'Topic :: Software Development',
            'Topic :: Text Processing :: Markup :: XML',
            'Topic :: Utilities',
        ]
    )


if __name__ == '__main__':
    main()
