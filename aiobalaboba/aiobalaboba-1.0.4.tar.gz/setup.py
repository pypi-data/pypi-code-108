# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiobalaboba']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.7.4,<4.0.0']

setup_kwargs = {
    'name': 'aiobalaboba',
    'version': '1.0.4',
    'description': 'Asynchronous wrapper for Yandex Balaboba',
    'long_description': '# aiobalaboba\n\nАсинхронная обёртка для [Яндекс Балабоба](https://yandex.ru/lab/yalm).\n\nСинхронная версия [здесь](https://github.com/monosans/balaboba).\n\n## Установка\n\n```sh\npython -m pip install aiobalaboba\n```\n\n## Примеры использования\n\n### Базовый пример\n\n```python\nimport asyncio\n\nfrom aiobalaboba import balaboba\n\n\nasync def main():\n    response = await balaboba("Привет")\n    print(response)\n\n\nif __name__ == "__main__":\n    asyncio.run(main())\n```\n\nВывод: `Привет! Я рад тебя видеть на моём канале. Здесь ты сможешь встретить много интересных аниме, музыки, видео, и многого другого.`\n\n### Варианты стилизации\n\nФункции `balaboba` в качестве аргумента `intro` можно передать желаемый вариант стилизации. Номера всех вариантов стилизации есть в [докстринге](https://github.com/monosans/aiobalaboba/blob/main/aiobalaboba/_balaboba.py#L24). В примере используется 11-й вариант стилизации "Народные мудрости" ([полный код примера](https://github.com/monosans/aiobalaboba/blob/main/examples/style.py)):\n\n```python\nresponse = await balaboba("Привет", intro=11)\n```\n\n### Свой экземпляр aiohttp.ClientSession\n\nФункции `balaboba` в качестве аргумента `session` можно передать экземпляр aiohttp.ClientSession ([полный код примера](https://github.com/monosans/aiobalaboba/blob/main/examples/client_session.py)):\n\n```python\nasync with ClientSession() as session:\n    response = await balaboba("Привет", session=session)\n```\n\n## Дисклеймер с сайта\n\nНейросеть не знает, что говорит, и может сказать всякое — если что, не обижайтесь. Распространяя получившиеся тексты, помните об ответственности.\n\n## License / Лицензия\n\n[MIT](https://github.com/monosans/aiobalaboba/blob/main/LICENSE)\n',
    'author': 'monosans',
    'author_email': 'hsyqixco@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/monosans/aiobalaboba',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
