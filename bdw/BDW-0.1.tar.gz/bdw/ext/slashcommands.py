from bdw.comm import *
from bdw.Guild import *
from bdw.Channel import *
from .Interaction import *
from bdw.Message import *

class ActionRow:
  '''
  This is used to hold components. Only requires one argument called, well, components.
  '''
  componentOBJ = {}
  def __init__(self, components):
    self.componentOBJ["components"] = []
    for component in components:
      self.componentOBJ["components"].append(component.getOBJ())
    self.componentOBJ["type"] = 1
  def getOBJ(self):
    return self.componentOBJ

class ButtonType:
  '''
  Contains all button types
  '''
  PRIMARY = 1
  SECONDARY = 2
  SUCCESS = 3
  DANGER = 4
  LINK = 5

class Button:
  '''
  This hold a button object, requires a name and either an id or url, there are also buttontype and enabled which are 1 and True by default.'''
  componentOBJ = {}
  def __init__(self, name, id="", buttontype=1, url="", enabled=True):
    self.componentOBJ["label"] = name
    self.componentOBJ["type"] = 2
    self.componentOBJ["style"] = buttontype
    self.componentOBJ["disabled"] = not enabled
    if not buttontype == ButtonType.LINK:
      self.componentOBJ["custom_id"] = id
    else:
      self.componentOBJ["url"] = url
  def disable(self):
    self.componentOBJ["disabled"] = True
  def enable(self):
    self.componentOBJ["enable"] = True
  def getOBJ(self):
    return self.componentOBJ

class Slashcommand:
  '''
  This creates a slashcommand which requires a name, a description and the bot object. Options are not implemented yet.'''
  def __init__(self, name, description, bot):
    self.bot = bot
    self.SCOBJ = {"name": name,"description":description,"type":1,"options":[]}
  def register(self):
    self.appid = APIcall("/users/@me", "GET",self.bot.auth,{})["id"]
    APIcall(f"/applications/{self.appid}/commands","POST",self.bot.auth,self.SCOBJ)

def registerCommands(cmds, bot):
  '''
  This requires the commands and the bot object, it adds the not registered ones and deletes the removed ones.
  '''
  if len(cmds) == 0:
    return None
  appid = APIcall("/users/@me", "GET",cmds[0].bot.auth,{})["id"]
  alreadyExisting = []
  ASCOBJS = APIcall(f"/applications/{appid}/commands", "GET", cmds[0].bot.auth, {})
  for scobj in ASCOBJS:
    alreadyExisting.append(scobj['name'])
  for cmd in cmds:
    if not cmd.SCOBJ["name"] in alreadyExisting:
      cmd.register()
  ASCOBJS = APIcall(f"/applications/{appid}/commands", "GET", cmds[0].bot.auth, {})
  alreadyExisting = []
  for scobj in ASCOBJS:
    # alreadyExisting.append(scobj['name'])
    qaq = []
    for cmd in cmds:
      qaq.append(cmd.SCOBJ["name"])
    if not scobj['name'] in qaq:
      ASCOBJS = APIcall(f"/applications/{appid}/commands/{scobj['id']}", "DELETE", cmds[0].bot.auth, {})