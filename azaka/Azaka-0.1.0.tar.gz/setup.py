# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['azaka', 'azaka.commands', 'azaka.connection', 'azaka.objects', 'azaka.tools']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'azaka',
    'version': '0.1.0',
    'description': 'A work in progress API Wrapper around The Visual Novel Database (VNDB) written in Python.',
    'long_description': '<p align="center"> <img src="https://cdn-icons-png.flaticon.com/512/2322/2322246.png" height=200> </p>\n\n# WELCOME!\n\nWelcome to Azaka, a work-in-progress asynchronous API wrapper around the [visual novel database](https://vndb.org/) written in python.\n\nThis wrapper is aimed to provide 100% API coverage being extremely simple to use and powerful. Now let\'s discuss why you should use it in next section.\n\n# LINKS -\n\n- [Features](https://github.com/mooncell07/Azaka#features--)\n- [Problems](https://github.com/mooncell07/Azaka#problems--)\n- [Installation](https://github.com/mooncell07/Azaka#installation--)\n- [Usage](https://github.com/mooncell07/Azaka#usage--)\n- [Docs. & Tuts.](https://github.com/mooncell07/Azaka#documentation--tutorial--)\n- [Thanks](https://github.com/mooncell07/Azaka#thanks)\n\n## FEATURES -\n\n- **Fully Asynchronous** - Everything which poses a threat of blocking the I/O for a significant amount of time is async.\n- **Caching** - Azaka supports caching responses, which saves us from getting throttled quickly!\n- **Easy to Use** - Azaka provides a really easy to use interface for creating complex commands and a bunch of ready-made presets for those in hurry.\n- **Well Typehinted** - Everything in this library is properly typehinted.\n- **No Dependency requirement** - No third party dependency is required to do anything in entire library.\n\n\n## PROBLEMS -\n\n*(yes, i am a gud person)*\n\n- **Bloat** - A few decisions have been taken which have caused the lib. to weigh too much but trust me, it\'s not dead weight, they help with UX.\n- **Slow Development & bug hunting** - I am the only person working on entire lib and i have a lot of work irl too so sorrryyy.\n- **Models are not well optimized** - All the models are fully constructed even if there is no need of some members.\n- **Support** - Well.. i can only help with it so yea you can contact me on discord `Nova#3379`.\n\n\n## INSTALLATION -\n\nYou can install Azaka using pip.\n\n`pip install -U azaka`\n\nThat\'s it! There is no other required requirement.\n\nAdditionally, you can also install\n\n- [uvloop](https://pypi.org/project/uvloop/)\n- [orjson](https://pypi.org/project/orjson/)\n\nfor speeding up the stuff!\n\n## USAGE -\n\n*Example of getting basic VN data.*\n\n```py\nimport azaka\n\nclient = azaka.Client()\n\n@client.register\nasync def main(ctx) -> None:\n    vn = await ctx.get_vn(lambda VN: VN.ID == 11)\n    print(vn[0])\n\nclient.start()\n```\n\nAbove example used a preset (`client.get_vn`), you can use azaka\'s Interface to build a command yourself!\n\n```py\nimport azaka\nfrom azaka import Flags\n\nclient = azaka.Client()\n\n@client.register\nasync def main(ctx) -> None:\n    with azaka.Interface(type=ctx.vn, flags=(Flags.BASIC,)) as interface:\n        interface.set_condition(lambda VN: (VN.SEARCH % "fate") & (VN.ID == 50))\n\n    vn = await client.get(interface)\n    print(vn[0])\n\nclient.start()\n```\n\n## DOCUMENTATION & TUTORIAL -\n\nDocumentation is still in development and will be available soon!\n\n\n## THANKS\n\nThank you for your visit :)\n',
    'author': 'mooncell07',
    'author_email': 'mooncell07@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
