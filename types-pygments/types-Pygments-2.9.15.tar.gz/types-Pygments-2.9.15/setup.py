from setuptools import setup

name = "types-Pygments"
description = "Typing stubs for Pygments"
long_description = '''
## Typing stubs for Pygments

This is a PEP 561 type stub package for the `Pygments` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `Pygments`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/Pygments. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `de5ec6a0d14351797a54b12b3910534b67df609e`.
'''.lstrip()

setup(name=name,
      version="2.9.15",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      install_requires=['types-docutils', 'types-setuptools'],
      packages=['pygments-stubs'],
      package_data={'pygments-stubs': ['__init__.pyi', 'cmdline.pyi', 'console.pyi', 'filter.pyi', 'filters/__init__.pyi', 'formatter.pyi', 'formatters/__init__.pyi', 'formatters/_mapping.pyi', 'formatters/bbcode.pyi', 'formatters/html.pyi', 'formatters/img.pyi', 'formatters/irc.pyi', 'formatters/latex.pyi', 'formatters/other.pyi', 'formatters/pangomarkup.pyi', 'formatters/rtf.pyi', 'formatters/svg.pyi', 'formatters/terminal.pyi', 'formatters/terminal256.pyi', 'lexer.pyi', 'lexers/__init__.pyi', 'modeline.pyi', 'plugin.pyi', 'regexopt.pyi', 'scanner.pyi', 'sphinxext.pyi', 'style.pyi', 'styles/__init__.pyi', 'token.pyi', 'unistring.pyi', 'util.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Typing :: Stubs Only",
      ]
)
