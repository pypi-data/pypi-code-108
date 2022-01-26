

import os
import sys
import time

from . import *
from .functions.helper import time_formatter, updater
from .startup.funcs import autopilot, customize, plug, ready, startup_stuff
from .startup.loader import load_other_plugins

# Option to Auto Update On Restarts..
if (
    udB.get_key("UPDATE_ON_RESTART")
    and os.path.exists(".git")
    and owen_bot.run_in_loop(updater())
):
    os.system("git pull -f -q && pip3 install --no-cache-dir -U -q -r requirements.txt")
    os.execl(sys.executable, "python3", "-m", "pyOwen")

startup_stuff()


owen_bot.me.phone = None
owen_bot.first_name = owen_bot.me.first_name

if not owen_bot.me.bot:
    udB.set_key("OWNER_ID", owen_bot.uid)


LOGS.info("Initialising...")


owen_bot.run_in_loop(autopilot())

pmbot = udB.get_key("PMBOT")
manager = udB.get_key("MANAGER")
addons = udB.get_key("ADDONS") or Var.ADDONS
vcbot = udB.get_key("VCBOT") or Var.VCBOT

load_other_plugins(addons=addons, pmbot=pmbot, manager=manager, vcbot=vcbot)

suc_msg = """
            ----------------------------------------------------------------------
                Owen has been deployed! Visit @OwenUserBot for updates!!
            ----------------------------------------------------------------------
"""

# for channel plugins
plugin_channels = udB.get_key("PLUGIN_CHANNEL")

# Customize Owen Assistant...
owen_bot.run_in_loop(customize())

# Load Addons from Plugin Channels.
if plugin_channels:
    owen_bot.run_in_loop(plug(plugin_channels))

# Send/Ignore Deploy Message..
if not udB.get_key("LOG_OFF"):
    owen_bot.run_in_loop(ready())

cleanup_cache()

if __name__ == "__main__":
    LOGS.info(
        f"Took {time_formatter((time.time() - start_time)*1000)} to start •Owen•"
    )
    LOGS.info(suc_msg)
    asst.run()
