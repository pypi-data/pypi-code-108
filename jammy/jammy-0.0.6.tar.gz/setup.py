# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['jammy',
 'jammy.cli',
 'jammy.collections',
 'jammy.comm',
 'jammy.concurrency',
 'jammy.event',
 'jammy.image',
 'jammy.io',
 'jammy.logging',
 'jammy.random',
 'jammy.storage.kv',
 'jammy.utils',
 'jamnp',
 'jamtorch',
 'jamtorch.cuda',
 'jamtorch.data',
 'jamtorch.ddp',
 'jamtorch.distributions',
 'jamtorch.io',
 'jamtorch.logging',
 'jamtorch.nn',
 'jamtorch.pl_callbacks',
 'jamtorch.prototype',
 'jamtorch.trainer',
 'jamtorch.utils',
 'jamviz',
 'jamviz.jupyter',
 'jamviz.plt',
 'jamweb',
 'jamweb.session',
 'jamweb.web']

package_data = \
{'': ['*']}

install_requires = \
['GitPython>=3.1.17,<4.0.0',
 'attrs>=20.3.0,<21.0.0',
 'einops>=0.3.0,<0.4.0',
 'gpustat>=0.6.0,<0.7.0',
 'h5py>=3.4.0,<4.0.0',
 'hydra-core>=1.1.0,<2.0.0',
 'ipdb>=0.13.8,<0.14.0',
 'line-profiler>=3.3.1,<4.0.0',
 'lmdb>=1.2.1,<2.0.0',
 'loguru>=0.5.3,<0.6.0',
 'matplotlib>=3.3.0,<4.0.0',
 'msgpack-numpy>=0.4.7,<0.5.0',
 'msgpack>=1.0.2,<2.0.0',
 'numpy>=1.20.3,<2.0.0',
 'parse>=1.19.0,<2.0.0',
 'pudb>=2022.1,<2023.0',
 'pyarrow>=6.0.0,<7.0.0',
 'python-memcached>=1.59,<2.0',
 'pytorch-lightning>=1.5.1,<2.0.0',
 'pyzmq>=22.3.0,<23.0.0',
 'scipy>=1.6.3,<2.0.0',
 'torch>=1.9.0,<2.0.0',
 'torchinfo>=1.5.3,<2.0.0',
 'torchvision>=0.10.0,<0.11.0',
 'tornado>=6.1,<7.0',
 'tqdm>=4.11.0,<5.0.0',
 'ubelt>=0.10.2,<0.11.0',
 'wandb>=0.10.31,<0.11.0']

entry_points = \
{'console_scripts': ['jgpuc = jammy.cli.gpu_sc:start_client',
                     'jgpus = jammy.cli.gpu_sc:start_sever']}

setup_kwargs = {
    'name': 'jammy',
    'version': '0.0.6',
    'description': 'Personal ToolBox',
    'long_description': '<h1 align="center"> Jammy (Jam) </h1>\n\n<p align="center">\n  <a href="https://pypi.org/project/jammy/">\n    <img src="https://img.shields.io/pypi/v/jammy?style=for-the-badge" alt="PyPI" />\n  </a>\n  <a href="#">\n    <img src="https://img.shields.io/pypi/l/jammy?style=for-the-badge" alt="PyPI - License" />\n  </a>\n  <a href="https://github.com/qsh-zh/jam">\n    <img src="https://img.shields.io/badge/-github-grey?style=for-the-badge&logo=github" alt="GitHub code" />\n  </a>\n  <a href="https://gitlab.com/qsh.zh/jam">\n    <img src="https://img.shields.io/badge/-gitlab-grey?style=for-the-badge&logo=gitlab" alt="GitLab code" />\n  </a>\n  <a href="https://jammy.readthedocs.io/en/stable/index.html">\n    <img src="https://img.shields.io/readthedocs/jammy?style=for-the-badge" alt="Read the Docs" />\n  </a>\n  <a href="#">\n    <img src="https://img.shields.io/pypi/pyversions/jammy?style=for-the-badge" alt="PyPI - Python Version" />\n  </a>\n  <a href="https://github.com/psf/black">\n    <img src="https://img.shields.io/badge/code%20style-black-000000.svg?style=for-the-badge" alt="Code style: black" />\n  </a>\n  <p align="center">\n    <i>A personal toolbox by <a href="https://qsh-zh.github.io/">Qsh.zh</a>.</i>\n  </p>\n</p>\n\n### Usage\n\n#### setup\n\n* For core package, run `pip install jammy`\n* To access functions in `bin`\n```shell\ngit clone https://gitlab.com/qsh.zh/jam.git --recursive\nexport PATH=<path_to_jam>/bin:$PATH\n# run python program\njam-run main.py\njam-crun 1 main.py # use second nvidia gpu\n```\n\n\n#### sample of io\n```python\nimport jammy.io as jio\nfrom jamtorch.utils import as_numpy\njio.dump("ndarray.npz", np.arange(10))\njio.dump("foo.pkl", {"foo": as_numpy(torch.arange(10).cuda())})\nndarray = jio.load("ndarray.npz")\njio.load("foo.pkl")\nmodel_dict = jio.load("checkpoint.pth")\n```\n```shell\n$ jam-inspect-file foo.pkl\n> python3\n[ins] print(f1)\n# content of foo.pkl\n\n```\n\n### Advanced Usage\n\n* [A DDP pytorch training framework](https://jammy.readthedocs.io/en/stable/jamtorch.ddp.html)\n* [Registry](https://jammy.readthedocs.io/en/stable/jammy.utils.html?highlight=registry#jammy.utils.registry.CallbackRegistry)\n* TODO\n\n### Etymology\n* The naming is inspired from [Jyutping](https://en.wikipedia.org/wiki/Jyutping) of [Qin](https://en.wiktionary.org/wiki/%E6%AC%BD).\n\n### MICS\n\n* The package and framework are inspired from [Jacinle](https://github.com/vacancy/Jacinle) by [vacancy](https://github.com/vacancy), from which I learn and take utility functions shamelessly.\n',
    'author': 'Qin',
    'author_email': 'qsh.zh27@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
