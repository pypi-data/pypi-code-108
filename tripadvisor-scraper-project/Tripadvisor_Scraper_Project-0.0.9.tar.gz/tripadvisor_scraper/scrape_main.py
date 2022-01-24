from .scraper import ScrapTrip

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from sqlalchemy import create_engine

from tqdm import tqdm



def main():
    city = input('Enter the name of the city from which you want to scrape hotel data from: ')
    page = int(input('Enter the number of the pages you want to scrap!'))
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('log-level=3')
    obj = ScrapTrip(chrome_options)
    time.sleep(3)
    obj.web_driver("https://www.tripadvisor.co.uk/")
    time.sleep(10)
    obj.accept_cookies_button('//*[@id="onetrust-accept-btn-handler"]')
    time.sleep(5)
    obj.search_city(city, '//*[@id="lithium-root"]/main/div[3]/div/div/div[2]/form/input[1]')
    time.sleep(5)
    obj.hotel_tab('//*[@id="search-filters"]/ul/li[2]/a')
    time.sleep(5)
    hotel_links = obj.get_urls_of_Hotel(page,'//a[@class = "review_count"]')
    time.sleep(5)
    image_links = obj.get_images(page,'//div[@class="prw_rup prw_common_responsive_image"]/div[1]/div')
    time.sleep(5)
    uuid_list = obj.gen_uuid(image_links)
    time.sleep(5)
    
    obj.download_images(city,image_links, uuid_list)
    time.sleep(3)
    hotel_data_dict = obj.get_hotel_data(uuid_list, hotel_links)
    
    time.sleep(3)
    obj.dict_json_s3(city,hotel_data_dict)

if __name__ == '__main__':
    main()