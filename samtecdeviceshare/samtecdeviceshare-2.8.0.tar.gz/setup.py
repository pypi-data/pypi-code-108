# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['samtecdeviceshare', 'samtecdeviceshare.balena', 'samtecdeviceshare.emulation']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'aiofiles>=0.6.0,<0.7.0',
 'fastapi>=0.63.0,<0.64.0',
 'httpx>=0.16.1,<0.17.0',
 'pyaml-env>=1.1.0,<2.0.0',
 'pydantic>=1.7.3,<2.0.0',
 'pyhumps>=1.6.1,<2.0.0',
 'uvicorn>=0.13.3,<0.14.0']

extras_require = \
{':sys_platform == "linux"': ['python-networkmanager', 'dbus-python']}

setup_kwargs = {
    'name': 'samtecdeviceshare',
    'version': '2.8.0',
    'description': 'Handles a variety of common routines for SDC-based applications',
    'long_description': '# Samtec Device Connect Service\n\nA Python 3 SDC conforming REST API to run on IoT devices that enables user discovery, viewing, and management.\n\n## Installation\n\n```bash\npip install samtecdeviceshare\n```\n\n## Running\n\nFirst ensure all environment variables are set correctly.\nNote: To test locally for development ensure EMULATION and PYTHON_ENV are set.\n\n```bash\npython -m samtecdeviceshare.server\n```\n\n## Environment Variables\n\nA number of environment variables are supported for configuration. These configurations can also be contained in a yaml/json configuration file specified using `SDC_CONFIGURATION_PATH`. Env vars take precedence over the configuration file.\n\n### SDC Server / General\n\nThese variables are specific to this SDC service. The variables can also start with prefix `SDC_`.\n\n| Name              | Description                   | Default                                     |\n| ----------------- | ----------------------------- | ------------------------------------------- |\n| REST_ADDRESS      | Rest API Address              | 0.0.0.0                                     |\n| REST_PORT         | Rest port                     | 47546                                       |\n| ROOT_PATH         | API root path                 | \'\'                                          |\n| PYTHON_ENV        | enum: development production  | production                                  |\n| EMULATION         | Use emulated devices/io       | null                                        |\n| LOG_VERBOSE       | boolean verbose logs          | false                                       |\n\n### Application\n\nThese variables are used to provide app info that will be shared by SDC.\n\n| Name              | Description                   | Default                                     |\n| ----------------- | ----------------------------- | ------------------------------------------- |\n| APP_NAME          | Name of app                   | SDC App                                     |\n| APP_VERSION       | SemVer of app                 | 0.0.0                                       |\n| APP_WEB_PORT      | Embedded web app port         | 80                                          |\n| APP_IMG_PATH      | app icon path                 | {CURDIR}../static/img.png                   |\n| APP_LOG_PATH      | Path to store log files       | default tempdir()                           |\n| APP_LOCK_PATH     | Path to update lock file      | .__sdc.lock                                 |\n\n### Wireless Networks\n\nSDC can handle configuring N wireless networks. Prefix *SDC_* is required. Us integer `i` in prefix for defining multiple networks.\nA network can optionally be defined default. This will be primary method used to handle updates and will be exposed through REST API.\n\n| Name                     | Description                   | Default                         |\n| ------------------------ | ----------------------------- | ------------------------------- |\n| SDC_WIFI[i]_SSID         | WiFi SSID                     | null*                           |\n| SDC_WIFI[i]_MODE         | enum: HOTSPOT CLIENT DISABLED | DISABLED                        |\n| SDC_WIFI[i]_PASS         | WiFi passphrase               | null                            |\n| SDC_WIFI[i]_IFACE        | WiFi hardware interface       | null                            |\n| SDC_WIFI[i]_DEFAULT      | Use as default for updates    | False                           |\n\n### Wired Networks\n\nSDC can handle configuring N wired networks. Prefix *SDC_* is required. Us integer `i` in prefix for defining multiple networks.\n`SDC_ETH[i]_IFACE` or `SDC_ETH[i]_REGEX_IFACE` is required with the latter supporting regex matching. Be careful defining multiple networks with generic regular expression.\n[Most Linux distros follow a predictable naming scheme for interfaces.](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/networking_guide/sec-understanding_the_predictable_network_interface_device_names). When searching for interfaces, a fullmatch is required `re.fullmatch()`.\n\n| Name                        | Description                   | Default                      |\n| --------------------------- | ----------------------------- | ---------------------------- |\n| SDC_ETH[i]_IFACE            | Interface name (str)          | null                         |\n| SDC_ETH[i]_REGEX_IFACE      | Interface name (regex)        | null                         |\n| SDC_ETH[i]_METHOD           | Primary method                | WiredConnectionMethod.auto   |\n| SDC_ETH[i]_TIMEOUT          | Timeout of primary            | 15                           |\n| SDC_ETH[i]_FALLBACK         | Fallback method               | null                         |\n| SDC_ETH[i]_FALLBACK_TIMEOUT | Timeout to get DHCP address   | -1                           |\n\n### Balena\n\nRefer to Balena [documentation](https://www.balena.io/docs/learn/develop/runtime/) for list and description of variables.\n\n- BALENA_SUPERVISOR_API_KEY\n- BALENA_APP_ID\n- BALENA_DEVICE_TYPE\n- BALENA\n- BALENA_SUPERVISOR_ADDRESS\n- BALENA_SUPERVISOR_HOST\n- BALENA_DEVICE_UUID\n- BALENA_API_KEY\n- BALENA_APP_RELEASE\n- BALENA_SUPERVISOR_VERSION\n- BALENA_APP_NAME\n- BALENA_DEVICE_NAME_AT_INIT\n- BALENA_HOST_OS_VERSION\n- BALENA_SUPERVISOR_PORT\n\n## Development\n\n### Installing\n\n```bash\ngit clone git@bitbucket.org:samteccmd/samtecdeviceshare.git samtecdeviceshare\ncd samtecdeviceshare\npoetry install --dev\npoetry shell\n```\n\n### Testing\n\nFirst, run dummy Balena supervisor:\n\n```bash\nbash ./tests/dummy-supervisor.sh\n```\n\nNext, fire up REST server using uvicorn:\n\n```bash\nEMULATION=1 \\\nPYTHON_ENV="development" \\\nDEBUG=1 \\\nuvicorn samtecdeviceshare.server:app --reload --reload-dir ./samtecdeviceshare\n```\n\n**Interactive API docs** will be available: <http://127.0.0.1:8000/docs>\n\n### Unit Tests\n\n```bash\npylint --rcfile .pylintrc samtecdeviceshare\npytest\n```\n',
    'author': 'Adam Page',
    'author_email': 'adam.page@samtec.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
