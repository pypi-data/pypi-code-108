# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mypy_boto3_builder',
 'mypy_boto3_builder.enums',
 'mypy_boto3_builder.import_helpers',
 'mypy_boto3_builder.parsers',
 'mypy_boto3_builder.parsers.docstring_parser',
 'mypy_boto3_builder.structures',
 'mypy_boto3_builder.type_annotations',
 'mypy_boto3_builder.type_maps',
 'mypy_boto3_builder.utils',
 'mypy_boto3_builder.writers']

package_data = \
{'': ['*'],
 'mypy_boto3_builder': ['boto3_stubs_static/*',
                        'boto3_stubs_static/docs/*',
                        'boto3_stubs_static/dynamodb/*',
                        'boto3_stubs_static/ec2/*',
                        'boto3_stubs_static/resources/*',
                        'boto3_stubs_static/s3/*',
                        'botocore_stubs_static/*',
                        'botocore_stubs_static/retries/*',
                        'templates/boto3-stubs/*',
                        'templates/boto3-stubs/boto3-stubs/*',
                        'templates/boto3_stubs_docs/*',
                        'templates/botocore-stubs/*',
                        'templates/botocore-stubs/botocore-stubs/*',
                        'templates/common/*',
                        'templates/master/*',
                        'templates/master/master/*',
                        'templates/service/*',
                        'templates/service/service/*',
                        'templates/service_docs/*']}

install_requires = \
['black>=21.12b0,<22.0',
 'boto3',
 'isort>=5.10.1,<6.0.0',
 'jinja2>=3.0.1,<4.0.0',
 'mdformat>=0.7.9,<0.8.0',
 'newversion>=1.8.2,<2.0.0',
 'pip',
 'pyparsing>=3.0.5,<4.0.0',
 'requests>=2.26.0,<3.0.0']

entry_points = \
{'console_scripts': ['mypy_boto3_builder = mypy_boto3_builder.main:main']}

