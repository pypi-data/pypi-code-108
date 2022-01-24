import pathlib
# emojis
THUMBS_UP = "👍"
THUMBS_DOWN = "👎"
ERROR = "❌"

# info

ROOT = pathlib.Path(__file__).parent
with open(ROOT / "version.txt", "r", encoding="utf-8") as f:
    VERSION = f.read()

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
