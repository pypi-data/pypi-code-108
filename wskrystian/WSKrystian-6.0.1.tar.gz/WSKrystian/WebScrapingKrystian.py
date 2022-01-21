from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

import requests
from bs4 import BeautifulSoup as bs


class Scraper:

    Keys = Keys
    By = By
    NAME = 'NAME'
    ID = 'ID'
    CSS = 'CSS'
    PCSS = 'PCSS'
    CLASS = 'CLASS'
    LINK_TEXT = 'LINK_TEXT'

    def __init__(self) -> None:
        pass
        


    def open(self, headless=False, path_to_file="C:/Users/Krystian/chromedriver.exe"):
        if headless: 
            options = Options()
            options.headless = True
            self.driver = webdriver.Chrome(path_to_file, options=options)

        else:
            self.driver = webdriver.Chrome(path_to_file)
        
    
    def quit(self):
        self.driver.quit()
        
        
    def get(self, url):
        self.driver.get(url)
    

    def simple_get(url):
        return requests.get(url).content
    
        
    def getsource(self, url=""):
        if url == "":
            return self.driver.page_source
        else:
            self.driver.get(url)
            return self.driver.page_source
        
    
    def getsoup(self, url=""):
        if url == "":
            return bs(self.getsource(), 'html.parser')
        else:
            return bs(self.getsource(url), 'html.parser')
    


    def wait_find(self, method, input_s):
        try:
            return WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((method, input_s)))
        
        except:
            return 'Element not found'

                
    def find(self, method, input_s, key="", value=""):
        if method == Driver.CSS:
            return self.driver.find_element_by_css_selector(input_s)
        elif method == Driver.CLASS:
            return self.driver.find_element_by_class_name(input_s)
        elif method == Driver.ID:
            return self.driver.find_element_by_id(input_s)
        elif method == Driver.NAME:
            return self.driver.find_element_by_name(input_s)
        elif method == Driver.LINK_TEXT:
            return self.driver.find_elements_by_link_text(input_s)
        


    def back(self):
        self.driver.back()


    def forward(self):
        self.driver.forward()


    def scroll(self, position='document.body.scrollHeight'):
        self.driver.execute_script(f"window.scrollTo(0, {position})") 


    def wait(self, time):
        self.driver.implicitly_wait(time)
