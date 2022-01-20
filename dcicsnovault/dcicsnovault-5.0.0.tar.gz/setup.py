# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['snovault', 'snovault.commands', 'snovault.elasticsearch', 'snovault.tests']

package_data = \
{'': ['*'], 'snovault': ['test_schemas/*']}

install_requires = \
['MarkupSafe>=0.23,<1',
 'Pillow>=6.2.2,<7.0.0',
 'PyBrowserID>=0.10.0,<0.11.0',
 'PyYAML>=5.1,<5.3',
 'SPARQLWrapper>=1.8.5,<2.0.0',
 'SQLAlchemy==1.3.16',
 'WSGIProxy2==0.4.2',
 'WebOb>=1.8.7,<2.0.0',
 'WebTest>=2.0.35,<3.0.0',
 'aws_requests_auth>=0.4.1,<0.5.0',
 'backports.statistics==0.1.0',
 'boto3>=1.17.53,<2.0.0',
 'dcicutils>=3.5.0,<4.0.0',
 'elasticsearch==6.8.1',
 'elasticsearch_dsl>=6.4.0,<7.0.0',
 'future>=0.15.2,<0.16.0',
 'futures>=3.1.1,<4.0.0',
 'html5lib==0.9999999',
 'humanfriendly>=1.44.9,<2.0.0',
 'jsonschema_serialize_fork>=2.1.1,<3.0.0',
 'netaddr>=0.8.0,<1',
 'passlib>=1.7.4,<2.0.0',
 'psutil>=5.8.0,<6.0.0',
 'psycopg2>=2.9.1,<3.0.0',
 'pyramid-multiauth>=0.9.0,<1',
 'pyramid-retry>=1.0,<2.0',
 'pyramid-tm>=2.4,<3.0',
 'pyramid-translogger>=0.1,<0.2',
 'pyramid==1.10.4',
 'pyramid_localroles>=0.1,<1',
 'python-dateutil>=2.8.2,<3.0.0',
 'python_magic==0.4.15',
 'pytz>=2021.1',
 'rdflib-jsonld>=0.5.0,<1.0.0',
 'rdflib>=4.2.2,<5.0.0',
 'rutter>=0.3,<1',
 'simplejson>=3.17.0,<4.0.0',
 'structlog>=19.2.0,<20',
 'subprocess_middleware>=0.3,<1',
 'transaction>=2.4.0,<3.0.0',
 'venusian>=1.2.0,<2.0.0',
 'xlrd>=1.0.0,<2.0.0',
 'zope.deprecation>=4.4.0,<5.0.0',
 'zope.interface>=4.7.2,<5.0.0',
 'zope.sqlalchemy==1.3']

entry_points = \
{'console_scripts': ['wipe-test-indices = '
                     'snovault.commands.wipe_test_indices:main']}

