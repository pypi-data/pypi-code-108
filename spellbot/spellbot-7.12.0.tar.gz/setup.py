# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['spellbot',
 'spellbot.cogs',
 'spellbot.interactions',
 'spellbot.migrations',
 'spellbot.migrations.versions',
 'spellbot.models',
 'spellbot.services',
 'spellbot.web',
 'spellbot.web.api']

package_data = \
{'': ['*'], 'spellbot.web': ['templates/*']}

install_requires = \
['Babel>=2.9.1,<3.0.0',
 'PyYAML>=6.0,<7.0',
 'SQLAlchemy-Utils>=0.37.9,<0.39.0',
 'SQLAlchemy>=1.4.27,<2.0.0',
 'aiohttp-jinja2>=1.5,<2.0',
 'aiohttp-retry>=2.4.6,<3.0.0',
 'aiohttp>=3.7.4,<4.0.0',
 'alembic>=1.7.5,<2.0.0',
 'asgiref>=3.4.1,<4.0.0',
 'click>=8.0.3,<9.0.0',
 'coloredlogs>=15.0.1,<16.0.0',
 'datadog>=0.43.0,<0.44.0',
 'ddtrace>=0.56.1,<0.58.0',
 'discord-py-interactions>=3.0.2,<4.0.0',
 'discord.py==1.7.3',
 'dunamai>=1.7.0,<2.0.0',
 'expiringdict>=1.2.1,<2.0.0',
 'gunicorn>=20.1.0,<21.0.0',
 'humanize>=3.12.0,<4.0.0',
 'hupper>=1.10.3,<2.0.0',
 'importlib-resources>=5.4.0,<6.0.0',
 'psycopg2-binary>=2.9.2,<3.0.0',
 'pygicord>=1.0.1,<2.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'python-dotenv>=0.19.1,<0.20.0',
 'pytz>=2021.3,<2022.0',
 'supervisor>=4.2.2,<5.0.0',
 'types-PyYAML>=6.0.1,<7.0.0',
 'types-python-dateutil>=2.8.3,<3.0.0',
 'types-pytz>=2021.3.1,<2022.0.0',
 'types-toml>=0.10.1,<0.11.0',
 'uvloop>=0.16.0,<0.17.0',
 'wrapt==1.13.2']

entry_points = \
{'console_scripts': ['spellbot = spellbot:main']}

