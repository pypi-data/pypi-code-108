# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mandown', 'mandown.sources']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.10.0,<5.0.0',
 'feedparser>=6.0.8,<7.0.0',
 'lxml>=4.7.1,<5.0.0',
 'natsort>=8.0.2,<9.0.0',
 'requests>=2.27.0,<3.0.0',
 'typer>=0.4.0,<0.5.0']

entry_points = \
{'console_scripts': ['mandown = mandown.cli:main']}

setup_kwargs = {
    'name': 'mandown',
    'version': '0.6.1',
    'description': 'Command line application and library to download and convert comics from various sources',
    'long_description': '# mandown\n\n<a href="https://www.codefactor.io/repository/github/potatoeggy/mandown"><img src="https://www.codefactor.io/repository/github/potatoeggy/mandown/badge" alt="CodeFactor" /></a>\n<a href="https://pypi.org/project/mandown"><img src="https://img.shields.io/pypi/v/mandown" /></a>\n<a href="https://aur.archlinux.org/packages/mandown-git"><img src="https://img.shields.io/aur/version/mandown-git" /></a>\n<a href="https://github.com/potatoeggy/mandown/releases/latest"><img src="https://img.shields.io/github/v/release/potatoeggy/mandown?display_name=tag" /></a>\n<a href="/LICENSE"><img src="https://img.shields.io/github/license/potatoeggy/mandown" /></a>\n\nComic downloader and converter to CBZ and EPUB as a Python library and command line application.\n\n## Supported sites\n\n- https://mangasee123.com\n- https://manganato.com\n- https://webtoons.com\n- https://mangadex.org\n- https://mangakakalot.com\n\n## Installation\n\nInstall the package from PyPI:\n\n```\npip3 install mandown\n```\n\nOr, to build from source:\n\nMandown depends on [poetry](https://github.com/python-poetry/poetry) for building.\n\n```\ngit clone https://github.com/potatoeggy/mandown.git\npoetry install\npoetry build\npip3 install dist/mandown*.whl\n```\n\n## Usage\n\n```\nmandown <URL>\n```\n\nTo convert the download contents to CBZ/EPUB, append the `--convert` option.\n\n```\nmandown <URL> --convert EPUB\n```\n\nTo only\n\nRun `mandown --help` for more info.\n\n## Library usage\n\n```python\nimport os\nfrom mandown import mandown\n\nmanga = mandown.query(url_to_manga)\nprint(manga.metadata, manga.chapters)\nfor c in manga.chapters:\n    mandown.download_chapter(c, dest_folder=os.getcwd(), maxthreads=4)\n```\n',
    'author': 'Daniel Chen',
    'author_email': 'danielchen04@hotmail.ca',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/potatoeggy/mandown',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