setup_kwargs = {
    'name': 'mypy-boto3-builder',
    'version': '6.4.0',
    'description': 'Builder for boto3-stubs',
    'long_description': "# mypy_boto3_builder\n\n[![Open in Visual Studio Code](https://open.vscode.dev/badges/open-in-vscode.svg)](https://open.vscode.dev/vemel/mypy_boto3_builder)\n\n[![PyPI - mypy-boto3-builder](https://img.shields.io/pypi/v/mypy-boto3-builder.svg?color=blue&label=mypy-boto3-builder)](https://pypi.org/project/mypy-boto3-builder)\n[![PyPI - boto3-stubs](https://img.shields.io/pypi/v/boto3-stubs.svg?color=blue&label=boto3-stubs)](https://pypi.org/project/boto3-stubs)\n[![PyPI - boto3](https://img.shields.io/pypi/v/boto3.svg?color=blue&label=boto3)](https://pypi.org/project/boto3)\n\n[![Docs](https://img.shields.io/readthedocs/mypy-boto3-builder.svg?color=blue&label=boto3-stubs%20docs)](https://vemel.github.io/boto3_stubs_docs/)\n[![Docs](https://img.shields.io/readthedocs/mypy-boto3-builder.svg?color=blue&label=Builder%20docs)](https://mypy-boto3-builder.readthedocs.io/)\n\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/boto3-stubs.svg?color=blue)](https://pypi.org/project/boto3-stubs)\n[![PyPI - Downloads](https://img.shields.io/pypi/dm/boto3-stubs?color=blue)](https://pypistats.org/packages/boto3-stubs)\n\n![boto3.typed](https://raw.githubusercontent.com/vemel/mypy_boto3_builder/master/logo.png)\n\nType annotations builder for [boto3-stubs](https://pypi.org/project/boto3-stubs/) project. Compatible with\n[VSCode](https://code.visualstudio.com/),\n[PyCharm](https://www.jetbrains.com/pycharm/),\n[Emacs](https://www.gnu.org/software/emacs/),\n[Sublime Text](https://www.sublimetext.com/),\n[mypy](https://github.com/python/mypy),\n[pyright](https://github.com/microsoft/pyright)\nand other tools.\n\nSee how it helps to find and fix potential bugs:\n\n![boto3-stubs demo](https://raw.githubusercontent.com/vemel/mypy_boto3_builder/master/demo.gif)\n\nDo you want more? Check the [documentation](https://vemel.github.io/boto3_stubs_docs/) and use `boto3` like a pro!\n\n- [mypy_boto3_builder](#mypy_boto3_builder)\n  - [Using boto3-stubs](#using-boto3-stubs)\n  - [How to build type annotations](#how-to-build-type-annotations)\n    - [Locally](#locally)\n    - [With Docker image](#with-docker-image)\n  - [Development](#development)\n  - [Versioning](#versioning)\n  - [Latest changes](#latest-changes)\n  - [Thank you](#thank-you)\n    - [Toolset](#toolset)\n    - [Contributors](#contributors)\n\n## Using boto3-stubs\n\nCheck [boto3-stubs](https://pypi.org/project/boto3-stubs/) project for installation\nand usage instructions.\n\nIf you use VSCode, add [AWS Boto3](https://marketplace.visualstudio.com/items?itemName=Boto3typed.boto3-ide)\nextension to your VSCode and run `AWS boto3: Quick Start` command.\n\nIf not, just install `boto3-stubs` with `pip`:\n\n```bash\npython -m pip install 'boto3-stubs[all]'\n\n# do not forget to install mypy or pyright\n```\n\nAnd you should already have auto-complete and type checking in your IDE! You can stop reading now.\n\nTHe rest of this document is about building `boto3-stubs` manually. For example, if you want to\nuse the latest features for an older `boto3` version.\n\n## How to build type annotations\n\n### Locally\n\n```bash\n# Install preferred version of `boto3`\npython -m pip install boto3==1.16.25 botocore==1.19.25\n\n# Install `mypy-boto3-builder`\npython -m pip install mypy-boto3-builder\n\n# Build all packages in mypy_boto3_output directory\npython -m mypy_boto3_builder mypy_boto3_output\n\n# Or specify required services explicitly\npython -m mypy_boto3_builder mypy_boto3_output -s ec2 s3\n\n# Install custom `boto3-stubs` packages\ncd mypy_boto3_output\npython -m pip install -e ./mypy_boto3_ec2_package\npython -m pip install -e ./mypy_boto3_s3_package\npython -m pip install -e ./boto3_stubs_package\n```\n\n### With Docker image\n\n- Install [Docker](https://docs.docker.com/install/)\n- Pull latest `mypy_boto3_builder` version and tag it\n\n```bash\ndocker pull docker.pkg.github.com/vemel/mypy_boto3_builder/mypy_boto3_builder_stable:latest\ndocker tag docker.pkg.github.com/vemel/mypy_boto3_builder/mypy_boto3_builder_stable:latest mypy_boto3_builder\n```\n\n- Generate stubs in `output` directory\n\n```bash\nmkdir output\n\n# generate stubs for all services\ndocker run -v `pwd`/output:/output -ti mypy_boto3_builder_stable\n\n# generate stubs for s3 service\ndocker run -v `pwd`/output:/output -ti mypy_boto3_builder_stable -s s3\n\n# generate stubs for a specific boto3 version\ndocker run -e BOTO3_VERSION=1.16.25 BOTOCORE_VERSION=1.19.25 -v `pwd`/output:/output -ti mypy_boto3_builder_stable\n```\n\n- Install packages from `output` directory as described above\n\n## Development\n\n- Install Python 3.10+, ideally with [pyenv](https://github.com/pyenv/pyenv)\n- Install [poetry](https://python-poetry.org/): `pip install poetry`\n- Install dependencies: `poetry install`\n- Use scripts for repo to check if everything works: `./scripts/build.sh`\n- Run manual pre-commit: `./scripts/before_commit.sh`\n\n## Versioning\n\n`mypy_boto3_builder` version is not related to `boto3` version and follows\n[PEP 440](https://www.python.org/dev/peps/pep-0440/).\n\n## Latest changes\n\nFull changelog can be found in [Releases](https://github.com/vemel/mypy_boto3_builder/releases).\n\n## Thank you\n\n### Toolset\n\n- [black](https://github.com/psf/black) developers for an awesome formatting tool\n- [Timothy Edmund Crosley](https://github.com/timothycrosley) for\n  [isort](https://github.com/PyCQA/isort) and how flexible it is\n- [mypy](https://github.com/python/mypy) developers for doing all dirty work for us\n- [pyright](https://github.com/microsoft/pyright) team for the new era of typed Python\n\n### Contributors\n\n- [Allie Fitter](https://github.com/alliefitter), author of original\n  [boto3-type-annotations](https://pypi.org/project/boto3-type-annotations/)\n- [jbpratt](https://github.com/jbpratt)\n- [Chris Hollinworth](https://github.com/chrishollinworth)\n- [Yoan Blanc](https://github.com/greut)\n- [Kostya Leschenko](https://github.com/kleschenko)\n- [pyto86](https://github.com/pyto86pri)\n- [Ashton Honnecke](https://github.com/ahonnecke)\n- [Mike Carey](https://github.com/mike-carey)\n- [Ole-Martin Bratteng](https://github.com/omBratteng)\n- [Nikhil Benesch](https://github.com/benesch)\n",
    'author': 'Vlad Emelianov',
    'author_email': 'vlad.emelianov.nz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://vemel.github.io/mypy_boto3_builder/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
