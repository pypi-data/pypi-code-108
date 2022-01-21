# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['PyMemAPI', 'PyMemAPI.exception', 'PyMemAPI.schema', 'PyMemAPI.text2speech']

package_data = \
{'': ['*']}

install_requires = \
['bs4>=0.0,<0.1',
 'googletrans==4.0.0rc1',
 'memrise>=1.3.0,<2.0.0',
 'pandas>=1.3.5,<2.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'pyttsx3>=2.90,<3.0',
 'text2ipa>=1.3,<2.0']

setup_kwargs = {
    'name': 'pymemapi',
    'version': '0.1.0rc0',
    'description': 'Memrise API',
    'long_description': '# Memrise API\n\n<p align="center"><img src="https://github.com/josephquang97/pymemapi/actions/workflows/test.yml/badge.svg"><a href="https://codecov.io/github/josephquang97/memrise/commit/8abed823b295beb7ecda8b564df2b81905fb81ad"><img src = "https://codecov.io/gh/josephquang97/pymemapi/branch/main/graphs/badge.svg?branch=main"></a></p>\n\n## Installation\n\n```\npython -m pip install PyMemAPI\n```\n\n## Major Features\n\n- API Memrise with some actions such as create new level, add bulk, rename level, ...\n- Automaticially generate the audio and upload to Memrise\n- Automaticially translate, get the International Phonetics Alphabet from database and sync with Memrise\n\n## Documentations\n\nThe library have 3 main classes `Memrise`, `Course` and `SQLite`.\n\n### Memrise\n\nMemrise object will control your connection to Memrise. It\'s required your username and password to take permissions. And then it\'ll grant the necessary permission for the further process.\n\n```python\nclass Memrise:\n    username: str = field(init=False)\n    password: str = field(init=False)\n    session: requests.Session = requests.Session()\n\t\n\tdef login(self, username, password) -> bool: ...\n\tdef courses(self) -> List[Course]: ...\n\tdef get(self, path: str, params: Optional[Dict[str, Any]] = None): ...\n\tdef post(\n        self,\n        path: str,\n        payload: Dict[str, Any],\n        headers: Dict[str, str],\n        files: Optional[Dict[str, Tuple[str, bytes, str]]] = None,\n    ) -> requests.Response: ...\n\n    def select_course(self) -> Course: ...\n```\n\n### Course\n\n\n### SQLite\n\n\n',
    'author': 'Joseph Quang',
    'author_email': 'tquangsdh20@fsob.win',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/josephquang97/memrise',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
