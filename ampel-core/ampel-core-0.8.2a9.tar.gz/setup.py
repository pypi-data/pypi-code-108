# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ampel',
 'ampel.abstract',
 'ampel.aux',
 'ampel.aux.filter',
 'ampel.cli',
 'ampel.config',
 'ampel.config.builder',
 'ampel.config.collector',
 'ampel.core',
 'ampel.demo',
 'ampel.dev',
 'ampel.ingest',
 'ampel.log',
 'ampel.log.handlers',
 'ampel.metrics',
 'ampel.model',
 'ampel.model.aux',
 'ampel.model.builder',
 'ampel.model.ingest',
 'ampel.model.purge',
 'ampel.model.t3',
 'ampel.model.time',
 'ampel.mongo',
 'ampel.mongo.model',
 'ampel.mongo.query',
 'ampel.mongo.query.var',
 'ampel.mongo.update',
 'ampel.mongo.update.var',
 'ampel.mongo.view',
 'ampel.ops',
 'ampel.run',
 'ampel.secret',
 'ampel.t1',
 'ampel.t2',
 'ampel.t3',
 'ampel.t3.include.session',
 'ampel.t3.stage',
 'ampel.t3.stage.filter',
 'ampel.t3.stage.project',
 'ampel.t3.supply',
 'ampel.t3.supply.complement',
 'ampel.t3.supply.load',
 'ampel.t3.supply.select',
 'ampel.template',
 'ampel.test',
 'ampel.util',
 'ampel.vendor.aiopipe']

package_data = \
{'': ['*'], 'ampel.test': ['test-data/*']}

install_requires = \
['PyYAML>=5.4,<7.0',
 'ampel-interface>=0.8.2-alpha.7,<0.8.3',
 'prometheus-client>=0.10,<0.12',
 'psutil>=5.8.0,<6.0.0',
 'pydantic>=1.8.1,<1.9',
 'pymongo>=4.0,<5.0',
 'schedule>=1.0.0,<2.0.0',
 'sjcl>=0.2.1,<0.3.0',
 'slackclient>=2.7,<3.0',
 'ujson>=4.0.0,<5.0.0',
 'xxhash>=2.0.2,<3.0.0',
 'yq>=2.12.0,<3.0.0']

extras_require = \
{'docs': ['Sphinx>=3.5.1,<5.0.0',
          'sphinx-press-theme>=0.5.1,<0.9.0',
          'sphinx-autodoc-typehints>=1.11.1,<2.0.0',
          'tomlkit>=0.7.0,<0.8.0'],
 'server': ['fastapi>=0.63,<0.69', 'uvicorn[standard]>=0.13.3,<0.16.0']}

entry_points = \
{'cli': ['buffer_Match_and_view_or_save_ampel_buffers = '
         'ampel.cli.BufferCommand',
         'config_Build_or_update_config._Fetch_or_append_config_elements = '
         'ampel.cli.ConfigCommand',
         'db_Initialize,_dump,_delete_specific_databases_or_collections = '
         'ampel.cli.DBCommand',
         'job_Run_provided_job_file = ampel.cli.JobCommand',
         'log_Select,_format_and_either_view_or_save_logs._Tail_mode_availabe '
         '= ampel.cli.LogCommand',
         'run_Run_selected_process(es)_from_config = ampel.cli.RunCommand',
         'start_Run_ampel_continuously._Processes_are_scheduled_according_to_config '
         '= ampel.cli.StartCommand',
         't2_Match_and_either_reset_or_view_raw_t2_documents = '
         'ampel.cli.T2Command',
         'view_Select,_load_and_save_fresh_"ampel_views" = '
         'ampel.cli.ViewCommand'],
 'console_scripts': ['ampel = ampel.cli.main:main',
                     'ampel-config = ampel.config.cli:main',
                     'ampel-controller = '
                     'ampel.core.AmpelController:AmpelController.main',
                     'ampel-db = ampel.db.AmpelDB:main']}

