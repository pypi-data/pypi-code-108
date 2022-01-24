# -*- coding: UTF-8 -*-
# Copyright 2015-2022 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

SETUP_INFO = dict(
    name='lino_react',
    version='22.1.2',
    install_requires=['lino'],
    tests_require=[],
    test_suite='tests',
    description="The React front end for Lino",
    license_files=['COPYING'],
    include_package_data=False,
    zip_safe=False,
    author='Rumma & Ko Ltd',
    author_email='info@lino-framework.org',
    url="https://gitlab.com/lino-framework/react",
    classifiers="""\
  Programming Language :: Python
  Programming Language :: Python :: 3
  Development Status :: 5 - Production/Stable
  Environment :: Web Environment
  Framework :: Django
  Intended Audience :: Developers
  Intended Audience :: System Administrators
  License :: OSI Approved :: GNU Affero General Public License v3
  Natural Language :: English
  Operating System :: OS Independent
  Topic :: Database :: Front-Ends
  Topic :: Home Automation
  Topic :: Office/Business
  Topic :: Software Development :: Libraries :: Application Frameworks""".splitlines())

SETUP_INFO.update(long_description="""\

The React front end for Lino

Project homepage is https://gitlab.com/lino-framework/react


""")

SETUP_INFO.update(packages=[str(n) for n in """
lino_react
lino_react.react
""".splitlines() if n])



SETUP_INFO.update(
    zip_safe=False,
    include_package_data=True)
