# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cyclonedx_py',
 'cyclonedx_py.exception',
 'cyclonedx_py.parser',
 'cyclonedx_py.utils']

package_data = \
{'': ['*']}

install_requires = \
['cyclonedx-python-lib>=1.3.0,<2.0.0']

entry_points = \
{'console_scripts': ['cyclonedx-bom = cyclonedx_py.client:main',
                     'cyclonedx-py = cyclonedx_py.client:main']}

setup_kwargs = {
    'name': 'cyclonedx-bom',
    'version': '2.0.1',
    'description': 'CycloneDX Software Bill of Materials (SBOM) generation utility',
    'long_description': '# CycloneDX Python SBOM Generation Tool\n\n[![shield_gh-workflow-test]][link_gh-workflow-test]\n[![shield_pypi-version]][link_pypi]\n[![shield_docker-version]][link_docker]\n[![shield_license]][license_file]  \n[![shield_website]][link_website]\n[![shield_slack]][link_slack]\n[![shield_groups]][link_discussion]\n[![shield_twitter-follow]][link_twitter]\n\n----\n\nThis project provides a runnable Python-based application for generating CycloneDX bill-of-material documents from either:\n\n* Your current Python Environment\n* Your project\'s manifest (e.g. `Pipfile.lock`, `poetry.lock` or `requirements.txt`)\n* Conda as a Package Manager\n\nThe BOM will contain an aggregate of all your current project\'s dependencies, or those defined by the manifest you supply.\n\nCycloneDX is a lightweight BOM specification that is easily created, human-readable, and simple to parse.\n\n## Installation\n\nInstall this from [PyPi.org][link_pypi] using your preferred Python package manager.\n\nExample using `pip`:\n\n```shell\npip install cyclonedx-bom\n```\n\nExample using `poetry`:\n\n```shell\npoetry add cyclonedx-bom\n```\n\n## Usage\n\nOnce installed, you can access the full documentation by running `--help`:\n\n```text\n$ cyclonedx-bom --help\nusage: cyclonedx-bom [-h] (-c | -cj | -e | -p | -pip | -r) [-i FILE_PATH]\n                 [--format {json,xml}] [--schema-version {1.3,1.2,1.1,1.0}]\n                 [-o FILE_PATH] [-F] [-X]\n\nCycloneDX SBOM Generator\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -c, --conda           Build a SBOM based on the output from `conda list\n                        --explicit` or `conda list --explicit --md5`\n  -cj, --conda-json     Build a SBOM based on the output from `conda list\n                        --json`\n  -e, --e, --environment\n                        Build a SBOM based on the packages installed in your\n                        current Python environment (default)\n  -p, --p, --poetry     Build a SBOM based on a Poetry poetry.lock\'s contents.\n                        Use with -i to specify absolute pathto a `poetry.lock`\n                        you wish to use, else we\'ll look for one in the\n                        current working directory.\n  -pip, --pip           Build a SBOM based on a PipEnv Pipfile.lock\'s\n                        contents. Use with -i to specify absolute pathto a\n                        `Pipefile.lock` you wish to use, else we\'ll look for\n                        one in the current working directory.\n  -r, --r, --requirements\n                        Build a SBOM based on a requirements.txt\'s contents.\n                        Use with -i to specify absolute pathto a\n                        `requirements.txt` you wish to use, else we\'ll look\n                        for one in the current working directory.\n  -X                    Enable debug output\n\nInput Method:\n  Flags to determine how `cyclonedx-bom` obtains it\'s input\n\n  -i FILE_PATH, --in-file FILE_PATH\n                        File to read input from, or STDIN if not specified\n\nSBOM Output Configuration:\n  Choose the output format and schema version\n\n  --format {json,xml}   The output format for your SBOM (default: xml)\n  --schema-version {1.3,1.2,1.1,1.0}\n                        The CycloneDX schema version for your SBOM (default:\n                        1.3)\n  -o FILE_PATH, --o FILE_PATH, --output FILE_PATH\n                        Output file path for your SBOM (set to \'-\' to output\n                        to STDOUT)\n  -F, --force           If outputting to a file and the stated file already\n                        exists, it will be overwritten.\n```\n\n\n\n## Python Support\n\nWe endeavour to support all functionality for all [current actively supported Python versions](https://www.python.org/downloads/).\nHowever, some features may not be possible/present in older Python versions due to their lack of support.\n\n## Contributing\n\nFeel free to open issues, bugreports or pull requests.  \nSee the [CONTRIBUTING][contributing_file] file for details.\n\n## Copyright & License\n\nCycloneDX BOM is Copyright (c) OWASP Foundation. All Rights Reserved.  \nPermission to modify and redistribute is granted under the terms of the Apache 2.0 license.  \nSee the [LICENSE][license_file] file for the full license.\n\n[license_file]: https://github.com/CycloneDX/cyclonedx-python/blob/master/LICENSE\n[contributing_file]: https://github.com/CycloneDX/cyclonedx-python/blob/master/CONTRIBUTING.md\n\n[shield_gh-workflow-test]: https://img.shields.io/github/workflow/status/CycloneDX/cyclonedx-python/Python%20CI/master?logo=GitHub&logoColor=white "build"\n[shield_pypi-version]: https://img.shields.io/pypi/v/cyclonedx-bom?logo=Python&logoColor=white&label=PyPI "PyPI"\n[shield_docker-version]: https://img.shields.io/docker/v/cyclonedx/cyclonedx-python?logo=docker&logoColor=white&label=docker "docker"\n[shield_license]: https://img.shields.io/github/license/CycloneDX/cyclonedx-python "license"\n[shield_website]: https://img.shields.io/badge/https://-cyclonedx.org-blue.svg "homepage"\n[shield_slack]: https://img.shields.io/badge/slack-join-blue?logo=Slack&logoColor=white "slack join"\n[shield_groups]: https://img.shields.io/badge/discussion-groups.io-blue.svg "groups discussion"\n[shield_twitter-follow]: https://img.shields.io/badge/Twitter-follow-blue?logo=Twitter&logoColor=white "twitter follow"\n[link_gh-workflow-test]: https://github.com/CycloneDX/cyclonedx-python/actions/workflows/python.yml?query=branch%3Amaster\n[link_pypi]: https://pypi.org/project/cyclonedx-bom/\n[link_docker]: https://hub.docker.com/r/cyclonedx/cyclonedx-python\n[link_website]: https://cyclonedx.org/\n[link_slack]: https://cyclonedx.org/slack/invite\n[link_discussion]: https://groups.io/g/CycloneDX\n[link_twitter]: https://twitter.com/CycloneDX_Spec\n',
    'author': 'Steven Springett',
    'author_email': 'steve.springett@owasp.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/CycloneDX/cyclonedx-python',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
