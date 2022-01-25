from setuptools import setup

name = "types-pep8-naming"
description = "Typing stubs for pep8-naming"
long_description = '''
## Typing stubs for pep8-naming

This is a PEP 561 type stub package for the `pep8-naming` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `pep8-naming`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/pep8-naming. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `7bc9c1625eb0df0500e70de96f3e1a698bb8c05a`.
'''.lstrip()

setup(name=name,
      version="0.12.0",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['pep8ext_naming-stubs'],
      package_data={'pep8ext_naming-stubs': ['__init__.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Stubs Only",
      ]
)
