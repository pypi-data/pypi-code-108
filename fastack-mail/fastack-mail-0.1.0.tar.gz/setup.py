# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['fastack_mail']

package_data = \
{'': ['*']}

install_requires = \
['aiosmtplib>=1.1.6,<2.0.0',
 'fastack>=4.0.0,<5.0.0',
 'pydantic[email]>=1.9.0,<2.0.0']

setup_kwargs = {
    'name': 'fastack-mail',
    'version': '0.1.0',
    'description': 'Simple plugin for sending email',
    'long_description': '# fastack-mail\n\nSimple plugin for sending email.\n\nThis plugin is inspired by [fastapi-mail](https://github.com/sabuhish/fastapi-mail)\n\n## Installation\n\n```\npip install fastack-mail\n```\n\n## Usage\n\n### Install plugin\n\n```py\nPLUGINS = [\n    ...,\n    "fastack_mail",\n]\n```\n\n### Configuration\n\n* `EMAIL_BACKEND` = "fastack_mail.backend.EmailBackend" [required]\n* `EMAIL_HOSTNAME` = SMTP Server (e.g. "localhost") [required]\n* `EMAIL_PORT` = SMTP Port Server (e.g. 8025) [required]\n* `EMAIL_USERNAME` = SMTP username (e.g. "john@doe.com") [optional]\n* `EMAIL_PASSWORD` = SMTP password (e.g. "luarbiasa") [optional]\n* `EMAIL_TIMEOUT` = Connection time out (default 60) [optional]\n* `EMAIL_USE_TLS` = If `True`, make the _initial_ connection to the server over TLS/SSL (default False)\n* `EMAIL_START_TLS` = If `True`, make the _initial_ connection to the server over plaintext, and then upgrade the connection to TLS/SSL. Not compatible with `EMAIL_USE_TLS`. (default False)\n* `EMAIL_VALIDATE_CERTS` = Determines if server certificates are validated (default True)\n* `EMAIL_CLIENT_CERT` = Path to client side certificate, for TLS verification. (default None)\n* `EMAIL_CLIENT_KEY` = Path to client side key, for TLS verification. (default None)\n* `EMAIL_CERT_BUNDLE` = Path to certificate bundle, for TLS verification. (default None)\n* `EMAIL_ASYNC_MODE` = If `True`, the `EmailBackend.send` function returns an awaitable object, if `False` it returns an immediate send result. (default False)\n* `DEFAULT_FROM_EMAIL` = Default sender email for use globally (if there is no sender email) (e.g. "Local \\<noreply@localhost\\>")\n\n### Example\n\nSee here https://github.com/fastack-dev/fastack-mail/tree/main/examples/mail\n',
    'author': 'aprilahijriyan',
    'author_email': 'hijriyan23@gmail.com',
    'maintainer': 'aprilahijriyan',
    'maintainer_email': '37798612+aprilahijriyan@users.noreply.github.com',
    'url': 'https://github.com/fastack-dev/fastack-mail',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.10',
}


setup(**setup_kwargs)
