# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['miguxes_py']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'miguxespy',
    'version': '1.0.2',
    'description': 'Modulo que traduz português para miguxês e suas variações (arcaico, moderno e NEO-miguxês). Inspirado no projeto de Aurelio Jargas, que pode ser encontrado em: https://aurelio.net/coisinha/miguxeitor',
    'long_description': '\nMiguxes\\_py\n===========\n<img alt="Twitter Follow" src="https://img.shields.io/twitter/follow/matheuszeen?style=for-the-badge">\n<img alt="PyPI" src="https://img.shields.io/pypi/v/miguxespy?style=for-the-badge">\n\n`miguxes_py` é um modulo que traduz português para as seguintes\nvariações de miguxês:\n\n- arcaico;\n- moderno;\n- NEO-miguxês.\n\nA principal função do módulo é a função `miguxar(texto, dialeto)`, que\nrecebe um texto para ser transformado e um dialeto.\n\nInstalação\n----------\n\nPode ser instalada através do pip, utilizando o comando:\n\n> `pip install miguxes_py`\n\nExemplo de uso:\n\n```python\nfrom miguxes_py.miguxes import miguxar\nfrom miguxes_py.dialetos import DialetoMiguxes\n\nif __name__ == "__main__":\n    print(miguxar("Você acha engraçado tirar screenshots dos NFTs das pessoas, hein?""", DialetoMiguxes.MIGUXES_MODERNO))\n```\n\nA saída seria:\n\n    vc axa engrassadu tirah screenxots dus nfts das pessoas... hein??!?!\n\nInspirado no projeto de Aurelio Jargas, que pode ser encontrado em: <https://aurelio.net/coisinha/miguxeitor>\n------------------------------------------------------------------------\n',
    'author': 'Matheus Alves',
    'author_email': 'theustloz@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/matheuszinn/miguxes_py',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
