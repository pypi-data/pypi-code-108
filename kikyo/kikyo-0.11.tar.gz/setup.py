import re
import sys
from os.path import join, dirname

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

with open(join(dirname(__file__), 'README.rst'), 'r', encoding='utf-8') as fd:
    long_description = fd.read()


def read_version():
    p = join(dirname(__file__), 'kikyo', '__init__.py')
    with open(p, 'r', encoding='utf-8') as f:
        return re.search(r"__version__ = '([^']+)'", f.read()).group(1)


def read_requirements(file):
    with open(join(dirname(__file__), 'requirements', file), 'r', encoding='utf-8') as f:
        return [l.strip() for l in f]


class PyTest(TestCommand):
    def run_tests(self):
        import pytest

        errno = pytest.main(['tests'])
        sys.exit(errno)


tests_require = read_requirements('test.txt')
install_requires = [
    'PyYAML>=5.4.1',
    'requests>=2.25.1',
    'pulsar-client>=2.7.0,<2.8',
    'minio>=7.0.1,<8.0',
    'elasticsearch>=7.13.1,<7.14',
    'oss2>=2.14.0',
    'fastavro>=0.24.0',
]


def main():
    if sys.version_info < (3, 6):
        raise RuntimeError('The minimal supported Python version is 3.6')

    setup(
        name='kikyo',
        version=read_version(),
        description='kikyo package',
        long_description=long_description,
        author='jadbin',
        author_email='jadbin.com@hotmail.com',
        license='MIT',
        zip_safe=False,
        packages=find_packages(exclude=('tests',)),
        include_package_data=True,
        python_requires='>=3.6',
        install_requires=install_requires,
        tests_require=tests_require,
        cmdclass={'test': PyTest},
        entry_points={'kikyo.plugins': 'kikyo_bundle = kikyo.bundle.config'},
        classifiers=[
            'License :: OSI Approved :: MIT License',
            'Intended Audience :: Developers',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )


if __name__ == '__main__':
    main()
