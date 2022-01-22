import os
import sys
from setuptools import setup, find_packages


def get_version(filename):
    import os
    import re

    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, filename)) as f:
        version_file = f.read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


version = get_version('aiodataloader.py')

build_require = [
    'wheel>=0.37.1',
    'twine>=3.7.1',
]
lint_require = [
    'flake8>=3.9.0',
]
test_require = [
    'pytest>=6.2.5',
    'pytest-cov',
    'coveralls',
    'mock',
    'pytest-asyncio'
]
typecheck_require = [
    'mypy>=0.930',
]

setup(
    name='aiodataloader-ng',
    version=version,
    description='Asyncio DataLoader implementation for Python',
    long_description=open('README.rst').read(),
    url='https://github.com/lablup/aiodataloader-ng',
    download_url='https://github.com/lablup/aiodataloader/releases',
    author='Syrus Akbary, Joongi Kim and other contributors',
    author_email='joongi@lablup.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
    ],
    keywords='concurrent future deferred aiodataloader',
    py_modules=['aiodataloader'],
    extras_require={
        'build': build_require,
        'lint': lint_require,
        'typecheck': typecheck_require,
        'test': test_require,
    },
)