setup_kwargs = {
    'name': 'dcicsnovault',
    'version': '5.0.0',
    'description': 'Storage support for 4DN Data Portals.',
    'long_description': '=============\nDCIC Snovault\n=============\n\n|Build status|_\n\n.. |Build status| image:: https://travis-ci.org/4dn-dcic/snovault.svg?branch=master\n.. _Build status: https://travis-ci.org/4dn-dcic/snovault\n\n.. Important::\n\n DCIC Snovault is a FORK of `snovault <https://pypi.org/project/snovault/>`_\n created at the `ENCODE DCC project at Stanford <https://github.com/ENCODE-DCC>`_.\n Our fork supports other projects of the\n `4D Nucleome Data Coordination and Integration Center (4DN-DCIC)\n <https://github.com/4dn-dcic>`_.\n Although this software is available as open source software,\n its primary function is to support our layered projects,\n and we are not at this time able to offer any active support for other uses.\n In particular, this fork does not purport to supersede\n the original `snovault <https://pypi.org/project/snovault/>`_.\n we just have a different use case that we are actively exploring.\n\nOverview\n========\n\nDCIC Snovault is a JSON-LD Database Framework that serves as the backend for the 4DN Data portal and CGAP. Check out our full documentation `here\n<https://snovault.readthedocs.io/en/latest/>`_.\n\n.. note::\n\n    This repository contains a core piece of functionality shared amongst several projects\n    in the 4DN-DCIC. It is meant to be used internally by the DCIC team\n    in support of `Fourfront <https://data.4dnucleome.org>`_\\ ,\n    the 4DN data portal, and at this point in time it is not expected to be useful\n    in a standalone/plug-and-play way to others.\n\nInstallation in 4DN components\n==============================\n\nDCIC Snovault is pip installable as the ``dcicsnovault`` package with::\n\n    $ pip install dcicsnovault``\n\nHowever, at the present time, the functionality it provides might only be useful in conjunction\nwith other 4DN-DCIC components.\n\nNOTE: If you\'d like to enable Elasticsearch mapping with type=nested, set the environment variable "MAPPINGS_USE_NESTED"\nor set the registry setting "mappings.use_nested".\n\nInstallation for Development\n============================\n\nCurrently these are for Mac OSX using homebrew. If using linux, install dependencies with a different package manager.\n\nStep 0: Install Xcode\n---------------------\n\nInstall Xcode (from App Store) and homebrew: http://brew.sh\n\nStep 1: Verify Homebrew Itself\n------------------------------\n\nVerify that homebrew is working properly::\n\n    $ brew doctor\n\nStep 2: Install Homebrewed Dependencies\n---------------------------------------\n\nInstall or update dependencies::\n\n    $ brew install libevent libmagic libxml2 libxslt openssl postgresql graphviz python3\n    $ brew install freetype libjpeg libtiff littlecms webp  # Required by Pillow\n    $ brew cask install adoptopenjdk8\n    $ brew install elasticsearch@5.6\n\nNOTES:\n\n* If installation of adtopopenjdk8 fails due to an ambiguity, it should work to do this instead::\n\n    $ brew cask install homebrew/cask-versions/adoptopenjdk8\n\n* If you try to invoke elasticsearch and it is not found,\n  you may need to link the brew-installed elasticsearch::\n\n    $ brew link --force elasticsearch@5.6\n\n* If you need to update dependencies::\n\n    $ brew update\n    $ rm -rf encoded/eggs\n\n* If you need to upgrade brew-installed packages that don\'t have pinned versions,\n  you can use the following. However, take care because there is no command to directly\n  undo this effect::\n\n    $ brew update\n    $ brew upgrade\n    $ rm -rf encoded/eggs\n\nStep 3: Running Poetry\n----------------------\n\nTo locally install using versions of Python libraries that have worked before, use this::\n\n    $ poetry install\n\n\nUpdating dependencies\n=====================\n\nTo update the version dependencies, use::\n\n    $ poetry update\n\nThis command also takes space-separated names of specific packages to update. For more information, do::\n\n    $ poetry help update\n\n\nManaging poetry.lock after update\n---------------------------------\n\nThere may be situations where you do this with no intent to check in the resulting updates,\nbut once you have checked that the updates are sound, you may wish to check the resulting\n``poetry.lock`` file.\n\nPublishing\n==========\n\nNormally, a successful build on a tagged branch (including a branch tagged as a beta)\nwill cause publication automatically. The process begins by obtaining the version. You might do\n\n    $ head pyproject.toml\n\nto see the first few lines of `pyproject.toml`, which will contain a line like ``version = 100.200.300``, which\nis the ``snovault`` version.  You should prepend the letter ``v`` to that version, and create the tag and push\nit to the GitHub server:\n\n    $ git tag v100.200.300\n    $ git push origin v100.200.300\n\nPlease do NOT use some other syntax for ``git push`` that pushes all of your tags. That might pick up tags that\ndo not belong on the server and can generally cause tag pollution. Push specifically the tag you intend to publish.\n\nPushing such a tag should trigger publication automatically within a few minutes.\n\nManual Publication\n------------------\n\nThere might be rare occasions where you need to do the publication manually, but normally it is not necessary\nor desirable. In most cases, it will either fail or will cause the automatic publication step to fail. The main\ncase where this is known to be needed is where publication has failed on a tagged branch for reasons other than\nthe fact of that tag being already published (e.g., a network interruption or a premature shutdown of the GitHub\nActions task). An incomplete publication on GitHub Actions cannot be easily retried, so only in that case you may\nneed to do:\n\n    $ make publish\n\nHowever, to do this command locally, you would need appropriate credentials on PyPi for such publication to succeed.\nAs presently configured, these credentials need to be in the environment variables ``PYPI_USER`` and ``PYPI_PASSWORD``.\nThe script that runs if you manually attempt ``make publish`` checks that you have properly declared credentials\nbefore it attempts to publish. Note that GitHub Actions is already configured with credentials, so you do not\nneed to worry about them if you just push a tag and let the pre-defined action do the publication.\n\nRunning tests\n=============\n\nTo run specific tests locally::\n\n    $ bin/test -k test_name\n\nTo run with a debugger::\n\n    $ bin/test --pdb\n\nSpecific tests to run locally for schema changes::\n\n    $ bin/test -k test_load_workbook\n\nRun the Pyramid tests with::\n\n    $ bin/test\n\n',
    'author': '4DN-DCIC Team',
    'author_email': 'support@4dnucleome.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/4dn-dcic/snovault',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.1,<3.7',
}


setup(**setup_kwargs)
