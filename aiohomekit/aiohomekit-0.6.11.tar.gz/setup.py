# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['aiohomekit',
 'aiohomekit.controller',
 'aiohomekit.controller.ip',
 'aiohomekit.crypto',
 'aiohomekit.http',
 'aiohomekit.model',
 'aiohomekit.model.characteristics',
 'aiohomekit.model.services',
 'aiohomekit.protocol',
 'aiohomekit.zeroconf']

package_data = \
{'': ['*']}

install_requires = \
['commentjson>=0.9.0,<0.10.0', 'cryptography>=2.9.2', 'zeroconf>=0.32.0']

entry_points = \
{'console_scripts': ['aiohomekitctl = aiohomekit.__main__:sync_main']}

setup_kwargs = {
    'name': 'aiohomekit',
    'version': '0.6.11',
    'description': 'An asyncio HomeKit client',
    'long_description': '# aiohomekit\n\n![CI](https://github.com/Jc2k/aiohomekit/workflows/CI/badge.svg?event=push) [![codecov](https://codecov.io/gh/Jc2k/aiohomekit/branch/master/graph/badge.svg)](https://codecov.io/gh/Jc2k/aiohomekit)\n\nThis library implements the HomeKit protocol for controlling Homekit accessories using asyncio.\n\nIt\'s primary use is for with Home Assistant. We target the same versions of python as them and try to follow their code standards.\n\nAt the moment we don\'t offer any API guarantees. API stability and documentation will happen after we are happy with how things are working within Home Assistant.\n\n## Contributing\n\n`aiohomekit` is primarily for use with Home Assistant. Lots of users are using it with devices from a wide array of vendors. As a community open source project we do not have the hardware or time resources to certify every device with multiple vendors projects. We may be conservative about larger changes or changes that are low level. We do ask where possible that any changes should be tested with a certified HomeKit implementations of shipping products, not just against emulators or other uncertified implementations.\n\nBecause API breaking changes would hamper our ability to quickly update Home Assistant to the latest code, if you can please submit a PR to update [homekit_controller](https://github.com/home-assistant/core/tree/dev/homeassistant/components/homekit_controller) too. If they don\'t your PR maybe on hold until someone is available to write such a PR.\n\nPlease bear in mind that some shipping devices interpret the HAP specification loosely. In general we prefer to match the behaviour of real HAP controllers even where their behaviour is not strictly specified. Here are just some of the kinds of problems we\'ve had to work around:\n\n* Despite the precise formatting of JSON being unspecified, there are devices in the wild that cannot handle spaces when parsing JSON. For example, `{"foo": "bar"}` vs `{"foo":"bar"}`. This means we never use a "pretty" encoding of JSON.\n* Despite a boolean being explicitly defined as `0`, `1`, `true` or `false` in the spec, some devices only support 3 of the 4. This means booleans must be encoded as `0` or `1`.\n* Some devices have shown themselves to be sensitive to headers being missing, in the wrong order or if there are extra headers. So we ensure that only the headers iOS sends are present, and that the casing and ordering is the same.\n* Some devices are sensitive to a HTTP message being split into separate TCP packets. So we take care to only write a full message to the network stack.\n\nAnd so on. As a rule we need to be strict about what we send and loose about what we receive.\n\n## Device compatibility\n\n`aiohomekit` is primarily tested via Home Assistant with a Phillips Hue bridge and an Eve Extend bridge. It is known to work to some extent with many more devices though these are not currently explicitly documented anywhere at the moment.\n\nYou can look at the problems your device has faced in the home-assistant [issues list](https://github.com/home-assistant/core/issues?q=is%3Aopen+is%3Aissue+label%3A%22integration%3A+homekit_controller%22).\n\n## FAQ\n\n### How do I use this?\n\nIt\'s published on pypi as `aiohomekit` but its still under early development - proceed with caution.\n\nThe main consumer of the API is the [homekit_controller](https://github.com/home-assistant/core/tree/dev/homeassistant/components/homekit_controller) in Home Assistant so that\'s the best place to get a sense of the API.\n\n### Does this support BLE accessories?\n\nNo. Eventually we hope to via [aioble](https://github.com/detectlabs/aioble) which provides an asyncio bluetooth abstraction that works on Linux, macOS and Windows.\n\n### Can i use this to make a homekit accessory?\n\nNo, this is just the client part. You should use one the of other implementations:\n\n * [homekit_python](https://github.com/jlusiardi/homekit_python/) (this is used a lot during aiohomekit development)\n * [HAP-python](https://github.com/ikalchev/HAP-python)\n\n### Why doesn\'t Home Assistant use library X instead?\n\nAt the time of writing this is the only python 3.7/3.8 asyncio HAP client with events support.\n\n### Why doesn\'t aiohomekit use library X instead?\n\nWhere possible aiohomekit uses libraries that are easy to install with pip, are ready available as wheels (including on Raspberry Pi via piwheels), are cross platform (including Windows) and are already used by Home Assistant. They should not introduce hard dependencies on uncommon system libraries. The intention here is to avoid any difficulty in the Home Assistant build process.\n\nPeople are often alarmed at the hand rolled HTTP code and suggest using an existing HTTP library like `aiohttp`. High level HTTP libraries are pretty much a non-starter because:\n\n* Of the difficulty of adding in HAP session security without monkey patches.\n* They don\'t expect responses without requests (i.e. events).\n* As mentioned above, some of these devices are very sensitive. We don\'t care if your change is compliant with every spec if it still makes a real world device cry. We are not in a position to demand these devices be fixed. So instead we strive for byte-for-byte accuracy on our write path. Any library would need to give us that flexibility.\n* Some parts of the responses are actually not HTTP, even though they look it.\n\nWe are also just reluctant to make a change that large for something that is working with a lot of devices. There is a big chance of introducing a regression.\n\nOf course a working proof of concept (using a popular well maintained library) that has been tested with something like a Tado internet bridge (including events) would be interesting.\n\n## Thanks\n\nThis library wouldn\'t have been possible without homekit_python, a synchronous implementation of both the client and server parts of HAP. \n',
    'author': 'John Carr',
    'author_email': 'john.carr@unrouted.co.uk',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Jc2k/aiohomekit',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
