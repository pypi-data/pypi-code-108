import requests
from requests.utils import quote

class APIerror(Exception):
  pass
def APIcall(URI, type, auth, payload) -> dict:
  res = {}
  if type == "GET":
    res = requests.get("https://discord.com/api/v9"+URI, headers={"Authorization": "Bot "+auth}, data=payload).json()
  elif type == "POST":
    res = requests.post("https://discord.com/api/v9"+URI, headers={"Authorization": "Bot "+auth,"Content-Type": "application/json"}, json=payload).json()
  elif type == "DELETE":
    res = requests.delete("https://discord.com/api/v9"+URI, headers={"Authorization": "Bot "+auth,"Content-Type": "application/json"}, json=payload).json()
  elif type == "PATCH":
    res = requests.patch("https://discord.com/api/v9"+URI, headers={"Authorization": "Bot "+auth,"Content-Type":"application/json"},json=payload).json()
  elif type == "PUT":
    try:
      res = requests.put("https://discord.com/api/v9"+URI, headers={"Authorization": "Bot "+auth,"Content-Type":"application/json"},json=payload).json()
    except:
      res = None
  if not res == None:
    if res.__contains__("code"):
      raise APIerror(res)
  return res

def URLencode(unenc) -> str:
  return quote(unenc)