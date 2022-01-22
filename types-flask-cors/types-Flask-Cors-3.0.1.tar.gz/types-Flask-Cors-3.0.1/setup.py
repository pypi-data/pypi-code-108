from setuptools import setup

name = "types-Flask-Cors"
description = "Typing stubs for Flask-Cors"
long_description = '''
## Typing stubs for Flask-Cors

This is a PEP 561 type stub package for the `Flask-Cors` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `Flask-Cors`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/Flask-Cors. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `de5ec6a0d14351797a54b12b3910534b67df609e`.
'''.lstrip()

setup(name=name,
      version="3.0.1",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['flask_cors-stubs'],
      package_data={'flask_cors-stubs': ['__init__.pyi', 'core.pyi', 'decorator.pyi', 'extension.pyi', 'version.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Stubs Only",
      ]
)
