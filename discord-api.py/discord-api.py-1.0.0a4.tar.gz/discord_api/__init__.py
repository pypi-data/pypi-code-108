"""
# discord-api.py
![PyPI](https://img.shields.io/pypi/v/discord-api.py) ![download](https://img.shields.io/pypi/dm/discord-api.py)

## introduction

This is discord api wrapper.

Easy to create a bot

## setup

```bash
discord-api setup main
```

## extension

If you want to create extention module.

Please do like this name.

`discord-api-{name}`

## low wrapper

If you want to use low wrapper, please watch [this](https://github.com/tuna2134/discord-api.py/blob/main/discord_api/low/README.md).

## sample

```python
from discord_api import Client, Command

client = Client(log = False)

client.add_command(Command("ping", "pong."))

@client.event
async def on_ready():
    print("ready")

@client.event
async def on_interaction(i):
    await i.send("Pong!", True)

client.run("token")
```

## license

Watch a `LICENSE`!
"""

from .client import Client
from .command import Command
from .embed import Embed
from .interaction import *

__version__ = "0.1.7a1"
