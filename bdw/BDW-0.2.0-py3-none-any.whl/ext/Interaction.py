from bdw.comm import *
from bdw.Channel import *
from bdw.User import *
from bdw.Utils import *
from bdw.Guild import *
from bdw.Message import *
class InteractionType:
  '''
  In this class, all interactiontypes values are stored
  '''
  PING = 1
  APPLICATION_COMMAND = 2
  MESSAGE_COMPONENT = 3
  APPLICATION_COMMAND_AUTOCOMPLETE = 4
class Interaction:
  '''
  This object makes it possible to interact with well interactions, requires the raw data and the bot object, there is one method called respond'''
  def __init__(self, data, bot):
    self.raw = data
    self.token = data["token"]
    self.id = data["id"]
    self.bot = bot
    self.type = data["type"]
    self.appid = data["application_id"]
    if data.__contains__("channel_id"):
      self.channel = data["channel_id"]
      self.channel = Channel(APIcall(f"/channels/{self.channel}", "GET", bot.auth, {}), bot)
    if data.__contains__("message"):
      self.message = data["message"]['id']
      self.message = get_message_with_id(self.channel.id, self.message, bot)
    if data.__contains__("guild_id"):
      self.guild = data["guild_id"]
      self.guild = Guild(self.guild, bot)
    if data.__contains__("user"):
      self.user = User(data["user"])
      print("user detected")
      print(self.user)
    if data.__contains__("data"):
      self.data = data["data"]
  def respond(self, content, embeds=[], components=[]):
    rembeds = []
    rcomponents = []
    for embed in embeds:
      rembeds.append(embed.getOBJ())
    for component in components:
      rcomponents.append(component.getOBJ())
    APIcall(f"/interactions/{self.id}/{self.token}/callback", 'POST', self.bot.auth, {
      "type": 4,
      "data" : {
        "content": content,
        "tts": False,
        "embeds": rembeds,
        "components": rcomponents,
        "allowed_mentions": { "parse": [] }
      }
    })