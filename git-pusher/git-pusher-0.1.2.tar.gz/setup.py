# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['git_pusher']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.26,<4.0.0', 'pyfiglet>=0.8.post1,<0.9']

entry_points = \
{'console_scripts': ['git-pusher = git_pusher:main']}

setup_kwargs = {
    'name': 'git-pusher',
    'version': '0.1.2',
    'description': 'Push files in multiple git repos in one go',
    'long_description': '[![Contributors][contributors-shield]][contributors-url]\n[![Forks][forks-shield]][forks-url]\n[![Stargazers][stars-shield]][stars-url]\n[![Issues][issues-shield]][issues-url]\n[![GPL3 License][license-shield]][license-url]\n[![LinkedIn][linkedin-shield]][linkedin-url]\n[![Ask Me Anything][ask-me-anything]][personal-page]\n\n<!-- PROJECT LOGO -->\n<br />\n<p align="center">\n  <a href="https://github.com/stiliajohny/python-git-pusher">\n    <img src="https://raw.githubusercontent.com/stiliajohny/python-git-pusher/master/.assets/logo.png" alt="Main Logo" width="80" height="80">\n  </a>\n\n  <h3 align="center">python-git-pusher</h3>\n\n  <p align="center">\n    Push files to multiple repos in one go\n    <br />\n    <a href="./README.md"><strong>Explore the docs »</strong></a>\n    <br />\n    <br />\n    <a href="https://github.com/stiliajohny/python-git-pusher/issues/new?labels=i%3A+bug&template=1-bug-report.md">Report Bug</a>\n    ·\n    <a href="https://github.com/stiliajohny/python-git-pusher/issues/new?labels=i%3A+enhancement&template=2-feature-request.md">Request Feature</a>\n  </p>\n</p>\n\n<!-- TABLE OF CONTENTS -->\n\n## Table of Contents\n\n- [Table of Contents](#table-of-contents)\n- [About The Project](#about-the-project)\n  - [Built With](#built-with)\n- [Getting Started](#getting-started)\n  - [Prerequisites](#prerequisites)\n  - [Installation](#installation)\n- [Usage](#usage)\n- [Roadmap](#roadmap)\n- [Contributing](#contributing)\n- [License](#license)\n- [Contact](#contact)\n- [Acknowledgements](#acknowledgements)\n\n<!-- ABOUT THE PROJECT -->\n\n## About The Project\n\nThis project is created out of neccessity to push multiple files into multiple git repos at once.\nFor example push a LICENSE or ISSUE TEMPLATE or Update a Github Action. This project is not limited to this.\n\n### Built With\n\n- Python\n- GIT\n- Poetry\n\n---\n\n<!-- GETTING STARTED -->\n\n## Getting Started\n\n### Prerequisites\n\n- Install Python 3.6 or higher\n\n### Installation\n\n- Install the tool via `pip3 install git-pusher`\n\n---\n\n<!-- USAGE EXAMPLES -->\n\n## Usage\n\n- Create a file that includes all the repos you want to push to\n- Run the tool with `git-pusher --repos <file> --files <file>`\n\n---\n\n<!-- ROADMAP -->\n\n## Roadmap\n\nSee the [open issues](https://github.com/stiliajohny/python-git-pusher/issues) for a list of proposed features (and known issues).\n\n---\n\n<!-- CONTRIBUTING -->\n\n## Contributing\n\nContributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.\n\n1. Fork the Project\n2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)\n3. Commit your Changes (`git commit -m \'Add some AmazingFeature\'`)\n4. Push to the Branch (`git push origin feature/AmazingFeature`)\n5. Open a Pull Request\n\n---\n\n<!-- LICENSE -->\n\n## License\n\nDistributed under the GPLv3 License. See `LICENSE` for more information.\n\n<!-- CONTACT -->\n\n## Contact\n\nJohn Stilia - stilia.johny@gmail.com\n\n<!--\nProject Link: [https://github.com/your_username/repo_name](https://github.com/your_username/repo_name)\n-->\n\n---\n\n<!-- ACKNOWLEDGEMENTS -->\n\n## Acknowledgements\n\n- [GitHub Emoji Cheat Sheet](https://www.webpagefx.com/tools/emoji-cheat-sheet)\n- [Img Shields](https://shields.io)\n- [Choose an Open Source License](https://choosealicense.com)\n- [GitHub Pages](https://pages.github.com)\n\n<!-- MARKDOWN LINKS & IMAGES -->\n<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->\n\n[contributors-shield]: https://img.shields.io/github/contributors/stiliajohny/python-git-pusher.svg?style=for-the-badge\n[contributors-url]: https://github.com/stiliajohny/python-git-pusher/graphs/contributors\n[forks-shield]: https://img.shields.io/github/forks/stiliajohny/python-git-pusher.svg?style=for-the-badge\n[forks-url]: https://github.com/stiliajohny/python-git-pusher/network/members\n[stars-shield]: https://img.shields.io/github/stars/stiliajohny/python-git-pusher.svg?style=for-the-badge\n[stars-url]: https://github.com/stiliajohny/python-git-pusher/stargazers\n[issues-shield]: https://img.shields.io/github/issues/stiliajohny/python-git-pusher.svg?style=for-the-badge\n[issues-url]: https://github.com/stiliajohny/python-git-pusher/issues\n[license-shield]: https://img.shields.io/github/license/stiliajohny/python-git-pusher?style=for-the-badge\n[license-url]: https://github.com/stiliajohny/python-git-pusher/blob/master/LICENSE.txt\n[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555\n[linkedin-url]: https://linkedin.com/in/johnstilia/\n[product-screenshot]: .assets/screenshot.png\n[ask-me-anything]: https://img.shields.io/badge/Ask%20me-anything-1abc9c.svg?style=for-the-badge\n[personal-page]: https://github.com/stiliajohny\n',
    'author': 'John Stilia',
    'author_email': 'stilia.johny@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://stiliajohny.github.io/python-git-pusher ',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
