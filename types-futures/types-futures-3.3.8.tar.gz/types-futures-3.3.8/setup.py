from setuptools import setup

name = "types-futures"
description = "Typing stubs for futures"
long_description = '''
## Typing stubs for futures

This is a PEP 561 type stub package for the `futures` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `futures`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/futures. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `0e185f40877a614c5ddd87815707cf8153296872`.
'''.lstrip()

setup(name=name,
      version="3.3.8",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['concurrent-python2-stubs'],
      package_data={'concurrent-python2-stubs': ['__init__.pyi', 'futures/__init__.pyi', 'futures/_base.pyi', 'futures/process.pyi', 'futures/thread.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Stubs Only",
      ]
)
