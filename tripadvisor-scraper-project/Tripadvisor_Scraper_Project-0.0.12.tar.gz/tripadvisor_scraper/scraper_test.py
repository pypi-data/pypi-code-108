import unittest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from .scraper import ScrapTrip

class TestScraper(unittest.TestCase):
    def setUp(self) -> None:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.instance = ScrapTrip(chrome_options)
        self.instance.driver.get("https://www.tripadvisor.co.uk/")
        #return super().setUp()

    def test_web_driver(self, URL = "https://www.tripadvisor.co.uk/")-> None:
        self.instance.driver.get("https://www.tripadvisor.co.uk/")
        
        assert "Tripadvisor" in self.instance.driver.title


    def test_accept_cookies_button(self, xpath = '//*[@id="onetrust-accept-btn-handler"]'):
        time.sleep(5)
        self.instance.accept_cookies_button(xpath)

    def test_search_city(self, city = "london", xpath = '//*[@id="lithium-root"]/main/div[3]/div/div/div[2]/form/input[1]'):
        time.sleep(5)
        self.instance.search_city(city, xpath)

        assert "london" in self.instance.driver.title


    
    
    def tearDown(self):
      self.instance.driver.close()


unittest.main(argv=[''], verbosity=2, exit=False)