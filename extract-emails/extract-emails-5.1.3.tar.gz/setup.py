# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['extract_emails',
 'extract_emails.browsers',
 'extract_emails.data_extractors',
 'extract_emails.errors',
 'extract_emails.factories',
 'extract_emails.link_filters',
 'extract_emails.models',
 'extract_emails.utils',
 'extract_emails.workers']

package_data = \
{'': ['*']}

install_requires = \
['loguru>=0.5.3,<0.6.0', 'pydantic>=1.8.2,<2.0.0']

setup_kwargs = {
    'name': 'extract-emails',
    'version': '5.1.3',
    'description': 'Extract email addresses and linkedin profiles from given URL.',
    'long_description': '# Extract Emails\n\n![Image](https://github.com/dmitriiweb/extract-emails/blob/docs_improvements/images/email.png?raw=true)\n\n[![PyPI version](https://badge.fury.io/py/extract-emails.svg)](https://badge.fury.io/py/extract-emails)\n\nExtract emails and linkedins profiles from a given website\n\n[Documentation](https://dmitriiweb.github.io/extract-emails/)\n\n## Requirements\n- Python >= 3.7\n\n## Installation\n```\npip install extract_emails\n```\n\n## Simple Usage\n```python\nfrom extract_emails.browsers.requests_browser import RequestsBrowser as Browser\nfrom extract_emails import DefaultFilterAndEmailFactory as Factory\nfrom extract_emails import DefaultWorker\n\nbrowser = Browser()\nurl = \'https://en.wikipedia.org/\'\nfactory = Factory(website_url=url, browser=browser)\nworker = DefaultWorker(factory)\ndata = worker.get_data()\nprint(data)\n"""\n[\n    PageData(\n        website=\'https://en.wikipedia.org/\',\n        page_url=\'https://en.wikipedia.org/Email_address\',\n        data={\'email\': [\'"John.Doe."@example.com\', \'x@example.com\']}\n    ),\n    PageData(\n        website=\'https://en.wikipedia.org/\',\n        page_url=\'https://en.wikipedia.org/Email_address2\',\n        data={\'email\': [\'"John.Doe2."@example.com\', \'x2@example.com\']}\n    ),\n]\n"""\n```\n',
    'author': 'Dmitrii Kurlov',
    'author_email': 'dmitriik@tutanota.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/dmitriiweb/extract-emails',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
