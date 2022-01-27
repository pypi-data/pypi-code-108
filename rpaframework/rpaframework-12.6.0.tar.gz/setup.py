# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['RPA',
 'RPA.Browser',
 'RPA.Cloud',
 'RPA.Cloud.objects',
 'RPA.Desktop',
 'RPA.Desktop.keywords',
 'RPA.Email',
 'RPA.Excel',
 'RPA.Outlook',
 'RPA.Robocloud',
 'RPA.Robocorp',
 'RPA.Word',
 'RPA.includes',
 'RPA.scripts',
 'tests',
 'tests.python',
 'tests.resources',
 'tests.scripts']

package_data = \
{'': ['*'],
 'tests': ['robot/*'],
 'tests.resources': ['emails/*',
                     'images/*',
                     'test-app/*',
                     'test-app/META-INF/*',
                     'work-items/items.json',
                     'work-items/items.json',
                     'work-items/items.json',
                     'work-items/items.json',
                     'work-items/mail-json.txt',
                     'work-items/mail-json.txt',
                     'work-items/mail-json.txt',
                     'work-items/mail-json.txt',
                     'work-items/mail-text.txt',
                     'work-items/mail-text.txt',
                     'work-items/mail-text.txt',
                     'work-items/mail-text.txt',
                     'work-items/mail-yaml.txt',
                     'work-items/mail-yaml.txt',
                     'work-items/mail-yaml.txt',
                     'work-items/mail-yaml.txt']}

install_requires = \
['PySocks>=1.5.6,!=1.5.7,<2.0.0',
 'PyYAML>=5.4.1,<6.0.0',
 'chardet>=3.0.0,<4.0.0',
 'click>=7.1.2,<8.0.0',
 'cryptography>=3.3.1,<4.0.0',
 'docutils',
 'exchangelib>=4.5.1,<5.0.0',
 'graphviz>=0.13.2,<0.14.0',
 'htmldocx>=0.0.6,<0.0.7',
 'java-access-bridge-wrapper>=0.9.1,<0.10.0',
 'jsonpath-ng>=1.5.2,<2.0.0',
 'mss>=6.0.0,<7.0.0',
 'netsuitesdk>=1.1.0,<2.0.0',
 'notifiers>=1.2.1,<2.0.0',
 'openpyxl>=3.0.9,<4.0.0',
 'pillow>=8.4.0,<9.0.0',
 'pynput-robocorp-fork>=4.0.0,<5.0.0',
 'pyperclip>=1.8.0,<2.0.0',
 'robotframework-pythonlibcore>=3.0.0,<4.0.0',
 'robotframework-requests>=0.9.1,<0.10.0',
 'robotframework-seleniumlibrary>=5.1.0,<6.0.0',
 'robotframework-seleniumtestability>=1.1.0,<2.0.0',
 'robotframework>=4.0.0,!=4.0.1,<5.0.0',
 'rpaframework-core>=6.5.1,<7.0.0',
 'rpaframework-dialogs>=0.4.1,<0.5.0',
 'rpaframework-pdf>=1.30.4,<2.0.0',
 'selenium>=3.141.0,<4.0.0',
 'simple_salesforce>=1.0.0,<2.0.0',
 'tenacity>=8.0.1,<9.0.0',
 'tweepy>=3.8.0,<4.0.0',
 'tzlocal>=2.1,<3.0',
 'xlrd>=2.0.1,<3.0.0',
 'xlutils>=2.0.0,<3.0.0',
 'xlwt>=1.3.0,<2.0.0']

extras_require = \
{':python_full_version < "3.7.6" and sys_platform == "win32" or python_full_version > "3.7.6" and python_full_version < "3.8.1" and sys_platform == "win32" or python_full_version > "3.8.1" and sys_platform == "win32"': ['pywinauto>=0.6.8,<0.7.0',
                                                                                                                                                                                                                            'pywin32>=300,<302'],
 ':python_version >= "3.6" and python_version < "3.7"': ['dataclasses>=0.7,<0.8'],
 ':sys_platform == "linux"': ['python-xlib>=0.17'],
 ':sys_platform == "win32"': ['robotframework-sapguilibrary>=1.1,<2.0',
                              'comtypes==1.1.10',
                              'comtypes-fork==1.1.10',
                              'psutil>=5.7.0,<6.0.0'],
 'aws': ['boto3>=1.13.4,<2.0.0',
         'amazon-textract-response-parser>=0.1.1,<0.2.0'],
 'cv': ['rpaframework-recognition>=1.0.0,<2.0.0'],
 'playwright:python_version >= "3.7" and python_version < "4.0"': ['robotframework-browser>=11.1.0,<12.0.0']}

