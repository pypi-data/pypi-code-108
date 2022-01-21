# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['ops2deb']

package_data = \
{'': ['*']}

install_requires = \
['Jinja2>=3,<4',
 'PyYAML>=6,<7',
 'aiofiles>=0.1.9',
 'httpx>=0.20.0',
 'pydantic>=1,<2',
 'python-debian>=0.1.42',
 'ruamel.yaml>=0.17.16',
 'semver==3.0.0.dev3',
 'typer>=0.4.0']

extras_require = \
{'pyinstaller': ['pyinstaller']}

entry_points = \
{'console_scripts': ['ops2deb = ops2deb.cli:main']}

setup_kwargs = {
    'name': 'ops2deb',
    'version': '0.19.1',
    'description': 'Build debian packages',
    'long_description': "![cicd](https://github.com/upciti/ops2deb/actions/workflows/cicd.yml/badge.svg)\n[![codecov](https://codecov.io/gh/upciti/ops2deb/branch/main/graph/badge.svg)](https://codecov.io/gh/upciti/ops2deb)\n[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)\n[![Generic badge](https://img.shields.io/badge/type_checked-mypy-informational.svg)](https://mypy.readthedocs.io/en/stable/introduction.html)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)\n[![PyPI version shields.io](https://img.shields.io/pypi/v/ops2deb.svg)](https://pypi.python.org/pypi/ops2deb/)\n[![Downloads](https://static.pepy.tech/personalized-badge/ops2deb?period=total&units=international_system&left_color=blue&right_color=green&left_text=Downloads)](https://pepy.tech/project/ops2deb)\n\n# ops2deb\n\nAre you tired of checking if your favorite devops tools are up-to-date? Are you using a debian based GNU/Linux distribution?\n`ops2deb` is designed to generate Debian packages for common devops tools such as kubectl, kustomize, helm, ...,\nbut it could be used to package any statically linked application. In short, it consumes a configuration file and outputs `.deb` packages.\n\n## Configuration file\n\nWritten in YAML and composed of a single blueprint object or a list of blueprints objects. A blueprint is defined by the following:\n\n| Field         | Meaning                                                                                                                                     | Default |\n| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------- | ------- |\n| `name`        | Component name, e.g. `kustomize`.                                                                                                           |         |\n| `version`     | Application release to package.                                                                                                             |         |\n| `homepage`    | Upstream project homepage.                                                                                                                  | `None`  |\n| `arch`        | Package architecture.                                                                                                                       | `amd64` |\n| `revision`    | Package revistion.                                                                                                                          | `1`     |\n| `summary`     | Package short description.                                                                                                                  |         |\n| `description` | Package full description.                                                                                                                   |         |\n| `fetch`       | A binary to download, and a `sha256` checksum. `tar.gz`, `tar.xz`, `tar` and `zip` (requires `unzip`) archives are extracted automatically. | `Null`  |\n| `script`      | List of build instructions templated with jinja2 and intepreted with the default `shell`.                                                   | `[]`    |\n| `depends`     | List of package dependencies. Corresponds to `Depends` entry in `debian/control`.                                                           | `[]`    |\n| `recommends`  | List of package recommended dependencies. Corresponds to `Recommends` entry in `debian/control`.                                            | `[]`    |\n| `conflicts`   | List of conflicting packages. Corresponds to `Conflicts` entry in `debian/control`.                                                         | `[]`    |\n\nExample of a configuration file a single blueprint:\n\n```yaml\nname: kubectl\nversion: 1.20.1\nsummary: Command line client for controlling a Kubernetes cluster\ndescription: |\n  kubectl is a command line client for running commands against Kubernetes clusters.\nfetch:\n  url: https://storage.googleapis.com/kubernetes-release/release/v{{version}}/bin/linux/amd64/kubectl\n  sha256: 3f4b52a8072013e4cd34c9ea07e3c0c4e0350b227e00507fb1ae44a9adbf6785\nscript:\n  - mv kubectl {{src}}/usr/bin/\n```\n\n## Dependencies\n\n- Python >= 3.9\n- To build debian packages with `ops2deb build` you need the following packages on your host:\n\n```shell\nsudo apt install build-essential fakeroot debhelper\n```\n\n## Installation\n\n### With [wakemeops](https://docs.wakemeops.com)\n\n```shell\nsudo apt-get install ops2deb\n```\n\n### With [pipx](https://github.com/pipxproject/pipx)\n\n```shell\npipx install ops2deb\n```\n\n## Getting started\n\nIn a test directory run:\n\n```shell\ncurl https://raw.githubusercontent.com/upciti/ops2deb/main/ops2deb.yml\nops2deb generate\nops2deb build\n```\n\nTo check for new releases run:\n\n```shell\nops2deb update\n```\n\nThis command updates each blueprint in the `ops2deb.yml` configuration file with the latest version of\nthe upstream application (currently only works for applications using semantic versioning).\n\nBy default `ops2deb` caches downloaded content in `/tmp/ops2deb_cache`:\n\n```shell\ntree /tmp/ops2deb_cache\n```\n\nThe cache can be flushed with:\n\n```shell\nops2deb purge\n```\n\nFor more information about existing subcommands and options run `ops2deb --help`.\n\n## Usage examples\n\n### Creating a metapackage\n\nOps2deb can be used to create [metapackages](https://www.debian.org/blends/hamradio/get/metapackages):\n\n```yaml\nname: allthethings\nversion: 0.1.9\narch: all\nsummary: Install various devops tools\ndescription: Some great description.\ndepends:\n  - kubectl\n  - kustomize\n  - helm\n  - helmfile\n  - devspace\n```\n\n### Packaging ops2deb with ops2deb\n\nNote that when the fetch key is not used, ops2deb will run the build script from the directory where it was called.\nHence for the following blueprint to succeed, you have to run ops2deb from the root directory of this github project.\n\n```yaml\nname: ops2deb\nversion: 0.15.0\nhomepage: https://github.com/upciti/ops2deb\nsummary: Debian packaging tool for portable applications\ndescription: |-\n  Ops2deb is primarily designed to easily generate Debian packages for portable\n  applications such as single binary applications and scripts. Packages are\n  described using a simple configuration file format. Ops2deb can track new\n  releases of upstream applications and automatically bump application versions\n  in its configuration file.\nscript:\n  - poetry install -E pyinstaller\n  - poetry run task single_binary_application\n  - install -m 755 build/x86_64-unknown-linux-gnu/release/install/ops2deb {{src}}/usr/bin/\n```\n\n## Development\n\nYou will need [poetry](https://python-poetry.org/), and probably [pyenv](https://github.com/pyenv/pyenv) if you don't have python 3.9 on your host.\n\n```shell\npoetry install\n```\n\nTo run ops2deb test suite run:\n\n```shell\npoetry run task check\n```\n\nTo build a python wheel:\n\n```shell\npoetry run poetry build\n```\n\nNote that the `poetry run` is important to enable [poetry-dynamic-versioning](https://github.com/mtkennerly/poetry-dynamic-versioning)\nwhich is installed as a dev dependency.\n\nTo build a single binary applicatin:\n\nInstall required build dependencies:\n\n```shell\nsudo apt install binutils python3-dev\npoetry install -E pyinstaller\n```\n\nAnd run:\n\n```shell\npoetry run task single_binary_application\n```\n\n## Important notes\n\n`ops2deb` **DOES NOT** sandbox build instructions so if you do something like:\n\n```shell\nscript:\n- rm -rf ~/*\n```\n\nYou will loose your files... To make sure that you won't mess with your system, run it within a container.\n",
    'author': 'Upciti',
    'author_email': 'support@upciti.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/upciti/ops2deb',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
