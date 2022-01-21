# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiospamc']

package_data = \
{'': ['*']}

install_requires = \
['certifi', 'loguru>=0.5.3,<0.6.0']

setup_kwargs = {
    'name': 'aiospamc',
    'version': '0.8.0',
    'description': "An asyncio-based library to communicate with SpamAssassin's SPAMD service.",
    'long_description': "========\naiospamc\n========\n\n|pypi| |docs| |license| |unit| |integration| |python|\n\n.. |pypi| image:: https://img.shields.io/pypi/v/aiospamc\n    :target: https://pypi.org/project/aiospamc/\n\n.. |unit| image:: https://github.com/mjcaley/aiospamc/actions/workflows/unit-tests.yml/badge.svg\n    :target: https://github.com/mjcaley/aiospamc/actions/workflows/unit-tests.yml\n\n.. |integration| image:: https://github.com/mjcaley/aiospamc/actions/workflows/integration-tests.yml/badge.svg\n    :target: https://github.com/mjcaley/aiospamc/actions/workflows/integration-tests.yml\n\n.. |docs| image:: https://readthedocs.org/projects/aiospamc/badge/?version=latest\n    :target: https://aiospamc.readthedocs.io/en/latest/\n\n.. |license| image:: https://img.shields.io/github/license/mjcaley/aiospamc\n    :target: ./LICENSE\n\n.. |python| image:: https://img.shields.io/pypi/pyversions/aiospamc\n    :target: https://python.org\n\n-----------\nDescription\n-----------\n\nPython asyncio-based library that implements the SPAMC/SPAMD client protocol used by SpamAssassin.\n\n-------------\nDocumentation\n-------------\n\nDocumentation can be found at: https://aiospamc.readthedocs.io/\n\n------------\nRequirements\n------------\n\n* Python 3.7 or higher\n\n-------\nExample\n-------\n\n.. code:: python\n    \n    import asyncio\n    import aiospamc\n\n\n    GTUBE = '''Subject: Test spam mail (GTUBE)\n    Message-ID: <GTUBE1.1010101@example.net>\n    Date: Wed, 23 Jul 2003 23:30:00 +0200\n    From: Sender <sender@example.net>\n    To: Recipient <recipient@example.net>\n    Precedence: junk\n    MIME-Version: 1.0\n    Content-Type: text/plain; charset=us-ascii\n    Content-Transfer-Encoding: 7bit\n\n    This is the GTUBE, the\n        Generic\n        Test for\n        Unsolicited\n        Bulk\n        Email\n\n    If your spam filter supports it, the GTUBE provides a test by which you\n    can verify that the filter is installed correctly and is detecting incoming\n    spam. You can send yourself a test mail containing the following string of\n    characters (in upper case and with no white spaces and line breaks):\n\n    XJS*C4JDBQADN1.NSBN3*2IDNEN*GTUBE-STANDARD-ANTI-UBE-TEST-EMAIL*C.34X\n\n    You should send this test mail from an account outside of your network.\n    '''.encode('ascii')\n\n    loop = asyncio.get_event_loop()\n    responses = loop.run_until_complete(asyncio.gather(\n\n        aiospamc.ping(host='localhost'),\n        aiospamc.check(GTUBE, host='localhost'),\n        aiospamc.headers(GTUBE, host='localhost')\n\n    ))\n    print(responses)\n",
    'author': 'Michael Caley',
    'author_email': 'mjcaley@darkarctic.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/mjcaley/aiospamc',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
