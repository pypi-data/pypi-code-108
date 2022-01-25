# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['spotidl']

package_data = \
{'': ['*']}

install_requires = \
['pytest-cov>=3.0.0,<4.0.0',
 'pytest>=6.2.5,<7.0.0',
 'python-dotenv>=0.19.2,<0.20.0',
 'spotipy>=2.19.0,<3.0.0',
 'yt-dlp>=2021.12.27,<2022.0.0']

entry_points = \
{'console_scripts': ['spotidl = spotidl.main:cli']}

setup_kwargs = {
    'name': 'spoti-dl',
    'version': '1.0.0',
    'description': 'spotidl: download songs, albums and playlists using Spotify links',
    'long_description': '# Introduction\n\nspoti-dl(I had a better name but that was already taken on PyPi), is a song downloader app that accepts Spotify links, fetches individual song—and basic album—metadata from Spotify, downloads the song from Youtube. The metadata is then written onto the downloaded song file using the trusty Mutagen library, this includes the album/song cover art as well. \n\nThe app currently supports downloading songs, albums and playlists. \n\nI got the inspiration for the project from my friend Swapnil\'s [spotify-dl](https://github.com/SwapnilSoni1999/spotify-dl) app written in JavaScript. This seemed like the perfect pet project to make and consequently learn from :)\n\n\n# Setup\n\nRun ```pip install spoti-dl``` to install the app first and foremost.\n\nspoti-dl needs two things to work: [FFmpeg](https://ffmpeg.org/download.html) and a Spotify developer account.\n\nSteps to make a Spotify developer account:\n1. Go to [Spotify Dev Dashboard](https://developer.spotify.com/dashboard/applications)\n2. Login with your credentials and click on "create an app".\n3. Enter any name of choice, app description, tick the checkbox and proceed.\n4. Now you have access to your client ID. Click on "Show client secret" to get your client secret.\n5. From here, click on "edit settings" and in the "redirect URIs" section add any localhost URL. I personally use ```http://localhost:8080/callback```\n\nFinally, define these three environment variables: \n```\nSPOTIPY_CLIENT_ID\nSPOTIPY_CLIENT_SECRET\nSPOTIPY_REDIRECT_URI\n```\n\nAlso note that the first time you run the app you might get a popup window in your browser asking to integrate your account to the app you just created in the Spotify app dashboard. Accept and close the window.\n\n# Usage\n\nMP3 is the selected codec (audio file format; MP3 is the standard) and 320KBPS the selected bitrate (audio quality). So by default, running this downloads the song/album/playlist with these defaults-\n```\nspotidl <spotify link>\n``` \n\nas an example, running this would download Rick Astley\'s \'Never Gonna Give You Up\'- \n```\nspotidl https://open.spotify.com/track/4PTG3Z6ehGkBFwjybzWkR8?si=06f5d7ab5bd240e7\n```\n\nThe following audio formats are supported:\n- mp3 \n- flac\n- m4a (the m4a format only has partial textual-metadata support 😅)\n\nThe following bitrates are supported:\n- best \n- 320kbps\n- 256kbps \n- 192kbps (slightly better than Spotify\'s \'high\' audio setting, this is the bare minimum in my opinion to have a good listening experience)\n- 96kbps\n- 32kbps\n- worst\n\nAgain, the following link types are supported:\n- song links\n- album links\n- playlist links \n\nNote: File names (audio files or folder names (eg., playlist\'s directory name) are changed to ensure compatibility with the operating systems since many characters like \'?\' or the \'/\' are illegal when making files/folders.\n',
    'author': 'Dhruv',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/good-times-ahead/spoti-dl/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
