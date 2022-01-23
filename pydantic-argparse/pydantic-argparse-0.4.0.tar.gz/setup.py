# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydantic_argparse',
 'pydantic_argparse.argparse',
 'pydantic_argparse.parsers',
 'pydantic_argparse.utils']

package_data = \
{'': ['*']}

install_requires = \
['pydantic>=1.8.2,<2.0.0', 'typing-inspect>=0.7.1,<0.8.0']

setup_kwargs = {
    'name': 'pydantic-argparse',
    'version': '0.4.0',
    'description': 'Typed Argument Parsing with Pydantic',
    'long_description': '# pydantic-argparse\n\n[![pypi](https://img.shields.io/pypi/v/pydantic-argparse.svg)](https://pypi.python.org/pypi/pydantic-argparse)\n[![downloads](https://pepy.tech/badge/pydantic-argparse)](https://pepy.tech/project/pydantic-argparse)\n[![versions](https://img.shields.io/pypi/pyversions/pydantic-argparse.svg)](https://github.com/SupImDos/pydantic-argparse)\n[![license](https://img.shields.io/github/license/SupImDos/pydantic-argparse.svg)](https://github.com/SupImDos/pydantic-argparse/blob/master/LICENSE)\n\n\nTyped Argument Parsing with Pydantic\n\n## Help\n\nDocumentation coming soon.\n\n## Installation\n\nInstall using:\n* `pip3 install pydantic-argparse`\n\n## Example\n\n```py\nimport pydantic\nimport pydantic_argparse\n\n\nclass Arguments(pydantic.BaseModel):\n    """Arguments for CLI"""\n    # Required Args\n    aaa: str = pydantic.Field(description="I\'m a required string")\n    bbb: int = pydantic.Field(description="I\'m a required integer")\n    ccc: bool = pydantic.Field(description="I\'m a required bool")\n\n    # Optional Args\n    ddd: bool = pydantic.Field(False, description="I\'m an optional bool (default False)")\n    eee: bool = pydantic.Field(True, description="I\'m an optional bool (default True)")\n\n\ndef main() -> None:\n    """Main example function."""\n    # Create Parser and Parse Args\n    parser = pydantic_argparse.ArgumentParser(\n        model=Arguments,\n        prog="Example",\n        description="Example Description",\n        version="0.0.1",\n        epilog="Example Epilog",\n    )\n    args = parser.parse_typed_args()\n\n    # Print Args\n    print(args)\n\n\nif __name__ == "__main__":\n    main()\n```\n\n```console\n$ python3 example.py --help\n\nusage: Example [-h] [-v] --aaa AAA --bbb BBB --ccc | --no-ccc [--ddd] [--no-eee]\n\nExample Description\n\nrequired arguments:\n  --aaa AAA          I\'m a required string\n  --bbb BBB          I\'m a required integer\n  --ccc, --no-ccc    I\'m a required bool\n\noptional arguments:\n  --ddd              I\'m an optional bool (default False)\n  --no-eee           I\'m an optional bool (default True)\n\nhelp:\n  -h, --help         show this help message and exit\n  -v, --version      show program\'s version number and exit\n\nExample Epilog\n```\n\n```console\n$ python3 example.py --aaa hello --bbb 123 --no-ccc\n\naaa=\'hello\' bbb=123 ccc=False ddd=False eee=True\n```\n',
    'author': 'Hayden Richards',
    'author_email': 'SupImDos@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/SupImDos/pydantic-argparse',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
