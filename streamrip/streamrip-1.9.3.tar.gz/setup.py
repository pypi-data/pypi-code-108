# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['rip', 'streamrip']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=9.0.0,<10.0.0',
 'aiodns>=3.0.0,<4.0.0',
 'aiofiles>=0.7.0,<0.8.0',
 'aiohttp>=3.7.4,<4.0.0',
 'appdirs>=1.4.4,<2.0.0',
 'cchardet>=2.1.7,<3.0.0',
 'cleo==1.0.0a4',
 'click>=8.0.1,<9.0.0',
 'deezer-py==1.3.6',
 'm3u8>=0.9.0,<0.10.0',
 'mutagen>=1.45.1,<2.0.0',
 'pathvalidate>=2.4.1,<3.0.0',
 'pycryptodomex>=3.10.1,<4.0.0',
 'requests>=2.25.1,<3.0.0',
 'tomlkit>=0.7.2,<0.8.0',
 'tqdm>=4.61.1,<5.0.0']

extras_require = \
{':sys_platform == "cygwin"': ['pick>=1.0.0,<2.0.0'],
 ':sys_platform == "darwin" or sys_platform == "linux"': ['simple-term-menu>=1.2.1,<2.0.0'],
 ':sys_platform == "win32" or sys_platform == "cygwin"': ['windows-curses>=2.2.0,<3.0.0']}

entry_points = \
{'console_scripts': ['rip = rip.cli:main']}

