# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['bobcat_miner']

package_data = \
{'': ['*']}

install_requires = \
['aiohttp>=3.8.1,<4.0.0',
 'backoff>=1.11.1,<2.0.0',
 'beautifulsoup4>=4.10.0,<5.0.0',
 'click>=8.0.3,<9.0.0',
 'discord-lumberjack>=1.0.4,<2.0.0',
 'filelock>=3.4.2,<4.0.0',
 'requests>=2.27.0,<3.0.0']

entry_points = \
{'console_scripts': ['bobcat = bobcat_miner.cli:cli']}

setup_kwargs = {
    'name': 'bobcat-miner',
    'version': '0.12.0',
    'description': "A command line tool used to automate the Bobcat miner. This project also offers a robust python SDK's for interacting with the Bobcat miner.",
    'long_description': '[![PyPI](https://img.shields.io/pypi/v/bobcat_miner.svg)](https://pypi.org/project/bobcat-miner/)\n[![Dockerhub](https://img.shields.io/docker/v/aidanmelen/bobcat?color=blue&label=docker%20build)](https://hub.docker.com/r/aidanmelen/bobcat)\n[![Release](https://github.com/aidanmelen/bobcat-miner-python/actions/workflows/release.yaml/badge.svg)](https://github.com/aidanmelen/bobcat-miner-python/actions/workflows/release.yaml)\n[![Tests](https://github.com/aidanmelen/bobcat-miner-python/actions/workflows/tests.yaml/badge.svg)](https://github.com/aidanmelen/bobcat-miner-python/actions/workflows/tests.yaml)\n[![Lint](https://github.com/aidanmelen/bobcat-miner-python/actions/workflows/lint.yaml/badge.svg)](https://github.com/aidanmelen/bobcat-miner-python/actions/workflows/lint.yaml)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/aidanmelen/bobcat-miner-python/actions/workflows/lint.yaml)\n\n\n# bobcat miner python\n\nA command line tool used to automate the Bobcat miner. This project also offers a robust python SDK\'s for interacting with the Bobcat miner.\n\n## Install\n\n```bash\n$ pipx install bobcat-miner\n```\n\nPlease see this [guide](https://packaging.python.org/en/latest/guides/installing-stand-alone-command-line-tools/) for more information about installing stand alone command line tools with [pipx](https://pypa.github.io/pipx/).\n\n## Quick Start\n\nThe `bobcat autopilot` command will automatically diagnose and repair the Bobcat miner!\n\n```bash\n$ bobcat autopilot\n✅ Sync Status: Synced (gap:-1) ✨\n✅ Relay Status: Not Relayed ✨\n✅ Network Status: Good 📶\n✅ Temperature Status: Good (38°C) ☀️\n```\n\nor run with the offical Docker container\n\n```bash\n$ docker run --rm -it aidanmelen/bobcat autopilot\n```\n\nRun `bobcat --help` to learn about the available commands and options.\n\n## Monitoring with Discord\n\nSend events to a Discord channel using a [webhook URL](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)\n\n```bash\n$ bobcat --discord-webhook-url https://discord.com/api/webhooks/xxx autopilot\n✅ Sync Status: Synced (gap:0) ✨\n⚠️ Relay Status: Relayed\n✅ Network Status: Good 📶\n❌ Temperature Status: Hot (78°C) 🌋\n```\n\nBy default, all events `WARNING` or higher (i.e. `ERROR` and `CRITICAL`) will now be sent to the Discord channel. This can be configured to include `DEBUG` and `INFO` events as well.\n\n<img src="https://raw.githubusercontent.com/aidanmelen/bobcat-miner-python/main/images/bobcat-autopilot-discord-app.png" alt="drawing" style="width:500px;"/>\n\n## Finding your Bobcat\n\n### Manually Specify the Hostname / IP Address\n\nBy default, the Bobcat Autopilot will search the common `192.168.0.0/24` and `10.0.0.0/24` local networks and try to establish a Bobcat connection.\n\nOtherwise, you can follow these [instructions](https://bobcatminer.zendesk.com/hc/en-us/articles/4412905935131-How-to-Access-the-Diagnoser) to find your Bobcats\'s ip address and manually specify it with:\n\n```bash\n$ bobcat --hostname 192.168.0.10 -S DEBUG autopilot\n🐛 Connected to Bobcat: 192.168.0.10\n🐛 The Bobcat Autopilot is starting 🚀 🚀 🚀\n```\n\n### Search for Bobcat by Animal Name\n\nThis will connect to the Bobcat on your network that matches the animal name.\n\n```bash\n$ bobcat --animal "Fancy Awesome Bobcat" -S DEBUG autopilot\n🐛 Connected to Bobcat: 192.168.0.10\n🐛 Refresh: Miner Data\n🐛 Verified Bobcat Animal: fancy-awesome-bobcat\n🐛 The Bobcat Autopilot is starting 🚀 🚀 🚀\n```\n\n<!-- ![Bobcat Autopilot Term](https://raw.githubusercontent.com/aidanmelen/bobcat-miner-python/main/images/bobcat-autopilot-term.png) -->\n### Bobcat Dry Run\n\nThis example is admittedly contrived, but it demonstrates how a dry run can show what actions would normally be performed against the bobcat.\n\n```bash\n$ bobcat --dry-run reboot\nDo you want to reboot the Bobcat? [y/N]: y\n⚠️ Dry run is enabled: Reboot Skipped\n```\n\n## Bobcat SDK Usage\n\n```python\nimport bobcat_miner\n\nbobcat = bobcat_miner.Bobcat("192.168.1.10")\n\n# refresh\nbobcat.refresh_status()\nbobcat.refresh_miner()\nbobcat.refresh_speed()\nbobcat.refresh_temp()\nbobcat.refresh_dig()\nbobcat.refresh() # all endpoints\n\n# properties\nbobcat.status\nbobcat.gap\nbobcat.blockchain_height\nbobcat.epoch\nbobcat.tip\nbobcat.ota_version\nbobcat.region\nbobcat.frequency_plan\nbobcat.animal\nbobcat.helium_animal\nbobcat.pubkey\nbobcat.state\nbobcat.miner_status\nbobcat.miner_height\nbobcat.miner_alert\nbobcat.miner_desc\nbobcat.names\nbobcat.image\nbobcat.created\nbobcat.p2p_status\nbobcat.ports_desc\nbobcat.ports\nbobcat.private_ip\nbobcat.public_ip\nbobcat.peerbook\nbobcat.timestamp\nbobcat.error\nbobcat.temp0\nbobcat.temp1\nbobcat.coldest_temp\nbobcat.hottest_temp\nbobcat.temp0_c\nbobcat.temp1_c\nbobcat.temp0_f\nbobcat.temp1_f\nbobcat.download_speed\nbobcat.upload_speed\nbobcat.latency\nbobcat.dig_name\nbobcat.dig_message\nbobcat.dig_dns\nbobcat.dig_records\n\n# actions\nbobcat.reboot()\nbobcat.reset()\nbobcat.resync()\nbobcat.fastsync()\n```\n\n## Troubleshooting\n\nPlease see [No Witness\'s Troubleshooting Guide](https://www.nowitness.org/troubleshooting/) for more information.\n\n## Donations\n\nDonations are welcome and appreciated! :gift:\n\n[![HNT: 14HmckNU4WHDDtGH29FMqVENzZAYh5a9XRiLfY2AN6ghfHMvAuR](https://raw.githubusercontent.com/aidanmelen/bobcat-miner-python/main/images/wallet.jpg)](https://explorer-v1.helium.com/accounts/14HmckNU4WHDDtGH29FMqVENzZAYh5a9XRiLfY2AN6ghfHMvAuR)\n\nHNT: [14HmckNU4WHDDtGH29FMqVENzZAYh5a9XRiLfY2AN6ghfHMvAuR](https://explorer-v1.helium.com/accounts/14HmckNU4WHDDtGH29FMqVENzZAYh5a9XRiLfY2AN6ghfHMvAuR)\n',
    'author': 'Aidan Melen',
    'author_email': 'aidanmelen@protonmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/aidanmelen/bobcat-miner-python',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
