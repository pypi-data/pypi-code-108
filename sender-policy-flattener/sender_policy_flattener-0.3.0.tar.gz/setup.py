# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sender_policy_flattener', 'sender_policy_flattener.test']

package_data = \
{'': ['*']}

install_requires = \
['dnspython>=2.2.0,<3.0.0', 'netaddr>=0.8.0,<0.9.0']

entry_points = \
{'console_scripts': ['spflat = sender_policy_flattener.cli:main']}

setup_kwargs = {
    'name': 'sender-policy-flattener',
    'version': '0.3.0',
    'description': 'Condense SPF records to network blocks to avoid DNS Lookup Limits',
    'long_description': "sender policy flattener\n=======================\nWe had a problem in our organisation that caused our SPF records to become invalid:\n\nWhen customers computers were querying our SPF records, there were more than 10 lookups required after following all of the ``include:`` remarks.\n\nSolution? Query them ourselves, and create a much more condense list of SPF records.\n\n#### But wait... What if the downstream records change?\n\nPart of what the script does is that it creates a JSON file that keeps track of the last list of IP Addresses that your combination of SPF records had.\n\nWhen the hashsum of your IP Addresses changes, it will send out an email (or just dump HTML if it can't find an email server) with a handy diff & BIND format for viewing what has changed, and promptly updating it.\n\nYou could theoretically extract the flat IP records from the resulting JSON file and automatically update your DNS configuration with it.\n\nInstallation\n--------------------\n\n#### via git clone\n\nClone this repo and run\n\n```shell\npip install poetry\npoetry install\n```\n\n\n#### via pip\n\n```shell\npip install sender_policy_flattener\n```\n\n\nUsage\n----------------\n\n```\nusage: spflat [-h] [-c CONFIG] [-r RESOLVERS] [-e MAILSERVER] [-t TOADDR]\n              [-f FROMADDR] [-s SUBJECT] [-D SENDING_DOMAIN] [-d DOMAINS]\n              [-o OUTPUT]\n\nA script that crawls and compacts SPF records into IP networks. This helps to\navoid exceeding the DNS lookup limit of the Sender Policy Framework (SPF)\nhttps://tools.ietf.org/html/rfc7208#section-4.6.4\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -c CONFIG, --config CONFIG\n                        Name/path of JSON configuration file\n  -r RESOLVERS, --resolvers RESOLVERS\n                        Comma separated DNS servers to be used\n  -e MAILSERVER, -mailserver MAILSERVER\n                        Server to use for mailing alerts\n  -t TOADDR, -to TOADDR\n                        Recipient address for email alert\n  -f FROMADDR, -from FROMADDR\n                        Sending address for email alert\n  -s SUBJECT, -subject SUBJECT\n                        Subject string, must contain {zone}\n  -D SENDING_DOMAIN, --sending-domain SENDING_DOMAIN\n                        The domain which emails are being sent from\n  -d DOMAINS, --domains DOMAINS\n                        Comma separated domain:rrtype to flatten to IP\n                        addresses. Imagine these are your SPF include\n                        statements.\n  -o OUTPUT, --output OUTPUT\n                        Name/path of output file\n```\n\nExample\n\n```shell\nspflat --resolvers 8.8.8.8,8.8.4.4 \\\n    --to me@mydomain.com \\\n    --from admin@mydomain.com \\\n    --subject 'SPF for {zone} has changed!' \\\n    --domains gmail.com:txt,sendgrid.com:txt,yahoo.com:a \\\n    --sending-domain mydomain.com\n```\nor\n\n```shell\nspflat --config spf.json\n```\nYou can specify a config file, or you can specify all of the optional arguments from the command line.\n\nI've provided a ``settings.json`` file with an example configuration file.\n\n\nSupported Python versions\n-------------------------\nSee the latest result of the build: https://github.com/cetanu/sender_policy_flattener/actions\n\n\n3rd party dependencies\n----------------------\n* netaddr\n* dnspython\n\n\nExample email format\n--------------------\n<img src='https://raw.githubusercontent.com/cetanu/sender_policy_flattener/master/example/email_example.png' alt='example screenshot'></img>\n",
    'author': 'Vasili Syrakis',
    'author_email': 'cetanu@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/cetanu/sender_policy_flattener',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6.2,<4.0.0',
}


setup(**setup_kwargs)
