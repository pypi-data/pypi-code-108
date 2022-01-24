from selenium import webdriver
import time
import requests
from bs4 import BeautifulSoup
import csv
import urllib.parse

class BaiduNewsSearch:
    def __init__(self,
                 webdriver_path="browsers/chromedriver.exe",
                 ):

        # -------------设置参数-----------------
        self.webdriver_path = webdriver_path

        # -------------结束设置参数-----------------

        pass

    def get_rea_url_from_baidu(self,baidu_url):
        try:
            r = requests.get(baidu_url)
            if r.url != baidu_url:
                return r.url
            obj = BeautifulSoup(r.text, features='lxml')
            meta = obj.find("noscript").find("meta")
            real_url = meta["content"].split(";")[1].split("'")[1]
            return real_url
        except:
            return ""

    def get_search_page_model(self,baidu_search_url):

        self.driver.get(baidu_search_url)
        time.sleep(1)
        body = self.driver.find_element_by_tag_name("body")

        # print(body.get_attribute("outerHTML"))

        html_obj = BeautifulSoup(body.get_attribute("outerHTML"), features='lxml')

        h3s = html_obj.findAll("h3", {"class": "news-title_1YtI1"})
        list_model = []
        for h3 in h3s:
            title = h3.find("a").text
            baidu_url = h3.find("a")["href"]
            print(title)
            print("Baidu url: ", baidu_url)
            try:
                # driver.get(baidu_url)
                # time.sleep(3)
                # real_url = driver.current_url
                real_url = baidu_url
            except:
                print("error in ", baidu_url)
                real_url = ""
            print("Real Url: ", real_url)
            # real_url=get_rea_url_from_baidu(baidu_url)
            print()
            # print(h3.find("a").text, h3.find("a")["href"], real_url)
            model = {
                "title": title,
                "baidu_url": baidu_url,
                "real_url": real_url
            }
            list_model.append(model)
        return list_model

    def fetch(self,raw_keywords,
                implicitly_wait=0.5,
                seconds_wait=10,
                func_process=None,
                silent=False,
                max_pages=100,
                save_path="",
                sleep_seconds_before_going_to_next_page=3):
        keywords = urllib.parse.quote(raw_keywords)
        if silent:
            options = webdriver.ChromeOptions()
            options.add_argument("--log-level=3")
            options.headless = True
            self.driver = webdriver.Chrome(executable_path=self.webdriver_path,
                                      chrome_options=options
                                      )
        else:
            self.driver = webdriver.Chrome(executable_path=self.webdriver_path)

        self.driver.implicitly_wait(implicitly_wait)

        # 首次打开，可能需要手动验证相关，验证后，等待10s再自动获取搜索结果列表
        self.driver.get(f"https://www.baidu.com/s?tn=news&word={keywords}")

        body = self.driver.find_element_by_tag_name("body")

        # print(body.text)
        # print(body.get_attribute("outerHTML"))
        # print()
        print("Waiting...")
        print("若百度页面弹出验证页面，请手动通过验证，在10秒内完成！一般来说，验证一次后面就无须验证！")
        time.sleep(seconds_wait)

        # print("current url: ",driver.current_url)

        print("Start to fetch list  ...")

        field_names = ["title", "baidu_url", "real_url"]
        encoding = 'utf-8'
        if save_path!="":
            with open(save_path, 'w', newline='', encoding=encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=field_names)
                writer.writeheader()
                for pi in range(0, max_pages):
                    print("Page ", pi+1)
                    baidu_search_url = f"https://www.baidu.com/s?tn=news&word={keywords}&pn={10 * pi}"
                    list_model = self.get_search_page_model(baidu_search_url)
                    if func_process!=None:
                        func_process(list_model)
                    writer.writerows(list_model)
                    csvfile.flush()
                    time.sleep(sleep_seconds_before_going_to_next_page)
                print()
        else:
            for pi in range(0, max_pages):
                print("Page ", pi + 1)
                baidu_search_url = f"https://www.baidu.com/s?tn=news&word={keywords}&pn={10 * pi}"
                list_model = self.get_search_page_model(baidu_search_url)
                if func_process != None:
                    func_process(list_model)
                time.sleep(sleep_seconds_before_going_to_next_page)

        self.driver.close()

