"""
This is an Ikea Web scraper Module.
A scraper designed to automatically open a URL, navigate to a specific web page, 
extract multiple data types from different variables, and store the data in an 
organised manner in an external storage service.
"""

import json
from tkinter import W
from typing import AsyncContextManager
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import boto3
import pandas as pd
import uuid
import tempfile
from tqdm import tqdm
import urllib
from sqlalchemy import create_engine

class Scraper():

    def __init__ (self, url: str = "https://www.ikea.com/gb/en/"):        
        """
        Initializes the desired URL.

        This function identifies the URL as the Ikea website home page and uses the Chrome Webdriver to open it.
        """
        self.driver = webdriver.Chrome()
        self.driver.get(url)
        self.WebDriverWait = WebDriverWait
        self.EC = EC
        self.BY = By
        self.s3_client = boto3.client('s3', aws_access_key_id=None, aws_secret_access_key=None)
    
    def accept_cookies(self):
        """
        This method accepts Cookies.
        This waits for the "Accept Cookies" pop-up to appear, identifies the button, and clicks it.
        """
        xpath = '//*[@id="onetrust-accept-btn-handler"]'
        self.WebDriverWait(self.driver, 20).until(self.EC.element_to_be_clickable((self.BY.XPATH, xpath))).click()

    def navigate_to_items(self):
        """
        This mathod navigates to the sofa category.
        This navigates to the desired web page - in this case, the one displaying all the sofas - through
        clicking a series of nested links one at a time, waiting an adequate amount of time between each click.
        
        The "Show More" button obtains more items and clicks it until as many items as we need are displayed.
        In this instance, there are 23 items on page 1, and 24 items on all other pages.
        """ 
        menu_button = '/html/body/header/div/div/div/ul/li[7]/button/span'
        products_button = '/html/body/aside/div[3]/nav[1]/ul[1]/li[1]/a'
        furniture_button = '/html/body/aside/div[3]/nav[2]/ul/li[6]/a'
        sofas_button = '/html/body/aside/div[3]/nav[2]/ul/li[6]/nav/ul/li[5]/a'

        self.WebDriverWait(self.driver, 20).until(self.EC.element_to_be_clickable((self.BY.XPATH, menu_button))).click()
        self.WebDriverWait(self.driver, 20).until(self.EC.element_to_be_clickable((self.BY.XPATH, products_button))).click()
        self.WebDriverWait(self.driver, 20).until(self.EC.element_to_be_clickable((self.BY.XPATH, furniture_button))).click()
        self.WebDriverWait(self.driver, 20).until(self.EC.element_to_be_clickable((self.BY.XPATH, sofas_button))).click()         
        
        for i in range(42):
            try:
                show_more_button = WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.XPATH,'/html/body/div[8]/div/div/div[5]/div[1]/div/div[3]/a')))
                self.driver.execute_script("arguments[0].click();", show_more_button)
            except TimeoutException:
                pass
         
    def get_links(self) -> list:
        """
        This method finds the container with all the sofas inside.
        This finds the container embedded in the webpage for the variables 
        we've selected (the sofas), and attaches a common HTML identifier to find each item.
        """
        self.sofa_items = self.driver.find_elements(self.BY.XPATH,".//div[@data-testid='plp-product-card']")

        #sofa link list 
        self.item_links_list = []
        self.image_links = []
        for sofa in self.sofa_items:
            a_tag = sofa.find_element(By.TAG_NAME,'a')
            sofa_link = a_tag.get_attribute('href')
            self.item_links_list.append(sofa_link)

            image_tag = sofa.find_element(self.BY.TAG_NAME, 'img')
            self.image_links.append(image_tag.get_attribute('src'))

    def extract_info(self):

        """
        This method extracts all the data points for each item, adds a UUID, and concatenates them into a dictionary.
        Each sofa has 5 data points available to scrape from the desired website (its name, price, product ID, description, image ). This method takes all of this scraped data, 
        adds a UUID to each variable (Universally Unique Identifier) and stores all 5 of these keys and values in a dictionary.
        """

        self.sofa_dict = {'UUID(v4)':[],'Product ID':[],'Name':[],'Price':[],'Description':[], 'Image':[], 'Image URL':[]}
        

        # extract images
        self.sofa_dict['Image'] = (self.image_links)

        for link in self.item_links_list:
            self.driver.get(link)

            #product_ID
            product_id_outer = self.driver.find_element(self.BY.XPATH, '//*[@id="content"]/div/div/div/div[2]')
            sofa_ID = product_id_outer.get_attribute('data-product-id')
            if sofa_ID not in self.sofa_dict['Product ID']:
                self.sofa_dict['Product ID'].append(sofa_ID)
            else:
                pass

            #sofa name
            item_name_outer = self.driver.find_element(self.BY.CSS_SELECTOR,"h1.range-revamp-header-section")
            item_name = item_name_outer.find_element(self.BY.XPATH,"./div").text
            self.sofa_dict['Name'].append(item_name)

            #sofa price
            item_price_outer= self.driver.find_element(self.BY.CSS_SELECTOR,'#content > div > div > div > div.range-revamp-product__subgrid.product-pip.js-product-pip > div.range-revamp-product__buy-module-container > div > div.js-price-package.range-revamp-pip-price-package > div.range-revamp-pip-price-package__wrapper > div.range-revamp-pip-price-package__price-wrapper')
            item_price = item_price_outer.find_element(self.BY.XPATH,'./div').text
            self.sofa_dict['Price'].append(item_price)

            #sofa description
            item_desc_outer = self.driver.find_element(self.BY.CSS_SELECTOR,"h1.range-revamp-header-section")
            item_description = item_desc_outer.find_element(self.BY.TAG_NAME,"span").text
            self.sofa_dict['Description'].append(item_description)

            #sofa UUID
            self.sofa_dict['UUID(v4)'].append(str(uuid.uuid4()))

    def upload_images(self):
        """
        This method uploads the images for each item, and stores them externally to an s3 bucket hosted by AWS
        (Amazon Web Services) for external storage.
        A temporary directory is created to download the images before they are uploaded. 

        Each of the image's object url is then appended to the Sofa dictionary Image URL key. This is down so that each image is correctly associated with it's item and obtain a unique identifier.     
        
        Now that the dictionary is complete, it is converted to a pandas dataframe.
        """
        self.s3_client = boto3.client('s3')

        #create temp directory to store images
        with tempfile.TemporaryDirectory() as temp_dir:
            for i, src in enumerate(tqdm(self.sofa_dict['Image'])):
                urllib.request.urlretrieve(src, f'{temp_dir}/{i}sofa.jpg')
                self.s3_client.upload_file(f'{temp_dir}/{i}sofa.jpg', 'aicore-group3-ikea-images', f'{i}sofa.jpg')
                time.sleep(1)
                self.sofa_dict["Image URL"].append("https://aicore-group3-ikea-images.s3.eu-west-2.amazonaws.com/" + f'{i}sofa.jpg')
        
    def check_dict(self):
        """
        This method checks if the dictionary keys have been populated with values.
        """
        if len(self.sofa_dict['Image']) > 1: 
            pass 
        else: 
            print('Dictionary has not been populated')
            
        # self.sofa_df=pd.DataFrame.from_dict(self.sofa_dict)


    def download_info(self):
        """
        This method converts the dictionary into a json file.
        """

        with open('sofa_samples.json', 'w', newline= '') as json_file:
            json.dump(self.sofa_dict, json_file)


    def upload_to_cloud(self):
        """
        This method uploads the json file to another s3 bucket hosted by AWS as storage for the tabular data
        """
        response = self.s3_client.upload_file('sofa_samples.json', 'aicore-group3-ikea-items', 'sofa_samples.json')

if __name__ == '__main__':
    ikea = Scraper()
    ikea.accept_cookies()
    ikea.navigate_to_items()
    ikea.get_links()
    ikea.extract_info()
    ikea.upload_images()
    ikea.download_info()
    ikea.upload_to_cloud()
