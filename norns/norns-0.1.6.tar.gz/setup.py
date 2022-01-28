import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

exec(open("norns/__about__.py").read())

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

# trick to get rst file for PyPi, see:
# http://stackoverflow.com/questions/26737222/pypi-description-markdown-doesnt-work/26737672#26737672
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

packages = [
    'norns',
]

package_data = {
}

requires = [
    'nose',
    'appdirs',
    'pyyaml',
]

scripts = [
]

classifiers = [
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
]

setup(
    name='norns',
    version=__version__,
    description='Simple yaml-based config module',
    long_description=long_description,
    packages=packages,
    package_data=package_data,
    scripts=scripts,
    install_requires=requires,
    author=__author__,
    author_email='simon.vanheeringen@gmail.com',
    url='https://github.com/simonvh/norns',
    license='MIT',
    classifiers=classifiers,
)
