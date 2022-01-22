from .comm import *
import bdw

class User:
  '''
  This is the object for a user, not usefull unles you want to have a bit of information about the account like id, username or discriminator/tag
  '''
  def __init__(self, raw, bot):
    self.raw = raw
    self.id = raw["id"]
    self.bot = bot
    self.username = raw["username"]
    self.discriminator = raw["discriminator"]
    self.pubflags = raw["public_flags"]
    # self.banner = raw["banner"]
    self.avatarhash = raw["avatar"]
    # self.bannercol = raw["banner_color"]
    self.accent = raw["accent_color"]
  def dm(self):
    return bdw.Channel(APIcall(f"/users/@me/channels", "POST", self.bot.auth, {
      "recipient_id": self.id
    }), self.bot)
  def __repr__(self):
    return f"{self.username}#{self.discriminator}"