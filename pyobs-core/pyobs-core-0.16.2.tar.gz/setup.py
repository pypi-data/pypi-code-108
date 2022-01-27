# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyobs',
 'pyobs.cli',
 'pyobs.comm',
 'pyobs.comm.dummy',
 'pyobs.comm.sleekxmpp',
 'pyobs.comm.sleekxmpp.xep_0009',
 'pyobs.comm.sleekxmpp.xep_0009_timeout',
 'pyobs.comm.sleekxmpp.xep_0009_timeout.stanza',
 'pyobs.comm.slixmpp',
 'pyobs.comm.slixmpp.xep_0009',
 'pyobs.comm.slixmpp.xep_0009_timeout',
 'pyobs.comm.slixmpp.xep_0009_timeout.stanza',
 'pyobs.events',
 'pyobs.images',
 'pyobs.images.meta',
 'pyobs.images.processors',
 'pyobs.images.processors.astrometry',
 'pyobs.images.processors.detection',
 'pyobs.images.processors.exptime',
 'pyobs.images.processors.misc',
 'pyobs.images.processors.offsets',
 'pyobs.images.processors.photometry',
 'pyobs.interfaces',
 'pyobs.mixins',
 'pyobs.modules',
 'pyobs.modules.camera',
 'pyobs.modules.flatfield',
 'pyobs.modules.focus',
 'pyobs.modules.image',
 'pyobs.modules.pointing',
 'pyobs.modules.robotic',
 'pyobs.modules.roof',
 'pyobs.modules.telescope',
 'pyobs.modules.test',
 'pyobs.modules.utils',
 'pyobs.modules.weather',
 'pyobs.robotic',
 'pyobs.robotic.lco',
 'pyobs.robotic.scripts',
 'pyobs.utils',
 'pyobs.utils.archive',
 'pyobs.utils.focusseries',
 'pyobs.utils.offsets',
 'pyobs.utils.pipeline',
 'pyobs.utils.publisher',
 'pyobs.utils.simulation',
 'pyobs.utils.skyflats',
 'pyobs.utils.skyflats.pointing',
 'pyobs.utils.skyflats.priorities',
 'pyobs.utils.threads',
 'pyobs.vfs',
 'pyobs.vfs.filelists']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'aiohttp>=3.8.1,<4.0.0',
 'astroplan>=0.8,<0.9',
 'astropy>=5.0,<6.0',
 'astroquery>=0.4.4,<0.5.0',
 'ccdproc>=2.2,<3.0',
 'lmfit>=1.0,<2.0',
 'numpy>=1.21,<2.0',
 'pandas>=1.1.5,<2.0.0',
 'paramiko>=2.8,<3.0',
 'photutils>=1.2,<2.0',
 'py-expression-eval>=0.3,<0.4',
 'python-telegram-bot>=13.8,<14.0',
 'pytz>=2021.3,<2022.0',
 'requests>=2.26,<3.0',
 'scipy>=1.7.2,<2.0.0',
 'single-source>=0.2.0,<0.3.0',
 'sleekxmpp>=1.3,<2.0',
 'slixmpp>=1.7.1,<2.0.0',
 'tornado>=6.1,<7.0',
 'typing-extensions>=4.0,<5.0']

extras_require = \
{':sys_platform == "linux"': ['sep>=1.2,<2.0',
                              'python-daemon>=2.3,<3.0',
                              'asyncinotify>=2.0.2,<3.0.0']}

entry_points = \
{'console_scripts': ['pyobs = pyobs.cli.pyobs:main',
                     'pyobsd = pyobs.cli.pyobsd:main',
                     'pyobsw = pyobs.cli.pyobsw:main']}

setup_kwargs = {
    'name': 'pyobs-core',
    'version': '0.16.2',
    'description': 'robotic telescope software',
    'long_description': None,
    'author': 'Tim-Oliver Husser',
    'author_email': 'thusser@uni-goettingen.de',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
