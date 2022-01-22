from .comm import *
from .Embed import Embed
from .User import *

class Channel:
  '''
  This is the channel object which uses the rawdata from an event or somewhere else and uses the bot for authorization.
  '''
  def __init__(self, rawdata, bot):
    self.bot = bot
    self.raw = rawdata
    self.id = rawdata["id"]
    rawtype = rawdata["type"]
    if rawtype == 0:
      self.type = "text_channel"
      self.topic = rawdata["topic"]
      self.RLPU = rawdata["rate_limit_per_user"]
      # self.banner = rawdata["banner"]
      self.nsfw = rawdata["nsfw"]
      self.parent_id = rawdata["parent_id"]
      self.name = rawdata["name"]
      self.position = rawdata["position"]
    elif rawtype == 1:
      self.type = "DM_channel"
      self.recipients = rawdata["recipients"]
    elif rawtype == 2:
      self.type = "voice_channel"
      self.bitrate = rawdata["bitrate"]
      self.userlimit = rawdata["user_limit"]
      self.region = rawdata["rtc_region"]
      self.parent_id = rawdata["parent_id"]
      self.position = rawdata["position"]
      self.name = rawdata["name"]
      self.nsfw = rawdata["nsfw"]
    elif rawtype == 4:
      self.type = "category_channel"
      self.parent_id = rawdata["parent_id"]
      self.position = rawdata["position"]
      self.name = rawdata["name"]
    elif rawtype == 5:
      self.type = "announcement_channel"
      self.position = rawdata["position"]
      self.parent_id = rawdata["parent_id"]
      self.name = rawdata["name"]
      self.nsfw = rawdata["nsfw"]
    elif rawtype == 10 or rawtype == 11 or rawtype==12:
      self.type = "Thread"
      self.id = self.rawdata["id"]
      self.guild_id = self.rawdata["guild_id"]
      self.parent_id = self.rawdata["parent_id"]
      self.owner_id = self.rawdata["owner_id"]
      self.name = self.rawdata["name"]
      self.last_message_id = self.rawdata["last_message_id"]
      self.message_count = self.rawdata["message_count"]
      self.member_count = self.rawdata["member_count"]
      self.ratelimit = self.rawdata["rate_limit_per_user"]
      self.metadata = self.rawdata["thread_metadata"]
    elif rawtype == 13:
      self.type = "stage_channel"
      self.bitrate = rawdata["bitrate"]
      self.userlimit = rawdata["user_limit"]
      self.region = rawdata["rtc_region"]
      self.parent_id = rawdata["parent_id"]
      self.name = rawdata["name"]
      self.nsfw = rawdata["nsfw"]
      self.position = rawdata["position"]
  def send(self, content=None, embeds=[], components= [], tts=False):
    from .Message import Message
    if self.type == "text_channel" or self.type == "announcement_channel" or self.type == "DM_channel":
      embedsreal = []
      componentsreal = []
      for embedobj in embeds:
        if isinstance(embedobj, Embed):
          embedsreal.append(embedobj.getObj())
        else:
          embedsreal.append(embedobj);
      for componentobj in components:
        componentsreal.append(componentobj.getOBJ())
      return Message(APIcall(f"/channels/{self.id}/messages", "POST", self.bot.auth, {
        "content": content,
        "tts": tts,
        "embeds": embedsreal,
        "components": componentsreal
      }),self.bot)
    else:
      raise APIerror("Cannot send in a non-text channel")