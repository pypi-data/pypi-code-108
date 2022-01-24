from turtle import back
from typing import List
import os

class SenkaSetting:
  def __init__(self, settings:dict):
    self.settings = settings

  def set_settings(self, settings:dict):
    self.settings = settings

  def get_settings(self) -> dict:
    return self.settings

  def get_available_chain(self, blacklist = []) -> List[str]:
    blacklist.append('__pycache__')
    path = '%s/chain' % os.path.dirname(__file__)
    files = os.listdir(path)
    dir = sorted([f for f in files if os.path.isdir(os.path.join(path, f)) and f not in blacklist])

    return dir