setup_kwargs = {
    'name': 'ampel-core',
    'version': '0.8.2a9',
    'description': 'Asynchronous and Modular Platform with Execution Layers',
    'long_description': '<img align="left" src="https://desycloud.desy.de/index.php/s/99Jkcyzn92rRpHF/preview" width="150" height="150"/>\n<br>\n\n# AMPEL-core\n<br><br>\n\n# Introduction\n\nAMPEL is a _modular_ and _scalable_ platform with explicit _provenance_ tracking, suited for systematically processing large - possibly complex and heterogeneous - datasets in real-time or not. This includes selecting, analyzing, updating, combining, enriching and reacting to data.\n\nThe framework requires analysis and reaction logic to be broken down in adequate indepentent units.\nAMPEL is general enough to be applicable in various fields,\nit was originaly developped to solve challenges in the context of experimental astrophysics.\n\nAMPEL is written in Python 3.9 and its codebase is fully typed.\n \n\n# Architecture\n\n## Tiers\nAMPEL is made of four execution layers (tiers) that replace a traditional pipeline architecture.\n<img align="left" src="https://desycloud.desy.de/index.php/s/fz2mnsH4MGEKwfD/preview"/>\n\nThe tiers are independently scheduled and the information exchange between tiers occurs via a dedicated database.\nThe execution layer architecture along with the database structure allow for simple parallelization.\n\n## Units\nEach tier is modular and executes so-called "units".\n\n<p align="center">\n<img src="https://desycloud.desy.de/index.php/s/P76f9qSWJse8oT7/preview" width=50%/>\n</p>\n\nAmpel _base units_ have standardized inputs and ouputs, enforced through abstract classes which units inherit.\n\n## Processes\n\nEvery change in AMPEL is triggered by a _process_.\nA process executes, at a given date and time, a _processor unit_ that itself runs one or multiple _base units_ with specific configurations.\nInformation about process executions are registred into the database.\nThe majority of processes are associated with a specific tier but general processes are possible.\n\nA working AMPEL system will spawn multiple processes, posssibly concurently, accross the four AMPEL tiers.\nThis will result in the ingestion and analysis of data and the triggering of automated reactions when given data states are detected.\n\n## Channels\n\n_Channels_ are convenient for multi-user or multi-prupose AMPEL systems.\nThey allow to define and enforce access rights and to privatize processes,\nmeaning that the output generated by the processes will be only accessible to processes\nbelonging to the same channel.\n\nInternally, _channels_ are just tags in database documents and ampel configuration files.  \nFrom a user perspective, a channel can be seen as a collection of private processes.\n\n<p align="center">\n<img src="https://desycloud.desy.de/index.php/s/YMiGJ2zckgEr54n/preview" width=50%/>\n<br/>\nProcesses associated with a given channel\n</p>\n\nNote that within AMPEL, different _channels_ requiring the same computation\nwill not result in the required computation being performed twice.\n\n\n# Repositories\n\nThe AMPEL code is partitioned in different repositories.  \nThe only mandatory repository in this list is _ampel-interface_\n\nPublic abstract class definitions:  \nhttps://github.com/AmpelProject/Ampel-interface\n\nSpecialized classes for Tier 0, capable of handling _alerts_:  \nhttps://github.com/AmpelProject/Ampel-alerts\n\nAn add-on that introduces two generic classes of datapoints:  \nhttps://github.com/AmpelProject/Ampel-photometry\n\nExample of an instrument specific implementation:  \nhttps://github.com/AmpelProject/Ampel-ztf\n\nNumerous _base units_, the majority being specific to astronomy:  \nhttps://github.com/AmpelProject/Ampel-contrib-HU/\n\n\n# Database\n\nMongoDB is used to store data.\nThe collections have been designed and indexed for fast insertion and query.\nUsers do not interact with the database directly.\nInformation exchange is instead regulated through (python) abstract base classes from which units are constructed.\nA specific set of internal classes handle database input and output.\n\n\n# Containers\n\nAll AMPEL software, can be combined into one container that defines an instance.\nThese containers can be used both to process real-time data as well as to reprocess archived data.\nThe containers themselves should be archived as well.\n\n<!--\nAstronomers have during the past century continuously refined tools for\nanalyzing individual astronomical transients. Simultaneously, progress in instrument and CCD\nmanufacturing as well as new data processing capabilities have led to a new generation of transient\nsurveys that can repeatedly scan large volumes of the Universe. With thousands of potential candidates\navailable, scientists are faced with a new kind of questions: Which transient should I focus on?\nWhat were those things that I dit not look at? Can I have them all?\n\nAmpel is a software framework meant to assist in answering such questions.\nIn short, Ampel assists in the the transition from studies of individual objects\n(based on more or less random selection) to systematically selected samples.\nOur design goals are to find a system where past experience (i.e. existing algorithms and code) can consistently be applied to large samples, and with built-in tools for controlling sample selection.\n-->\n\n# Installing Ampel\n\nThe latest release of `ampel-core` can be installed from PyPI with `pip`, e.g.:\n\n```\npip install ampel-core\n```\n\nOther projects like `ampel-alerts`, `ampel-ztf`, etc. can also be installed with `pip`.\n\n# Development\n\n`ampel-core` uses [poetry](http://poetry.eustace.io/) for dependency management and packaging. To work with an editable install it\'s recommended that you set up `poetry` and install `ampel-core` in a virtual environment by doing\n\n```console\npoetry install\n```\n\nAlternatively, may also use a `setuptools`-style editable install from `setup.py`:\n\n```console\npip install -e .\n```\n\nNote that `setup.py` and `requirements.txt` are auto-generated; any changes you commit will be overwritten the next time `pyproject.toml` is updated.\n',
    'author': 'Valery Brinnel',
    'author_email': None,
    'maintainer': 'Jakob van Santen',
    'maintainer_email': 'jakob.van.santen@desy.de',
    'url': 'https://ampelproject.github.io',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.10',
}


setup(**setup_kwargs)
