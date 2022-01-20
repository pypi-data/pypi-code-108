# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['bobcat_miner']

package_data = \
{'': ['*']}

install_requires = \
['backoff>=1.11.1,<2.0.0',
 'click>=8.0.3,<9.0.0',
 'discord-lumberjack>=1.0.4,<2.0.0',
 'filelock>=3.4.2,<4.0.0',
 'requests>=2.27.0,<3.0.0']

entry_points = \
{'console_scripts': ['bobcat = bobcat_miner.cli:cli']}

setup_kwargs = {
    'name': 'bobcat-miner',
    'version': '0.11.1',
    'description': "A command line tool used to automate the Bobcat miner. This project also offers a robust python SDK's for interacting with the Bobcat miner.",
    'long_description': '[![PyPI](https://img.shields.io/pypi/v/bobcat_miner.svg)](https://pypi.org/project/bobcat-miner/)\n[![Dockerhub](https://img.shields.io/docker/v/aidanmelen/bobcat?color=blue&label=docker%20build)](https://hub.docker.com/r/aidanmelen/bobcat)\n[![Release](https://github.com/aidanmelen/bobcat-miner-python/actions/workflows/release.yaml/badge.svg)](https://github.com/aidanmelen/bobcat-miner-python/actions/workflows/release.yaml)\n[![Tests](https://github.com/aidanmelen/bobcat-miner-python/actions/workflows/tests.yaml/badge.svg)](https://github.com/aidanmelen/bobcat-miner-python/actions/workflows/tests.yaml)\n[![Lint](https://github.com/aidanmelen/bobcat-miner-python/actions/workflows/lint.yaml/badge.svg)](https://github.com/aidanmelen/bobcat-miner-python/actions/workflows/lint.yaml)\n[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/aidanmelen/bobcat-miner-python/actions/workflows/lint.yaml)\n\n\n# bobcat miner python\n\nA command line tool used to automate the Bobcat miner. This project also offers a robust python SDK\'s for interacting with the Bobcat miner.\n\n## Install\n\n```bash\n# install command line tools\n$ pipx install bobcat-miner\n\n# install SDK\n$ pip3 install bobcat-miner\n```\n\nPlease see this [guide](https://packaging.python.org/en/latest/guides/installing-stand-alone-command-line-tools/) for more information about installing stand alone command line tools with [pipx](https://pypa.github.io/pipx/).\n\n## Bobcat Autopilot Usage\n\nThe `bobcat autopilot` command will automatically diagnose and repair the Bobcat!\n\nFollow these [instructions](https://bobcatminer.zendesk.com/hc/en-us/articles/4412905935131-How-to-Access-the-Diagnoser) to find your Bobcats\'s ip address.\n\n![Bobcat Autopilot Term](https://raw.githubusercontent.com/aidanmelen/bobcat-miner-python/main/images/bobcat-autopilot-term.png)\n\nThe `bobcat` command line tool accepts both command line options and environment variables. Please see the `bobcat --help` for more information.\n\n### Bobcat Dry Run\n\nDiagnostics checks will run and all actions will be skipped during a Bobcat dry run.\n\n```bash\n$ bobcat -i 192.168.0.10 -l DEBUG --dry-run autopilot\n🚧 Bobcat Autopilot Dry Run Enabled. Actions such as reboot, reset, resync, and fastsync will be skipped. Wait times will only last 1 second.\n```\n\n### Discord Monitoring\n\nSend `bobcat` logs to a Discord channel using a [webhook url](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks)\n\n```bash\n$ export BOBCAT_LOG_LEVEL=DEBUG\n$ export BOBCAT_IP_ADDRESS=192.168.0.10\n$ export BOBCAT_DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/xxx/xxx\n$ bobcat autopilot\n🚀 The Bobcat Autopilot is starting\n```\n\nand watch your logs stream your Discord channel!\n\n![Bobcat Autopilot Discord](https://raw.githubusercontent.com/aidanmelen/bobcat-miner-python/main/images/bobcat-autopilot-discord.png)\n\n### Log File\n\nSend logs to a file\n\n```bash\n$ bobcat --ip-address 192.168.0.10 --log-file bobcat-autopilot.log autopilot\n🚀 The Bobcat Autopilot is starting\n```\n\n### Bobcat Docker Container\n\nRun the `bobcat` command line tool as a docker container.\n\n```bash\n$ docker run --rm -it aidanmelen/bobcat -i 192.168.0.10 status\n{\n    "status": "Synced",\n    "gap": "-2",\n    "miner_height": "1185959",\n    "blockchain_height": "1185957",\n    "epoch": "31260"\n}\n```\n\n## Bobcat Autopilot SDK Usage\n\n```python\nimport bobcat_miner\n\nbobcat = bobcat_miner.Bobcat("192.168.1.100")\nautopilot = bobcat_miner.Autopilot(bobcat)\n\n# Automatically diagnose and repair the Bobcat\nautopilot.run()\n\n# diagnostics\nautopilot.is_relayed()\nautopilot.is_temp_dangerous()\nautopilot.is_network_speed_slow()\nautopilot.is_syncing()\nautopilot.has_errors()\n\n# actions\nautopilot.ping()        # Ping the Bobcat until it connects or attempts are maxed out\nautopilot.reboot()      # Reboot the Bobcat and wait for connection\nautopilot.reset()       # Reset the Bobcat and wait for connection or exceeds max attempts\nautopilot.resync()      # Fastsync the Bobcat and wait for connection\nautopilot.fastsync()    # Fastsync the Bobcat until the gap is less than 400 or exceeds max attempts\nautopilot.is_syncing()  # Poll the Bobcat\'s gap to see if it is syncing over time\n```\n\n## Bobcat SDK Usage\n\n```python\nimport bobcat_miner\n\nbobcat = bobcat_miner.Bobcat("192.168.1.100")\n\n# refresh\nbobcat.refresh_status()\nbobcat.refresh_miner()\nbobcat.refresh_speed()\nbobcat.refresh_temp()\nbobcat.refresh_dig()\nbobcat.refresh()\n\n# properties\nbobcat.status\nbobcat.gap\nbobcat.miner_height\nbobcat.blockchain_height\nbobcat.epoch\nbobcat.tip\nbobcat.ota_version\nbobcat.region\nbobcat.frequency_plan\nbobcat.animal\nbobcat.name\nbobcat.pubkey\nbobcat.state\nbobcat.miner_status\nbobcat.names\nbobcat.image\nbobcat.created\nbobcat.p2p_status\nbobcat.ports_desc\nbobcat.ports\nbobcat.private_ip\nbobcat.public_ip\nbobcat.peerbook\nbobcat.peerbook_miner\nbobcat.peerbook_listen_address\nbobcat.peerbook_peers\nbobcat.timestamp\nbobcat.error\nbobcat.temp0\nbobcat.temp1\nbobcat.temp0_c\nbobcat.temp1_c\nbobcat.temp0_f\nbobcat.temp1_f\nbobcat.download_speed\nbobcat.upload_speed\nbobcat.latency\nbobcat.dig_name\nbobcat.dig_message\nbobcat.dig_dns\nbobcat.dig_records\n\n# actions\nbobcat.ping()\nbobcat.reboot()\nbobcat.reset()\nbobcat.resync()\nbobcat.fastsync()\n\n# diagnostics\nbobcat.is_bobcat()\n```\n\n## Troubleshooting\n\nPlease see [No Witness\'s Troubleshooting Guide](https://www.nowitness.org/troubleshooting/) for more information.\n\n## Donations\n\nDonations are welcome and appreciated! :gift:\n\n[![HNT: 14HmckNU4WHDDtGH29FMqVENzZAYh5a9XRiLfY2AN6ghfHMvAuR](https://raw.githubusercontent.com/aidanmelen/bobcat-miner-python/main/images/wallet.jpg)](https://explorer-v1.helium.com/accounts/14HmckNU4WHDDtGH29FMqVENzZAYh5a9XRiLfY2AN6ghfHMvAuR)\n\nHNT: [14HmckNU4WHDDtGH29FMqVENzZAYh5a9XRiLfY2AN6ghfHMvAuR](https://explorer-v1.helium.com/accounts/14HmckNU4WHDDtGH29FMqVENzZAYh5a9XRiLfY2AN6ghfHMvAuR)\n',
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
