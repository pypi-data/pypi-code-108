from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from typing import TypedDict
import os


class Raiz(TypedDict):
  etimologia: str
  acepciones: list[str]


class Definitions():
  def __init__(self):
    options = Options()
    options.headless = True
    self.browser = webdriver.Firefox(
      options=options, service_log_path=os.devnull
    )
    self.url = "https://dle.rae.es/"

  def get_definition(self, word: str) -> list[Raiz]:
    palabra: list[Raiz] = []
    acepciones = []
    self.browser.get(self.url + word)
    raices = self.browser.find_elements(
      By.XPATH,
      "//div[@id='resultados']/article",
    )
    for raiz in raices:
      id = raiz.get_attribute('id')
      article = f"//article[@id='{id}']/"
      etimologia = self.browser.find_element(
        By.XPATH,
        article + "p[starts-with(@class, 'n2')]",
      )
      acepciones = self.browser.find_elements(
        By.XPATH,
        article + "p[starts-with(@class, 'j')]",
      )
      palabra.append(
        {
          "etimologia": etimologia.text,
          "acepciones": [acepcion.text for acepcion in acepciones],
        }
      )
    self.browser.close()
    return palabra
