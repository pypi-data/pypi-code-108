# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['obserware',
 'obserware.sources',
 'obserware.sources.commons',
 'obserware.sources.readers',
 'obserware.sources.readers.cputwind',
 'obserware.sources.readers.cyclwind',
 'obserware.sources.readers.lgptwind',
 'obserware.sources.readers.mainwind',
 'obserware.sources.readers.phptwind',
 'obserware.sources.readers.procwind',
 'obserware.sources.readers.sostwind',
 'obserware.sources.screens',
 'obserware.sources.screens.cputwind',
 'obserware.sources.screens.cyclwind',
 'obserware.sources.screens.lgptwind',
 'obserware.sources.screens.mainwind',
 'obserware.sources.screens.phptwind',
 'obserware.sources.screens.procwind',
 'obserware.sources.screens.sostwind',
 'obserware.sources.widgets',
 'obserware.sources.widgets.cputwdgt',
 'obserware.sources.widgets.cyclwdgt',
 'obserware.sources.widgets.lgptwdgt',
 'obserware.sources.widgets.ntwkwdgt',
 'obserware.sources.widgets.phptwdgt']

package_data = \
{'': ['*'], 'obserware': ['appdata/*']}

install_requires = \
['distro>=1.6.0,<2.0.0',
 'psutil>=5.8.0,<6.0.0',
 'py-cpuinfo>=8.0.0,<9.0.0',
 'pyqt5>=5.15.6,<6.0.0',
 'pyqtchart>=5.15.2,<6.0.0']

entry_points = \
{'console_scripts': ['obserware = obserware.main:main']}

