from .comm import *
from .Channel import *

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
  def ban(self, person, reason="", delete_message_days=7):
    APIcall(f"/guilds/{self.id}/bans/{person.id}", "PUT", self.bot.auth, {"reason": reason,"delete_message_days":delete_message_days})
  def kick(self, person):
    APIcall(f"/guilds/{self.id}/members/{person.id}","DELETE",self.bot.auth,{})
    