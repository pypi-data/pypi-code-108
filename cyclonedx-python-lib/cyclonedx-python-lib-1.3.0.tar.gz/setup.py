# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cyclonedx',
 'cyclonedx.exception',
 'cyclonedx.model',
 'cyclonedx.output',
 'cyclonedx.output.serializer',
 'cyclonedx.parser']

package_data = \
{'': ['*'], 'cyclonedx': ['schema/*', 'schema/ext/*']}

install_requires = \
['packageurl-python>=0.9',
 'setuptools>=47.0.0',
 'toml>=0.10.0,<0.11.0',
 'types-setuptools>=57.0.0',
 'types-toml>=0.10.0,<0.11.0']

extras_require = \
{':python_version < "3.8"': ['importlib-metadata>=3.4',
                             'typing-extensions>=3.10,<4.0']}

setup_kwargs = {
    'name': 'cyclonedx-python-lib',
    'version': '1.3.0',
    'description': 'A library for producing CycloneDX SBOM (Software Bill of Materials) files.',
    'long_description': '# Python Library for generating CycloneDX\n\n[![shield_gh-workflow-test]][link_gh-workflow-test]\n[![shield_pypi-version]][link_pypi]\n[![shield_conda-forge-version]][link_conda-forge]\n[![shield_license]][license_file]  \n[![shield_website]][link_website]\n[![shield_slack]][link_slack]\n[![shield_groups]][link_discussion]\n[![shield_twitter-follow]][link_twitter]\n\n----\n\nThis CycloneDX module for Python can generate valid CycloneDX bill-of-material document containing an aggregate of all\nproject dependencies.\n\nThis module is not designed for standalone use.  \nIf you\'re looking for a CycloneDX tool to run to generate (SBOM) software bill-of-materials documents, why not checkout: [CycloneDX Python][cyclonedx-python]\n\nAdditionally, the following tool can be used as well (and this library was written to help improve it) [Jake][jake].\n\nAdditionally, you can use this module yourself in your application to programmatically generate SBOMs.\n\nCycloneDX is a lightweight BOM specification that is easily created, human-readable, and simple to parse.\n\nView our documentation [here](https://cyclonedx-python-library.readthedocs.io/).\n\n## Python Support\n\nWe endeavour to support all functionality for all [current actively supported Python versions](https://www.python.org/downloads/).\nHowever, some features may not be possible/present in older Python versions due to their lack of support.\n\n## Changelog\n\nSee our [CHANGELOG][chaneglog_file].\n\n## Contributing\n\nFeel free to open issues, bugreports or pull requests.  \nSee the [CONTRIBUTING][contributing_file] file for details.\n\n## Copyright & License\n\nCycloneDX Python Lib is Copyright (c) OWASP Foundation. All Rights Reserved.  \nPermission to modify and redistribute is granted under the terms of the Apache 2.0 license.  \nSee the [LICENSE][license_file] file for the full license.\n\n[cyclonedx-python]: https://github.com/CycloneDX/cyclonedx-python\n[jake]: https://github.com/sonatype-nexus-community/jake\n\n[license_file]: https://github.com/CycloneDX/cyclonedx-python-lib/blob/master/LICENSE\n[chaneglog_file]: https://github.com/CycloneDX/cyclonedx-python-lib/blob/master/CHANGELOG.md\n[contributing_file]: https://github.com/CycloneDX/cyclonedx-python-lib/blob/master/CONTRIBUTING.md\n\n[shield_gh-workflow-test]: https://img.shields.io/github/workflow/status/CycloneDX/cyclonedx-python-lib/Python%20CI/main?logo=GitHub&logoColor=white "build"\n[shield_pypi-version]: https://img.shields.io/pypi/v/cyclonedx-python-lib?logo=pypi&logoColor=white&label=PyPI "PyPI"\n[shield_conda-forge-version]: https://img.shields.io/conda/vn/conda-forge/cyclonedx-python-lib?logo=anaconda&logoColor=white&label=conda-forge "conda-forge"\n[shield_license]: https://img.shields.io/github/license/CycloneDX/cyclonedx-python-lib "license"\n[shield_website]: https://img.shields.io/badge/https://-cyclonedx.org-blue.svg "homepage"\n[shield_slack]: https://img.shields.io/badge/slack-join-blue?logo=Slack&logoColor=white "slack join"\n[shield_groups]: https://img.shields.io/badge/discussion-groups.io-blue.svg "groups discussion"\n[shield_twitter-follow]: https://img.shields.io/badge/Twitter-follow-blue?logo=Twitter&logoColor=white "twitter follow"\n[link_gh-workflow-test]: https://github.com/CycloneDX/cyclonedx-python-lib/actions/workflows/poetry.yml?query=branch%3Amain\n[link_pypi]: https://pypi.org/project/cyclonedx-python-lib/\n[link_conda-forge]: https://anaconda.org/conda-forge/cyclonedx-python-lib\n[link_website]: https://cyclonedx.org/\n[link_slack]: https://cyclonedx.org/slack/invite\n[link_discussion]: https://groups.io/g/CycloneDX\n[link_twitter]: https://twitter.com/CycloneDX_Spec\n\n[PEP-508]: https://www.python.org/dev/peps/pep-0508/\n',
    'author': 'Paul Horton',
    'author_email': 'phorton@sonatype.com',
    'maintainer': 'Paul Horton',
    'maintainer_email': 'phorton@sonatype.com',
    'url': 'https://github.com/CycloneDX/cyclonedx-python-lib',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
