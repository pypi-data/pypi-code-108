class Embed:
  '''
  This object is used to send embeds.
  '''
  def __init__(self, title, desc, color=0):
    self.embedOBJ = {"title": title, "description": desc, "fields": [], "color": color, "footer": {}}
    self.footer = {}
    self.thumbnail = {}
    self.author = {}
  def add_field(self, name, value, inline=False):
    field = {"name": name, "value": value, "inline":inline}
    self.embedOBJ["fields"].append(field)
  def set_footer(self, text, footerIMG=""):
    footerOBJ = {"text": text,"icon_url":footerIMG}
    self.embedOBJ["footer"] = footerOBJ
  def set_author(self, name, url="", authorIMG=""):
    authorOBJ = {"name": name, "url": url,"icon_url":authorIMG}
    self.author = authorOBJ
  def set_thumbnail(self, url, width=100, height=100):
    thumbnailOBJ = {"url": url,"width":width,"height":height}
    self.thumbnail = thumbnailOBJ
  def getObj(self) -> dict:
    embedObj = {"title":self.title,"description":self.description,"fields":self.fields,"color":self.color, "footer":self.footer,"author":self.author,"thumbnail":self.thumbnail}
    return embedObj