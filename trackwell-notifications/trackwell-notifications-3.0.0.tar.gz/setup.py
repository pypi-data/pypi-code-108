import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='trackwell-notifications',
    version='3.0.0',
    packages=find_packages(),
    include_package_data=True,
    license='NA',  # example license
    description='A simple Django app to support Notifications.',
    long_description=README,
    long_description_content_type='text/markdown',
    url='',
    author='trackwell',
    author_email='',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django', 'djangorestframework', 'django-filter',
    ]
)
