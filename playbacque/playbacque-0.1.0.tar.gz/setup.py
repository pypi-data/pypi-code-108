# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['playbacque']
install_requires = \
['SoundFile>=0.10.3,<0.11.0', 'sounddevice>=0.4.4,<0.5.0']

entry_points = \
{'console_scripts': ['playbacque = playbacque:main']}

setup_kwargs = {
    'name': 'playbacque',
    'version': '0.1.0',
    'description': 'Loop play audio',
    'long_description': '# playbacque\n\nLoop play audio\n\n## Usage\n\n```sh\n> pip install playbacque\n> playbacque "audio.wav"\n```\n\nUse Ctrl+C to stop playback\n\nSupports most file formats (as this uses soundfile which uses libsndfile)\n\nNotable exceptions include .mp3 and .ogg\n\nAs an alternative, one can first convert to a .wav using FFmpeg and pipe into\n`playbacque -`, where - means to take audio from stdin\n\n```sh\n> ffmpeg -i "audio.mp3" -f wav pipe: | playbacque -\n```\n\nNote when passing -, the entire stdin is buffered before playback\n',
    'author': 'George Zhang',
    'author_email': 'geetransit@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://pypi.org/project/playbacque/',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