setup_kwargs = {
    'name': 'spellbot',
    'version': '7.12.0',
    'description': 'The Discord bot for SpellTable',
    'long_description': '<img align="right" width="200" alt="spellbot" src="https://raw.githubusercontent.com/lexicalunit/spellbot/main/spellbot.png" />\n\n# SpellBot\n\n[![build][build-badge]][build]\n[![uptime][uptime-badge]][uptime]\n[![codecov][codecov-badge]][codecov]\n[![CodeFactor][factor-badge]][factor]\n[![heroku][heroku-badge]][heroku]\n[![python][python-badge]][python]\n[![pypi][pypi-badge]][pypi]\n[![discord.py][discord-py-badge]][discord-py]\n[![discord-interactions][discord-interactions-badge]][discord-interactions]\n[![docker][docker-badge]][docker-hub]\n[![black][black-badge]][black]\n[![mit][mit-badge]][mit]\n[![metrics][metrics-badge]][metrics]\n[![patreon][patreon-button]][patreon]\n[![follow][follow-badge]][follow]\n\n<br />\n<br />\n<br />\n<br />\n<p align="center"><a href="https://discordapp.com/api/oauth2/authorize?client_id=725510263251402832&permissions=2416045137&scope=applications.commands%20bot"><img align="center" alt="Add to Discord" src="https://user-images.githubusercontent.com/1903876/88951823-5d6c9a00-d24b-11ea-8523-d256ccbf4a3c.png" /></a><br />The Discord bot for <a href="https://spelltable.wizards.com/">SpellTable</a></p>\n<br />\n\n## 🤖 Using SpellBot\n\nJust looking to play a game of Magic? Run the command `/lfg` and SpellBot will help you out!\n\n<p align="center"><img src="https://user-images.githubusercontent.com/1903876/137987904-6fcdf273-5b60-4692-9389-a51d65c0a424.png" width="600" alt="/lfg" /></p>\n\nSpellBot uses [Discord slash commands](https://discord.com/blog/slash-commands-are-here). Each command provides its own help documentation that you can view directly within Discord itself before running the command. Take a look and see what\'s available by typing `/` and browsing the commands for SpellBot!\n\n## 🔭 Where to Play?\n\nThese communities are using SpellBot to play Magic! Maybe one of them is right for you?\n\n<table>\n    <tr>\n        <td align="center"><a href="https://www.playedh.com/"><img width="160" height="160" src="https://user-images.githubusercontent.com/1903876/140843874-78510411-dcc8-4a26-a59a-0d6856698dcc.png" alt="PlayEDH" /><br />PlayEDH</a></td>\n        <td align="center"><a href="https://www.reddit.com/r/CompetitiveEDH/"><img height="160" src="https://user-images.githubusercontent.com/1903876/140865281-19774420-a49b-4d0e-bf0c-db3ad937022e.png" alt="r/cEDH" /><br />r/cEDH</a></td>\n        <td align="center"><a href="https://www.commandthecause.org/"><img height="160" src="https://user-images.githubusercontent.com/1903876/140864827-a56b9ee4-a545-41f1-90ea-06d35bce2bf9.png" alt="Command the Cause" /><br />Command&nbsp;the&nbsp;Cause</a></td>\n    </tr>\n    <tr>\n        <td align="center"><a href="https://www.patreon.com/ihateyourdeck"><img width="230" src="https://user-images.githubusercontent.com/1903876/140844363-e07a5552-d2de-47d3-b1f7-faf6fbbd5b78.png" alt="I Hate Your Deck" /><br />I&nbsp;Hate&nbsp;Your&nbsp;Deck</a></td>\n        <td align="center"><a href="https://www.patreon.com/NitpickingNerds"><img height="141" src="https://user-images.githubusercontent.com/1903876/140844623-8d8528a9-b60c-49c6-be0f-1d627b85adba.png" alt="The Nitpicking Nerds" /><br />The&nbsp;Nitpicking&nbsp;Nerds</a></td>\n        <td align="center"><a href="https://www.facebook.com/EDHTambayan/"><img height="130" src="https://user-images.githubusercontent.com/1903876/148892328-335ab0ea-633f-44c2-b59e-61b5a38c9fdd.png" alt="EDH Tambayan" /><br />EDH&nbsp;Tambayan</a></td>\n    </tr>\n    <tr>\n        <td align="center"><a href="https://disboard.org/server/752261529390284870"><img height="130" src="https://user-images.githubusercontent.com/1903876/140845571-12e391d0-4cc8-4766-bf40-071f32503a7d.jpg" alt="Commander SpellTable (DE)" /><br />Commander&nbsp;SpellTable&nbsp;(DE)</a></td>\n        <td align="center"><a href="https://www.patreon.com/PlayingWithPowerMTG"><img height="130" src="https://user-images.githubusercontent.com/1903876/148892809-60b7d7f0-d773-4667-a863-829338d6aaed.png" alt="Playing with Power" /><br />Playing&nbsp;with&nbsp;Power</a></td>\n        <td align="center"><a href="https://disboard.org/server/815001383979450368"><img height="130" src="https://user-images.githubusercontent.com/1903876/140863859-9ec1997b-9983-498e-9295-fa594d242b4d.jpg" alt="EDH Fight Club" /><br />EDH&nbsp;Fight&nbsp;Club</a></td>\n    </tr>\n    <tr>\n        <td align="center"><a href="https://disboard.org/server/806995731268632596"><img height="130" src="https://user-images.githubusercontent.com/1903876/140845585-8053037f-a42b-4c1c-88f2-1b3c403fea09.jpg" alt="The Mages Guild" /><br />The&nbsp;Mages&nbsp;Guild</a></td>\n        <td align="center"><a href="https://discord.gg/commander"><img height="130" src="https://user-images.githubusercontent.com/1903876/147596500-3cd08eef-84ad-4c02-a219-2eef0642a973.jpg" alt="Commander RC" /><br />Commander&nbsp;RC</td>\n        <td align="center"><a href="https://www.patreon.com/asylumgamingmtg"><img height="141" src="https://user-images.githubusercontent.com/1903876/140862514-5057c356-c166-48a0-a71c-329d33480003.png" alt="Asylum Gaming" /><br />Asylum&nbsp;Gaming</a></td>\n    </tr>\n    <tr>\n        <td align="center"><a href="https://discord.gg/YeFrEqae3N"><img height="130" src="https://user-images.githubusercontent.com/1903876/148895425-0c72426c-d7dd-4974-99d7-21949f80e893.png" alt="コマンドフェストオンライン" /><br />コマンドフェストオンライン</a></td>\n        <td align="center"><a href="https://disboard.org/server/848414032398516264"><img height="130" src="https://user-images.githubusercontent.com/1903876/140863856-00482a5a-7fe5-4cbb-8c4b-2442504925ea.jpg" alt="Commander en Español" /><br />Commander&nbsp;en&nbsp;Español</a></td>\n        <td align="center"><a href="https://discord.gg/7gJDYU44gM"><img height="130" src="https://user-images.githubusercontent.com/1903876/147705994-909a94cc-ce70-431b-823a-127d257cdb52.png" alt="MTG let\'s play!!" /><br />MTG&nbsp;let&apos;s&nbsp;play!!</td>\n    </tr>\n    <tr>\n        <td align="center">&nbsp;</td>\n        <td align="center"><a href="https://discord.gg/Rgp3xaV7HU"><img height="130" src="https://user-images.githubusercontent.com/1903876/148823767-5e1feb59-37d8-4340-ae23-148d8415699f.png" alt="Torre de Mando" /><br />Torre&nbsp;de&nbsp;Mando&nbsp;</a></td>\n        <td align="center">&nbsp;</td>\n    </tr>\n</table>\n\nWant your community to be featured here as well? Please contact me at [spellbot@lexicalunit.com](mailto:spellbot@lexicalunit.com)!\n\n## 🎤 Feedback\n\nThoughts and suggestions? Come join us on the\n[SpellTable Discord server][discord-invite]! Please also feel free\nto [directly report any bugs][issues] that you encounter.\n\n## 🙌 Support Me\n\nI\'m keeping SpellBot running using my own money but if you like the bot and want\nto help me out, please consider [becoming a patron][patreon].\n\n## ❤️ Contributing\n\nIf you\'d like to become a part of the SpellBot development community please\nfirst know that we have a documented [code of conduct](CODE_OF_CONDUCT.md) and\nthen see our [documentation on how to contribute](CONTRIBUTING.md) for details\non how to get started.\n\n## 🐳 Docker Support\n\nSpellBot can be run via docker. Our image is published to\n[lexicalunit/spellbot][docker-hub]. See [our documentation on Docker Support](DOCKER.md) for help\nwith installing and using it.\n\n## 🔍 Fine-print\n\nAny usage of SpellBot implies that you accept the following policies.\n\n- [Privacy Policy](PRIVACY_POLICY.md)\n- [Terms of Service](TERMS_OF_SERVICE.md)\n\n---\n\n[MIT][mit] © [amy@lexicalunit][lexicalunit] et [al][contributors]\n\n[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg\n[black]: https://github.com/psf/black\n[build-badge]: https://github.com/lexicalunit/spellbot/workflows/build/badge.svg\n[build]: https://github.com/lexicalunit/spellbot/actions\n[codecov-badge]: https://codecov.io/gh/lexicalunit/spellbot/branch/main/graph/badge.svg\n[codecov]: https://codecov.io/gh/lexicalunit/spellbot\n[contributors]: https://github.com/lexicalunit/spellbot/graphs/contributors\n[discord-interactions-badge]: https://img.shields.io/badge/discord--interactions-3.x-blue\n[discord-interactions]: https://github.com/goverfl0w/discord-interactions\n[discord-invite]: https://discord.gg/zXzgqMN\n[discord-py-badge]: https://img.shields.io/badge/discord.py-1.7.3-blue\n[discord-py]: https://github.com/Rapptz/discord.py\n[docker-badge]: https://img.shields.io/docker/pulls/lexicalunit/spellbot.svg\n[docker-hub]: https://hub.docker.com/r/lexicalunit/spellbot\n[factor-badge]: https://www.codefactor.io/repository/github/lexicalunit/spellbot/badge\n[factor]: https://www.codefactor.io/repository/github/lexicalunit/spellbot\n[follow-badge]: https://img.shields.io/twitter/follow/SpellBotIO?style=social\n[follow]: https://twitter.com/intent/follow?screen_name=SpellBotIO\n[heroku-badge]: https://img.shields.io/badge/heroku-deployed-green\n[heroku]: https://dashboard.heroku.com/apps/lexicalunit-spellbot\n[issues]: https://github.com/lexicalunit/spellbot/issues\n[lexicalunit]: http://github.com/lexicalunit\n[metrics-badge]: https://img.shields.io/badge/metrics-grafana-orange.svg\n[metrics]: https://lexicalunit.grafana.net/d/4TSUCbcMz/spellbot?orgId=1\n[mit-badge]: https://img.shields.io/badge/License-MIT-yellow.svg\n[mit]: https://opensource.org/licenses/MIT\n[patreon-button]: https://img.shields.io/endpoint.svg?url=https%3A%2F%2Fshieldsio-patreon.vercel.app%2Fapi%3Fusername%3Dlexicalunit%26type%3Dpatrons88951826-5e053080-d24b-11ea-9a81-f1b5431a5d4b.png\n[patreon]: https://www.patreon.com/lexicalunit\n[pypi-badge]: https://img.shields.io/pypi/v/spellbot\n[pypi]: https://pypi.org/project/spellbot/\n[python-badge]: https://img.shields.io/badge/python-3.8+-blue.svg\n[python]: https://www.python.org/\n[security]: https://github.com/lexicalunit/spellbot/security\n[spelltable]: https://spelltable.wizards.com/\n[uptime-badge]: https://img.shields.io/uptimerobot/ratio/m785764282-c51c742e56a87d802968efcc\n[uptime]: https://uptimerobot.com/dashboard#785764282\n',
    'author': 'Amy Troschinetz',
    'author_email': 'spellbot@lexicalunit.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'http://spellbot.io/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4',
}


setup(**setup_kwargs)
