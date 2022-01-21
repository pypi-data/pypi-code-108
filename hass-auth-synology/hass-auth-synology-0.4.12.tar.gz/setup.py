# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['hass_auth_synology']

package_data = \
{'': ['*']}

install_requires = \
['homeassistant>=2021.11.2,<2022.0.0']

entry_points = \
{'console_scripts': ['hass-auth-synology = hass_auth_synology.install:cli']}

setup_kwargs = {
    'name': 'hass-auth-synology',
    'version': '0.4.12',
    'description': 'Synology authentication provider for Home Assistant',
    'long_description': "# Authentication provider using Synology DSM users for Home Assistant\n\n![PyPI](https://img.shields.io/pypi/v/hass-auth-synology)\n![GitHub branch checks state](https://img.shields.io/github/checks-status/sdebruyn/hass-auth-synology/main?label=build)\n![Codecov](https://img.shields.io/codecov/c/github/sdebruyn/hass-auth-synology?token=XC9UFW1RKH)\n![Maintenance](https://img.shields.io/maintenance/yes/2022)\n![GitHub](https://img.shields.io/github/license/sdebruyn/hass-auth-synology)\n\nThe Synology authentication provider lets you authenticate using the users in your Synology DSM. Anyone with a user account on your Synology NAS will be able to login.\n\nThe provider supports 2-factor authentication, according to what is configured in DSM.\nWhen logging in, there will be a field to enter the 2FA code. The field is optional, but it should be used if your account in DSM requires 2FA. Otherwise, it can be left empty.\n\nThe use of 2FA within this provider is independent of the 2FA configuration in Home Assistant. If you enable 2FA in Home Assistant, and it is also enabled in Synology, you will have to enter 2 2FA codes.\n\nThe provider requires DSM 7.0 or newer.\n\n## Installation\n\n### Home Assistant Container\n\nUse this package's container instead of the Home Assistant one.\n\n```\nghcr.io/sdebruyn/hass-auth-synology:latest\n```\n\n### Home Assistant Core\n\nThe installation will have to be redone everytime you update Home Assistant.\n\n1. Make sure the Home Assistant virtualenv is activated: `source bin/activate`\n2. Install this package: `pip3 install hass-auth-synology`\n3. Run the installation command: `hass-auth-synology install`\n\n### Home Assistant Supervised\n\nThe installation will have to be redone everytime you update Home Assistant.\n\n1. Search for the “SSH & Web Terminal” add-on in the add-on store and install it.\n2. Configure the username and password/authorized_keys options.\n3. Start the “SSH & Web Terminal” add-on\n4. Run the following code through the web terminal:\n    ```shell\n    pip3 install hass-auth-synology\n   hass-auth-synology install\n    ```\n5. You can now disable and remove the “SSH & Web Terminal” add-on again.\n\n## Configuration\n\nAdd the following to your Home Assistant configuration:\n\n```yaml\nhomeassistant:\n  auth_providers:\n    - type: synology\n      host: nas.local\n      port: 443\n      secure: true\n      verify_cert: true\n```\n\n* `host`: IP address or hostname of your NAS.\n* `port`: Port on which DSM is available. Make sure to use one corresponding to HTTP or HTTPS as configured with `secure` .\n* `secure` (optional): Enable this to use HTTPS instead of HTTP. (default: false)\n* `verify_cert` (optional): Enable this to verify the certificate when using HTTPS (default: false).\nMake sure to disable this when using self-signed certificates or an IP address instead of a hostname.\nThe setting is ignored when `secure` is false.\n\n## Troubleshooting\n\nIf any errors occur, make sure to check your Home Assistant logs. If the connection succeeds, but authentication fails, Synology DSM will output an error code.\nThe meaning of the error code can be found [in the Synology DSM Login API documentation](https://global.download.synology.com/download/Document/Software/DeveloperGuide/Os/DSM/All/enu/DSM_Login_Web_API_Guide_enu.pdf).\n\nFeel free to open an issue on GitHub if you encounter any issues.\n\n## License & attribution\n\nApache v2.0\n\nTest utilities under `tests` are coming from [Home Assistant Core](https://github.com/home-assistant/core).\n",
    'author': 'Sam Debruyn',
    'author_email': 'sam@debruyn.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/sdebruyn/hass-auth-synology',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
