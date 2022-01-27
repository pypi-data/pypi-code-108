import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='danceschool-dancervax',
    version='0.1.1',
    packages=['danceschool_dancervax'],
    include_package_data=True,
    license='BSD License',
    description='DancerVax API integration for The Django Dance School project',
    long_description=README,
    url='https://github.com/django-danceschool/danceschool-dancervax',
    author='Lee Tucker',
    author_email='lee.c.tucker@gmail.com',
    install_requires=[
        'django-danceschool>=0.9.3',
        'Django>=3.1.13',
        'requests-oauthlib>=1.3.0',
        'requests>=2.22.0',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content'
    ],
)
