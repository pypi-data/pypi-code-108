# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mat2py', 'mat2py.core']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.21.4,<2.0.0']

extras_require = \
{':python_version < "3.8"': ['importlib_metadata>=4.5.0,<5.0.0']}

setup_kwargs = {
    'name': 'mat2py',
    'version': '0.0.6',
    'description': 'mat2py mean to be drop-in replacement of Matlab by wrapping Numpy/Scipy/... packages.',
    'long_description': '# mat2py\n\n<div align="center">\n\n[![Build status](https://github.com/mat2py/mat2py/workflows/build/badge.svg?branch=master&event=push)](https://github.com/mat2py/mat2py/actions?query=workflow%3Abuild)\n[![Python Version](https://img.shields.io/pypi/pyversions/mat2py.svg)](https://pypi.org/project/mat2py/)\n[![Dependencies Status](https://img.shields.io/badge/dependencies-up%20to%20date-brightgreen.svg)](https://github.com/mat2py/mat2py/pulls?utf8=%E2%9C%93&q=is%3Apr%20author%3Aapp%2Fdependabot)\n\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)\n[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/mat2py/mat2py/blob/master/.pre-commit-config.yaml)\n[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/mat2py/mat2py/releases)\n[![License](https://img.shields.io/github/license/mat2py/mat2py)](https://github.com/mat2py/mat2py/blob/master/LICENSE)\n![Coverage Report](assets/images/coverage.svg)\n\nmat2py mean to be drop-in replacement of Matlab by wrapping Numpy/Scipy/... packages.\n\n</div>\n\n## First Steps\n\n### Installation\n\n```bash\npip install -U mat2py\n```\n\nor install with `Poetry`\n\n```bash\npoetry add mat2py\n```\n\n### Install fork of `miss_hit` for `mh_python` if needed\n```bash\ngit clone https://github.com/chaoqing/miss_hit\ncd miss_hit\npython3 setup_gpl.py install --user\npython3 setup_agpl.py install --user\ncd -\nrm -rf miss_hit\n```\n\n### Try the example `demo_fft`\n\n```bash\n# download the one already converted and formatted\nwget https://raw.githubusercontent.com/mat2py/mat2py/main/tests/test_example/demo_fft.py\n\n# or convert it yourself\necho "wget https://raw.githubusercontent.com/chaoqing/miss_hit/matlab2numpy/tests/mat2np/demo_fft.m"\necho "mh_python --python-alongside --format demo_fft.m"\n\n# run it...\npython3 demo_fft.py\n```\n\n## For Developer\n\n### Initialize your code\n\n1. Clone `mat2py`:\n\n```bash\ngit clone https://github.com/mat2py/mat2py \n```\n\n2. If you don\'t have `Poetry` installed run:\n\n```bash\nmake poetry-download\nsource ~/.poetry/env\n```\n\n3. Initialize poetry and install `pre-commit` hooks:\n\n```bash\nmake install\nmake pre-commit-install\n```\n\n4. Run the lint to check:\n\n```bash\nmake lint\n```\n\n## 📈 Releases\n\nYou can see the list of available releases on the [GitHub Releases](https://github.com/mat2py/mat2py/releases) page.\n\nWe follow [Semantic Versions](https://semver.org/) specification.\n\nWe use [`Release Drafter`](https://github.com/marketplace/actions/release-drafter). As pull requests are merged, a draft release is kept up-to-date listing the changes, ready to publish when you’re ready. With the categories option, you can categorize pull requests in release notes using labels.\n\n## 🛡 License\n\n[![License](https://img.shields.io/github/license/mat2py/mat2py)](https://github.com/mat2py/mat2py/blob/master/LICENSE)\n\nThis project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/mat2py/mat2py/blob/master/LICENSE) for more details.\n\n## 📃 Citation\n\n```bibtex\n@misc{mat2py,\n  author = {mat2py},\n  title = {mat2py mean to be drop-in replacement of Matlab by wrapping Numpy/Scipy/... packages.},\n  year = {2021},\n  publisher = {GitHub},\n  journal = {GitHub repository},\n  howpublished = {\\url{https://github.com/mat2py/mat2py}}\n}\n```\n\n## Credits [![🚀 Your next Python package needs a bleeding-edge project structure.](https://img.shields.io/badge/python--package--template-%F0%9F%9A%80-brightgreen)](https://github.com/TezRomacH/python-package-template)\n\n- This project was initially generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)\n- The Matlab to Python translator `mh_python` is developed under fork of [MISS HIT](https://github.com/florianschanda/miss_hit), a fantastic Matlab static analysis tool.\n',
    'author': 'mat2py',
    'author_email': 'chaoqingwang.nick@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mat2py/mat2py',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
