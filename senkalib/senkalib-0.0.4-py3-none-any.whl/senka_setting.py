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