# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': '.'}

packages = \
['iometrics', 'iometrics.pytorch_lightning']

package_data = \
{'': ['*']}

install_requires = \
['psutil>=5.8.0,<6.0.0']

entry_points = \
{'console_scripts': ['iometrics = iometrics.cli:iometrics_cli_entrypoint']}

setup_kwargs = {
    'name': 'iometrics',
    'version': '0.0.8',
    'description': 'Network and Disk I/O Stats Monitor',
    'long_description': '# iometrics\n\n[![Python](https://github.com/elgalu/iometrics/raw/main/docs/img/badges/language.svg)](https://devdocs.io/python/)\n\nMonitor and log Network and Disks statistics in MegaBytes per second.\n\n## Install\n\n```sh\npip install iometrics\n```\n\n## Usage\n\n### Pytorch-lightning integration\n\n```py\nfrom pytorch_lightning import Trainer\nfrom iometrics.pytorch_lightning.callbacks import NetworkAndDiskStatsMonitor\n\nnet_disk_stats = NetworkAndDiskStatsMonitor()\n\ntrainer = Trainer(callbacks=[net_disk_stats])\n```\n\n#### Metrics generated\n\n* **network/recv_MB_per_sec**    – Received MB/s on all relevant network interfaces as a SUM.\n* **network/sent_MB_per_sec**    – Sent     MB/s on all relevant network interfaces as a SUM.\n* **disk/util%**                 – Disk utilization percentage as the average of all disk devices.\n* **disk/read_MB_per_sec**       – Disks read MB/s    as the sum of all disk devices.\n* **disk/writ_MB_per_sec**       – Disks written MB/s as the sum of all disk devices.\n* **disk/io_read_count_per_sec** – Disks read I/O operations per second    as the sum of all disk devices.\n* **disk/io_writ_count_per_sec** – Disks written I/O operations per second as the sum of all disk devices.\n\n#### Screen shot\n\n<img id="png_recv_MB_per_sec" width="450"\n src="https://github.com/elgalu/iometrics/raw/main/docs/img/metrics/network_recv_MB_per_sec.png" />\n\n### Pure-Python implementation (zero dependencies)\n\n#### Quick check\n\n```sh\npython -c \'from iometrics.example import usage; usage()\'\n```\n\n#### Example output\n\n```markdown\n|        Network (MBytes/s)       | Disk Util |            Disk MBytes          |           Disk I/O          |\n|     Received    |     Sent      |     %     |    MB/s Read    |  MB/s Written |     I/O Read    | I/O Write |\n|   val  |   avg  |  val  |  avg  | val | avg |  val   |  avg   |  val  |  avg  |   val  |   avg  | val | avg |\n| ------:| ------:| -----:| -----:| ---:| ---:| ------:| ------:| -----:| -----:| ------:| ------:| ---:| ---:|\n|    4.6 |    3.5 |   0.1 |   0.1 |  49 |   2 |   52.8 |    1.1 |   0.0 |   0.9 |    211 |      4 |   5 |  18 |\n|    4.1 |    3.5 |   0.1 |   0.1 |  61 |   3 |   60.4 |    2.4 |  40.3 |   1.7 |    255 |     10 | 149 |  21 |\n```\n\n#### Full code\n\n```py\nimport time\nfrom iometrics import NetworkMetrics, DiskMetrics\nfrom iometrics.example import DUAL_METRICS_HEADER\nnet  = NetworkMetrics()\ndisk = DiskMetrics()\nfor i in range(100):\n    time.sleep(1)\n    net.update_stats()\n    disk.update_stats()\n    if i % 15 == 0:\n        print(DUAL_METRICS_HEADER)\n    row = (\n        f"| {net.mb_recv_ps.val:6.1f} | {net.mb_recv_ps.avg:6.1f} "\n        f"| {net.mb_sent_ps.val:5.1f} | {net.mb_sent_ps.avg:5.1f} "\n        f"| {int(disk.io_util.val):3d} | {int(disk.io_util.avg):3d} "\n        f"| {disk.mb_read.val:6.1f} | {disk.mb_read.avg:6.1f} "\n        f"| {disk.mb_writ.val:5.1f} | {disk.mb_writ.avg:5.1f} "\n        f"| {int(disk.io_read.val):4d} | {int(disk.io_read.avg):4d} "\n        f"| {int(disk.io_writ.val):3d} | {int(disk.io_writ.avg):3d} "\n        f"|"\n    )\n    print(row)\n```\n\n## Run in a Docker container\n\nContainers don\'t have access to the host\'s network statistics, therefore this workaround is needed.\n\n```sh\n# on the host machine (not inside the container)\niometrics replicate proc &\n```\n\nafter you run above script in the host you should mount the `/host/proc/net/dev` to the container. for example:\n\n```sh\ndocker run -it -v "/tmp/proc_net_dev:/host/proc/net/dev:ro" <YOURIMAGE>\n```\n\n## Contributing\n\nSee [CONTRIBUTING.md](CONTRIBUTING.md)\n',
    'author': 'Leo Gallucci',
    'author_email': 'elgalu3@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/elgalu/iometrics',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
