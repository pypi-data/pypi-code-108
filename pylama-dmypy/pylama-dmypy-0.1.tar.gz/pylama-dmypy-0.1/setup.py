from pylama_dmypy import VERSION

from setuptools import setup

# fmt: off

setup(
      name = "pylama-dmypy"
    , version = VERSION
    , py_modules = ['pylama_dmypy']

    , extras_require =
      { 'tests':
        [ "pylama==8.3.7"
        , "mypy==0.931"
        ]
      }

    , entry_points =
      { 'pylama.linter': ['dmypy = pylama_dmypy.linter:Linter']
      }

    # metadata
    , url = "http://github.com/delfick/pylama-dmypy"
    , author = "Stephen Moore"
    , author_email = "stephen@delfick.com"
    , description = "Linting plugin for pylama to see dmypy"
    , long_description = open("README.rst").read()
    , license = "MIT"
    )

# fmt: on
