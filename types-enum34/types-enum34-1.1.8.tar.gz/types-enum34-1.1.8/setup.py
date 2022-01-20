from setuptools import setup

name = "types-enum34"
description = "Typing stubs for enum34"
long_description = '''
## Typing stubs for enum34

This is a PEP 561 type stub package for the `enum34` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `enum34`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/enum34. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `aea52b35d1f5a9306f66e1b98314f4ecbe0ffa7a`.
'''.lstrip()

setup(name=name,
      version="1.1.8",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['enum-python2-stubs'],
      package_data={'enum-python2-stubs': ['__init__.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Stubs Only",
      ]
)
