import importlib.machinery
import os
import subprocess
import types
from setuptools import setup, find_packages


BASE_VERSION = '2.1'
SOURCE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)
VCSINFO_DIR = os.path.join(SOURCE_DIR, 'vcsinfo')
VERSION_FILE = os.path.join(VCSINFO_DIR, 'version.py')
HEADER_FILE = os.path.join(SOURCE_DIR, '.pylint-license-header')


with open(os.path.join(SOURCE_DIR, 'README.rst')) as fobj:
    long_description = fobj.read().strip()


def get_version():
    """
    Call out to the git command line to get the current commit "number".
    """
    if os.path.exists(VERSION_FILE):
        # Read version from file
        loader = importlib.machinery.SourceFileLoader('vcsinfo_version', VERSION_FILE)
        version_mod = types.ModuleType(loader.name)
        loader.exec_module(version_mod)
        existing_version = version_mod.__version__  # pylint: disable=no-member
        print(f'Using existing vcsinfo version: {existing_version}')
        return existing_version

    # Generate the version from the base version and the git commit number, then store it in the file
    try:
        cmd = subprocess.Popen(
            args=[
                'git',
                'rev-list',
                '--count',
                'HEAD',
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding='utf8',
        )
        stdout = cmd.communicate()[0]
        output = stdout.strip()
        if cmd.returncode == 0:
            new_version = '{0}.{1}'.format(BASE_VERSION, output)
            print(f'Setting version to {new_version}')

            # write the version file
            if os.path.exists(VCSINFO_DIR):
                with open(HEADER_FILE, 'r', encoding='utf8') as fobj:
                    header = fobj.read()
                with open(VERSION_FILE, 'w', encoding='utf8') as fobj:
                    fobj.write(f"{header}\n__version__ = '{new_version}'\n")
            return new_version
    except Exception as exc:
        print(f'Could not generate version from git commits: {exc}')
    # If all else fails, use development version
    return f'{BASE_VERSION}.DEVELOPMENT'


# pylint: disable=C0301
setup(
    name='vcsinfo',
    version=get_version(),
    author='Adobe',
    author_email='noreply@adobe.com',
    license='MIT',
    url='https://github.com/adobe/vcsinfo',
    description='Utilities to normalize working with different Version Control Systems',
    long_description=long_description,
    long_description_content_type='text/x-rst',
    packages=find_packages(exclude=("tests",)),
    scripts=[
        'bin/vcsinfo',
    ],
    install_requires=[
        'GitPython<4',
        'gitdb<5',
    ],
    extras_require={
        # Make everything except git an optional dependency
        'hg': ['mercurial'],
        'p4': ['p4python'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
