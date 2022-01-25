# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mmf_serve']

package_data = \
{'': ['*']}

install_requires = \
['PyTurboJPEG>=1.6.5,<2.0.0',
 'XlsxWriter>=3.0.2,<4.0.0',
 'aio-pika>=6.8.1,<7.0.0',
 'aiofile>=3.7.4,<4.0.0',
 'cryptography>=36.0.1,<37.0.0',
 'fastapi>=0.73.0,<0.74.0',
 'mmf-meta>=0.1.3,<0.2.0',
 'opencv-python>=4.5.5,<5.0.0',
 'openpyxl>=3.0.9,<4.0.0',
 'orjson>=3.6.6,<4.0.0',
 'pandas>=1.4.0,<2.0.0',
 'pydantic[dotenv]>=1.9.0,<2.0.0',
 'python-multipart>=0.0.5,<0.0.6',
 'requests>=2.27.1,<3.0.0',
 'xlrd>=2.0.1,<3.0.0']

entry_points = \
{'console_scripts': ['mmfserve = mmf_serve:cli']}

setup_kwargs = {
    'name': 'mmf-serve',
    'version': '0.1.1',
    'description': 'Часть проекта MMF отвечающая за serving',
    'long_description': '# MMF-meta\nЭта библиотека - часть проекта Model Management Framework.\n\nОтвечает за serving\n\n### Пример использования\n```shell\nmmfserve serve_rabbit --n_proc=2 --queue_name=tasks_que --results_exchange=result_exchange main.py\n```\n\n[Подробная документация](https://mm-framework.github.io/docs/)\n',
    'author': 'Викторов Андрей Германович',
    'author_email': 'andvikt@gmail.com',
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
