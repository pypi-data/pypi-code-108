# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mmf_meta']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'pydantic>=1.9.0,<2.0.0']

entry_points = \
{'console_scripts': ['mmfmeta = mmf_meta:cli']}

setup_kwargs = {
    'name': 'mmf-meta',
    'version': '0.1.2b0',
    'description': '',
    'long_description': '# MMF-meta\nЭта библиотека - часть проекта Model Management Framework.\n\nОтвечает за оформление пользовательских функций\n\n### Пример использования\n```python\nimport pickle\nimport time\nimport pandas\nimport mmf_meta as mmf\n\n\n@mmf.target(\n    description="Супер-функция",\n    returns=mmf.DataFrame(out_format=mmf.DataFrameFormat.CSV),\n)\ndef score(\n    df: pandas.DataFrame = mmf.DataFrame(description="Описание df"),\n    # other: dict = mmf.JsonFile(description="Описание other"),\n):\n    return df\n\n\n@mmf.target(\n    description="Другая супер-функция",\n    returns=mmf.String(),\n)\ndef other(\n    inp=mmf.String(description="важный параметр"),\n    another=mmf.Integer(description="еще один важный параметр"),\n):\n    time.sleep(30)\n    return inp\n\n\nmmf.artifact("some_file")\n\n\n@mmf.artifact("other")\ndef model():\n    with open("other", "br") as f:\n        return pickle.load(f)\n\n```\n\n[Подробная документация](https://mm-framework.github.io/docs/)\n',
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
