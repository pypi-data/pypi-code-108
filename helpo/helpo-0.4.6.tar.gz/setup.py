# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['helpo']

package_data = \
{'': ['*']}

install_requires = \
['atlassian-python-api>=3.10.0,<4.0.0',
 'cloudflare>=2.8.15,<3.0.0',
 'hvac>=0.11.2,<0.12.0',
 'jsonmerge>=1.8.0,<2.0.0',
 'loguru>=0.5.3,<0.6.0',
 'minio>=7.0.3,<8.0.0',
 'namecom>=0.5.0,<0.6.0',
 'packaging>=21.3,<22.0',
 'requests>=2.25.1,<3.0.0',
 'slumber>=0.7.1,<0.8.0',
 'tenacity>=8.0.1,<9.0.0',
 'tldextract>=3.1.2,<4.0.0',
 'typer>=0.4.0,<0.5.0',
 'zxpy>=1.2.2,<2.0.0']

entry_points = \
{'console_scripts': ['helpo = helpo.main:app']}

setup_kwargs = {
    'name': 'helpo',
    'version': '0.4.6',
    'description': 'zg helper cli scripts',
    'long_description': '<!-- ABOUT THE PROJECT -->\n## About The Project\n\nHere\'s a blank template to get started: To avoid retyping too much info. Do a search and replace with your text editor for the following: `github_username`, `repo_name`, `twitter_handle`, `linkedin_username`, `email`, `email_client`, `project_title`, `project_description`\n\n### Built With\n\n* [Next.js](https://nextjs.org/)\n* [React.js](https://reactjs.org/)\n* [Vue.js](https://vuejs.org/)\n* [Angular](https://angular.io/)\n* [Svelte](https://svelte.dev/)\n* [Laravel](https://laravel.com)\n* [Bootstrap](https://getbootstrap.com)\n* [JQuery](https://jquery.com)\n\n## Getting Started\n\nThis is an example of how you may give instructions on setting up your project locally.\nTo get a local copy up and running follow these simple example steps.\n\n### Prerequisites\n\nThis is an example of how to list things you need to use the software and how to install them.\n* npm\n  ```sh\n  npm install npm@latest -g\n  ```\n\n### Installation\n\n1. Get a free API Key at [https://example.com](https://example.com)\n2. Clone the repo\n   ```sh\n   git clone https://github.com/github_username/repo_name.git\n   ```\n3. Install NPM packages\n   ```sh\n   npm install\n   ```\n4. Enter your API in `config.js`\n   ```js\n   const API_KEY = \'ENTER YOUR API\';\n   ```\n\n<!-- USAGE EXAMPLES -->\n## Usage\n\nUse this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.\n\n_For more examples, please refer to the [Documentation](https://example.com)_\n\n<!-- ROADMAP -->\n## Roadmap\n\n- [] Feature 1\n- [] Feature 2\n- [] Feature 3\n    - [] Nested Feature\n\nSee the [open issues](https://github.com/github_username/repo_name/issues) for a full list of proposed features (and known issues).\n\n<!-- CONTRIBUTING -->\n## Contributing\n\nContributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.\n\nIf you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".\nDon\'t forget to give the project a star! Thanks again!\n\n1. Fork the Project\n2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)\n3. Commit your Changes (`git commit -m \'Add some AmazingFeature\'`)\n4. Push to the Branch (`git push origin feature/AmazingFeature`)\n5. Open a Pull Request\n\n<!-- LICENSE -->\n## License\n\nDistributed under the MIT License. See `LICENSE.txt` for more information.\n\n<!-- CONTACT -->\n## Contact\n\nYour Name - [@twitter_handle](https://twitter.com/twitter_handle) - email@email_client.com\n\nProject Link: [https://github.com/github_username/repo_name](https://github.com/github_username/repo_name)\n\n<!-- ACKNOWLEDGMENTS -->\n## Acknowledgments\n\n* []()\n* []()\n* []()\n\n<!-- MARKDOWN LINKS & IMAGES -->\n<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->\n[contributors-shield]: https://img.shields.io/github/contributors/github_username/repo_name.svg?style=for-the-badge\n[contributors-url]: https://github.com/github_username/repo_name/graphs/contributors\n[forks-shield]: https://img.shields.io/github/forks/github_username/repo_name.svg?style=for-the-badge\n[forks-url]: https://github.com/github_username/repo_name/network/members\n[stars-shield]: https://img.shields.io/github/stars/github_username/repo_name.svg?style=for-the-badge\n[stars-url]: https://github.com/github_username/repo_name/stargazers\n[issues-shield]: https://img.shields.io/github/issues/github_username/repo_name.svg?style=for-the-badge\n[issues-url]: https://github.com/github_username/repo_name/issues\n[license-shield]: https://img.shields.io/github/license/github_username/repo_name.svg?style=for-the-badge\n[license-url]: https://github.com/github_username/repo_name/blob/master/LICENSE.txt\n[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555\n[linkedin-url]: https://linkedin.com/in/linkedin_username\n[product-screenshot]: images/screenshot.png',
    'author': 'Ahmed Kamel',
    'author_email': 'ahmedk@zadgroup.net',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
