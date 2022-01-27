# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['catt']

package_data = \
{'': ['*']}

install_requires = \
['click>=7.1.2',
 'ifaddr>=0.1.7',
 'pychromecast==9.2.0',
 'requests>=2.23.0',
 'yt-dlp>=2021.12.1',
 'zeroconf==0.31.0']

entry_points = \
{'console_scripts': ['catt = catt.cli:main']}

setup_kwargs = {
    'name': 'catt',
    'version': '0.12.7',
    'description': 'Cast All The Things allows you to send videos from many, many online sources to your Chromecast.',
    'long_description': 'Cast All The Things\n===================\n\n[![image](https://img.shields.io/pypi/v/catt.svg)](https://pypi.python.org/pypi/catt)\n[![image](https://img.shields.io/travis/skorokithakis/catt.svg)](https://travis-ci.org/skorokithakis/catt)\n[![image](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/skorokithakis/catt)\n\nCast All The Things allows you to send videos from many, many online\nsources (YouTube, Vimeo, and a few hundred others) to your Chromecast.\nIt also allows you to cast local files or render websites.\n\nInstallation\n------------\n\nYou can install Cast All The Things with pipx:\n\n    pipx install catt\n\nOr with pip, but that\'s not as good:\n\n    pip3 install catt\n\n`catt` is only compatible with Python 3. If you need a Python\n2-compatible version, please install `0.5.6`, the last py2-compatible\nrelease.\n\nUsage\n-----\n\nTo use Cast All The Things, just specify a URL:\n\n    catt cast "https://www.youtube.com/watch?v=dQw4w9WgXcQ"\n\n`catt` supports any service that yt-dlp supports, which includes most\nonline video hosting services.\n\n`catt` can also cast local files (if they\'re in a format the Chromecast\nsupports natively):\n\n    catt cast ./myvideo.mp4\n\nYou can also control your Chromecast through `catt` commands, for\nexample with `catt pause`. Try running `catt --help` to see the full\nlist of commands.\n\nIf you have subtitles and the name is similar to the name of the local\nfile, `catt` will add them automatically. You can, of course, specify\nany other subtitle if you want. Although Chromecast only supports\nWEBVTT, TTML and Line 21 subtitles, `catt` conveniently converts SRTs to\nWEBVTT for you on the fly. Here is how to use it:\n\n    catt cast -s ./mysubtitle.srt /myvideo.mp4\n\n`catt` can also tell your Chromecast to display any website:\n\n    catt cast_site https://en.wikipedia.org/wiki/Rickrolling\n\nPlease note that the Chromecast has a slow CPU but a reasonably recent\nversion of Google Chrome. The display resolution is 1280x720.\n\nIf you want to pass yt-dlp options to catt through the [-y]{.title-ref}\ncommand-line flag, you need to use yt-dlp\'s [internal option\nname](https://github.com/yt-dlp/yt-dlp/blob/master/yt_dlp/__init__.py#L620),\nrather than its command-line name.\n\nIf you notice that catt stops working with video sites (YouTube, Vimeo,\netc), just upgrade yt-dlp with [pip install -U yt-dlp]{.title-ref} and\nthat will probably fix it. This is because sites keep changing and\nyt-dlp is updated very regularly to keep them all working.\n\nYou can also run `catt` in Docker, if you prefer:\n\n    docker run --net=host --rm -it python:3.7 /bin/bash -c "pip install catt; catt cast \'https://www.youtube.com/watch?v=dQw4w9WgXcQ\'"\n\n### Configuration file\n\nCATT can utilize a config-file stored at `~/.config/catt/catt.cfg`\n(`%APPDATA%\\catt\\catt.cfg` on Windows).\n\nThe format is as following:\n\n```ini\n[options]\ndevice = chromecast_one\n\n[aliases]\none = chromecast_one\ntwo = chromecast_two\n```\n\nIn the `[options]` section, `device` denotes the default device that\nwill be selected, when you have not selected a device via the cli.\n\nYou can write your choice of default device to `catt.cfg` by doing:\n\n    catt -d <name_of_chromecast> set_default\n\nIn the `[aliases]` section, you can specify aliases for the names of\nyour chromecasts. You can then select a device just by doing:\n\n    catt -d <alias> <command>\n\nYou can write an alias name for a device to `catt.cfg` by doing:\n\n    catt -d <name_of_chromecast> set_alias <alias>\n\nContributing\n------------\n\nIf you want to contribute a feature to `catt`, please open an issue (or\ncomment on an existing one) first, to make sure it\'s something that the\nmaintainers are interested in. Afterwards, just clone the repository and\nhack away!\n\nTo run `catt` in development, you can use the following command:\n\n    python -m catt.cli --help\n\nBefore committing, please make sure you install `pre-commit` and install\nits hooks:\n\n    pip install pre-commit\n    pre-commit install\n\nThat\'s all, now you can commit and the hooks will run. Black (which is\nused to format the code) requires Python 3.6 to run, but please make the\neffort, as our CI will yell at you if the code is not formatted, and\nnobody wants that.\n\nThanks!\n\nInfo\n----\n\n-   Free software: BSD license\n\nFeatures\n--------\n\n- Casts videos to Chromecast\n- From [many, many online\n  sources](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)\n- Casts local files (videos, photos and music)\n- Casts any website to Chromecast\n\nThanks\n------\n\nCatt would not be possible without these great projects:\n\n- [pychromecast](https://github.com/balloob/pychromecast) - Library\n  for Python 3 to communicate with the Google Chromecast\n- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Command-line program to\n  download videos from YouTube.com and other video sites\n- [casttube](https://github.com/ur1katz/casttube) - YouTube Chromecast\n  API\n',
    'author': 'Stavros Korokithakis',
    'author_email': 'hi@stavros.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/skorokithakis/catt',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7',
}


setup(**setup_kwargs)
