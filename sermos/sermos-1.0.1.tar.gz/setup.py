""" Sermos Library Setup
"""
import re
import ast
import sys
import os
from typing import List

from setuptools import setup, find_packages, Extension
from setuptools.command.build_py import build_py
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    """ PyTest Command
    """

    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ''

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import coverage
        import pytest

        if self.pytest_args and len(self.pytest_args) > 0:
            self.test_args.extend(self.pytest_args.strip().split(' '))
            self.test_args.append('tests/')

        cov = coverage.Coverage()
        cov.start()
        errno = pytest.main(self.test_args)
        cov.stop()
        cov.report()
        cov.html_report()
        print("Wrote coverage report to htmlcov directory")
        sys.exit(errno)


# Defaults that will be overridden/updated if do_cythonize is true.
#
ext_modules = []
cmdclass = {'test': PyTest}
packages = find_packages(exclude=["tests"])

do_cythonize = os.getenv('CYTHONIZE', 'false').lower() == 'true'
if do_cythonize:
    try:
        from Cython.Build import cythonize
        from Cython.Distutils import build_ext

        cmdclass['build_ext'] = build_ext  # Use cython's build_ext

        def scandir(directory: str,
                    exclude_paths: List[str] = None,
                    paths: List[str] = None,
                    directories: List[str] = None,
                    return_directories: bool = False,
                    recursive: bool = True):
            """ Scan a given directory recursively and produce a list
                of file paths (e.g. ['sermos/app.py', 'sermos/config.py'])
                or directroies (e.g. ['sermos/api', 'sermos/utils'])
            """
            if paths is None:
                paths = []
            if directories is None:
                directories = []
            if exclude_paths is None:
                exclude_paths = []

            for file in os.listdir(directory):
                path = os.path.join(directory, file)
                if any([p in path for p in exclude_paths]):
                    continue

                if '__init__.py' in path or '__pycache__' in path:
                    continue

                if os.path.isfile(path) and path.endswith(".py"):
                    paths.append(path)
                elif os.path.isdir(path) and recursive:
                    directories.append(path)
                    scandir(path,
                            exclude_paths=exclude_paths,
                            paths=paths,
                            directories=directories,
                            return_directories=return_directories,
                            recursive=recursive)

            if return_directories:
                return directories
            return paths

        def make_extension(ext_path: str):
            """ Generate an Extension() object. Takes a path
                e.g. sermos/app.py
                and generates a valid Extension
                e.g. Extension('sermos.app', ['sermos/app.py'])
            """
            extName = ext_path.replace("/", ".")[:-3]
            return Extension(extName, [ext_path], include_dirs=["."])

        to_cythonize = scandir('sermos',
                               exclude_paths=[
                                   'sermos/templates', 'sermos/static',
                                   'sermos/celery.py',
                                   'sermos/tools/thumbnail/thumbnail.py',
                                   'sermos/lib/config_server.py'
                               ])

        ext_modules = cythonize(
            [make_extension(path) for path in to_cythonize], language_level=3)

        class MyBuildPy(build_py):
            """ Update standard build_py to exclude any files we
                explicitly cythonize.
            """
            def find_package_modules(self, package, package_dir):
                """ Return list of all package modules that are *not* cythonized
                    for regular packaging.
                """
                modules = super().find_package_modules(package, package_dir)
                filtered_modules = []
                for tup in modules:
                    if tup[2] in to_cythonize:
                        continue
                    filtered_modules.append(tup)
                return filtered_modules

        cmdclass['build_py'] = MyBuildPy

    except ImportError:
        pass

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('sermos/__init__.py', 'rb') as f:
    __version__ = str(
        ast.literal_eval(
            _version_re.search(f.read().decode('utf-8')).group(1)))

with open('requirements.txt', 'r') as f:
    install_requires = f.read().splitlines()

setup(
    name='sermos',
    version=__version__,
    description="Sermos - Machine Learning for the Real World",
    long_description=open('README.md', 'r').read(),
    long_description_content_type="text/markdown",
    author="Sermos, LLC",
    license="Apache License 2.0",
    url="https://gitlab.com/sermos/sermos",
    packages=packages,
    include_package_data=True,
    package_data={'sermos': ['templates/*']},
    cmdclass=cmdclass,
    ext_modules=ext_modules,
    install_requires=install_requires,
    extras_require={
        'build': ['wheel', 'twine'],
        'cli': [
            # TODO Need to address celery dependency, same as under `deploy`
            # and `workers` extras
            'celery==5.1.2'
        ],
        'flask':
        ['Flask>=1.1.1', 'rho-web[smorest]>=0.3.3', 'flask-smorest>=0.23.0'],
        'flask_auth': ['Flask-RhoAuth[openid]>=2.2.1'],
        'proxy': ['PyJWT>=2.1.0,<3', 'cryptography>=3.4.7,<4'],
        'web': ['gunicorn', 'gevent'],
        'workers': [
            # TODO Upgrade. Something between 4.4.2 and 4.4.7 breaks
            # tests related to generating a chain and the resultant object
            # types, e.g. test test_chain_helper_with_retry()
            'celery[redis]==5.1.2',
            'networkx>=2.4',
        ],
        'deploy': [
            # TODO Need to address the celery pegged version in addition to
            # the fact that celery is currently required for properly parsing
            # the Sermos Yaml format (due to use of crontab_parser for
            # scheduled tasks). Feels like Celery is a heavy dependency for
            # just a deployment task.
            'requests>=2.22',
            'celery==5.1.2'
        ],
        'dev':
        ['honcho>=1.0.1', 'awscli>=1.11'
         'pylint>=2.5.3', 'pip-licenses'],
        'docs': ['sphinx>=3.0.2', 'boto3>=1.11', 'celery==5.1.2'],
        'test': [
            'pytest-cov>=2.6.1,<3',
            'tox>=3.14.1,<4',
            'mock>=1,<2',
            'moto>=1.3.16,<2',
            'responses>=0.10.16,<0.11',
            'fakeredis==1.0.5',
        ]
    },
    entry_points="""
    [console_scripts]
    sermos=sermos.cli.core:sermos
    """,
)
