# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['balaboba']

package_data = \
{'': ['*']}

install_requires = \
['cloudscraper>=1.2.58,<2.0.0']

setup_kwargs = {
    'name': 'balaboba',
    'version': '1.0.5',
    'description': 'Wrapper for Yandex Balaboba',
    'long_description': '# balaboba\n\nОбёртка для [Яндекс Балабоба](https://yandex.ru/lab/yalm).\n\nАсинхронная версия [здесь](https://github.com/monosans/aiobalaboba).\n\n## Установка\n\n```sh\npython -m pip install balaboba\n```\n\n## Примеры использования\n\n### Базовый пример\n\n```python\nfrom balaboba import balaboba\n\nresponse = balaboba("Привет")\nprint(response)\n```\n\nВывод: `Привет! Я рад тебя видеть на моём канале. Здесь ты сможешь встретить много интересных аниме, музыки, видео, и многого другого.`\n\n### Варианты стилизации\n\nФункции `balaboba` в качестве аргумента `intro` можно передать желаемый вариант стилизации. Номера всех вариантов стилизации есть в [докстринге](https://github.com/monosans/balaboba/blob/main/balaboba/_balaboba.py#L24). В примере используется 11-й вариант стилизации "Народные мудрости" ([полный код примера](https://github.com/monosans/balaboba/blob/main/examples/style.py)):\n\n```python\nresponse = balaboba("Привет", intro=11)\n```\n\n### Свой экземпляр cloudscraper.CloudScraper\n\nФункции `balaboba` в качестве аргумента `session` можно передать экземпляр `cloudscraper.CloudScraper` ([полный код примера](https://github.com/monosans/balaboba/blob/main/examples/client_session.py)):\n\n```python\nwith CloudScraper() as session:\n    response = balaboba("Привет", session=session)\n```\n\n## Дисклеймер с сайта\n\nНейросеть не знает, что говорит, и может сказать всякое — если что, не обижайтесь. Распространяя получившиеся тексты, помните об ответственности.\n\n## License / Лицензия\n\n[MIT](https://github.com/monosans/balaboba/blob/main/LICENSE)\n',
    'author': 'monosans',
    'author_email': 'hsyqixco@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/monosans/balaboba',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
