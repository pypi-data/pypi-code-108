# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['alteia',
 'alteia.apis',
 'alteia.apis.client',
 'alteia.apis.client.analytics',
 'alteia.apis.client.annotations',
 'alteia.apis.client.auth',
 'alteia.apis.client.comments',
 'alteia.apis.client.datacapture',
 'alteia.apis.client.datamngt',
 'alteia.apis.client.externalproviders',
 'alteia.apis.client.featuresservice',
 'alteia.apis.client.projectmngt',
 'alteia.apis.client.tags',
 'alteia.core',
 'alteia.core.connection',
 'alteia.core.resources',
 'alteia.core.resources.analytics',
 'alteia.core.resources.datamngt',
 'alteia.core.resources.projectmngt',
 'alteia.core.utils',
 'alteia.core.utils.vertcrs']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4.3,<2.0.0',
 'pathvalidate>=2.3.0,<3.0.0',
 'semantic-version>=2.8.5,<3.0.0',
 'urllib3>=1.26,<2.0']

extras_require = \
{':python_version < "3.7"': ['importlib-resources>=1.4'],
 'documentation': ['sphinx>=4.1.2,<5.0.0',
                   'sphinx_autodoc_typehints>=1.12.0,<2.0.0',
                   'sphinx-autobuild>=2021.3.14,<2022.0.0',
                   'recommonmark>=0.7.1,<0.8.0']}

setup_kwargs = {
    'name': 'alteia',
    'version': '1.3.7',
    'description': 'High-level Python interface to Alteia API',
    'long_description': '<p align="center">\n<img src="https://raw.githubusercontent.com/alteia-ai/alteia-python-sdk/master/docs/images/SDK_Python.png" alt="logo" style="max-width:100%;">\n\n<p align="center">\n<a href="https://pypi.org/project/alteia/" rel="nofollow"><img src="https://img.shields.io/pypi/v/alteia.svg" alt="pypi version" style="max-width:100%;"></a>\n<a href="https://pypi.org/project/alteia/" rel="nofollow"><img src="https://img.shields.io/pypi/pyversions/alteia.svg" alt="compatible python versions" style="max-width:100%;"></a>\n</p>\n\n> This SDK offers a high-level Python interface to [Alteia APIs](https://www.alteia.com).\n\n## Installation\n\n```bash\npip install alteia\n```\n\n**requires Python >= 3.6.1*\n\n## Basic usage\n\n```python\nimport alteia\n\nsdk = alteia.SDK(user="YOUR_EMAIL_ADDRESS", password="YOUR_ALTEIA_PASSWORD")\n\nprojects = sdk.projects.search(name="*")\n\nfor project in projects:\n    print(project.name)\n\n# My awesome project\n```\n\n<p>&nbsp;</p>\n\n## 📕 Documentation\n\n- [Reference documentation](https://alteia.readthedocs.io/en/latest/index.html)\n- [Jupyter notebook tutorials](https://github.com/alteia-ai/tutorials)\n\n## Contributing\n\nPackage installation:\n\n```bash\npoetry install\n```\n\n(Optional) To install pre-commit hooks (and detect problems before the pipelines):\n\n```bash\npip install pre-commit\npre-commit install\npre-commit run --all-files\npre-commit autoupdate  # Optional, to update pre-commit versions\n```\n',
    'author': 'Alteia Backend team',
    'author_email': 'backend-team@alteia.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/alteia-ai/alteia-python-sdk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.1,<4.0.0',
}


setup(**setup_kwargs)