entry_points = \
{'console_scripts': ['rpa-crypto = RPA.scripts.crypto:main',
                     'use-robocorp-vault = RPA.scripts.robocorp_cloud:main']}

setup_kwargs = {
    'name': 'rpaframework',
    'version': '12.6.0',
    'description': 'A collection of tools and libraries for RPA',
    'long_description': 'RPA Framework\n=============\n\n.. contents:: Table of Contents\n   :local:\n   :depth: 1\n\n.. include-marker\n\nIntroduction\n------------\n\n`RPA Framework` is a collection of open-source libraries and tools for\nRobotic Process Automation (RPA), and it is designed to be used with both\n`Robot Framework`_ and Python_. The goal is to offer well-documented and\nactively maintained core libraries for Software Robot Developers.\n\nLearn more about RPA at `Robocorp Documentation`_.\n\n**The project is:**\n\n- 100% Open Source\n- Sponsored by Robocorp_\n- Optimized for Robocorp `Control Room`_ and `Developer Tools`_\n- Accepting external contributions\n\n.. _Robot Framework: https://robotframework.org\n.. _Robot Framework Foundation: https://robotframework.org/foundation/\n.. _Python: https://python.org\n.. _Robocorp: https://robocorp.com\n.. _Robocorp Documentation: https://robocorp.com/docs/\n.. _Control Room: https://robocorp.com/docs/control-room\n.. _Developer Tools: https://robocorp.com/downloads\n.. _Installing Python Packages: https://robocorp.com/docs/setup/installing-python-package-dependencies\n\nLinks\n^^^^^\n\n- Homepage: `<https://www.github.com/robocorp/rpaframework/>`_\n- Documentation: `<https://rpaframework.org/>`_\n- PyPI: `<https://pypi.org/project/rpaframework/>`_\n- Release notes: `<https://rpaframework.org/releasenotes.html>`_\n- RSS feed: `<https://rpaframework.org/releases.xml>`_\n\n------------\n\n.. image:: https://img.shields.io/github/workflow/status/robocorp/rpaframework/main?style=for-the-badge\n   :target: https://github.com/robocorp/rpaframework/actions?query=workflow%3Amain\n   :alt: Status\n\n.. image:: https://img.shields.io/pypi/dw/rpaframework?style=for-the-badge\n   :target: https://pypi.python.org/pypi/rpaframework\n   :alt: rpaframework\n\n.. image:: https://img.shields.io/pypi/l/rpaframework.svg?style=for-the-badge&color=brightgreen\n   :target: http://www.apache.org/licenses/LICENSE-2.0.html\n   :alt: License\n\n------------\n\nPackages\n--------\n\n.. image:: https://img.shields.io/pypi/v/rpaframework.svg?label=rpaframework&style=for-the-badge\n   :target: https://pypi.python.org/pypi/rpaframework\n   :alt: rpaframework latest version\n\n\n.. image:: https://img.shields.io/pypi/v/rpaframework-core.svg?label=rpaframework-core&style=for-the-badge\n   :target: https://pypi.python.org/pypi/rpaframework-core\n   :alt: rpaframework-core latest version\n\n\n\n.. image:: https://img.shields.io/pypi/v/rpaframework-dialogs.svg?label=rpaframework-dialogs&style=for-the-badge&color=blue\n   :target: https://pypi.python.org/pypi/rpaframework-dialogs\n   :alt: rpaframework-dialogs latest version\n\n\n\n.. image:: https://img.shields.io/pypi/v/rpaframework-google.svg?label=rpaframework-google&style=for-the-badge&color=blue\n   :target: https://pypi.python.org/pypi/rpaframework-google\n   :alt: rpaframework-google latest version\n\n\n\n.. image:: https://img.shields.io/pypi/v/rpaframework-pdf.svg?label=rpaframework-pdf&style=for-the-badge&color=blue\n   :target: https://pypi.python.org/pypi/rpaframework-pdf\n   :alt: rpaframework-pdf latest version\n\n\n\n.. image:: https://img.shields.io/pypi/v/rpaframework-recognition.svg?label=rpaframework-recognition&style=for-the-badge&color=blue\n   :target: https://pypi.python.org/pypi/rpaframework-recognition\n   :alt: rpaframework-recognition latest version\n\n\n\n.. image:: https://img.shields.io/pypi/v/rpaframework-windows.svg?label=rpaframework-windows&style=for-the-badge&color=blue\n   :target: https://pypi.python.org/pypi/rpaframework-windows\n   :alt: rpaframework-windows latest version\n\nFrom the above packages **rpaframework-core** and **rpaframework-recognition** are support packages, which themselves do **not** contain any libraries.\n\n\nLibraries\n---------\n\nThe RPA Framework project currently includes the following libraries:\n\nThe ``x`` in the **PACKAGE** column means that library **is** included in the **rpaframework** package and for example. ``x,dialogs`` means that ``RPA.Dialogs`` library is provided in both the **rpaframework** and **rpaframework-dialogs** packages.\n\n+----------------------------+----------------------------------------------+-------------+\n| **LIBRARY NAME**           | **DESCRIPTION**                              | **PACKAGE** |\n+----------------------------+----------------------------------------------+-------------+\n| `Archive`_                 | Archiving TAR and ZIP files                  | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Browser.Selenium`_        | Control browsers and automate the web        | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Browser.Playwright`_      | Newer way to control browsers                | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Cloud.AWS`_               | Use Amazon AWS services                      | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Cloud.Azure`_             | Use Microsoft Azure services                 | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Cloud.Google`_            | Use Google Cloud services                    | google      |\n+----------------------------+----------------------------------------------+-------------+\n| `Crypto`_                  | Common hashing and encryption operations     | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Database`_                | Interact with databases                      | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Desktop`_                 | Cross-platform desktop automation            | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Desktop.Clipboard`_       | Interact with the system clipboard           | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Desktop.OperatingSystem`_ | Read OS information and manipulate processes | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Desktop.Windows`_         | Automate Windows desktop applications        | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Dialogs`_                 | Request user input during executions         | x,dialogs   |\n+----------------------------+----------------------------------------------+-------------+\n| `Email.Exchange`_          | E-Mail operations (Exchange protocol)        | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Email.ImapSmtp`_          | E-Mail operations (IMAP & SMTP)              | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Excel.Application`_       | Control the Excel desktop application        | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Excel.Files`_             | Manipulate Excel files directly              | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `FileSystem`_              | Read and manipulate files and paths          | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `FTP`_                     | Interact with FTP servers                    | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `HTTP`_                    | Interact directly with web APIs              | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Images`_                  | Manipulate images                            | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `JavaAccessBridge`_        | Control Java applications                    | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `JSON`_                    | Manipulate JSON objects                      | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Notifier`_                | Notify messages using different services     | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Outlook.Application`_     | Control the Outlook desktop application      | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `PDF`_                     | Read and create PDF documents                | x,pdf       |\n+----------------------------+----------------------------------------------+-------------+\n| `Robocorp.Process`_        | Use the Robocorp Process API                 | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Robocorp.WorkItems`_      | Use the Robocorp Work Items API              | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Robocorp.Vault`_          | Use the Robocorp Secrets API                 | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Salesforce`_              | Salesforce operations                        | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `SAP`_                     | Control SAP GUI desktop client               | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Tables`_                  | Manipulate, sort, and filter tabular data    | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Tasks`_                   | Control task execution                       | x           |\n+----------------------------+----------------------------------------------+-------------+ \n| `Twitter`_                 | Twitter API interface                        | x           |\n+----------------------------+----------------------------------------------+-------------+\n| `Windows`_                 | Alternative library for Windows automation   | windows     |\n+----------------------------+----------------------------------------------+-------------+\n| `Word.Application`_        | Control the Word desktop application         | x           |\n+----------------------------+----------------------------------------------+-------------+\n\n.. _Archive: https://rpaframework.org/libraries/archive/\n.. _Browser.Playwright: https://rpaframework.org/libraries/browser_playwright/\n.. _Browser.Selenium: https://rpaframework.org/libraries/browser_selenium/\n.. _Cloud.AWS: https://rpaframework.org/libraries/cloud_aws/\n.. _Cloud.Azure: https://rpaframework.org/libraries/cloud_azure/\n.. _Cloud.Google: https://rpaframework.org/libraries/cloud_google/\n.. _Crypto: https://rpaframework.org/libraries/crypto/\n.. _Database: https://rpaframework.org/libraries/database/\n.. _Desktop: https://rpaframework.org/libraries/desktop/\n.. _Desktop.Clipboard: https://rpaframework.org/libraries/desktop_clipboard/\n.. _Desktop.Operatingsystem: https://rpaframework.org/libraries/desktop_operatingsystem/\n.. _Desktop.Windows: https://rpaframework.org/libraries/desktop_windows/\n.. _Dialogs: https://rpaframework.org/libraries/dialogs/\n.. _Email.Exchange: https://rpaframework.org/libraries/email_exchange/\n.. _Email.ImapSmtp: https://rpaframework.org/libraries/email_imapsmtp/\n.. _Excel.Application: https://rpaframework.org/libraries/excel_application/\n.. _Excel.Files: https://rpaframework.org/libraries/excel_files/\n.. _FileSystem: https://rpaframework.org/libraries/filesystem/\n.. _FTP: https://rpaframework.org/libraries/ftp/\n.. _HTTP: https://rpaframework.org/libraries/http/\n.. _Images: https://rpaframework.org/libraries/images/\n.. _JavaAccessBridge: https://rpaframework.org/libraries/javaaccessbridge/\n.. _JSON: https://rpaframework.org/libraries/json/\n.. _Notifier: https://rpaframework.org/libraries/notifier/\n.. _Outlook.Application: https://rpaframework.org/libraries/outlook_application/\n.. _PDF: https://rpaframework.org/libraries/pdf/\n.. _Robocorp.Process: https://rpaframework.org/libraries/robocorp_process/\n.. _Robocorp.WorkItems: https://rpaframework.org/libraries/robocorp_workitems/\n.. _Robocorp.Vault: https://rpaframework.org/libraries/robocorp_vault/\n.. _Salesforce: https://rpaframework.org/libraries/salesforce/\n.. _SAP: https://rpaframework.org/libraries/sap/\n.. _Tables: https://rpaframework.org/libraries/tables/\n.. _Tasks: https://rpaframework.org/libraries/tasks/\n.. _Twitter: https://rpaframework.org/libraries/twitter/\n.. _Windows: https://rpaframework.org/libraries/windows/\n.. _Word.Application: https://rpaframework.org/libraries/word_application/\n\nInstallation\n------------\n\nLearn about installing Python packages at `Installing Python Packages`_.\n\nDefault installation method with Robocorp `Developer Tools`_ using conda.yaml:\n\n.. code-block:: yaml\n\n   channels:\n     - conda-forge\n   dependencies:\n     - python=3.7.5\n     - pip=20.1\n     - pip:\n       - rpaframework==12.0.0\n\nTo install all extra packages (including Playwright dependencies), you can use:\n\n.. code-block:: yaml\n\n   channels:\n     - conda-forge\n   dependencies:\n     - python=3.7.5\n     - tesseract=4.1.1\n     - pip=20.1\n     - nodejs=14.17.4\n     - pip:\n       - rpaframework[aws]==12.0.0\n       - rpaframework-google==1.0.0\n       - rpaframework-recognition==1.0.0\n       - rpaframework-windows==1.2.1\n       - robotframework-browser==10.0.3\n   rccPostInstall:\n     - rfbrowser init\n\nSeparate installation of PDF and Dialogs libraries without main rpaframework:\n\n.. code-block:: yaml\n\n   channels:\n     - conda-forge\n   dependencies:\n     - python=3.7.5\n     - pip=20.1\n     - pip:\n       - rpaframework-dialogs==0.4.2  # included in the rpaframework by default\n       - rpaframework-pdf==1.26.11  # included in the rpaframework by default\n\n\n.. note:: Python 3.6 or higher is required\n\nExample\n-------\n\nAfter installation the libraries can be directly imported inside\n`Robot Framework`_:\n\n.. code:: robotframework\n\n    *** Settings ***\n    Library    RPA.Browser.Selenium\n\n    *** Tasks ***\n    Login as user\n        Open available browser    https://example.com\n        Input text    id:user-name    ${USERNAME}\n        Input text    id:password     ${PASSWORD}\n\nThe libraries are also available inside Python_:\n\n.. code:: python\n\n    from RPA.Browser.Selenium import Selenium\n\n    lib = Selenium()\n\n    lib.open_available_browser("https://example.com")\n    lib.input_text("id:user-name", username)\n    lib.input_text("id:password", password)\n\nSupport and contact\n-------------------\n\n- `rpaframework.org <https://rpaframework.org/>`_ for library documentation\n- `Robocorp Documentation`_ for guides and tutorials\n- **#rpaframework** channel in `Robot Framework Slack`_ if you\n  have open questions or want to contribute\n- `Robocorp Forum`_ for discussions about RPA\n- Communicate with your fellow Software Robot Developers and Robocorp experts\n  at `Robocorp Developers Slack`_\n\n.. _Robot Framework Slack: https://robotframework-slack-invite.herokuapp.com/\n.. _Robocorp Forum: https://forum.robocorp.com\n.. _Robocorp Developers Slack: https://robocorp-developers.slack.com\n\nContributing\n------------\n\nFound a bug? Missing a critical feature? Interested in contributing?\nHead over to the `Contribution guide <https://rpaframework.org/contributing/guide.html>`_\nto see where to get started.\n\nLicense\n-------\n\nThis project is open-source and licensed under the terms of the\n`Apache License 2.0 <http://apache.org/licenses/LICENSE-2.0>`_.\n',
    'author': 'RPA Framework',
    'author_email': 'rpafw@robocorp.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://rpaframework.org/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
