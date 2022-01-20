from setuptools import setup

name = "types-colorama"
description = "Typing stubs for colorama"
long_description = '''
## Typing stubs for colorama

This is a PEP 561 type stub package for the `colorama` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `colorama`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/colorama. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `aea52b35d1f5a9306f66e1b98314f4ecbe0ffa7a`.
'''.lstrip()

setup(name=name,
      version="0.4.7",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['colorama-stubs'],
      package_data={'colorama-stubs': ['__init__.pyi', 'ansi.pyi', 'ansitowin32.pyi', 'initialise.pyi', 'win32.pyi', 'winterm.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Stubs Only",
      ]
)
