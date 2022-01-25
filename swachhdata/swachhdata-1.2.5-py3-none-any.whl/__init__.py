import os

try:
    version_file = os.path.join(os.path.dirname(__file__), "VERSION.md")
    with open(version_file) as infile:
        __version__ = infile.read().strip()
except:
    __version__ = 'Unknown! Please check your installation.'

__author__ = 'Kritik Seth'
__maintainer__ = __author__
__license__ = 'Mozilla Public License Version 2.0'
__url__ = 'https://swachhdata.readthedocs.io/'
__connect__ = 'https://www.linkedin.com/in/kritikseth/'
