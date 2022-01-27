# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['file_retention']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0', 'click>=8.0.3,<9.0.0']

setup_kwargs = {
    'name': 'file-retention',
    'version': '0.3.0',
    'description': 'Delete files based on predefined dates',
    'long_description': '# file-retention\nCLI para retenção de arquivos com base em qualquer data \n\nComo instalar:\n~~~\npython3 -m pip install --upgrade pip\npython3 -m pip install file_retention\n~~~\n\nComo utilizar:\n\nPrimeiro é necessário executar com o comando install para \ncriar os diretórios e arquivos de configuração necessários\n~~~\npython3 -m file_retention install\n~~~\n\nTirar um snapshot dos arquivos recursivamente:\n~~~\npython3 -m file_retention snapshot /tmp/create_files/ -e ini\n~~~\n\nDeletar os arquivos:\n~~~\npython3 -m file_retention delete -r 15 -y\n~~~\n\n\nEnviar e-mail:\n~~~\npython3 -m file_retention mail ~/.file_retention/mail.yml -r 15\n~~~\n\nPara mais informaões:\n~~~\npython3 -m file_retention --help\npython3 -m file_retention snapshot --help\npython3 -m file_retention mail --help\npython3 -m file_retention delete --help\n~~~\n',
    'author': 'Gabriel de Mello Barbosa',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ollemg/file_retention',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
