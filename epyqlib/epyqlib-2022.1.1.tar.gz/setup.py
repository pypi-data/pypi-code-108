# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['epyqlib',
 'epyqlib.autodevice',
 'epyqlib.autodevice.template',
 'epyqlib.cli',
 'epyqlib.pm',
 'epyqlib.tabs',
 'epyqlib.tabs.files',
 'epyqlib.tests',
 'epyqlib.tests.autodevice',
 'epyqlib.tests.pm',
 'epyqlib.tests.sync',
 'epyqlib.tests.utils',
 'epyqlib.twisted',
 'epyqlib.utils',
 'epyqlib.widgets']

package_data = \
{'': ['*'], 'epyqlib': ['resources/*']}

install_requires = \
['GitPython==2.1.15',
 'Pint==0.11',
 'PyQt5==5.14.1',
 'PyQt5Designer>=5.14.1,<6.0.0',
 'QtAwesome==0.6.0',
 'Twisted==21.2.0',
 'alqtendpy==0.0.4',
 'appdirs==1.4.3',
 'arrow==0.12.1',
 'attrs==19.3.0',
 'bitstruct==6.0.0',
 'black==20.8b1',
 'boto3-type-annotations==0.3.1',
 'boto3==1.14.41.0',
 'canmatrix==0.9.1',
 'certifi==2020.6.20',
 'click==7.1.2',
 'dulwich==0.20.6',
 'fab==3.0.0',
 'graham==0.1.11',
 'marshmallow==2.16.3',
 'natsort==5.5.0',
 'paho-mqtt==1.4.0',
 'pyelftools==0.25',
 'pysunspec>=2.1.1,<3.0.0',
 'pytest-qt==3.3.0',
 'pytest-rerunfailures==5.0',
 'pytest-twisted==1.12',
 'pytest-xvfb==1.2.0',
 'pytest==5.3.5',
 'python-can>=3.3.4,<4.0.0',
 'python-dateutil==2.7.5',
 'python-docx==0.8.7',
 'python-dotenv==0.9.1',
 'qt5reactor==0.5',
 'siphash-cffi>=0.1.4,<0.2.0',
 'sunspecdemo>=0.1.6,<0.2.0',
 'treq==21.1.0',
 'twine==1.13.0']

extras_require = \
{':sys_platform == "Darwin"': ['certitude==1.0.1']}

entry_points = \
{'console_scripts': ['autodevice = epyqlib.autodevice.cli:cli',
                     'buildui = buildui:compile_ui',
                     'cangenmanual = epyqlib.cangenmanual:_entry_point',
                     'collectdevices = epyqlib.collectdevices:main',
                     'contiguouscommits = '
                     'epyqlib.utils.contiguouscommits:_entry_point [dulwich]',
                     'epyqflash = epyqlib.flash:_entry_point',
                     'epyqlib = epyqlib.cli.main:cli',
                     'genbuildinfo = epyqlib.genbuildinfo:write_build_file',
                     'generateversion = epyqlib.cli.generateversion:cli',
                     'patchvenv = epyqlib.patchvenv:main',
                     'updateepc = epyqlib.updateepc:main',
                     'versionfile = epyqlib.cli.versionfile:cli'],
 'pytest11': ['epyqlib = epyqlib.tests.pytest_plugin']}

setup_kwargs = {
    'name': 'epyqlib',
    'version': '2022.1.1',
    'description': '',
    'long_description': None,
    'author': 'Alex Anker',
    'author_email': 'alex.anker@epcpower.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
