# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['northern_lights_forecast', 'northern_lights_forecast.savgol']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.0,<8.0',
 'matplotlib>=3.5.1,<4.0.0',
 'numpy>=1.20.2,<2.0.0',
 'opencv-python>=4.5.1,<5.0.0',
 'pyTelegramBotAPI>=4.3.0,<5.0.0',
 'pytesseract>=0.3.7,<0.4.0',
 'telegram-send>=0.25,<0.26',
 'wget>=3.2,<4.0']

entry_points = \
{'console_scripts': ['nlf = northern_lights_forecast.__main__:main']}

setup_kwargs = {
    'name': 'northern-lights-forecast',
    'version': '2.0.2',
    'description': 'A simple web scraping northern lights forecast that automatically send a telegram notification during substorm events',
    'long_description': "Northern Lights Forecast\n========================\n\n|PyPI| |Python Version| |License| |Read the Docs|\n\n|Tests| |Codecov| |pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/northern-lights-forecast.svg\n   :target: https://pypi.org/project/northern-lights-forecast/\n   :alt: PyPI\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/northern-lights-forecast\n   :target: https://pypi.org/project/northern-lights-forecast\n   :alt: Python Version\n.. https://img.shields.io/pypi/l/northern-lights-forecast\n.. |License| image:: https://img.shields.io/badge/license-MIT-blue\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/northern-lights-forecast/stable.svg?label=Read%20the%20Docs\n   :target: https://northern-lights-forecast.readthedocs.io/\n   :alt: Read the documentation at https://northern-lights-forecast.readthedocs.io/\n.. |Tests| image:: https://github.com/engeir/northern-lights-forecast/workflows/Tests/badge.svg\n   :target: https://github.com/engeir/northern-lights-forecast/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/engeir/northern-lights-forecast/branch/main/graph/badge.svg\n   :target: https://codecov.io/gh/engeir/northern-lights-forecast\n   :alt: Codecov\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\nFeatures\n--------\n\nGet notified whenever there are good chances of seeing northern lights! Follow\n:code:`@NorthernLightsForecastBot` on telegram for updates on the Tromsø magnetometer, or\nset up your own telegram bot with this project. Setting up a telegram bot is easy as pie,\njust follow `this guide`_.\n\nRequirements\n------------\n\nThe project uses `tesseract` to read the scale off a magnetogram plot. See installation\ninstructions below.\n\nInstallation\n------------\n\n.. You can install *Northern Lights Forecast* via pip_ from PyPI_:\n\n.. .. code:: console\n\n..    $ pip install northern-lights-forecast\n\nClone the repository:\n\n.. code:: console\n\n    git clone https://github.com/engeir/northern-lights-forecast.git nlf && cd nlf\n\nInstall tesseract_, used with the package pytesseract.\n\nThen get yourself a telegram bot using `this guide`_.\n\nYou might need to install :code:`opencv` manually. If you want to run the bot on for\nexample a raspberry pi, check out `this video`_ for installation of :code:`opencv`.\n\nSet up a virtual environment and activate. (Use whatever, for example poetry:\n:code:`poetry shell`.)\n\nNow we are ready to install the project; run :code:`poetry install` in the root of the\nproject.\n\n.. :code:`pillow` is a bit picky, and might have to be installed directly with\n.. pip: :code:`pip install pillow`. And :code:`pip install scipy`, :code:`pip install\n.. scikit-image`, :code:`pip install opencv-python`.\n\nSet up a cron job:\n\n.. code:: console\n\n   sh crontab.sh\n\nRunning :code:`sh croptab.sh -p` will print to the console instead of installing a new\ncron job.\n\nUsage\n-----\n\nPlease see the `Command-line Reference <Usage_>`_ for details. Below is the output of\n:code:`nlf --help`:\n\n.. code:: console\n\n    Usage: nlf [OPTIONS]\n\n      Northern Lights Forecast.\n\n    Options:\n      --version                     Show the version and exit.\n      -l, --location TEXT           Which magnetometer to use. Run with '--\n                                    locations' option to list all available\n                                    locations.  [default: Tromsø]\n\n      --locations / --no-locations  List out available magnetometer locations.\n                                    [default: False]\n\n      --test / --no-test            Test sending message to telegram.  [default:\n                                    False]\n\n      --help                        Show this message and exit.\n\nTelegram\n^^^^^^^^\n\nIt is also possible to visit the telegram bot (:code:`@NorthernLightsForecastBot`) and\nquery for forecasts live. This includes the commands:\n\n* :code:`/start` and :code:`/help`: this will do the same thing, greet you with a helpful\n  message\n* :code:`/locations`: which will print out the valid locations a forecast can be obtained\n  from\n* :code:`Forecast <location>`: that is, any message that starts with the word\n  :code:`forecast` and has a valid location as any of the succeeding words.\n\n.. image:: assets/telegram_screendump.gif\n\nHow?\n----\n\nThe script implements an automated Northern Lights forecast by taking advantage of the web\nsite of `Tromsø Geophysical Observatory`_ (TGO).\n\nImage analysis\n^^^^^^^^^^^^^^\n\nThe script will try to download a :code:`.gif` file with plots of the components of a\nmagnetometer. One component is all that is needed (blue line) and the script will then\nlocate the blue pixels and fit a graph to the pixel locations with a `Savitzky-Golay\nfilter`_.\n\nBelow is an example with the original image above the new reverse engineered graph.\n\n.. image:: assets/before.jpg\n\n.. image:: assets/after.png\n\nAt a given threshold of the derivative of the X component of a magnetometer in Tromsø (or\none of the supported locations, see :code:`nlf --locations`), a notification is sent to a\ntelegram bot to let the user know of the current substorm event.\n\nCron\n----\n\nThe script can be run every hour from 18:00 through 08:00 during the months September\nthrough March, using cron to automate the task. Run\n\n.. code:: console\n\n    sh crontab.sh\n\nto set this up, or edit the cron script manually with\n\n.. code:: console\n\n    env EDITOR=nano crontab -e\n\nThe general form of how you edit cron is as shown below, but to get the exact string you\ncan run :code:`sh crontab.sh -p`, where the option :code:`-p` will make the script print\nto the console rather than edit cron. The same options can be used when running the script\nas a cron job as is specified in the `Command-line Reference <Usage_>`_ (e.g.\\ the\n:code:`-l` option).\n\n.. code:: console\n\n    0 0-8,18-23 * 9-12,1-3 * export DISPLAY=:0 && cd /path/to/folder/containing/script && python src/northern_lights_forecast/__main__.py > t.txt 2>&1\n\nTo change when the script is run, edit the cron scheduling to a custom setting:\nhttps://crontab.guru/\n\nThe :code:`crontab.sh` script will try to find the tesseract executable and add this to\npath, which is needed for the cronjob to work.  If it cannot find tesseract, a comment is\ninstead printed warning about this, and you have to verify the installation of tesseract\nand possibly add it to path manually.\n\nContributing\n------------\n\nContributions are very welcome.\nTo learn more, see the `Contributor Guide`_.\n\n\nLicense\n-------\n\nDistributed under the terms of the `MIT license`_,\n*Northern Lights Forecast* is free and open source software.\n\n\nIssues\n------\n\nIf you encounter any problems,\nplease `file an issue`_ along with a detailed description.\n\n\nCredits\n-------\n\nThis project was generated from `@cjolowicz`_'s `Hypermodern Python Cookiecutter`_ template.\n\n.. _@cjolowicz: https://github.com/cjolowicz\n.. _Cookiecutter: https://github.com/audreyr/cookiecutter\n.. _MIT license: https://opensource.org/licenses/MIT\n.. _PyPI: https://pypi.org/\n.. _Hypermodern Python Cookiecutter: https://github.com/cjolowicz/cookiecutter-hypermodern-python\n.. _file an issue: https://github.com/engeir/northern-lights-forecast/issues\n.. _pip: https://pip.pypa.io/\n.. _tesseract: https://tesseract-ocr.github.io/tessdoc/Compiling-%E2%80%93-GitInstallation.html\n.. _RealPython: https://realpython.com/python-send-email/#option-1-setting-up-a-gmail-account-for-development\n.. _Tromsø Geophysical Observatory: https://www.tgo.uit.no/\n.. _this guide: https://medium.com/@robertbracco1/how-to-write-a-telegram-bot-to-send-messages-with-python-bcdf45d0a580\n.. _this video: https://www.youtube.com/watch?v=rdBTLOx0gi4\n.. _Savitzky-Golay filter: https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.savgol_filter.html\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Usage: https://northern-lights-forecast.readthedocs.io/en/latest/usage.html\n",
    'author': 'Eirik Rolland Enger',
    'author_email': 'eirroleng@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/engeir/northern-lights-forecast',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
