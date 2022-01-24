try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
from cleepcli.version import VERSION

requirements = []
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name = 'cleepcli',
    version = VERSION,
    description = 'Cleep-cli helps developers to build great Cleep applications from command line.',
    author = 'Tanguy Bonneau',
    author_email = 'tanguy.bonneau@gmail.com',
    maintainer = 'Tanguy Bonneau',
    maintainer_email = 'tanguy.bonneau@gmail.com',
    url = 'http://www.github.com/tangb/cleep-cli/',
    packages = ['cleepcli'],
    include_package_data = True,
    install_requires = requirements,
    scripts = ['bin/cleep-cli', 'bin/ccli']
)

