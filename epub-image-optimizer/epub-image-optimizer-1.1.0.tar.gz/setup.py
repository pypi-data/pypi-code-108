# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['epub_image_optimizer']

package_data = \
{'': ['*']}

install_requires = \
['Pillow==9.0.0',
 'click>=8.0.1,<9.0.0',
 'coloredlogs>=15.0.1,<16.0.0',
 'defusedxml>=0.7.1,<0.8.0',
 'lxml>=4.6.3,<5.0.0',
 'rich>=11.0.0,<12.0.0',
 'tinify==1.5.2']

entry_points = \
{'console_scripts': ['epub-image-optimizer = epub_image_optimizer.cli:main']}

setup_kwargs = {
    'name': 'epub-image-optimizer',
    'version': '1.1.0',
    'description': 'Small application to optimize images (and cover) inside epub files',
    'long_description': "# epub-image-optimizer\n\n![GitHub Workflow Status](https://img.shields.io/github/workflow/status/jabbo16/epub-image-optimizer/tests)\n![PyPI](https://img.shields.io/pypi/v/epub-image-optimizer)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/epub-image-optimizer)\n[![codecov](https://codecov.io/gh/Jabbo16/epub-image-optimizer/branch/main/graph/badge.svg?token=FCE3APT4ZP)](https://codecov.io/gh/Jabbo16/epub-image-optimizer)\n[![DeepSource](https://deepsource.io/gh/Jabbo16/epub-image-optimizer.svg/?label=active+issues&show_trend=true)](https://deepsource.io/gh/Jabbo16/epub-image-optimizer/?ref=repository-badge)\n![GitHub](https://img.shields.io/github/license/jabbo16/epub-image-optimizer)\n\nSmall Python CLI application to optimize images (including the cover) inside epub files. Perfect fit for optimizing LNs as they usually have a lot of images.\n\n## Installation\n\nFrom [PyPI](https://pypi.python.org/pypi/epub-image-optimizer/) directly:\n\n```shell\npip install epub-image-optimizer\n```\n\nor\n\n```shell\npython3 -m pip install epub-image-optimizer\n```\n\n## Usage\n\n```text\nUsage: epub-image-optimizer [OPTIONS]\n\n  EPUB Image Optimization tool\n\nOptions:\n  --input-dir DIRECTORY           Input folder\n  --output-dir DIRECTORY          Output folder\n  --input-file FILE               Path to Epub Input file\n  --max-image-resolution <INTEGER INTEGER>...\n                                  Fit image resolution to this values, good\n                                  for handling images with higher\n                                  resolutions than your ebook-reader\n  --tinify-api-key TEXT           Tinify api-key\n  --only-cover                    Optimize only the cover image, ignoring all\n                                  other images\n  --keep-color                    If this flag is present images will preserve\n                                  colors (not converted to BW)\n  --log-level [INFO|DEBUG|WARN|ERROR]\n                                  Set log level, default is 'INFO'\n  --version                       Show current version\n  --help                          Show this message and exit.\n```\n\n## Examples\n\n### Convert all images to BW\n\n```shell\nepub-image-optimizer --input-file <my-epub>\n```\n\n### Convert only cover to BW\n\n```shell\nepub-image-optimizer --input-file <my-epub> --only-cover\n```\n\n### Optimize all images while keeping colors\n\n```shell\nepub-image-optimizer --input-file <my-epub> --keep-color\n```\n\nNote: At the moment this won't do anything as there is currently no optimization if not using Tinify.\n\n### Optimize all images using Tinify while keeping colors\n\n```shell\nepub-image-optimizer --input-file <my-epub> --keep-color --tinify-api-key <tinify-api-key>\n```\n\nNote: You can obtain your Tinify API Key [here](https://tinypng.com/developers). Free tier is limited to 500 images/month.\n\n### Optimize and fit all images to custom resolution while keeping colors\n\n```shell\nepub-image-optimizer --input-dir <folder> --max-image-resolution 1680 1264 --tinify-api-key <tinify-api-key>\n```\n\nNote: This will optimize all epubs inside `input-dir` folder, used my Kobo Libra H2O screen size as example.\n\n## Development\n\n[Poetry](https://github.com/python-poetry/poetry) is used for managing packages, dependencies and building the project.\n\nPoetry can be installed by following the [instructions](https://github.com/python-poetry/poetry). Afterwards you can use `poetry install` within the project folder to install all dependencies.\n",
    'author': 'Javier Sacido',
    'author_email': 'jabbo16@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Jabbo16/epub-image-optimizer',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