class BaiduWebSearch:
    def __init__(self,
                 webdriver_path="browsers/chromedriver.exe",

                 ):

        # -------------设置参数-----------------

        self.webdriver_path = webdriver_path

        # -------------结束设置参数-----------------



        pass

    def get_rea_url_from_baidu(self, baidu_url):
        try:
            r = requests.get(baidu_url)
            if r.url != baidu_url:
                return r.url
            obj = BeautifulSoup(r.text, features='lxml')
            meta = obj.find("noscript").find("meta")
            real_url = meta["content"].split(";")[1].split("'")[1]
            return real_url
        except:
            return ""

    def get_search_page_model(self, baidu_search_url, sleep_seconds_after_visit_page=3):

        self.driver.get(baidu_search_url)
        time.sleep(1)
        body = self.driver.find_element_by_tag_name("body")

        # print(body.get_attribute("outerHTML"))

        html_obj = BeautifulSoup(body.get_attribute("outerHTML"), features='lxml')

        h3s = html_obj.findAll("h3", {"class": "t"})
        list_model = []
        for h3 in h3s:
            title = h3.find("a").text
            baidu_url = h3.find("a")["href"]
            print(title)
            print("Baidu url: ", baidu_url)
            try:
                self.driver.get(baidu_url)
                time.sleep(sleep_seconds_after_visit_page)
                real_url = self.driver.current_url
                # real_url = baidu_url
            except:
                print("error in ", baidu_url)
                real_url = ""
            print("Real Url: ", real_url)
            # real_url=get_rea_url_from_baidu(baidu_url)
            print()
            # print(h3.find("a").text, h3.find("a")["href"], real_url)
            model = {
                "title": title,
                "baidu_url": baidu_url,
                "real_url": real_url
            }
            list_model.append(model)
        return list_model

    def fetch(self, raw_keywords, implicitly_wait=0.5, seconds_wait=10, func_process=None,silent=False,
              max_pages=100,
              save_path="",
              sleep_seconds_before_going_to_next_page=5,
              sleep_seconds_after_visit_page=3
              ):
        keywords = urllib.parse.quote(raw_keywords)
        if silent:
            options = webdriver.ChromeOptions()
            options.add_argument("--log-level=3")
            options.headless = True
            self.driver = webdriver.Chrome(executable_path=self.webdriver_path,
                                           chrome_options=options
                                           )
        else:
            self.driver = webdriver.Chrome(executable_path=self.webdriver_path)


        self.driver.implicitly_wait(implicitly_wait)

        # 首次打开，可能需要手动验证相关，验证后，等待10s再自动获取搜索结果列表
        self.driver.get(f"https://www.baidu.com/s?t&wd={keywords}")

        body = self.driver.find_element_by_tag_name("body")

        # print(body.text)
        # print(body.get_attribute("outerHTML"))
        # print()
        print("Waiting...")
        print("若百度页面弹出验证页面，请手动通过验证，在10秒内完成！一般来说，验证一次后面就无须验证！")
        time.sleep(seconds_wait)

        # print("current url: ",driver.current_url)

        print("Start to fetch list  ...")

        field_names = ["title", "baidu_url", "real_url"]
        encoding = 'utf-8'
        if save_path!="":
            with open(save_path, 'w', newline='', encoding=encoding) as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=field_names)
                writer.writeheader()
                for pi in range(0, max_pages):
                    print("Page ", pi + 1)
                    baidu_search_url = f"https://www.baidu.com/s?wd={keywords}&pn={10 * pi}"
                    list_model = self.get_search_page_model(baidu_search_url,sleep_seconds_after_visit_page)
                    if func_process != None:
                        func_process(list_model)
                    writer.writerows(list_model)
                    csvfile.flush()
                    time.sleep(sleep_seconds_before_going_to_next_page)
                print()
        else:
            for pi in range(0, max_pages):
                print("Page ", pi + 1)
                baidu_search_url = f"https://www.baidu.com/s?wd={keywords}&pn={10 * pi}"
                list_model = self.get_search_page_model(baidu_search_url)
                if func_process != None:
                    func_process(list_model)
                time.sleep(sleep_seconds_before_going_to_next_page)
            print()

        self.driver.close()

