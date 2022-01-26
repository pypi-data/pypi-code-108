# Copyright 2013-2021 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

# This module has no docstring because it is to be execfile'd
# from `setup.py`, `atelier/__init__.py` and possibly some external
# tools, too.

SETUP_INFO = dict(
    name='atelier',
    version='1.1.41',
    description="A collection of tools for software artists",
    license_files=['COPYING'],
    author='Rumma & Ko Ltd',
    author_email='info@lino-framework.org',
    url="https://gitlab.com/lino-framework/atelier")

install_requires = ['invoke', 'argh', 'six',
                    'future', 'Babel',
                    'python-dateutil', 'Sphinx', 'rstgen']
install_requires.append('requests')
install_requires.append('sphinx-panels')
install_requires.append('sphinx-rtd-theme')
install_requires.append('pydata-sphinx-theme')
install_requires.append('insipid-sphinx-theme')
install_requires.append('gitpython')

# trying to fix #3246
tests_require = ['pytest-cov']

# # Explicitly install `importlib` under Python 2.6. Thanks to
# # https://stackoverflow.com/questions/9418064
# try:
#     import importlib
# except ImportError:
#     install_requires.append('importlib')

SETUP_INFO.update(
    install_requires=install_requires,
    tests_require=tests_require,
    # scripts=['scripts/per_project'],
    entry_points={
        'console_scripts': ['per_project = atelier.cli.per_project:main']
    },
    test_suite='tests',
    long_description="""\

`atelier` is a collection of tools for managing and maintaining Python software
projects.

It contains:

- some general Python utilities
  (`atelier.utils <https://lino-framework.gitlab.io/atelier/api/atelier.utils.html>`_)
- some Sphinx extensions
  (`atelier.sphinxconf <https://lino-framework.gitlab.io/atelier/api/atelier.sphinxconf.html>`_)
- a library of invoke commands
  (`atelier.invlib <https://lino-framework.gitlab.io/atelier/api/atelier.invlib.html>`_)
- a minimalistic project management
  (`atelier.projects <https://lino-framework.gitlab.io/atelier/api/atelier.projects.html>`_)

The central project homepage is https://lino-framework.gitlab.io/atelier

""",
    classifiers="""\
Programming Language :: Python
Programming Language :: Python :: 3.7
Framework :: Sphinx :: Extension
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
License :: OSI Approved :: GNU Affero General Public License v3
Natural Language :: English
Operating System :: OS Independent""".splitlines())

SETUP_INFO.update(packages=[n for n in """
atelier
atelier.sphinxconf
atelier.invlib
atelier.cli
""".splitlines() if n])

SETUP_INFO.update(
    zip_safe=False,
    include_package_data=True)

# SETUP_INFO.update(package_data=dict())
#
# def add_package_data(package, *patterns):
#     l = SETUP_INFO['package_data'].setdefault(package, [])
#     l.extend(patterns)
#     return l
#
# add_package_data('atelier.sphinxconf', '*.html')
