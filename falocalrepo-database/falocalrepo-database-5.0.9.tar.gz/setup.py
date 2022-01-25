# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['falocalrepo_database']

package_data = \
{'': ['*']}

install_requires = \
['chardet>=4.0.0,<5.0.0', 'filetype>=1.0.9,<2.0.0', 'psutil>=5.9.0,<6.0.0']

setup_kwargs = {
    'name': 'falocalrepo-database',
    'version': '5.0.9',
    'description': 'Database functionality for falocalrepo.',
    'long_description': '<div align="center">\n\n<img alt="logo" width="400" src="https://raw.githubusercontent.com/FurryCoders/Logos/main/logos/falocalrepo-database-transparent.png">\n\n# FALocalRepo-Database\n\nDatabase functionality for [falocalrepo](https://pypi.org/project/falocalrepo).\n\n[![](https://img.shields.io/github/v/tag/FurryCoders/falocalrepo-database?label=github&sort=date&logo=github&color=blue)](https://github.com/FurryCoders/falocalrepo-database)\n[![](https://img.shields.io/pypi/v/falocalrepo-database?logo=pypi)](https://pypi.org/project/falocalrepo-database/)\n[![](https://img.shields.io/pypi/pyversions/falocalrepo-database?logo=Python)](https://www.python.org)\n\n</div>\n\n## Tables\n\nTo store its information, the database uses separate tables: `USERS`, `SUBMISSIONS`, `JOURNALS`, `SETTINGS`,\nand `HISTORY`.\n\n**Note**: bar-separated lists are formatted as `|item1||item2|` to properly isolate all elements\n\n### Users\n\nThe users\' table contains a list of all the users that have been download with the program, the folders that have been\ndownloaded, and the submissions found in each of those.\n\nEach entry contains the following fields:\n\n* `USERNAME` the URL username of the user (no underscores or spaces)\n* `FOLDERS` the folders downloaded for that specific user, sorted and bar-separated\n* `USERPAGE` the user\'s profile text\n\n### Submissions\n\nThe submissions\' table contains the metadata of the submissions downloaded by the program and information on their files\n\n* `ID` the id of the submission\n* `AUTHOR` the username of the author (uploader) in full format\n* `TITLE`\n* `DATE` upload date in ISO format _YYYY-MM-DDTHH:MM_\n* `DESCRIPTION` description in html format\n* `TAGS` bar-separated tags\n* `CATEGORY`\n* `SPECIES`\n* `GENDER`\n* `RATING`\n* `TYPE` image, text, music, or flash\n* `FILEURL` the remote URL of the submission file\n* `FILEEXT` the extensions of the downloaded file. Can be empty if the file contained errors and could not be recognised\n  upon download\n* `FILESAVED` file and thumbnail download status as a 2bit flag: `1x` if the file was downloaded `0x` if not, `x1` if\n  thumbnail was downloaded, `x0` if not. Possible values are `0`, `1`, `2`, `3`.\n* `FAVORITE` a bar-separated list of users that have "faved" the submission\n* `MENTIONS` a bar-separated list of users that are mentioned in the submission description as links\n* `FOLDER` the folder of the submission (`gallery` or `scraps`)\n* `USERUPDATE` whether the submission was added as a user update or favorite/single entry\n\n### Journals\n\nThe journals\' table contains the metadata of the journals downloaded by the program.\n\n* `ID` the id of the journal\n* `AUTHOR` the username of the author (uploader) in full format\n* `TITLE`\n* `DATE` upload date in ISO format _YYYY-MM-DDTHH:MM_\n* `CONTENT` content in html format\n* `MENTIONS` a bar-separated list of users that are mentioned in the journal content as links\n* `USERUPDATE` whether the journal was added as a user update or single entry\n\n### Settings\n\nThe settings table contains settings for the program and variable used by the database handler and main program.\n\n* `COOKIES` cookies for the download program, stored in JSON format\n* `FILESFOLDER` location of downloaded submission files\n* `VERSION` database version\n\n### History\n\nThe history table holds events related to the database.\n\n* `TIME` event time in ISO format _YYYY-MM-DDTHH:MM:SS.ssssss_\n* `EVENT` the event description\n\n## Submission Files\n\nThe `save_submission` functions saves the submission metadata in the database and stores the files.\n\nSubmission files are saved in a tiered tree structure based on their submission ID. IDs are zero-padded to 10 digits and\nthen broken up in 5 segments of 2 digits; each of these segments represents a folder tha will be created in the tree.\n\nFor example, a submission `1457893` will be padded to `0001457893` and divided into `00`, `01`, `45`, `78`, `93`. The\nsubmission file will then be saved as `00/01/45/78/93/submission.file` with the correct extension extracted from the\nfile itself (FurAffinity links do not always contain the right extension and sometimes confuse JPEG and PNG).\n\n## Upgrading Database\n\n_Note:_ versions prior to 4.19.0 are not supported by falocalrepo-database version 5.0.0 and above. To update from\nthose, use [falocalrepo v3.25.0](https://pypi.org/project/falocalrepo/v3.25.0) to upgrade the database to version\n4.19.0.<br/>\n_Note:_ Versions prior to 2.7.0 are not supported by falocalrepo-database version 3.0.0 and above. To update from those\nto the new version use [falocalrepo v2.11.2](https://github.com/FurryCoders/FALocalRepo/releases/tag/v2.11.2) to upgrade\nthe database to version 2.7.0\n',
    'author': 'Matteo Campinoti',
    'author_email': 'matteo.campinoti94@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/FurryCoders/falocalrepo-database',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
