#!/usr/bin/env python
from setuptools import find_packages, setup

from simple_sso import __version__


REQUIREMENTS = [
    'Django>=2.2',
    'itsdangerous~=2.0',
    'webservices[django]',
]


CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Web Environment',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Framework :: Django',
    'Framework :: Django :: 2.2',
    'Framework :: Django :: 3.0',
    'Framework :: Django :: 3.1',
    'Topic :: Internet :: WWW/HTTP',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries',
]


setup(
    name='django-simple-sso.hga',
    version=__version__,
    author='Rafael Leira, Andrew Eitel',
    author_email='rafael.leira@naudit.es, aeitel@hga-llc.com',
    url='http://github.com/andreweitel/django-simple-sso',
    license='BSD-3-Clause',
    description='Simple SSO for Django',
    long_description=open('README.rst').read(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=REQUIREMENTS,
    classifiers=CLASSIFIERS,
    test_suite='tests.settings.run',
)