setup_kwargs = {
    'name': 'streamrip',
    'version': '1.9.3',
    'description': 'A fast, all-in-one music ripper for Qobuz, Deezer, Tidal, and SoundCloud',
    'long_description': '# streamrip\n\n[![Downloads](https://pepy.tech/badge/streamrip)](https://pepy.tech/project/streamrip)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)\n\nA scriptable stream downloader for Qobuz, Tidal, Deezer and SoundCloud.\n\n![Streamrip downloading an album](https://github.com/nathom/streamrip/blob/dev/demo/download_album.png?raw=true)\n\n\n## Features\n\n- Super fast, as it utilizes concurrent downloads and conversion\n- Downloads tracks, albums, playlists, discographies, and labels from Qobuz, Tidal, Deezer, and SoundCloud\n- Supports downloads of Spotify and Apple Music playlists through [last.fm](https://www.last.fm)\n- Automatically converts files to a preferred format\n- Has a database that stores the downloaded tracks\' IDs so that repeats are avoided\n- Easy to customize with the config file\n- Integration with `youtube-dl`\n\n## Installation\n\nFirst, ensure [Python](https://www.python.org/downloads/) (version 3.8 or greater) and [pip](https://pip.pypa.io/en/stable/installing/) are installed. If you are on Windows, install [Microsoft Visual C++ Tools](https://docs.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170). Then run the following in the command line:\n\n```bash\npip3 install streamrip --upgrade\n```\n\nWhen you type\n\n```bash\nrip\n```\n\nit should show the main help page. If you have no idea what these mean, or are having other issues installing, check out the [detailed installation instructions](https://github.com/nathom/streamrip/wiki#detailed-installation-instructions).\n\nIf you would like to use `streamrip`\'s conversion capabilities, download TIDAL videos, or download music from SoundCloud, install [ffmpeg](https://ffmpeg.org/download.html). To download music from YouTube, install [youtube-dl](https://github.com/ytdl-org/youtube-dl#installation).\n\n### Streamrip beta\n\nIf you want to get access to the latest and greatest features without waiting for a new release, install\nfrom the `dev` branch with the following command\n\n```bash\npip3 install git+https://github.com/nathom/streamrip.git@dev\n```\n\n## Example Usage\n\n**For Tidal and Qobuz, you NEED a premium subscription.**\n\nDownload an album from Qobuz\n\n```bash\nrip url https://www.qobuz.com/us-en/album/rumours-fleetwood-mac/0603497941032\n```\n\nDownload multiple albums from Qobuz\n\n```bash\nrip url https://www.qobuz.com/us-en/album/back-in-black-ac-dc/0886444889841 https://www.qobuz.com/us-en/album/blue-train-john-coltrane/0060253764852\n```\n\n\n\nDownload the album and convert it to `mp3`\n\n```bash\nrip url --codec mp3 https://open.qobuz.com/album/0060253780968\n```\n\n\n\nTo set the maximum quality, use the `--max-quality` option to `0, 1, 2, 3, 4`:\n\n| Quality ID | Audio Quality         | Available Sources                            |\n| ---------- | --------------------- | -------------------------------------------- |\n| 0          | 128 kbps MP3 or AAC   | Deezer, Tidal, SoundCloud (most of the time) |\n| 1          | 320 kbps MP3 or AAC   | Deezer, Tidal, Qobuz, SoundCloud (rarely)    |\n| 2          | 16 bit, 44.1 kHz (CD) | Deezer, Tidal, Qobuz, SoundCloud (rarely)    |\n| 3          | 24 bit, ≤ 96 kHz      | Tidal (MQA), Qobuz, SoundCloud (rarely)      |\n| 4          | 24 bit, ≤ 192 kHz     | Qobuz                                        |\n\n\n\n```bash\nrip url --max-quality 3 https://tidal.com/browse/album/147569387\n```\n\nSearch for albums matching `lil uzi vert` on SoundCloud\n\n```bash\nrip search --source soundcloud \'lil uzi vert\'\n```\n\n![streamrip interactive search](https://github.com/nathom/streamrip/blob/dev/demo/album_search.png?raw=true)\n\nSearch for *Rumours* on Tidal, and download it\n\n```bash\nrip search \'fleetwood mac rumours\'\n```\n\nWant to find some new music? Use the `discover` command (only on Qobuz)\n\n```bash\nrip discover --list \'best-sellers\'\n```\n\nDownload a last.fm playlist using the lastfm command\n\n```\nrip lastfm https://www.last.fm/user/nathan3895/playlists/12126195\n```\n\nFor extreme customization, see the config file\n\n```\nrip config --open\n```\n\n\n\nIf you\'re confused about anything, see the help pages. The main help pages can be accessed by typing `rip` by itself in the command line. The help pages for each command can be accessed with the `-h` flag. For example, to see the help page for the `url` command, type\n\n```\nrip url -h\n```\n\n![example_help_page.png](https://github.com/nathom/streamrip/blob/dev/demo/example_help_page.png?raw=true)\n\n## Other information\n\nFor more in-depth information about `streamrip`, see the help pages and the [wiki](https://github.com/nathom/streamrip/wiki/).\n\n\n## Contributions\n\nAll contributions are appreciated! You can help out the project by opening an issue\nor by submitting code.\n\n### Issues\n\nIf you\'re opening an issue **use the Feature Request or Bug Report templates properly**. This ensures\nthat I have all of the information necessary to debug the issue. If you do not follow the templates,\n**I will silently close the issue** and you\'ll have to deal with it yourself.\n\n### Code\n\nIf you\'re new to Git, follow these steps to open your first Pull Request (PR):\n\n- Fork this repository\n- Clone the new repository\n- Commit your changes\n- Open a pull request to the `dev` branch\n\nPlease document any functions or obscure lines of code.\n\n### The Wiki\n\nTo help out `streamrip` users that may be having trouble, consider contributing some information to the wiki. \nNothing is too obvious and everything is appreciated.\n\n## Acknowledgements\n\nThanks to Vitiko98, Sorrow446, and DashLt for their contributions to this project, and the previous projects that made this one possible.\n\n`streamrip` was inspired by:\n\n- [qobuz-dl](https://github.com/vitiko98/qobuz-dl)\n- [Qo-DL Reborn](https://github.com/badumbass/Qo-DL-Reborn)\n- [Tidal-Media-Downloader](https://github.com/yaronzz/Tidal-Media-Downloader)\n- [scdl](https://github.com/flyingrub/scdl)\n\n\n\n## Disclaimer\n\n\nI will not be responsible for how you use `streamrip`. By using `streamrip`, you agree to the terms and conditions of the Qobuz, Tidal, and Deezer APIs.\n\n## Donations/Sponsorship\n\n<a href="https://www.buymeacoffee.com/nathom" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/default-orange.png" alt="Buy Me A Coffee" height="41" width="174"></a>\n\n\nConsider contributing some funds [here](https://www.buymeacoffee.com/nathom), which will go towards holding\nthe premium subscriptions that I need to debug and improve streamrip. Thanks for your support!\n',
    'author': 'nathom',
    'author_email': 'nathanthomas707@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/nathom/streamrip',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
