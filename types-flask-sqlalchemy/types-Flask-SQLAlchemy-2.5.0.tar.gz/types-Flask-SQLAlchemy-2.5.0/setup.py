from setuptools import setup

name = "types-Flask-SQLAlchemy"
description = "Typing stubs for Flask-SQLAlchemy"
long_description = '''
## Typing stubs for Flask-SQLAlchemy

This is a PEP 561 type stub package for the `Flask-SQLAlchemy` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `Flask-SQLAlchemy`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/Flask-SQLAlchemy. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `3a22bf2411c7357bffb2fe1dc675486a8da97177`.
'''.lstrip()

setup(name=name,
      version="2.5.0",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['flask_sqlalchemy-stubs'],
      package_data={'flask_sqlalchemy-stubs': ['__init__.pyi', 'model.pyi', 'utils.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Stubs Only",
      ]
)
