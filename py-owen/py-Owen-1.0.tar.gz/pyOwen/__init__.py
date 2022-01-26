

import time

from .configs import Var
from .startup import *
from .startup._database import OwenDB
from .startup.BaseClient import OwenClient
from .startup.connections import session_file, vc_connection, where_hosted
from .startup.funcs import _version_changes, autobot
from .version import owen_version

start_time = time.time()
_ult_cache = {}
# sys.exit = sys_exit()
HOSTED_ON = where_hosted()

udB = OwenDB()

LOGS.info(f"Connecting to {udB.name}...")
if udB.ping():
    LOGS.info(f"Connected to {udB.name} Successfully!")

BOT_MODE = udB.get_key("BOTMODE")
DUAL_MODE = udB.get_key("DUAL_MODE")

if BOT_MODE:
    if DUAL_MODE:
        udB.del_key("DUAL_MODE")
        DUAL_MODE = False
    owen_bot = None
else:
    owen_bot = OwenClient(
        session_file(LOGS),
        udB=udB,
        app_version=owen_version,
        device_model="OwenUserBot",
        proxy=udB.get_key("TG_PROXY"),
    )

if not BOT_MODE:
    owen_bot.run_in_loop(autobot())
else:
    if not udB.get_key("BOT_TOKEN") and Var.BOT_TOKEN:
        udB.set_key("BOT_TOKEN", Var.BOT_TOKEN)
    if not udB.get_key("BOT_TOKEN"):
        LOGS.info('"BOT_TOKEN" not Found! Please add it, in order to use "BOTMODE"')
        import sys

        sys_exit()

asst = OwenClient(None, bot_token=udB.get_key("BOT_TOKEN"), udB=udB)

if BOT_MODE:
    owen_bot = asst

vcClient = vc_connection(udB, owen_bot)

_version_changes(udB)

HNDLR = udB.get_key("HNDLR") or "."
DUAL_HNDLR = udB.get_key("DUAL_HNDLR") or "/"
SUDO_HNDLR = udB.get_key("SUDO_HNDLR") or HNDLR
