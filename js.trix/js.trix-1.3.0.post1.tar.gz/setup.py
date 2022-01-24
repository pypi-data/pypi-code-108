from setuptools import setup, find_packages
import os

# The version of the wrapped library is the starting point for the
# version number of the python package.
# In bugfix releases of the python package, add a '-' suffix and an
# incrementing integer.
# For example, a packaging bugfix release version 1.4.4 of the
# js.jquery package would be version 1.4.4-1 .

version = '1.3.0.post1'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.rst')
    + '\n' +
    read('js', 'trix', 'test_trix.txt')
    + '\n' +
    read('CHANGES.txt')
    )

setup(
    name='js.trix',
    version=version,
    description="Fanstatic packaging of Trix",
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    keywords='',
    license='MIT',
    url='https://github.com/minddistrict/js.trix',
    packages=find_packages(),
    namespace_packages=['js'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'fanstatic',
        'setuptools',
        ],
    entry_points={
        'fanstatic.libraries': [
            'trix = js.trix:library',
            ],
        },
    )
