from .Channel import *
from .comm import *
from .Guild import *
from .Message import *

def get_message_with_id(channelid, messageid, bot) -> Message:
  return Message(APIcall(f"/channels/{channelid}/messages/{messageid}", "GET", bot.auth, {}),b)

def get_emoji_id(self, guild, emoji_name, bot) -> str:
  emojis = APIcall(f"/guilds/{guild.id}/emojis", "GET", bot.auth, {})
  final = None
  for emoji in emojis:
    if emoji['name'] == emoji_name:
      final = emoji_name+":"+str(emoji['id'])
      break
  return final