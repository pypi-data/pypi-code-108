from .User import User
from .comm import APIcall, URLencode
from .Channel import Channel
from .Embed import Embed
from threading import Thread
from time import sleep

class Message:
  '''
  This is used to get the message data, this is technically not implemented because the attachments, embeds, reactions and components are still just raw.
  '''
  id = 0
  channel = None 
  guild = None
  author = 0
  content = ""
  timestamp = 0
  etimestamp = 0
  tts = False
  attachments = [] # EH
  embeds = [] # EH
  reactions = [] # EH
  pinned = False
  msgtype = 0
  components = [] # EH
  def __init__(self, dataraw, bot):
    self.bot = bot
    self.id = dataraw["id"]
    self.author = dataraw["author"]["id"]
    self.author = User(APIcall(f"/users/{self.author}", "GET", bot.auth, None), bot)
    self.msgtype = dataraw["type"]
    self.content = dataraw["content"]
    self.timestamp = dataraw["timestamp"]
    self.etimestamp = dataraw["edited_timestamp"]
    self.tts = dataraw["tts"]
    self.attachments = dataraw["attachments"]
    self.embeds = dataraw["embeds"]
    self.pinned = dataraw["pinned"]
    self.components = dataraw["components"]
    if dataraw.__contains__("channel_id"):
      self.channel = Channel(APIcall(f"/channels/{dataraw['channel_id']}", "GET", bot.auth, {}), bot)
    try:
      self.reaction = dataraw["reactions"]
    except:
      pass
    if dataraw.__contains__("guild_id"):
      from .Guild import Guild
      self.guild = Guild(dataraw["guild_id"], bot)
  def edit(self, content=None, embeds=[], components= []):
    embedsreal = []
    componentsreal = []
    for embedobj in embeds:
      if isinstance(embedobj, Embed):
        embedsreal.append(embedobj.getObj())
      else:
        embedsreal.append(embedobj);
    for componentobj in components:
      componentsreal.append(componentobj.getOBJ())
    APIcall(f"/channels/{self.channel.id}/messages/{self.id}", "PATCH", self.bot.auth, {
      "content": content,
      "embeds": embedsreal,
      "components": componentsreal
    })
  def delete(self):
    APIcall(f"/channels/{self.channel.id}/messages/{self.id}", "DELETE", self.bot.auth, {})
    del self
  def reply(self, content="", embeds=[], components= [], tts=False):
    embedsreal = []
    componentsreal = []
    for embedobj in embeds:
      if isinstance(embedobj, Embed):
        embedsreal.append(embedobj.getObj())
      else:
        embedsreal.append(embedobj);
    for componentobj in components:
      componentsreal.append(componentobj.getOBJ())
    referenceDuc = {"message_id": self.id, "channel_id": self.channel.id}
    return Message(APIcall(f"/channels/{self.channel.id}/messages", "POST", self.bot.auth, {
      "content": content,
      "tts": tts,
      "embeds": embedsreal,
      "components": componentsreal,
      "message_reference": referenceDuc
    }),self.bot)
  def react(self, emoji, custom=False):
    from .Utils import get_emoji_id
    f_emoji = emoji
    if custom:
      f_emoji = get_emoji_id(self, self.guild, emoji, self.bot)
      APIcall(f"/channels/{self.channel.id}/messages/{self.id}/reactions/{URLencode(f_emoji)}/@me", "PUT", self.bot.auth, {})
    else:
      d = Thread(target=APIcall, args=(f"/channels/{self.channel.id}/messages/{self.id}/reactions/{URLencode(f_emoji)}/@me", "PUT", self.bot.auth, {}),daemon=True)
      d.start()
      sleep(0.5)