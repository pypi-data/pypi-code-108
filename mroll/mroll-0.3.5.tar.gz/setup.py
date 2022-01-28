# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['mroll', 'mroll.databases', 'mroll.templates']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0', 'pymonetdb>=1.3.1,<2.0.0', 'sqlparse>=0.3.1,<0.4.0']

entry_points = \
{'console_scripts': ['mroll = mroll.commands:cli']}

setup_kwargs = {
    'name': 'mroll',
    'version': '0.3.5',
    'description': 'monetdb migration tool',
    'long_description': '![mroll ci](https://github.com/MonetDBSolutions/mroll/workflows/ci_workflow/badge.svg)\n\n# Mroll migration tool\n`mroll` has been designed to aid MonetDB users with managing database migrations.\nThe functionality covers both roll forward and backward migration functionality.\nAlthough you can deploy `mroll` from any point in time onwards, it is advised to use it\nfrom day one, i.e. the creation of the database.\n`mroll` has been used internally to manage the continuous integration workflow of MonetDB.\n\n## Install\n\nInstall mroll from PyPi\n\n```\n$ pip install mroll\n```\n\n## Synopsis\nThe command synopsis summarizes the functionality.\n\n```\n$ mroll --help\nUsage: commands.py [OPTIONS] COMMAND1 [ARGS]... [COMMAND2 [ARGS]...]...\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  config    Set up mroll configuration under $HOME/.config/mroll\n  history   Shows applied revisions.\n  init      Creates mroll_revisions tbl.\n  revision  Creates new revision from a template.\n  rollback  Downgrades to previous revision by default.\n  setup     Set up work directory.\n  show      Shows revisions information.\n  upgrade   Applies all revisions not yet applied in work dir.\n  version   Shows current version\n```\n\nEach command may come with some options, explained by the `--help` addition.\nFor example, the location of the migration directory can be specified when you install mroll\nwith an option `--path` option to specify location. For an example, `--path "/tmp/migration"` location.\n\nTo update/set `mroll` configuration use the `config` command.\nFor example to update configuration setting for working directory path run.\n```\nmroll config -p <workdir_path>\n```\n\n## Usage\nTo illustrate the functionality we walk you through the steps to get a MonetDB database, called\n*demo*, created and managed. We assume you have downloaded `mroll` (see below) and are all set to give it a try.\n\n#### Setup \n`mroll` needs a working directory for each database you want to manage. There is no restriction on\nits location, but you could keep the migration scripts in your application \nfolder, e.g. `.../app/migrations`. From the `.../app` directory issue the command:\n\n```\n$ mroll setup\nok\n```\nA subdirectory `migrations` is being created to manage migrations versions.\n\n#### Configuration\n`mroll` needs information on the database whereabouts and credentials to initiate the migration steps.\nMake sure you have already created and released the demo database using the `monetdb` tools.\nThen complete the file `migrations/mroll.ini` to something like:\n```\n[db]\ndb_name=demo\nuser=monetdb\npassword=monetdb\nport=50000\n\n[mroll]\nrev_history_tbl_name = mroll_revisions\n```\nThe final step for managing the migrations is\n```\n$ mroll init\n```\n#### Define the first revision\nThe empty database will be populated with a database schema.\nFor this we define a revision. Revision names are generated\n\n```\n$ mroll revision -m "Initialize the database"\nok\n$ mroll show all_revisions\n<Revision id=fe00de6bfa19 description=Initialize the database>\n```\nA new revison file was added under `/tmp/migrations/versions`. \nOpen it and add the SQL commands under `-- migration:upgrade` and `-- migration:downgrade` sections.\n\n```\nvi tmp/migrations/versions/<rev_file>\n-- identifiers used by mroll\n-- id=fe00de6bfa19\n-- description=create tbl foo\n-- ts=2020-05-08T14:19:46.839773\n-- migration:upgrade\n\tcreate table foo (a string, b string);\n\talter table foo add constraint foo_pk primary key (a);\n-- migration:downgrade\n\tdrop table foo;\n```\nThen run "upgrade" command.\n\n```\n$ mroll upgrade\nDone\n```\n\nInspect what has being applied with "history" command\n```\n$ mroll history\n<Revision id=fe00de6bfa19 description=create tbl foo>\n```\nFor revisions overview use `mroll show [all|pending|applied]`, `mroll applied` is equivalent to \n`mroll history`.\n```\n$mroll show applied\n<Revision id=fe00de6bfa19 description=create tbl foo>\n```\n\nTo revert last applied revision run the `rollback` command. That will run the sql under `migration:downgrade`\nsection.\n```\n$ mroll rollback \nRolling back id=fe00de6bfa19 description=create tbl foo ...\nDone\n```\n\n## Development\n### Developer notes\n\n`mroll` is developed using [Poetry](https://python-poetry.org/), for dependency management and\npackaging.\n\n### Installation for development\nIn order to install `mroll` do the following:\n\n```\n  pip3 install --user poetry\n  PYTHON_BIN_PATH="$(python3 -m site --user-base)/bin"\n  export PATH="$PATH:$PYTHON_BIN_PATH"\n\n  git clone git@github.com:MonetDBSolutions/mroll.git\n  cd mroll\n  poetry install\n  poetry run mroll/commands.py --help\n```\nInstall project dependencies with\n\n```\npoetry install\n```\nThis will create virtual environment and install dependencies from the `poetry.lock` file. Any of the above \ncommands then can be run with poetry\n\n```\npoetry run mroll/commands.py <command>\n```\n## Testing\nRun all unit tests\n```\nmake test\n```\n',
    'author': 'svetlin',
    'author_email': 'svetlin.stalinov@monetdbsolutions.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/MonetDBSolutions/mroll',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
