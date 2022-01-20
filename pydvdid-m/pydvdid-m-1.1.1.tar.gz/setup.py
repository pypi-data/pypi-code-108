# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pydvdid_m']

package_data = \
{'': ['*']}

install_requires = \
['pycdlib>=1.12.0,<2.0.0', 'python-dateutil>=2.8.2,<3.0.0']

extras_require = \
{'win_raw_dev:sys_platform == "win32"': ['pywin32==301']}

entry_points = \
{'console_scripts': ['dvdid = pydvdid_m.pydvdid_m:main']}

setup_kwargs = {
    'name': 'pydvdid-m',
    'version': '1.1.1',
    'description': 'Pure Python implementation of the Windows API method IDvdInfo2::GetDiscID.',
    'long_description': '# pydvdid-m\n\n![downloads](https://pepy.tech/badge/pydvdid-m)\n![license](https://img.shields.io/pypi/l/pydvdid-m.svg)\n![wheel](https://img.shields.io/pypi/wheel/pydvdid-m.svg)\n![versions](https://img.shields.io/pypi/pyversions/pydvdid-m.svg)\n\nPure Python implementation of the Windows API method [IDvdInfo2::GetDiscID].  \nThis is a modification of [sjwood\'s pydvdid](https://github.com/sjwood/pydvdid).\n\nThe Windows API method [IDvdInfo2::GetDiscID] is used by Windows Media Center to compute a\n\'practically unique\' 64-bit CRC for metadata retrieval. It\'s metadata retrieval API has\nsadly since shutdown around October 2019 and all it\'s information is presumably lost.\n\n  [IDvdInfo2::GetDiscID]: <https://docs.microsoft.com/en-us/windows/win32/api/strmif/nf-strmif-idvdinfo2-getdiscid>\n\n## Changes compared to sjwood\'s repo\n\n1. License changed from Apache-2.0 to GPL-3.0.\n2. Moved build tools and dependency management from setuptools and requirements.txt to poetry.\n3. Support for Python 2.x and Python <3.6 has been dropped. \n4. All tests were removed entirely simply because a lot of the tests would need to be refactored\n   for general code changes, and some tests might not be needed anymore.\n5. All custom exceptions were removed entirely and replaced with built-in ones.\n6. CRC-64 related code were refactored and merged as one CRC64 class in one file.\n7. The merged CRC64 class contains various improvements over the original code, including\n   improvements with doc-strings, formatting, and such.\n8. Various BASH shell scripts and config files were removed entirely as they are deemed unnecessary.\n9. Uses pycdlib to read from ISO and direct disc drives, instead of assuming that it\'s a folder.\n\nOther than that, the rest of the changes are general code improvements in various ways.\nThere may be more differences as the repo gets commits, but these are the primary differences from\n[sjwood\'s commit](https://github.com/sjwood/pydvdid/commit/03914fb7e24283c445e5af724f9d919b23caaf95) to\nthe beginnings of this repository.\n\n## Important Information on DVD ID Accuracy\n\n1. The DVD ID generated assumes that the input Disc, ISO, or VIDEO_TS folder has the original untouched\n   file timestamps, file names, and header data. Any change or missing file will result in a different DVD ID.\n2. Because of this, AnyDVD HD, DVDFab Passkey, or anything similar that may change the disc data at a\n   driver-level should be disabled before the use of pydvdid-m.\n3. Just because it is an ISO file, does not mean it is truly untouched in the header areas that matter.\n   AnyDVD HD (and maybe others) may alter some bytes here and there when removing protection.\n4. VIDEO_TS folders are typically created by extracting the data from an ISO or Disc, which will most likely\n   re-generate file creation and modified timestamps. If you want truly accurate DVD IDs, I cannot advise\n   the use of this project on VIDEO_TS folders.\n\nIf you want truly accurate DVD IDs, then only use this project direct from discs with all DVD ripping software\ndisabled and closed. Make sure nothing like AnyDVD HD or DVDFab Passkey is running in the background.\n\n## Installation\n\n```shell\n$ pip install pydvdid-m\n```\n\n## Usage\n\nYou can run DvdId on all types of DVD video file structures:\n\n- Direct from Disc, e.g., `/dev/sr0`, `\\\\.\\E:`, or such.\n- An ISO file, e.g., `/mnt/cdrom`, `C:/Users/John/Videos/FAMILY_GUY_VOLUME_11_DISC_1.ISO`.\n- A VIDEO_TS folder*, `C:/Users/John/Videos/THE_IT_CROWD_D1/`.\n\nNote: Generating a DVD ID from a VIDEO_TS folder has a high chance of providing an\ninvalid DVD ID. The algorithm uses file creation timestamps, and extracting VIDEO_TS folders\ndirect from Disc or from an ISO will most likely change them, especially when transferred or moved.\n\n### CLI\n\n```shell\nphoenix@home@~$ dvdid "FAMILY_GUY_VOLUME_11_DISC_1.ISO"\n<Disc>\n<Name>FAMILY_GUY_VOLUME_11_DISC_1</Name>\n<ID>db3804e3|1645f594</ID>\n</Disc>\n```\n\nYou can provide a path to an ISO file, or a mounted device, e.g.:\n\n```shell\nphoenix@home@~$ dvdid "/dev/sr0"\n<Disc>\n<Name>BBCDVD3508</Name>\n<ID>3f041dfc|27ffd3a8</ID>\n</Disc>\n```\n\nor on Windows via Raw Mounted Device:\n\n```shell\nPS> dvdid "\\\\.\\E:"\n<Disc>\n<Name>BBCDVD3508</Name>\n<ID>3f041dfc|27ffd3a8</ID>\n</Disc>\n```\n\n### Package\n\nYou can also use pydvdid-m in your own Python code by importing it.  \nHere\'s a couple of things you can do, and remember, you can use both ISO paths and mounted device targets.\n\n```python\n>>> from pydvdid_m import DvdId\n>>> dvd_id = DvdId(r"C:\\Users\\John\\Videos\\FAMILY_GUY_VOLUME_11_DISC_1.ISO")\n>>> dvd_id.disc_label\n\'BBCDVD3508\'\n>>> repr(dvd_id.checksum)\n\'<CRC64 polynomial=0x92c64265d32139a4 xor=0xffffffffffffffff checksum=0x3f041dfc27ffd3a8>\'\n>>> dvd_id.checksum\n\'3f041dfc|27ffd3a8\'\n>>> dvd_id.checksum.as_bytes\nb"?\\x04\\x1d\\xfc\'\\xff\\xd3\\xa8"\n>>> dvd_id.dumps()\n\'<Disc>\\n<Name>BBCDVD3508</Name>\\n<ID>3f041dfc|27ffd3a8</ID>\\n</Disc>\'\n```\n\n## License\n\n[GNU General Public License, Version 3](https://raw.githubusercontent.com/rlaphoenix/pydvdid-m/master/LICENSE)\n',
    'author': 'rlaphoenix',
    'author_email': 'rlaphoenix@pm.me',
    'maintainer': 'rlaphoenix',
    'maintainer_email': 'rlaphoenix@pm.me',
    'url': 'https://github.com/rlaphoenix/pydvdid-m',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
