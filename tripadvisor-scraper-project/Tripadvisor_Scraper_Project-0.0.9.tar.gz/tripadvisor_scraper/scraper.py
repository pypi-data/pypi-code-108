from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd
from sqlalchemy import create_engine
import boto3
import tempfile
import os
from tqdm import tqdm
import urllib.request
import uuid
import json
import warnings


warnings.filterwarnings("ignore", category=DeprecationWarning)

class ScrapTrip():
    
    def __init__(self, chrome_options):
        

        self.driver = webdriver.Chrome(options=chrome_options)
        
    def web_driver(self, URL: str)-> None:
        """get webdriver to pointing website

        Args:
            URL (str): url of website

        
        """
        self.driver.get(URL)

    def accept_cookies_button(self, xpath : str) ->None:
        """accept cookies button
        # xpath of accept button  : //*[@id="onetrust-accept-btn-handler"]
        Args:
            
            xpath (str): xpath of cookies accept Button
        """

        #driver.get(URL)
        time.sleep(3)
        try:
            cookies_btn = self.driver.find_element_by_xpath(xpath)
            cookies_btn.click()
        except:
            print(cookies_btn.text)
        print("Cookies button accepted")

    def search_city(self, city : str, xpath : str)-> None:

        """Search city
        # xpath of searchbar : //*[@id="onetrust-accept-btn-handler"]
        Args:
            
            xpath (str): xpath of searchBar 
            city (str): city to search in search bar
        """
        time.sleep(3)
        serch_section = self.driver.find_element_by_xpath(xpath)
       

        serch_section.send_keys(Keys.RETURN)
        serch_section.send_keys(city)
        serch_section.send_keys(Keys.RETURN)
        print(f'{city} enter')

    def hotel_tab(self, xpath_hotel_tab: str) -> None:
        """click to hotel tab

        Args:
            xpath_hotel_tab (str): xpath of hotel tab
        """
        time.sleep(3)
        self.driver.find_element_by_xpath(xpath_hotel_tab).click()
        print("hotel tab clicked")


    def get_urls_of_Hotel(self,page_n:int, xpath_hotel: str)-> list:
        """Get url of all hotel

        Args:
            
            xpath_hotel (str): xpath of hotel '//a[@class = "review_count"]'
            
        """
        time.sleep(3)
        
        hotel_links =[]
        for i in range(1,page_n+1):
            
            list_hotels = self.driver.find_elements_by_xpath(xpath_hotel)
            for i in range(len(list_hotels)):
                link = (list_hotels[i].get_attribute('href')).replace("#REVIEWS","")
                hotel_links.append(link)
            
            # next page button click
            self.driver.find_element_by_link_text("Next").click()
            
            len(hotel_links) 
            time.sleep(5)
        print("hotel links done")
        return hotel_links

    def get_images(self,page_n:int, xpath_img: str)-> list:
        """Get url of all hotel

        Args:
            
            xpath_img (str): xpath of hotel '//div[@class="prw_rup prw_common_responsive_image"]/div[1]/div'
            
        """
        time.sleep(3)
        
        image_links = []
        
        for i in range(1,page_n+1):
            

            # images  
            div_img = self.driver.find_elements_by_xpath(xpath_img)
            #imgtags = self.driver.find_elements_by_xpath('//div[@class="inner"]')
            print(len(div_img))
            for j in range(len(div_img)):
                imgpath = div_img[j].get_attribute("style")
                image_links.append(imgpath[23:-3])
                #print(imgpath[23:-3])
            


            # next page button click
            self.driver.find_element_by_link_text("Next").click()
            
             
            time.sleep(5)
        print("image link done")
        return image_links

    
    def gen_uuid(self,links : list)-> list:
        uuid_list = []
        for i in range(len(links)):
            uuid_list.append(uuid.uuid4().int)
        print("uuid gen done")
        return uuid_list
    
    def download_images(self,city:str,image_links:list, uid_list:list, path='.') -> None:
        '''
        This method will download the images to the specified path
        '''
        s3_client = boto3.client('s3')
        id_image_dict = dict(zip(uid_list,image_links))
        #print(id_image_dict)
        #if not os.path.exists(f'{path}/images/{city}'):
        #    os.makedirs(f'{path}/images/{city}')
        #if image_links is None:
        #    print('No images found, plase run get_images() first')
        #    return None
        
        #for i, scr in enumerdownlodedate(tqdm(image_links)):
        #    urllib.request.urlretrieve(scr, f'{path}/images/hotel_{i}.jpg')

        #for key, value in tqdm(id_image_dict.items()):
        #    urllib.request.urlretrieve(value, f'{path}/images/{city}/{key}.jpg')
            #s3_client.upload_file(f'{path}/images/{city}/{key}.jpg', 'aicoredata', f'images/{city}/{key}.jpg')
            #time.sleep(2)
        #print("image downloded")

        #for key, value in tqdm(id_image_dict.items()):
            #urllib.request.urlretrieve(value, f'{path}/images/{city}/{key}.jpg')
        #    s3_client.upload_file(f'{path}/images/{city}/{key}.jpg', 'aicoredata', f'images/{city}/{key}.jpg')
            #time.sleep(2)
        #print("image uploaded")

        with tempfile.TemporaryDirectory() as temp_dir:
            for key, value in tqdm(id_image_dict.items()):
                print(value)
                urllib.request.urlretrieve(value, f'{temp_dir}/{key}.jpg')
                s3_client.upload_file(f'{temp_dir}/{key}.jpg', 'aicoredata', f'images/{city}/{key}.jpg')
                time.sleep(2)
    

    
    def upload_image_aws(self, image_links : list):
        # extracting images
        s3_client = boto3.client('s3')
        # Create a temporary directory, so you don't store images in your local machine
        with tempfile.TemporaryDirectory() as temp_dir:
            for i, scr in enumerate(tqdm(image_links)):
                urllib.request.urlretrieve(scr, f'{temp_dir}/{i}hotel.jpg')
                s3_client.upload_file(f'{temp_dir}/{i}hotel.jpg', 'aicoredata', f'{i}hotel.jpg')
                time.sleep(2)
    

    def get_hotel_data(self, uidlist:list, hotellist : list)-> dict:
        """get hotel information,UK220117-59732534 and ameneties
        Args:
            hotellist (list): list of hotels
        """
       

        hotel_info = {"id":[],"name":[],"address":[], "reviews":[], "mail_id":[],"rating": [],"amenities": []}
        hotel_info['id'] = uidlist

        
        for i in tqdm(range(len(hotellist))):
            time.sleep(2)
            
            self.driver.get(hotellist[i])
            
            
            
            try:
                hotel_name = self.driver.find_element_by_xpath('//h1[@id = "HEADING"]').text

                
            except:
                hotel_name = ""
            hotel_info["name"].append(hotel_name)
            

            try:
                hotel_address = self.driver.find_element_by_xpath('//div[@class = "ewock"]').text
            except:
                hotel_address = ""
            hotel_info["address"].append(hotel_address)
            


            try:
                hotel_reviews = self.driver.find_element_by_xpath('//span[@class="HFUqL"]').text
            except:
                hotel_reviews = ""    
            hotel_info["reviews"].append(hotel_reviews)
            

            '''try:
                hotel_phone = self.driver.find_element_by_xpath('//div[@class="fdbDs"]').text
            except:
                hotel_phone = ""
            hotel_info["phone"].append(hotel_phone)
            print(hotel_phone)
            '''

            try:
                hotel_mail_id = self.hotel_linksdriver.find_element_by_xpath('//a[@class = "bIWzQ fWKZw"]').get_attribute('href')
            except:
                hotel_mail_id = ""
            hotel_info["mail_id"].append(hotel_mail_id)
            #print(hotel_mail_id)


            try:
                hotel_rating = self.driver.find_element_by_xpath('//span[@class="bvcwU P"]').text
            except:
                hotel_rating = ""
            hotel_info["rating"].append(hotel_rating)
            #print(hotel_rating)

            amenities = self.driver.find_elements_by_xpath('//div[@class="bUmsU f ME H3 _c"]')
            property_amenities = []
            for i in range(len(amenities)):
                amenity = amenities[i].text
                if amenity != '':
                    property_amenities.append(amenity)
            hotel_info["amenities"].append(' ,'.join(map(str,list(set(property_amenities)))))

        print("hotel data get done")
        return hotel_info

    def dict_json_s3(self,city:str, hotel_data_dict:dict):
            
        
        s3 = boto3.client('s3')
            
        # Serializing json  
        with open(f'{city}.json', "w") as outfile:
            json.dump(hotel_data_dict, outfile)

        with open(f'{city}.json', "rb") as f:
            s3.upload_fileobj(f, "aicoredata", f'jsonfile/{city}.json')
        print("json file added to s3")



