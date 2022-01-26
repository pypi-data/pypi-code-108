#!/usr/bin/python3 -u
"""
Setup script for PLIB3.EXTENSIONS package
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information
"""


version = "1.3"

name = "plib3.extensions"
description = "Useful Python 3 Python/C API functions."

author = "Peter A. Donis"
author_email = "peterdonis@alum.mit.edu"

dev_status = "Production/Stable"

license = "GPLv2"

ext_names = [
    'plib.extensions._extensions',
    'plib.test.extensions._extensions_testmod'
]
ext_srcdir = "src"

classifiers = """
Environment :: Console
Environment :: MacOS X
Environment :: Win32 (MS Windows)
Intended Audience :: Developers
Operating System :: MacOS :: MacOS X
Operating System :: Microsoft :: Windows
Operating System :: POSIX
Operating System :: POSIX :: Linux
Topic :: Software Development :: Libraries :: Python Modules
"""

# Note: when building with a PEP 517 backend, setuputils3 does not
# need to be listed in the requirements below; however, they are
# listed anyway for completeness and to allow builds that are not
# using a PEP 517 backend to work
requires = install_requires = """
plib3.stdlib (>=2.1)
setuputils3 (>=2.1)
"""

setup_requires = """
setuputils3 (>=2.1)
"""


if __name__ == '__main__':
    from setuputils import setup_py_vars
    from setuptools import setup
    setup(**setup_py_vars(globals()))
