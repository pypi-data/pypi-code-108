from conf import *
from setuptools import setup, Extension

NAME_EXTRAS = 'clickhouse-toolset-extras'
VERSION = '0.15.dev0'

chext = Extension(
    'chtoolsetext._extras',
    sources=['extras/extras.cpp'],
    depends=[]
)
setup(
    name=NAME_EXTRAS,
    version=VERSION,
    url='https://gitlab.com/tinybird/clickhouse-toolset',
    author='Tinybird.co',
    author_email='support@tinybird.co',
    packages=['chtoolsetext'],
    package_dir={'': 'extras'},
    python_requires='>=3.7, <3.11',
    install_requires=[],
    extras_require={
        'test': requirements_from_file('requirements-test.txt')
    },
    cmdclass={
        'clickhouse': ClickHouseBuildExt,
        'build_ext': CustomBuildWithClang,
    },
    ext_modules=[chext]
)
