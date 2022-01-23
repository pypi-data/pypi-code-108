# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['resolve_name_clash', 'resolve_name_clash.tests']

package_data = \
{'': ['*']}

install_requires = \
['click>=8.0.3,<9.0.0']

entry_points = \
{'console_scripts': ['resolve-name-clash = '
                     'resolve_name_clash.resolve_name_clash:cli']}

setup_kwargs = {
    'name': 'resolve-name-clash',
    'version': '0.1.3',
    'description': 'Simple utility that takes a source file and a destination directory and determines a unique name for the source file in the destination directory that will not clash with any existing file.',
    'long_description': '# resolve-name-clash\n\nSay you want to copy file `a.txt` into directory `/path/to/destination/` but if `/path/to/destination/a.txt` exists, you don\'t want to overwrite it but instead copy the file to `/path/to/destination/a_1.txt`. This is a simple utility that does exactly one thing: given a source filename and a destination directory, it figures out a form of the source file\'s name in the destination directory that doesn\'t clash with any existing file. \n\nThe algorithm it uses to find a unique filename is as follows. Given a path to a source file and a path to a destination directory:\n* Set `src_filename` to the filename (last path segment) of the path to the source file\n* If `path/to/dest/src_filename` does not exist, return it\n* If `path/to/dest/src_filename` exists:\n  * Set `src_file_basename` to `src_filename` with all the extensions removed and `src_file_extensions` to all the extensions of `src_filename`\n  * Successively try `path/to/dest/src_file_basename + "_1" + src_file_extensions`, `path/to/dest/src_file_basename + "_2" + src_file_extensions`, and so on until one is found that doesn\'t exist. Return that one.\n\nYou can use it on the command line: \n```\n$ resolve-name-clash ~/src/a.txt ~/dest/\n/Users/spather/dest/a_1.txt\n```\n\nIt\'s particularly useful used in a subshell with a copy or move command:\n```\ncp ~/src/a.txt $(resolve-name-clash ~/src/a.txt ~/dest)\n```\n\nOr you can us it in a python program:\n\n```python\nfrom resolve_name_clash import resolve_name_clash\n\nsrc = Path("/path/to/src/a.txt")\ndest = Path("/path/to/dest")\nunique_path = resolve_name_clash(src, dest)\n# unique_path will be a Path object to something like /path/to/dest/a_1.txt\n```\n',
    'author': 'Shyam Pather',
    'author_email': 'shyam.pather@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/spather/resolve-name-clash',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
