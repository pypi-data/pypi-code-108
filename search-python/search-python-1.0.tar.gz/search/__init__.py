from bs4 import BeautifulSoup
from requests import get
from urllib.parse import quote

def google(query, max_results = 10, lang = "en", proxies = {}):
  page = get(f"https://www.google.com/search?q={quote(query, safe='')}&num={max_results}&hl={lang}", headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ''Chrome/61.0.3163.100 Safari/537.36'}, proxies = {}).text
  chunk = BeautifulSoup(page, "lxml").find_all("div", attrs={"class": "yuRUbf"})
  results = {}
  for i in range(len(chunk)):
    results.update({i: {"title": chunk[i].find("h3").text, "url": chunk[i].find("a", href = True)["href"]}})
  return results

def yahoo(query, proxies = {}):
  page = get(f"https://search.yahoo.com/search?p={quote(query, safe='')}", headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ''Chrome/61.0.3163.100 Safari/537.36'}).text
  chunk = BeautifulSoup(page, "lxml").find_all("div", attrs={"class": "options-toggle"})
  results = {}
  for i in range(len(chunk)):
    results.update({i: {"title": chunk[i].find("h3").text, "url": chunk[i].find("a", href = True)["href"]}})
  return results

def bing(query, proxies = {}):
  page = get(f"https://www.bing.com/search?q={quote(query, safe='')}", headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ''Chrome/61.0.3163.100 Safari/537.36'}, proxies = {}).text
  chunk = BeautifulSoup(page, "lxml").find_all("li", attrs={"class": "b_algo"})
  results = {}
  for i in range(len(chunk)):
    results.update({i: {"title": chunk[i].find("h2").text, "url": chunk[i].find("a", href = True)["href"]}})
  return results

def aol(query, proxies = {}):
  page = get(f"https://search.aol.com/aol/search?q={quote(query, safe='')}", headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ''Chrome/61.0.3163.100 Safari/537.36'}, proxies = {}).text
  chunk = BeautifulSoup(page, "lxml").find_all("div", attrs={"class": "options-toggle"})
  results = {}
  for i in range(len(chunk)):
    results.update({i: {"title": chunk[i].find("h3").text, "url": chunk[i].find("a", href = True)["href"]}})
  return results