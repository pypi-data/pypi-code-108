# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['webex_skills',
 'webex_skills.api',
 'webex_skills.api.middlewares',
 'webex_skills.cli',
 'webex_skills.crypto',
 'webex_skills.dialogue',
 'webex_skills.models',
 'webex_skills.static']

package_data = \
{'': ['*'],
 'webex_skills.static': ['default_domains/greeting/exit/*',
                         'default_domains/greeting/greet/*']}

install_requires = \
['cryptography>=35.0.0,<36.0.0',
 'fastapi>=0.68.1,<0.69.0',
 'pydantic[dotenv]>=1.8.2,<2.0.0',
 'requests>=2.22.0,<3.0.0',
 'typer>=0.4.0,<0.5.0',
 'uvicorn>=0.15.0,<0.16.0']

extras_require = \
{'mindmeld': ['mindmeld>=4.4.0,<5.0.0']}

entry_points = \
{'console_scripts': ['webex-skills = webex_skills.cli:main']}

setup_kwargs = {
    'name': 'webex-skills',
    'version': '2.0.11',
    'description': 'An SDK for skills for the Webex Assistant.',
    'long_description': '# Webex Assistant Skills SDK\n\nThe Webex Skills SDK is designed to simplify the process of creating a Webex Assistant Skill. It provides some\ntools that help to easily set up a template skill, deal with encryption and test the skill locally, among other\nthings.\n\nThis is a simplified version of the documentation, for more information visit the official  \n[Webex Assistant Skills SDK website](https://developer.webex.com/docs/api/guides/webex-assistant-skills-guide).\n\n## Installing the SDK\n\nThis SDK supports `Python 3.7` and above. If you want to be able to build\n[MindMeld Skills](https://developer.webex.com/docs/api/guides/webex-assistant-skills-guide#building-a-mindmeld-skill),\nyou will need to use `Python 3.7` for compatibility with the [MindMeld library](https://www.mindmeld.com/).\n\n### Using pip\n\nCreate a virtual environment with `Python 3.7`:\n\n```python\npyenv install 3.7.5\npyenv virtualenv 3.7.5 webex-skills\npyenv local webex-skills\n```\n\nInstall using `pip`:\n\n```python\npip install webex-skills\n```\n\nIn order to build `MindMeld Skills` you need the `mindmeld` extra:\n\n```python\npip install \'webex-skills[mindmeld]\'\n```\n\n### Install from Source\n\nYou can install from source using `Poetry`. Set up python 3.7.5 locally:\n\n```python\npyenv install 3.7.5\npyenv local 3.7.5\n```\n\nNow you can run `Poetry`\'s `install` command:\n\n```python\npoetry install\n```\n\nIn order to build `MindMeld Skills` you need the `mindmeld` extra:\n\n```python\npoetry install --extras "mindmeld"\n```\n\n\n## Building Skills\n\nYou can follow the next guides for building your first skills:\n\n- [Simple Skills vs MindMeld Skills](https://developer.webex.com/docs/api/guides/webex-assistant-skills-guide#simple-skills-vs-mindmeld-skills)\n- [Building a Simple Skill](https://developer.webex.com/docs/api/guides/webex-assistant-skills-guide#building-a-simple-skill)\n- [Building a MindMeld Skill](https://developer.webex.com/docs/api/guides/webex-assistant-skills-guide#building-a-mindmeld-skill)\n',
    'author': 'James Snow',
    'author_email': 'jasnow@cisco.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cisco/webex-assistant-sdk',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
