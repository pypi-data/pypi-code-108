from .comm import *
from .Channel import *

class AuditEvents:
  GUILD_UPDATE = 1
  CHANNEL_CREATE = 10
  CHANNEL_UPDATE = 11
  CHANNEL_DELETE = 12
  CHANNEL_OVERWRITE_CREATE = 13
  CHANNEL_OVERWRITE_UPDATE = 14
  CHANNEL_OVERWRITE_DELETE = 15
  MEMBER_KICK = 20
  MEMBER_PRUNE = 21
  MEMBER_BAN_ADD = 22
  MEMBER_BAN_REMOVE = 23
  MEMBER_UPDATE = 24
  MEMBER_ROLE_UPDATE = 25
  MEMBER_MOVE = 26
  MEMBER_DISCONNECT = 27
  BOT_ADD = 28
  ROLE_CREATE = 30
  ROLE_UPDATE = 31
  ROLE_DELETE = 32
  INVITE_CREATE = 40
  INVITE_UPDATE = 41
  INVITE_DELETE = 42
  WEBHOOK_CREATE = 50
  WEBHOOK_UPDATE = 51
  WEBHOOK_DELETE = 52
  EMOJI_CREATE = 60
  EMOJI_UPDATE = 61
  EMOJI_DELETE = 62
  MESSAGE_DELETE = 72
  MESSAGE_BULK_DELETE = 73
  MESSAGE_PIN = 74
  MESSAGE_UNPIN = 75
  INTEGRATION_CREATE = 80
  INTEGRATION_UPDATE = 81
  INTEGRATION_DELETE = 82
  STAGE_INSTANCE_CREATE = 83
  STAGE_INSTANCE_UPDATE = 84
  STAGE_INSTANCE_DELETE = 85
  STICKER_CREATE = 90
  STICKER_UPDATE = 91
  STICKER_DELETE = 92
  GUILD_SCHEDULED_EVENT_CREATE = 100
  GUILD_SCHEDULED_EVENT_UPDATE = 101
  GUILD_SCHEDULED_EVENT_DELETE = 102
  THREAD_CREATE = 110
  THREAD_UPDATE = 111
  THREAD_DELETE = 112
class Guild:
  '''
  This object is used to interact with guilds, but this works a bit diffrently because its not possible to just put the raw data into the guild, you have to only put the id, which can be useful or annoying. This might get changed.
  '''
  def __init__(self, id, bot):
    self.bot = bot
    self.raw = APIcall(f"/guilds/{id}", "GET", self.bot.auth, {});
    self.initialize()
  def initialize(self):
    self.id = self.raw["id"]
    self.name = self.raw["name"]
    self.owner = self.raw["owner_id"]
    self.desc = self.raw['description']
    self.region = self.raw["region"]
    self.afkchannel = self.raw["afk_channel_id"]
    self.afkchanneltimeout = self.raw["afk_timeout"]
    self.systemchannel = self.raw["system_channel_id"]
    self.verif = self.raw["verification_level"]
    self.roles = self.raw["roles"]
    self.maxvideochannel = self.raw["max_video_channel_users"]
    self.vanity = self.raw["vanity_url_code"],
    self.language = self.raw["preferred_locale"]
    self.ruleschannel = self.raw["rules_channel_id"]
    self.publicupdates = self.raw["public_updates_channel_id"],
    self.hubtype = self.raw["hub_type"]
    self.nsfw = self.raw["nsfw"]
    self.nsfwlvl = self.raw["nsfw_level"]
    self.channels = []
    rawchannels = APIcall(f"/guilds/{self.id}/channels", "GET", self.bot.auth, {})
    for channel in rawchannels:
      self.channels.append(Channel(channel, self.bot))
  def ban(self, person, reason="", delete_message_days=7):
    APIcall(f"/guilds/{self.id}/bans/{person.id}", "PUT", self.bot.auth, {"reason": reason,"delete_message_days":delete_message_days})
  def kick(self, person):
    APIcall(f"/guilds/{self.id}/members/{person.id}","DELETE",self.bot.auth,{})
  def getAuditLog(user=None,action=None,before_id=None,limit=50):
    if not type(limit) == int:
      raise Exception("limit must be type int, not "+str(type(limit)))
    if limit < 0 or limit > 100:
      raise Exception("Cannot get audit logs with limit: "+str(limit))
    params = {}
    if user:
      params["user_id"] = user.id
    if action:
      params["action_type"] = action
    if before_id:
      params["before"] = before_id
    params["limit"] = limit
    rawres = APIcall(f"/guilds/{self.id}/audit-logs","GET", self.bot.auth, params)
    new = rawres
    new["threads"] = []
    for thread in rawres["threads"]:
      new["threads"] = Channel(thread, self.bot)
    return new