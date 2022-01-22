from setuptools import setup

name = "types-JACK-Client"
description = "Typing stubs for JACK-Client"
long_description = '''
## Typing stubs for JACK-Client

This is a PEP 561 type stub package for the `JACK-Client` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `JACK-Client`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/JACK-Client. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `46159aeca319775ad8616e4e47d4bdecce4cb978`.
'''.lstrip()

setup(name=name,
      version="0.5.4",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['jack-stubs'],
      package_data={'jack-stubs': ['__init__.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Stubs Only",
      ]
)
