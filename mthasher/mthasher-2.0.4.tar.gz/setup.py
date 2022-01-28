# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['mthasher']

package_data = \
{'': ['*']}

entry_points = \
{'console_scripts': ['mthasher = mthasher.__main__:entrypoint']}

setup_kwargs = {
    'name': 'mthasher',
    'version': '2.0.4',
    'description': 'Calculate multiple hash digests for a piece of data in parallel, one algo/thread.',
    'long_description': '# MtHasher\n\nCalculate multiple hash digests for a piece of data in parallel, one algo/thread.\n\nBased on the code of Peter Wu <peter@lekensteyn.nl> (https://git.lekensteyn.nl/scripts/tree/digest.py).\n\n# Usage\n\n## From CLI\n\nAdd data over STDIN and/or as arguments and select the desired algorithms:\n\n```bash\ncat data.txt | python3 -m mthasher -i data2.txt - --sha1 --sha256 -o checksums.txt\n```\n\nAt least one algorithm is mandatory and by default the script reads from STDIN and writes to STDOUT.\n\n## From Python\n\n### The exposed API is the following\n\n- `ALGORITHMS_GUARANTEED`: The tuple of the supported algorithms\n- `Hasher()`: Single-threaded hasher, takes an iterable (e.g. list of algorithms to use)\n- `MtHasher()` Multi-threaded hasher, takes an iterable (e.g. list of algorithms to use)\n\n### Both hashers expose the following API\n\n- `header`: tuple of header elements ("filename" and the list of algorithms in the supplied order)\n- `algos`: tuple of supplied algorithms\n- `hash_file()`: Takes a filename or a file-like object on bytes, returns the digest tuple in same order as header (the filename is omited)\n- `hash_multiple_files()`:Takes an iterable of filenames or file-like objects on bytes,returns the generator of filename + digest tuples in same order as header, one for every input object\n\n### Example\n\n```python\nfrom io import BytesIO\n\nfrom mthasher import MtHasher\n\nhasher = MtHasher((\'sha1\', \'md5\'))\nfilename_header, sha1_header, md5_header = hasher.header\nsha1_digest, md5_digest = hasher.hash_file(\'data.txt\')\nfor filename, sha1_digest, md5_digest in hasher.hash_multiple_files((\'data.txt\', open(\'data2.txt\', \'rb\'), \'-\', BytesIO(\'bytesstring\'))):\n    # First the header and then the digests\n    print(filename, sha1_digest, md5_digest, sep=\'\\t\')\n```\n\n## Supported algorithms\n\n- md5\n- sha1\n- sha224\n- sha256\n- sha384\n- sha512\n- sha3_224\n- sha3_256\n- sha3_384\n- sha3_512\n- blake2b\n- blake2s\n\n# License\n\nLicensed under the MIT license <http://opensource.org/licenses/MIT>\n',
    'author': 'dlazesz',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ELTE-DH/mthasher',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