setup_kwargs = {
    'name': 'obserware',
    'version': '0.2.7',
    'description': 'An advanced system monitor utility written in Python and Qt',
    'long_description': '# Obserware\n\nAn advanced system monitor utility written in Python and Qt\n\n## About\n\nObserware makes monitoring of advanced metrics accessible with the use of interactive graphs and charts. It is built on free and open-source technologies such as Python, Psutil, PyCPUinfo, Distro and Qt5. With the use of the utility, you can monitor\n\n- Advanced overview of the system health by monitoring CPU usage, memory utilization and swapping rate\n- Granular counts of context switches, system calls and interrupts of both natures, software and hardware\n- Per-core/per-thread CPU utilization, measured in both stress percentage and active clock speeds\n- Per-core/per-thread CPU state times, measured in both occupancy percentage and duration in seconds\n- Usage/availability information, measured in both occupancy percentage and active size in megabytes\n- Storage counters, measured in unit counts, size in bytes, duration in seconds, merge counts and busy time in seconds\n- Global network statistics gathered from all network interface cards, measured in packet count rate and size rate\n- Statistics of uploads and downloads made since boot, measured in packet counts and size in bytes\n- Per-NIC activity, transfer rate in packet counts and bytes, total transmission, dropped transfers and more\n- Per-unit metrics in both, occupancy percentage and active size of physical and logical partitions\n- Static information about mount location, file system, unit name and much more of physical and logical partitions\n- Dynamic listing of processes in process IDs, names, terminal, usernames, states, CPU and memory usage and thread counts\n- Per-process information with process IDs, CPU and memory usage, CPU/thread counts, context switches and more\n- Per-process control with options to kill, resume, terminate or suspend those on demand\n- Static software information on operating system and kernel as well as dependency versions for the application\n- Static hardware information on CPU name, vendor, frequency, available feature flags and more\n- While adapting to the global system-wide theming options on Qt-based desktop environments like KDE Plasma or LXQt\n\n## Find it on\n\n1. [**PyPI**](https://pypi.org/project/obserware/)  \n   [![PyPI version](https://img.shields.io/pypi/v/obserware?style=flat-square)](https://pypi.org/project/obserware/)  \n2. [**Fedora COPR**](https://copr.fedorainfracloud.org/coprs/t0xic0der/obserware/)  \n   [![Copr build status](https://copr.fedorainfracloud.org/coprs/t0xic0der/obserware/package/obserware/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/t0xic0der/obserware/package/obserware/)  \n3. [**Product Hunt**](https://www.producthunt.com/posts/obserware)  \n   1. [Vote](https://www.producthunt.com/posts/obserware?utm_source=badge-featured&utm_medium=badge&utm_souce=badge-obserware)  \n      [![](https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=321452&theme=dark)](https://www.producthunt.com/posts/obserware?utm_source=badge-featured&utm_medium=badge&utm_souce=badge-obserware)  \n   2. [Review](https://www.producthunt.com/posts/obserware?utm_source=badge-review&utm_medium=badge&utm_souce=badge-obserware#discussion-body)  \n      [![](https://api.producthunt.com/widgets/embed-image/v1/review.svg?post_id=321452&theme=dark)](https://www.producthunt.com/posts/obserware?utm_source=badge-review&utm_medium=badge&utm_souce=badge-obserware#discussion-body)  \n\n## Installation\n\n### For development\n\n#### Using Poetry\n\n1. `sudo dnf install python3-poetry`\n2. `git clone https://gitlab.com/t0xic0der/obserware.git`\n3. `cd obserware`\n4. `virtualenv venv`\n5. `source venv/bin/activate`\n6. `poetry install`\n7. `deactivate`\n\n### For consumption\n\n#### From Fedora COPR\n\n1. `sudo dnf install dnf-plugins-core -y`\n2. `sudo dnf copr enable t0xic0der/obserware -y`\n3. `sudo dnf install obserware -y`\n\n#### From PyPI\n\n1. `virtualenv venv`\n2. `source venv/bin/activate`\n3. `pip3 install obserware`\n4. `deactivate`\n\n## Usage\n\n### For development\n\n#### If installed via Poetry\n\n1. `source venv/bin/activate`\n2. `obserware`\n3. `deactivate`\n\n### For consumption\n\n#### If installed from Fedora COPR\n\n1. Either, run `obserware` in a terminal\n2. Or, invoke the created desktop entry\n\n#### If installed from PyPI\n\n1. `source venv/bin/activate`\n2. `obserware`\n3. `deactivate`\n\n## Screenshots\n\n1. **Windows**  \n   1. _Performance tabscreen_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_mainperf.png  \n      ![](https://gitlab.com/t0xic0der/obserware/-/raw/main/screenshots/obsr_mainperf.png)  \n   2. _Processes tabscreen_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_mainproc.png  \n      ![](https://gitlab.com/t0xic0der/obserware/-/raw/main/screenshots/obsr_mainproc.png)  \n   3. _Connections tabscreen_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_mainproc.png  \n      ![](https://gitlab.com/t0xic0der/obserware/-/raw/main/screenshots/obsr_mainntwk.png)  \n   4. _Information tabscreen_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_maininfo.png  \n      ![](https://gitlab.com/t0xic0der/obserware/-/raw/main/screenshots/obsr_maininfo.png)  \n   5. _Contribute tabscreen_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_maincntb.png  \n      ![](https://gitlab.com/t0xic0der/obserware/-/raw/main/screenshots/obsr_maincntb.png)  \n2. **Dialogs**  \n   1. _CPU cycles dialog_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_cyclwind.png  \n      ![](https://gitlab.com/t0xic0der/obserware/-/raw/main/screenshots/obsr_cyclwind.png)  \n   2. _CPU times dialog_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_cputwind.png  \n      ![](https://gitlab.com/t0xic0der/obserware/-/raw/main/screenshots/obsr_cputwind.png)  \n   3. _Storage counters dialog_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_sostwind.png  \n      ![](https://gitlab.com/t0xic0der/obserware/-/raw/main/screenshots/obsr_sostwind.png)  \n   4. _Physical partitions dialog_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_phptwind.png  \n      ![](https://gitlab.com/t0xic0der/obserware/-/raw/main/screenshots/obsr_phptwind.png)  \n   5. _Logical partitions dialog_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_lgptwind.png  \n      ![](https://gitlab.com/t0xic0der/obserware/-/raw/main/screenshots/obsr_lgptwind.png)  \n   6. _Process information dialog_  \n      Find here https://gitlab.com/t0xic0der/obserware/-/blob/main/screenshots/obsr_procwind.png  \n      ![](https://gitlab.com/t0xic0der/obserware/-/raw/main/screenshots/obsr_procwind.png)  \n',
    'author': 'Akashdeep Dhar',
    'author_email': 'akashdeep.dhar@gmail.com',
    'maintainer': 'Akashdeep Dhar',
    'maintainer_email': 'akashdeep.dhar@gmail.com',
    'url': 'https://gitlab.com/t0xic0der/obserware',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
