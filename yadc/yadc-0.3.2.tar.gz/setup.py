# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['yadc']

package_data = \
{'': ['*']}

install_requires = \
['coloredlogs>=15.0.1,<16.0.0',
 'fake-useragent>=0.1.11,<0.2.0',
 'halo>=0.0.31,<0.0.32',
 'numpy>=1.21.4,<2.0.0',
 'psutil>=5.8.0,<6.0.0',
 'pydantic>=1.8.2,<2.0.0',
 'selenium>=4.0.0,<5.0.0']

entry_points = \
{'console_scripts': ['yadc = yadc.cli:main']}

setup_kwargs = {
    'name': 'yadc',
    'version': '0.3.2',
    'description': 'Yet Another DVSA Cancellation checker',
    'long_description': "# YADC: Yet Another (DVSA) cancellations Checker\n\nYADC is yet another checker for driving cancellations in the UK.\n\n-   **why another?:** Because all the code I found on github doesn't work with the\n    latest anti-bot protections on dvsa.  Besides, it was all rather\n    spaghettified.  YADC is, I hope a little cleaner and more modular.  It should\n    be easier to modify down the line.\n-   **why a bot?:** Because I can't get a driving test.  Note that I *do not think*\n    this solution is remotely ideal.  See the appeal below.\n-   **will you maintain this?:** Not if I get a test and pass.  But hopefully it\n    should be a better framework for the next generation to come along and do the\n    same.\n\n\n\n# Features\n\nYADC is:\n\n-   cleanly written and object-oriented\n-   neat.  We use a context manager to handle the browser; I'm pretty proud of\n    that.\n-   easy to extend\n-   easy (hopefully) to get around the next rubbish DVSA put up\n-   pretty immune to blocking (thanks to TOR)\n-   pretty colourful, too. We have coloured logs (thanks to `coloredlogs`),\n    spinners (thanks to `Halo`) and well-formatted output. When things go wrong,\n    we save a traceback, a screenshot, and the html the browser was seeing.\n\nYADC is not:\n\n-   my idea.  I started with [this repo](https://github.com/tp223/Driving-Test-Cancellations) and extensively rewrote the logic from\n    the ground up.  I got the idea of the poisson sleep from [this repo](https://github.com/birdcolour/dvsa-practicals), although\n    I didn't take any code directly from anything.\n-   infallible\n-   capable of booking tests for you (thanks to @chrishat34 it will reserve them, though).\n-   always going to work\n-   properly supported\n\n\n\n# Installation\n\n## With pip\n\n`YADC` is now deployed on PyPi, so you can just\n\n```bash\npython3 -m pip install YADC\n```\n\nHowever, since every individual setup is going to vary somewhat, `YADC` *is only\na library*.  You still have to decide how to use it.  A starting point is\nprovided in the `main.py` of this repository: save it somewhere, edit it, and\noff you go.  A dummy CLI is provided which will merely direct you to do this ;)\n\nIf anyone wishes to write a proper CLI I will happily merge it.\n\nNote that if you want captcha defeating you need to download [buster](https://github.com/dessant/buster/releases) and unzip it\nsomewhere you can get at from your `main.py`.  Likewise if you want `tor`, it\nneeds to be installed and executable as the user running your \\`main.py\\`.\n\n\n## From git (for development).\n\n-   clone the repo\n-   run `poetry install`\n-   run `poetry shell`\n-   (optional) to download [buster](https://github.com/dessant/buster/releases) and unzip it.\n-   (optional) install `tor` and ensure it can be run as a user.\n-   edit `main.py` with your setup.\n-   run `python -m yadc.main`\n\n\n# Usage\n\nCurrently you have to be at the computer to do anything.  You will see the\nbrowser moving, which should help.  If you want to interact with it manually,\nhit \\`Ctrl-z\\` in the terminal to stop execution of the script, and the browser\nis yours (note that manual interaction increases the chance of being detected\nby some anti-bot measures).  If the script finds a test it will notify you\nwith the notify function you set (the default is just \\`print\\`, so do set\nsomething more appropriate!  A nice service is \\`pushover\\`, though it does have\na once-off payment).  If the script does find a test it will block\n\n\n# Roadmap\n\n-   [ ] Currently we don't use `undetected_chromedriver` as I couldn't get it\n    playing nicely with remote controlling.  This should be easy to fix, but I\n    haven't looked into it.  We may not need it anyhow, but it might be a good\n    idea to take the default options from uc and use them.  A pr for this would\n    be welcome.\n-   [ ] We have no cli.  That's probably not an issue, but it would be trivial\n    to add one, e.g. with click.\n\n\n# Appeal to DVSA\n\nThe current situation is a mess.  Because of the pandemic, there are no tests\nfor months; that is not your fault.  So we are all forced either to wait for\nmonths, or to book a last-minute cancellation. But we can't do that, because\nall the companies using bots to find tests snatch them up.  So we all use\nthose companies; and then DVSA's website becomes even more useless.  There\nare two **easy** solutions you could adopt:\n\n-   Add an auto-booking with queue feature to the website.  Once a test is\n    booked you get to specify criteria for a better test, and enter in a queue.\n    When you rise to the top of that queue, you get whatever matches reserved\n    for you.  In other words, implement the third-party solution yourself.  I\n    would gladly pay a reasonable sum for it.  And the third-party firms will\n    go out of business and stop spamming your website.\n\n-   Add an API, and charge for access.  That way the third parties will use the\n    API.  You can release tests to the API after x minutes to give humans a\n    chance as well.  You can go after anyone who tries to use a bot to get\n    round the limit, and providing your API is reasonable, nobody will mind.\n\nInstead of these, you make the already useless website even harder to use.\nBot protection is an uphill battle.  So is bot developing.  The only people\nwho profit from this are companies like google (via chrome/chromium).\n\n",
    'author': 'John Maximilian',
    'author_email': '2e0byo@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
