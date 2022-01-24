# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pwnedpasswords_offline', 'pwnedpasswords_offline.tools']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['pwnedpasswords_offline_seed_bloom = '
                     'pwnedpasswords_offline.tools.seed_bloom:main']}

setup_kwargs = {
    'name': 'pwnedpasswords-offline',
    'version': '1.2.0',
    'description': 'Pwned Passwords check (offline)',
    'long_description': '# Pwned Passwords check (offline)\n\n[![PyPI](https://img.shields.io/pypi/v/pwnedpasswords-offline)](https://pypi.org/project/pwnedpasswords-offline/)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n\n## Features\n\n * Check passwords or plain SHA-1 hashes against haveibeenpwned password list\n * Fully offline operation, needs to be provided with external database file (~35 GB)\n * Optional [Bloom filter](https://en.wikipedia.org/wiki/Bloom_filter) to speed up common (negative) case\n\n## Quickstart\n\n* Download "SHA-1" version "(ordered by hash)" from https://haveibeenpwned.com/Passwords\n* Extract file, yielding `pwned-passwords-sha1-ordered-by-hash-v8.txt` (for current version 8), put into `data` directory under current directory\n* Install with `pip install pwnedpasswords_offline`\n* Optional: Seed Bloom filter: `pwnedpasswords_offline_seed_bloom`, takes about 45min to run, will generate a 512MiB file\n\n## Speed\n\n(Results approximate, measured on my personal laptop)\n\n|                        | w/o Bloom filter | w/ Bloom filter |\n|------------------------|-----------------:|----------------:|\n| Positive match (pwned) |         61 us/op |       198 us/op |\n| Negative match         |        121 us/op |        14 us/op |\n| Average @ 1% positive  |         64 us/op |        16 us/op |\n\nThese results were measured with batch operation at 20000 items. One-shot operation will be much slower due to the overhead of opening data files.\n\nThe data files are opened with mmap(2), and accessed in random order. No explicit non-garbage-collected Python objects are generated during operation, so it should be safe to open the data files once at the start of your application and then keep them open until your process ends. Note: The memory mapping will not survive a fork(2), so you cannot use a pre-forking webserver such as gunicorn to only open the data files once. Each process needs to open its own copy. \n\n## Simple usage\n````python\nfrom pwnedpasswords_offline import PwnedPasswordsOfflineChecker\nif PwnedPasswordsOfflineChecker("data/pwned-passwords-sha1-ordered-by-hash-v8.txt").lookup_raw_password("Password1!"):\n    print("Pwned!")\n````\n\n## Batch usage\nYou can also pre-open the database file, especially if you\'re checking multiple passwords in bulk:\n\n````python\nfrom pwnedpasswords_offline import PwnedPasswordsOfflineChecker\nchecker = PwnedPasswordsOfflineChecker("data/pwned-passwords-sha1-ordered-by-hash-v8.txt")\nchecker.open()\nfor password in ["Password1!", "correct horse battery staple", "actress stapling driver placidly swivel doorknob"]:\n    if checker.lookup_raw_password(password):\n        print(f"\'{password}\' is pwned!")\nchecker.close()\n````\n\nYou should not forget to call `.close()` after you\'re done.\n\n## As context manager\n\nYou can use the object as a context manager to automatically open and close it:\n\n`````python\nfrom pwnedpasswords_offline import PwnedPasswordsOfflineChecker\nwith PwnedPasswordsOfflineChecker("data/pwned-passwords-sha1-ordered-by-hash-v8.txt") as checker:\n    for password in ["Password1!", "correct horse battery staple", "actress stapling driver placidly swivel doorknob"]:\n        if checker.lookup_raw_password(password):\n            print(f"\'{password}\' is pwned!")\n`````\n\n## Check hash directly\n\nInstead of calling `.lookup_raw_password()` you can call `.lookup_hash()` if you already have the plain SHA-1 hash:\n\n````python\nfrom pwnedpasswords_offline import PwnedPasswordsOfflineChecker\nif PwnedPasswordsOfflineChecker("data/pwned-passwords-sha1-ordered-by-hash-v8.txt").lookup_hash("32CA9FD4B3F319419F2EA6F883BF45686089498D"):\n    print("Pwned!")\n````\n',
    'author': 'Henryk Plötz',
    'author_email': 'henryk@ploetzli.ch',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/henryk/pwnedpasswords-offline',
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
