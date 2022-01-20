# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qdarktheme',
 'qdarktheme.__pyinstaller',
 'qdarktheme.qtpy',
 'qdarktheme.qtpy.QtCore',
 'qdarktheme.qtpy.QtGui',
 'qdarktheme.qtpy.QtSvg',
 'qdarktheme.qtpy.QtWidgets',
 'qdarktheme.themes',
 'qdarktheme.themes.dark',
 'qdarktheme.themes.light',
 'qdarktheme.widget_gallery',
 'qdarktheme.widget_gallery.ui']

package_data = \
{'': ['*'],
 'qdarktheme.themes.dark': ['svg/*'],
 'qdarktheme.themes.light': ['svg/*'],
 'qdarktheme.widget_gallery': ['svg/*']}

extras_require = \
{'docs': ['pydata-sphinx-theme>=0.7.2,<0.9.0', 'sphinx-panels>=0.6.0,<0.7.0']}

entry_points = \
{'pyinstaller40': ['hook-dirs = qdarktheme.__pyinstaller:get_hook_dirs']}

setup_kwargs = {
    'name': 'pyqtdarktheme',
    'version': '1.0.3',
    'description': 'Flat dark theme for PySide and PyQt.',
    'long_description': '# PyQtDarkTheme\n\nPyQtDarkTheme applies a flat dark theme to QtWidgets application(PySide and PyQt). There\'s a light theme too. Color and style balanced from a dark theme for easy viewing in daylight.\n\nCheck out the [complete documentation](https://pyqtdarktheme.readthedocs.io).\n\n**Project status**  \n[![PyPI Latest Release](https://img.shields.io/pypi/v/pyqtdarktheme.svg?color=orange)](https://pypi.org/project/pyqtdarktheme/)\n[![Python Versions](https://img.shields.io/pypi/pyversions/pyqtdarktheme.svg?color=blue)](https://www.python.org/downloads/)\n[![Qt Versions](https://img.shields.io/badge/Qt-5%20|%206-blue.svg?&logo=Qt&logoWidth=18&logoColor=white)](https://www.qt.io/qt-for-python)\n[![License](https://img.shields.io/github/license/5yutan5/PyQtDarkTheme.svg?color=green)](https://github.com/5yutan5/PyQtDarkTheme/blob/main/LICENSE.txt/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-black.svg)](https://github.com/python/black)\n\n**Tests**  \n[![tests](https://github.com/5yutan5/PyQtDarkTheme/actions/workflows/test.yml/badge.svg)](https://github.com/5yutan5/PyQtDarkTheme/actions/workflows/test.yml)\n[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/5yutan5/PyQtDarkTheme/main.svg)](https://results.pre-commit.ci/latest/github/5yutan5/PyQtDarkTheme/main)\n[![codecov](https://codecov.io/gh/5yutan5/PyQtDarkTheme/branch/main/graph/badge.svg?token=RTS8O0V6SF)](https://codecov.io/gh/5yutan5/PyQtDarkTheme)\n[![Total alerts](https://img.shields.io/lgtm/alerts/g/5yutan5/PyQtDarkTheme.svg?logo=lgtm&logoWidth=18&color=success)](https://lgtm.com/projects/g/5yutan5/PyQtDarkTheme/alerts/)\n[![Documentation Status](https://readthedocs.org/projects/pyqtdarktheme/badge/?version=latest)](https://pyqtdarktheme.readthedocs.io/en/latest/?badge=latest)\n\n## Features\n\n- A flat dark and light theme\n- Support PySide and PyQt\n- Support some freezing library(PyInstaller, cx_Freeze)\n- Resolve the style differences between Qt versions\n- QPalette of dark and light theme\n\n## Themes\n\n### Dark Theme\n\n![widget_gallery_dark_theme](https://raw.githubusercontent.com/5yutan5/PyQtDarkTheme/main/images/widget_gallery_dark.png)\n\n### Light Theme\n\n![widget_gallery_light_them](https://raw.githubusercontent.com/5yutan5/PyQtDarkTheme/main/images/widget_gallery_light.png)\n\n## Requirements\n\n- [Python 3.7+](https://www.python.org/downloads/)\n- Qt 5.11+\n- PySide6, PyQt6, PyQt5 or PySide2\n\n## Installation Method\n\n- Last released version\n\n   ```plaintext\n   pip install pyqtdarktheme\n   ```\n\n- Latest development version\n\n   ```plaintext\n   pip install git+https://github.com/5yutan5/PyQtDarkTheme.git@main\n   ```\n\n## Usage\n\n```Python\nimport sys\n\nfrom PySide6.QtWidgets import QApplication, QMainWindow, QPushButton\n\nimport qdarktheme\n\napp = QApplication(sys.argv)\nmain_win = QMainWindow()\npush_button = QPushButton("PyQtDarkTheme!!")\nmain_win.setCentralWidget(push_button)\n\n# Apply dark theme to Qt application\napp.setStyleSheet(qdarktheme.load_stylesheet())\n\nmain_win.show()\n\napp.exec()\n\n```\n\n> ⚠ The image quality may be lower on Qt5(PyQt5, PySide2) due to the use of svg. You can add the following attribute to improve the quality of images.\n>\n> ```Python\n> app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps)\n> ```\n\n### Light theme\n\n```Python\napp.setStyleSheet(qdarktheme.load_stylesheet("light"))\n```\n\n### Dark and Light palette\n\nYou can get color of dark and light theme by loading QPalette.\nTo load palette, run:\n\n```Python\npalette = qdarktheme.load_palette()\n# or\npalette = qdarktheme.load_palette("light")\n```\n\nFor example, you can apply a link color to your application.\n\n```Python\nimport sys\n\nfrom PyQt5.QtGui import QPalette\nfrom PyQt5.QtWidgets import QApplication\n\nimport qdarktheme\n\napp = QApplication(sys.argv)\ndark_palette = qdarktheme.load_palette()\npalette = app.palette()\npalette.setColor(QPalette.ColorRole.Link, dark_palette.link().color())\napp.setPalette(palette)\n\n```\n\nFurther information can be found in our docs:\n\n- [Usage Guide](https://pyqtdarktheme.readthedocs.io/en/latest/how_to_use.html)\n\n## Example\n\nTo check example app, run:\n\n```plaintext\npython -m qdarktheme.widget_gallery\n```\n\n## License\n\nThe svg files for the PyQtDarkTheme are derived [Material design icons](https://fonts.google.com/icons)(Apache License Version 2.0). Qt stylesheets are originally fork of [QDarkStyleSheet](https://github.com/ColinDuquesnoy/QDarkStyleSheet)(MIT License). Other files are covered by PyQtDarkTheme\'s MIT license.\n\n## Contributing\n\nAll contributions, bug reports, bug fixes, documentation improvements, enhancements, and ideas are welcome. You can get started by reading this:\n\n- [Contributing Guide](https://pyqtdarktheme.readthedocs.io/en/latest/contributing.html)\n\n## Change log\n\nSee [Releases](https://github.com/5yutan5/PyQtDarkTheme/releases).\n',
    'author': 'Yunosuke Ohsugi',
    'author_email': '63651161+5yutan5@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/5yutan5/PyQtDarkTheme',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
