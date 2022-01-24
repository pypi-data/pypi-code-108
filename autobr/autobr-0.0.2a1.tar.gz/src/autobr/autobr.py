import os

from autobr.baidu import BaiduNewsSearch,BaiduWebSearch

def get_baidu_news(keywords,max_page=10,silent=True, driver_path="browsers/chromedriver.exe",save_path=""):
    baidu_news = BaiduNewsSearch(
        webdriver_path=driver_path,
    )
    baidu_news.fetch(raw_keywords=keywords,
                     max_pages=max_page,
                     silent=silent,
                     save_path=save_path)

def get_baidu_pages(keywords,max_page=10,silent=True, driver_path="browsers/chromedriver.exe",save_path=""):
    baidu_pages = BaiduWebSearch(
        webdriver_path=driver_path,
    )

    baidu_pages.fetch(raw_keywords=keywords, max_pages=max_page, silent=silent, save_path=save_path)

def get_baidu_news_with_keyword_combination(first_keyword_path,second_keyword_path,
                max_search_page=10,silent=True, driver_path="browsers/chromedriver.exe",save_folder=""
                                            ):

    country_keywords = [w.strip() for w in open(first_keyword_path, 'r', encoding='utf-8').readlines() if
                        w.strip() != ""]

    carbon2_keywords = [w.strip() for w in open(second_keyword_path, 'r', encoding='utf-8').readlines() if
                        w.strip() != ""]

    print(country_keywords)
    print(carbon2_keywords)

    baidu_news = BaiduNewsSearch(
        webdriver_path=driver_path,
    )

    for country in country_keywords:
        for keyword in carbon2_keywords:
            search_keyword = f"{country} {keyword}"
            print(f"Searching news.baidu.com with the keywords \"{search_keyword}\"...")
            try:
                if not os.path.exists(save_folder):
                    os.mkdir(save_folder)
                saved_path = f"{save_folder}/{search_keyword}-{max_search_page}.csv"
                if open(saved_path, 'r', encoding='utf-8').read().strip() == "title,baidu_url,real_url":
                    baidu_news.fetch(raw_keywords=search_keyword, max_pages=max_search_page, silent=silent,
                                     save_path=saved_path)
            except Exception as err:
                print(err)


def get_baidu_pages_with_keyword_combination(first_keyword_path, second_keyword_path,
                                            max_search_page=10, silent=False, driver_path="browsers/chromedriver.exe",
                                            save_folder=""
                                            ):
    country_keywords = [w.strip() for w in open(first_keyword_path, 'r', encoding='utf-8').readlines() if
                        w.strip() != ""]

    carbon2_keywords = [w.strip() for w in open(second_keyword_path, 'r', encoding='utf-8').readlines() if
                        w.strip() != ""]

    print(country_keywords)
    print(carbon2_keywords)

    baidu_pages = BaiduWebSearch(
        webdriver_path=driver_path,
    )

    for country in country_keywords:
        for keyword in carbon2_keywords:
            search_keyword = f"{country} {keyword}"
            print(f"Searching www.baidu.com with the keywords \"{search_keyword}\"...")
            try:
                if not os.path.exists(save_folder):
                    os.mkdir(save_folder)
                saved_path = f"{save_folder}/{search_keyword}-{max_search_page}.csv"
                if open(saved_path, 'r', encoding='utf-8').read().strip() == "title,baidu_url,real_url":
                    baidu_pages.fetch(raw_keywords=search_keyword, max_pages=max_search_page, silent=silent,
                                     save_path=saved_path)
            except Exception as err:
                print(err)