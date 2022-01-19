from selenium import webdriver
import time
import requests
from bs4 import BeautifulSoup
import csv

def get_rea_url_from(b_url):
    try:
        r = requests.get(b_url)
        # print(r.status_code)
        # print(r.headers)
        # print(r.text)
        # print(r.url)
        if r.url!=b_url:
            return r.url

        # print(r.url)
        obj = BeautifulSoup(r.text, features='lxml')
        meta = obj.find("noscript").find("meta")
        real_url = meta["content"].split(";")[1].split("'")[1]

        # print(meta)
        # print(real_url)
        return real_url
    except:
        return ""

def init_browser(init_url, driver_path=r"D:\web\chromedriver_win32\chromedriver.exe",implicitly_wait=0.5,wait_after_init=10):
    # set chromodriver.exe path
    driver = webdriver.Chrome(driver_path)
    driver.implicitly_wait(implicitly_wait)
    # launch URL: verify
    driver.get(init_url)
    # identify search box
    # body = driver.find_element_by_tag_name("body")

    # print(body.text)

    # print(body.get_attribute("outerHTML"))

    # print()

    time.sleep(wait_after_init)

    # print("current url: ", driver.current_url)
    return driver

def start(init_url,url_format,save_path,field_names,driver_path, encoding='utf-8'):
    driver = init_browser(init_url=init_url,driver_path=driver_path)
    with open(save_path, 'w', newline='', encoding=encoding) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        for pi in range(0, 1000):
            print("Page ", pi)
            search_url=url_format.replace("{pi}",str(pi*10))
            list_model = get_search_page_model(driver, search_url)
            writer.writerows(list_model)
            csvfile.flush()
            time.sleep(5)
        print()

def get_search_page_model(driver,search_url):
    driver.get(search_url)
    time.sleep(1)
    body = driver.find_element_by_tag_name("body")
    html_obj = BeautifulSoup(body.get_attribute("outerHTML"), features='lxml')

    h3s = html_obj.findAll("h3", {"class": "t"})
    list_model=[]
    for h3 in h3s:
        title = h3.find("a").text
        b_url = h3.find("a")["href"]
        print(title)
        print(b_url)
        try:
            driver.get(b_url)
            time.sleep(3)
            real_url = driver.current_url
        except:
            print("error in ", b_url)
            real_url = ""
        print("Real Url: ",real_url)
        # real_url=get_rea_url_from(baidu_url)
        print()
        # print(h3.find("a").text, h3.find("a")["href"], real_url)
        model = {
            "title": title,
            "b_url": b_url,
            "real_url": real_url
        }
        list_model.append(model)
    return list_model
