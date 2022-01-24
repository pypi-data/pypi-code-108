import pathlib
import os

from dotenv import load_dotenv

# emojis
THUMBS_UP = "👍"
THUMBS_DOWN = "👎"
ERROR = "❌"

# info

ROOT = pathlib.Path(__file__).parent
VERSION = "1.7"

BLACKLIST_HELP = """
Send the name of the commands you want to blacklist the user from.
    => Seperate the command names by a comma
    => Send 'all' to blacklist the user from every command
"""
DESCRIPTION = f"""
Welcome to disnake-debug v{VERSION}
-----------------------------
waiting:
    - when the bot sends a question (non-embed message) it is waiting for you to send a response to that question
        => to stop this just type q
"""
PATH_HELP = """
Type the path you want to go to (eg /blacklist/user)
Not all paths are available because some require additional info (eg which guild to leave in leave_guild/leave)
"""
class InvalidEnv(Exception):
    """ """

try:
    load_dotenv()
    os.environ["EMBED_COLOR"]
except KeyError:
    with open("./.env", "a") as env:
        env.write("\n#disnake-debug\nEMBED_COLOR = 0x0000ff")
try:
    load_dotenv()
    EMBED_COLOR = int(os.environ["EMBED_COLOR"], 16)
except (TypeError, ValueError):
    raise InvalidEnv("EMBED_COLOR must be hex")