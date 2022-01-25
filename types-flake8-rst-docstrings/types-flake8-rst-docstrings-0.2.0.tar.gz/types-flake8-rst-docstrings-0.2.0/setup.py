from setuptools import setup

name = "types-flake8-rst-docstrings"
description = "Typing stubs for flake8-rst-docstrings"
long_description = '''
## Typing stubs for flake8-rst-docstrings

This is a PEP 561 type stub package for the `flake8-rst-docstrings` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `flake8-rst-docstrings`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/flake8-rst-docstrings. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `7bc9c1625eb0df0500e70de96f3e1a698bb8c05a`.
'''.lstrip()

setup(name=name,
      version="0.2.0",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=[],
      packages=['flake8_rst_docstrings-stubs'],
      package_data={'flake8_rst_docstrings-stubs': ['__init__.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Stubs Only",
      ]
)
