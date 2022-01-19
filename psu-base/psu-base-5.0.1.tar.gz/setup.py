"""
Python setup file for the psu-base app.

In order to register your app at pypi.python.org, create an account at
pypi.python.org and login, then register your new app like so:

    python setup.py register

If your name is still free, you can now make your first release but first you
should check if you are uploading the correct files:

    python setup.py sdist

Inspect the output thoroughly. There shouldn't be any temp files and if your
app includes staticfiles or templates, make sure that they appear in the list.
If something is wrong, you need to edit MANIFEST.in and run the command again.

If all looks good, you can make your first release:

    python setup.py sdist upload

For new releases, you need to bump the version number in
psu_base/__init__.py and re-run the above command.

For more information on creating source distributions, see
http://docs.python.org/3/distutils/sourcedist.html
"""
import os
from setuptools import find_packages, setup
import psu_base as app


# Function for reading the contents of a file
def read(filename):
    try:
        return open(os.path.join(os.path.dirname(__file__), filename)).read()
    except IOError:
        return ''


os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='psu-base',
    version=app.__version__,
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description='Basic features used in all PSU Django apps',
    long_description="Reusable Django app specifically for PSU's custom-built web applications. ",
    long_description_content_type="text/markdown",
    url='https://github.com/PSU-OIT-ARC/django-psu-base',
    author='Mike Gostomski',
    author_email='mjg@pdx.edu',
    classifiers=[
        'Framework :: Django :: 2.2',
        "License :: OSI Approved :: MIT License",
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=read('requirements.txt').splitlines()
)
