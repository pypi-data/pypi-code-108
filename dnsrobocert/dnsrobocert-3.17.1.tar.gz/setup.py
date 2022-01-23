# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['dnsrobocert', 'dnsrobocert.core']

package_data = \
{'': ['*']}

install_requires = \
['acme>=1,<2',
 'boto3',
 'certbot>=1,<2',
 'cffi>=1',
 'colorama>=0',
 'coloredlogs>=14',
 'cryptography>=2',
 'dns-lexicon[full]>=3,<4',
 'dnspython>=2',
 'jsonschema>=3',
 'localzone',
 'lxml>=4',
 'pem>=20',
 'pyopenssl>=19',
 'pyyaml>=5',
 'schedule>=0',
 'softlayer',
 'tldextract>=3',
 'xmltodict',
 'zeep']

entry_points = \
{'console_scripts': ['dnsrobocert = dnsrobocert.core.main:main']}

setup_kwargs = {
    'name': 'dnsrobocert',
    'version': '3.17.1',
    'description': 'A tool to manage your DNS-challenged TLS certificates',
    'long_description': '======\n|logo|\n======\n\n|version| |python_support| |docker| |ci| |coverage|\n\n.. |logo| image:: https://adferrand.github.io/dnsrobocert/images/dnsrobocert.svg\n    :alt: DNSroboCert\n.. |version| image:: https://img.shields.io/pypi/v/dnsrobocert\n    :target: https://pypi.org/project/dnsrobocert/\n.. |python_support| image:: https://img.shields.io/pypi/pyversions/dnsrobocert\n    :target: https://pypi.org/project/dnsrobocert/\n.. |docker| image:: https://img.shields.io/docker/image-size/adferrand/dnsrobocert\n    :target: https://microbadger.com/images/adferrand/dnsrobocert\n.. |ci| image:: https://img.shields.io/azure-devops/build/adferrand/338d4cba-ab35-4cf9-a9c6-1d2601554b32/21/master\n    :target: https://dev.azure.com/adferrand/dnsrobocert/_build/latest?definitionId=21&branchName=master\n.. |coverage| image:: https://img.shields.io/azure-devops/coverage/adferrand/338d4cba-ab35-4cf9-a9c6-1d2601554b32/21\n    :target: https://dev.azure.com/adferrand/dnsrobocert/_build?definitionId=21&view=ms.vss-pipelineanalytics-web.new-build-definition-pipeline-analytics-view-cardmetrics\n\n.. tag:intro-begin\n\n.. contents:: Table of Contents\n   :local:\n\nFeatures\n========\n\nDNSroboCert is designed to manage `Let\'s Encrypt`_ SSL certificates based on `DNS challenges`_.\n\n* Let\'s Encrypt wildcard and regular certificates generation by Certbot_ using DNS challenges,\n* Integrated automated renewal of almost expired certificates,\n* Standardized API through Lexicon_ library to insert the DNS challenge with various DNS providers,\n* Centralized YAML configuration file to maintain several certificates and several DNS providers\n  with configuration validity control,\n* Modification of container configuration without restart,\n* Flexible hooks upon certificate creation/renewal including containers restart, commands in containers\n  or custom hooks,\n* Support for `DNS alias mode`_ (see the ``follow_cnames`` option in the `certificate section`_),\n* Linux, Mac OS X and Windows support, with a particular care for Docker services,\n* Delivered as a standalone application and a Docker image.\n\n.. _DNS alias mode: https://github.com/acmesh-official/acme.sh/wiki/DNS-alias-mode\n.. _certificate section: https://dnsrobocert.readthedocs.io/en/latest/configuration_reference.html#certificate-properties\n\nWhy use DNSroboCert\n===================\n\nIf you are reading these lines, you certainly want to secure all your services using Let\'s Encrypt SSL\ncertificates, which are free and accepted everywhere.\n\nIf you want to secure Web services through HTTPS, there is already plenty of great tools. In the Docker\nworld, one can check Traefik_, or nginx-proxy_ + letsencrypt-nginx-proxy-companion_. Basically, theses tools\nwill allow automated and dynamic generation/renewal of SSL certificates, based on TLS or HTTP challenges,\non top of a reverse proxy to encrypt everything through HTTPS.\n\nSo far so good, but you may fall in one of the following categories:\n\n1. You are in a firewalled network, and your HTTP/80 and HTTPS/443 ports are not opened to the outside world.\n2. You want to secure non-Web services (like LDAP, IMAP, POP, etc.) were the HTTPS protocol is of no use.\n3. You want to generate a wildcard certificate, valid for any sub-domain of a given domain.\n\nFor the first case, ACME servers need to be able to access your website through HTTP (for HTTP challenges)\nor HTTPS (for TLS challenges) in order to validate the certificate. With a firewall these two challenges -\nwhich are widely used in HTTP proxy approaches - will not be usable: you need to ask a DNS challenge.\nPlease note that traefik embed DNS challenges, but only for few DNS providers.\n\nFor the second case, there is no website to use TLS or HTTP challenges, and you should ask a DNS challenge.\nOf course you could create a "fake" website to validate the domain using a HTTP challenge, and reuse the\ncertificate on the "real" service. But it is a workaround, and you have to implement a logic to propagate\nthe certificate, including during its renewal. Indeed, most of the non-Web services will need to be\nrestarted each time the certificate is renewed.\n\nFor the last case, the use of a DNS challenge is mandatory. Then the problems concerning certificates\npropagation that have been discussed in the second case will also occur.\n\nThe solution is a dedicated and specialized tool which handles the creation/renewal of Let\'s Encrypt\ncertificates, and ensure their propagation in the relevant services. It is the purpose of\nthis project.\n\n.. _Let\'s Encrypt: https://letsencrypt.org/\n.. _DNS challenges: https://tools.ietf.org/html/draft-ietf-acme-acme-01#page-44\n.. _Certbot: https://github.com/certbot/certbot\n.. _Lexicon: https://github.com/AnalogJ/lexicon\n.. _Traefik: https://hub.docker.com/_/traefik/\n.. _nginx-proxy: https://hub.docker.com/r/jwilder/nginx-proxy/\n.. _letsencrypt-nginx-proxy-companion: https://hub.docker.com/r/jrcs/letsencrypt-nginx-proxy-companion/\n\n.. tag:intro-end\n\nDocumentation\n=============\n\nOnline documentation (user guide, configuration reference) is available in the `DNSroboCert documentation`_.\n\nFor a quick start, please have a look in particular at the `User guide`_ and the `Lexicon provider configuration`_.\n\nSupport\n=======\n\nDo not hesitate to join the `DNSroboCert community on Spectrum`_ if you need help to use or develop DNSroboCert!\n\nContributing\n============\n\nIf you want to help in the DNSroboCert development, you are welcome!\nPlease have a look at the `Developer guide`_ page to know how to start.\n\n.. _DNSroboCert documentation: https://dnsrobocert.readthedocs.io\n.. _User guide: https://dnsrobocert.readthedocs.io/en/latest/user_guide.html\n.. _Lexicon provider configuration: https://dnsrobocert.readthedocs.io/en/latest/providers_options.html\n.. _Developer guide: https://dnsrobocert.readthedocs.io/en/latest/developer_guide.html\n.. _DNSroboCert community on Spectrum: https://spectrum.chat/dnsrobocert\n',
    'author': 'Adrien Ferrand',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://dnsrobocert.readthedocs.io',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
