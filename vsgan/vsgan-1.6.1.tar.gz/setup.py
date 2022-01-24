# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['vsgan', 'vsgan.archs', 'vsgan.networks']

package_data = \
{'': ['*']}

install_requires = \
['numpy>=1.19.5,<2.0.0']

extras_require = \
{'docs': ['Sphinx>=4.3.2,<5.0.0',
          'furo>=2021.11.23,<2022.0.0',
          'dunamai>=1.7.0,<2.0.0',
          'm2r2>=0.3.2,<0.4.0',
          'sphinxcontrib-youtube>=1.0.1,<2.0.0',
          'sphinxcontrib-images>=0.9.4,<0.10.0'],
 'pytorch': ['torch>=1.10.0,<2.0.0'],
 'vs': ['VapourSynth>=57,<58']}

setup_kwargs = {
    'name': 'vsgan',
    'version': '1.6.1',
    'description': 'VapourSynth Single Image Super-Resolution Generative Adversarial Network (GAN)',
    'long_description': '![banner](https://rawcdn.githack.com/rlaphoenix/VSGAN/d7ad537bffb52bdbd1ad07c825cf016964ac57a2/banner.png)\n\n[![Build Tests](https://img.shields.io/github/workflow/status/rlaphoenix/VSGAN/Version%20test?label=Python%203.6%2B%20builds)](https://github.com/rlaphoenix/VSGAN/actions?query=workflow%3A%22Version+test%22)\n[![License](https://img.shields.io/github/license/rlaphoenix/VSGAN?style=flat)](https://github.com/rlaphoenix/VSGAN/blob/master/LICENSE)\n[![DeepSource](https://deepsource.io/gh/rlaphoenix/VSGAN.svg/?label=active+issues)](https://deepsource.io/gh/rlaphoenix/VSGAN/?ref=repository-badge)\n<a href="https://colab.research.google.com/github/rlaphoenix/VSGAN/blob/master/VSGAN.ipynb">\n    <img align="right" src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab"/>\n</a>\n\nVSGAN is a Single Image Super-Resolution Generative Adversarial Network (GAN) which uses the VapourSynth processing framework to handle input and output image data.\n\n**Documentation**: https://vsgan.phoeniix.dev  \n**License**: [MIT License](LICENSE)\n',
    'author': 'PHOENiX',
    'author_email': 'rlaphoenix@pm.me',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rlaphoenix/vsgan',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.6.2,<4.0',
}


setup(**setup_kwargs)
