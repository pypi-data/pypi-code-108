# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['deqr']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'deqr',
    'version': '0.2.1',
    'description': 'qr code decoding library',
    'long_description': '## deqr\n\nA python library for decoding QR codes. Implemented as a cython wrapper around\ntwo different QR code decoding backends (quirc and qrdec).\n\n### Install\n\n```\npip install deqr\n```\n\n### [Documentation][documentation]\n\n[documentation]: https://torque.github.io/deqr-docs/latest-dev/\n',
    'author': 'torque',
    'author_email': 'torque@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/torque/deqr',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
