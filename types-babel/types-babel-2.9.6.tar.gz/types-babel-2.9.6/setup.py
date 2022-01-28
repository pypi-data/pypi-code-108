from setuptools import setup

name = "types-babel"
description = "Typing stubs for babel"
long_description = '''
## Typing stubs for babel

This is a PEP 561 type stub package for the `babel` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `babel`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/babel. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `67766f282fd21a048cb7ee2d8ea5558196a3af03`.
'''.lstrip()

setup(name=name,
      version="2.9.6",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=['types-pytz'],
      packages=['babel-stubs'],
      package_data={'babel-stubs': ['__init__.pyi', '_compat.pyi', 'core.pyi', 'dates.pyi', 'languages.pyi', 'lists.pyi', 'localedata.pyi', 'localtime/__init__.pyi', 'localtime/_unix.pyi', 'localtime/_win32.pyi', 'messages/__init__.pyi', 'messages/catalog.pyi', 'messages/checkers.pyi', 'messages/extract.pyi', 'messages/frontend.pyi', 'messages/jslexer.pyi', 'messages/mofile.pyi', 'messages/plurals.pyi', 'messages/pofile.pyi', 'numbers.pyi', 'plural.pyi', 'support.pyi', 'units.pyi', 'util.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Stubs Only",
      ]
)