'''
def main():
    city = input('Enter the name of the city from which you want to scrape hotel data from: ')
    page = int(input('Enter the number of the pages you want to scrap!'))
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('log-level=3')
    obj = ScrapTrip(chrome_options)
    time.sleep(3)
    obj.web_driver("https://www.tripadvisor.co.uk/")
    time.sleep(3)
    obj.accept_cookies_button('//*[@id="onetrust-accept-btn-handler"]')
    time.sleep(3)
    obj.search_city(city, '//*[@id="lithium-root"]/main/div[3]/div/div/div[2]/form/input[1]')
    time.sleep(3)
    obj.hotel_tab('//*[@id="search-filters"]/ul/li[2]/a')
    time.sleep(3)
    hotel_links = obj.get_urls_of_Hotel(page,'//a[@class = "review_count"]')
    time.sleep(3)
    image_links = obj.get_images(page,'//div[@class="prw_rup prw_common_responsive_image"]/div[1]/div')
    time.sleep(3)
    uuid_list = obj.gen_uuid(image_links)
    time.sleep(3)
    
    obj.download_images(city,image_links, uuid_list)
    time.sleep(3)
    hotel_data_dict = obj.get_hotel_data(uuid_list, hotel_links)
    
    time.sleep(3)
    obj.dict_json_s3(city,hotel_data_dict)


   # upload_aws_rds(hotel_data_dict)


def upload_aws_rds(hotel_dict:dict):
    df = pd.DataFrame.from_dict(hotel_dict)
    DATABASE_TYPE = 'postgresql'
    DBAPI = 'psycopg2'
    ENDPOINT = 'tripadvisordb.cq2ysoq9uibp.eu-west-2.rds.amazonaws.com' # Change it for your AWS endpoint
    USER = 'postgres'
    PASSWORD = 'tripadvisor2805'
    PORT = 5432
    DATABASE = 'postgres'
    engine = create_engine(f"{DATABASE_TYPE}+{DBAPI}://{USER}:{PASSWORD}@{ENDPOINT}:{PORT}/{DATABASE}")
    engine.connect()
    df.to_sql('tripadvisor_dataset', engine, if_exists='replace')
    
'''