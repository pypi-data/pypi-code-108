# skypy(skypy-api) by FuchsCrafter - https://github.com/FuchsCrafter/skypy

import requests
import json

class skypy:
  """ The skypy class for the module. Uses a api key that you can find by running /api on mc.hypixel.net """
  def __init__(self, key):
    global apikey
    apikey = str(key)
    r = requests.get("https://api.hypixel.net/key?key="+ key)
    returns = json.loads(r.text)
    if not returns["success"]:
      print("Invalid API Key! Please note that you cant use some modules now!")

  def getNews(self):
    """ Gets th latest SkyBlock news"""
    r = requests.get("https://api.hypixel.net/skyblock/news?key=" + apikey)
    returns = json.loads(r.text)
    if not returns["success"]:
      print("Failed! Make sure that you api key is correct!")
    else:
      return returns["items"]

  class bazaar:
    """ The bazaar class was made to get bazaar values from certain items. """
    def __init__(self):
      pass

    def fetchAllProducts(self):
      """ Fetches all products and returns them as a JSON string. """
      r = requests.get("https://api.hypixel.net/skyblock/bazaar")
      r = json.loads(r.text)
      return r["products"]

    def fetchProduct(self, itemname):
      """ Fetches a specific product and returns his data as a JSON string. """
      r = requests.get("https://api.hypixel.net/skyblock/bazaar")
      bazaarProducts = json.loads(r.text)
      bazaarProducts = bazaarProducts["products"]
      try:
        return bazaarProducts[itemname]
      except:
        return False
  class auction:
    """ The auction class is there to get auction informations. It requires the Hypixel api key (log into mc.hypixel.net and type /api in chat)."""
    def __init__(self):
      pass

    def getAuctionByPlayer(self, uuid):
      """ Gets the auction by a player uuid. """
      r = requests.get("https://api.hypixel.net/skyblock/auction?key=" + apikey + "&player=" + uuid)
      returns = json.loads(r.text)
      if not returns["success"]:
        print("Failed! Make sure, that you api key and the uuid is correct!")
      else:
        return returns["auctions"]

    def getAuctionByPlayerName(self, player):
      """ Uses the Mojang API to get the uuid of a player. """
      r = requests.get("https://api.mojang.com/users/profiles/minecraft/" + player)
      returns = json.loads(r.text)
      try:
        playeruuid = returns["id"]
        return self.getAuctionByPlayer(playeruuid)
      except:
        print("Invalid Playername!")

    def getAuction(self, auctionid):
      """ Gets an auction by its ID. """
      r = requests.get("https://api.hypixel.net/skyblock/auction?key=" + apikey + "&uuid=" + auctionid)
      returns = json.loads(r.text)
      if not returns["success"]:
        print("Failed! Make sure, that you api key and the auction-id is correct!")
      else:
        return returns["auctions"]
   
    def getAuctions(self):
      """ Gets all active auctions. You dont need an API key for this. """
      r = requests.get("https://api.hypixel.net/skyblock/auctions")
      returns = json.loads(r.text)
      return returns["auctions"]

    def getEndedAuctions(self):
      """ Gets the latest ended auctions. It works also without any authorization."""
      r = requests.get("https://api.hypixel.net/skyblock/auctions_ended")
      returns = json.loads(r.text)
      return returns["auctions"]

  
