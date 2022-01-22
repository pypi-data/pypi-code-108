import dotenv
import os

try:
    dotenv.load_dotenv()
    os.environ['EMBED_COLOR']
except KeyError:
    with open('./.env', 'a') as env:
        env.write("\n\n#disnake-debug\nEMBED_COLOR = 0x0000ff")
        
from .dialogs import *
from .utils import *
from .debug import *
from .cog import *