# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['calculadora_do_cidadao',
 'calculadora_do_cidadao.adapters',
 'calculadora_do_cidadao.rows',
 'calculadora_do_cidadao.rows.plugins']

package_data = \
{'': ['*']}

install_requires = \
['lxml>=4.7.1,<5.0.0',
 'requests>=2.22.0',
 'typer>=0.0.8',
 'unicodecsv>=0.14.1,<0.15.0',
 'xlrd>=2.0.1,<3.0.0',
 'xlwt>=1.3.0,<2.0.0']

extras_require = \
{'docs': ['pip>=20.0.0',
          'readthedocs-sphinx-ext>=2.1.3',
          'sphinx>=3.4.3',
          'sphinx-rtd-theme>=0.5.1']}

setup_kwargs = {
    'name': 'calculadora-do-cidadao',
    'version': '0.5.3',
    'description': 'Tool for Brazilian Reais monetary adjustment/correction',
    'long_description': '# Calculadora do Cidadão\n\n[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/cuducos/calculadora-do-cidadao/Tests)](https://github.com/cuducos/calculadora-do-cidadao/actions)\n[![Code Climate maintainability](https://img.shields.io/codeclimate/maintainability-percentage/cuducos/calculadora-do-cidadao)](https://codeclimate.com/github/cuducos/calculadora-do-cidadao/maintainability)\n[![Code Climate coverage](https://img.shields.io/codeclimate/coverage/cuducos/calculadora-do-cidadao)](https://codeclimate.com/github/cuducos/calculadora-do-cidadao/test_coverage)\n[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/calculadora-do-cidadao)](https://pypi.org/project/calculadora-do-cidadao/)\n[![PyPI](https://img.shields.io/pypi/v/calculadora-do-cidadao)](https://pypi.org/project/calculadora-do-cidadao/)\n[![](https://img.shields.io/readthedocs/calculadora-do-cidadao)](https://calculadora-do-cidadao.readthedocs.io/)\n\nPacote em Python para correção de valores. Confira a [documentação](https://calculadora-do-cidadao.readthedocs.io/) e o [mini-guia de contribuição](CONTRIBUTING.md) para mais detalhes!\n\n## Exemplo de uso\n\n```python\nIn [1]: from datetime import date\n   ...: from decimal import Decimal\n   ...: from calculadora_do_cidadao import Ipca\n\nIn [2]: ipca = Ipca()\n\nIn [3]: ipca.adjust(date(2018, 7, 6))\nOut[3]: Decimal(\'1.051202206630561280035407253\')\n\nIn [4]: ipca.adjust("2014-07-08", 7)\nOut[4]: Decimal(\'9.407523138792336916983267321\')\n\nIn [5]: ipca.adjust("12/07/1998", 3, "01/07/2006")\nOut[5]: Decimal(\'5.279855889296777979447848574\')\n```\n\n[![asciicast](https://asciinema.org/a/295920.svg)](https://asciinema.org/a/295920)\n',
    'author': 'Eduardo Cuducos',
    'author_email': 'cuducos@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://calculadora-do-cidadao.readthedocs.io/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
