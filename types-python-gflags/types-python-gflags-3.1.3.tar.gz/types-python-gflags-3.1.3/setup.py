from setuptools import setup

name = "types-python-gflags"
description = "Typing stubs for python-gflags"
long_description = '''
## Typing stubs for python-gflags

This is a PEP 561 type stub package for the `python-gflags` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `python-gflags`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/python-gflags. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `aea52b35d1f5a9306f66e1b98314f4ecbe0ffa7a`.
'''.lstrip()

setup(name=name,
      version="3.1.3",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['gflags-stubs'],
      package_data={'gflags-stubs': ['__init__.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Stubs Only",
      ]
)
