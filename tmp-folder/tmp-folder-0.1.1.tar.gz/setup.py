# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tmp_folder']

package_data = \
{'': ['*']}

install_requires = \
['typing-extensions>=4.0.1,<5.0.0']

setup_kwargs = {
    'name': 'tmp-folder',
    'version': '0.1.1',
    'description': 'Extends python `TemporaryDirectory` and make it even easier to use, as a decorator.',
    'long_description': '<p align="center">\n\n  <a href="https://codecov.io/gh/jalvaradosegura/tmp-folder">\n    <img src="https://codecov.io/gh/jalvaradosegura/tmp-folder/branch/main/graph/badge.svg?token=IL5PVTYVRV"/>\n  </a>\n\n  <a href="https://github.com/psf/black" target="_blank">\n    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="black">\n  </a>\n\n  <a href="https://pycqa.github.io/isort/" target="_blank">\n    <img src="https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336" alt="isort">\n  </a>\n\n  <a href="https://github.com/jalvaradosegura/tmp-folder/actions/workflows/unit_tests.yml" target="_blank">\n    <img src="https://github.com/jalvaradosegura/tmp-folder/actions/workflows/unit_tests.yml/badge.svg" alt="License">\n  </a>\n\n</p>\n\n---\n\nDocumentation: https://jalvaradosegura.github.io/tmp-folder/\n\n---\n\n## tmp-folder\nEasily create a temporary folder. Put files in it and after you\'re done tmp-folder will delete the folder automatically.\n\n## Installation\n\nInstall from PyPI:\n\n```\npip install tmp-folder\n```\n\n## Usage\n```py\nfrom pathlib import Path\n\nfrom tmp_folder.main import use_tmp_folder\n\n\n@use_tmp_folder  # this decorator does the magic\ndef this_func_create_a_tmp_file_and_return_its_path(tmp_folder: Path) -> Path:\n    tmp_file_path = tmp_folder / "tmp_file.txt"\n    with open(tmp_file_path, "w") as file:\n        file.write("Hello World")\n\n    assert tmp_file_path.exists()  # double check that the file actually exists\n\n    return tmp_file_path\n\n\nif __name__ == "__main__":\n    tmp_file_path = this_func_create_a_tmp_file_and_return_its_path()\n\n    # After the function is executed, the folder and its files are gone.\n    assert not tmp_file_path.exists()\n\n```\n\nJust decorate the function in which you need a temporary folder. Then add as first parameter, the variable that will hold the folder path (it can be named however you want). After the function is done executing, the folder and its file will be deleted.\n',
    'author': 'Jorge Alvarado',
    'author_email': 'alvaradosegurajorge@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://jalvaradosegura.github.io/tmp-folder/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
