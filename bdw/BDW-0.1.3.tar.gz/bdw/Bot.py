from .comm import *
from .Intents import *
import websocket, threading, json, time

class Bot:
  '''
  This is the main library for constructing the bots. It requires a list of intents and you will receive events accordingly of the inputted intents. To interact with an event you need to use the @bot.event decorator with the function name being the event. You get d as the argument which is the raw json of the event which you can put into another object to use the data unless you want it raw. You can use method bot.start(auth) to run the bot. Note that nothing is async... because yes.
  '''
  def __init__(self, intents=[]):
    self.guilds = []
    self.intents = IG(intents)
    self.s = None
    self.bot = self
    self.events = {}
  def heartbeat(self, ws, interval):
    while True:
      time.sleep(interval*0.001)
      heartbeatdata = {
        "op": 1,
        "t": None,
        "s": None,
        "d": self.s
      }
      ws.send(json.dumps(heartbeatdata))
  # Events 
  def NTEV(self, EVN):
    return EVN.upper()
  def event(self, func):
    def eventwrapper():
      self.events[self.NTEV(func.__name__)] = func
    return eventwrapper()
  # Gate way stuff begin
  def on_message(self, ws, msg):
    data = json.loads(msg)
    self.s = data["s"]
    if data["op"] == 10:
      authorization = {
        "op": 2,
        "t": None,
        "s": None,
        "d": {
          "token": self.auth,
          "intents": self.intents.getIntent(),
          "properties": {
            "$os": "UDNSystems",
            "$browser": "Icefox",
            "$device": "Internet"
          }
        }
      }
      ws.send(json.dumps(authorization))
      self.heartbeatthread = threading.Thread(target=self.heartbeat, args=(ws, data["d"]["heartbeat_interval"],), daemon=True)
      self.heartbeatthread.start() 
    if data["op"] == 0:
      if self.events.__contains__(data["t"]):
        self.events[data["t"]](data["d"])
  def on_close(self, ws, status, msg):
    print("Closed connection with status code"+str(status)+". Last message: \n"+msg)
  def on_error(self, ws, err):
    if not str(err).startswith("Expecting value: line"):
      print("ERROR: \n"+str(err))
  def on_ready(self, ws):
    pass
  # Gateway stuff end
  def start(self, auth):
    self.guilds = APIcall("/users/@me/guilds","GET", auth,{})
    self.botws = websocket.WebSocketApp(
      "wss://gateway.discord.gg/?v=9&encoding=json",
      on_open=self.on_ready,
      on_error=self.on_error,
      on_message=self.on_message,
      on_close=self.on_close
    )
    self.auth = auth
    self.botws.run_forever()
  def __repr__(self):
    usr = APIcall("/users/@me", "GET", self.auth, {})
    return usr['username']+"#"+str(usr['discriminator'])