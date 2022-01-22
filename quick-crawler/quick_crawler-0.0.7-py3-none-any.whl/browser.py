import time
from selenium import webdriver
import urllib.request
from urllib.parse import urlparse
import os
from quick_crawler.page import *

def get_domain(url):
    domain = urlparse(url).netloc
    return domain

def get_html_str_with_browser(url,driver_path="chromedriver.exe",implicitly_wait=0.5,root_ele="html",slient=False, wait_seconds=-1):

    if not os.path.exists(driver_path):
        print("Please set browser driver path in this function, versions between driver and browser must be same!")
        return

    # set chromedriver.exe's path
    if slient:
        options = webdriver.ChromeOptions()
        options.add_argument("--log-level=3")
        options.headless = True
        driver = webdriver.Chrome(executable_path=driver_path,
                                   chrome_options=options
                                  )
    else:
        driver = webdriver.Chrome(executable_path=driver_path
                                  )
    driver.implicitly_wait(implicitly_wait)
    # launch the page
    driver.get(url)

    html_obj = driver.find_element_by_tag_name(root_ele)
    if wait_seconds!=-1:
        time.sleep(5)

    html_str=html_obj.get_attribute("outerHTML")

    driver.close()
    return html_str

def get_page_meta(html_str):
    soup = BeautifulSoup(html_str, features="lxml")

    keywords=""
    description=""
    title=""
    if soup!=None:
        if soup.title!=None:
            title = soup.title.string
    else:
        return {
        "title":"",
        "lang":"",
        "keywords":"",
        "description":""
    }

    print('title = ', title)

    # print(soup.attrs)
    html=soup.find("html")
    if "lang" in html.attrs.keys():
        lang = html["lang"]
    else:
        lang = ""
    print("lang = ",lang)

    meta = soup.find_all('meta')
    # print(html_str)
    for tag in meta:
        if 'name' in tag.attrs.keys():
            name=tag.attrs['name'].strip().lower()
            if name=="description":
                description=tag.attrs['content']
            if name=="keywords":
                keywords=tag.attrs['content']
    if title==None:
        title=""
    if lang==None:
        lang=""
    if keywords==None:
        keywords=""
    if description==None:
        description=""
    model = {
        "title":title.replace("\n",""),
        "lang":lang,
        "keywords":keywords.replace("\n",""),
        "description":description.replace("\n","")
    }
    return model



def check_url_ok(url,timeout=1):
    try:
        return urllib.request.urlopen(url,timeout=timeout).getcode() == 200
    except:
        return False

def revise_config_path(file_path,dict_kv):
    current_path = os.path.dirname(os.path.realpath(__file__))
    # spider_path = current_path + "/scrapy_projects/news_site/news_site/spiders/news_spider_template.py"
    script_text = open(file_path, 'r', encoding='utf-8').read()
    for k in dict_kv:
        script_text = script_text.replace(k, str(dict_kv[k]))

    spider_path_new = file_path.replace("_template", "")
    f_out = open(spider_path_new, 'w', encoding='utf-8')
    f_out.write(script_text)
    f_out.close()

def fetch_meta_info_from_sites(list_item,saved_folder="",download_time_out=30,dns_time_out=20,max_num_urls=1000,is_save_fulltext=False,use_plain_text=False,use_keywords=False):

    from pathlib import Path
    # list_result = page.quick_read_csv("datasets/news_sites.csv", fields=['Id', 'Title', 'Name', 'URL'])

    current_path = os.path.dirname(os.path.realpath(__file__))

    # url = list_result[330]
    for url in list_item:
        name = url[0]
        start_url = url[1]
        domain = get_domain(url[1])
        keywords=""
        if len(url)>=3:
            keywords=url[2]
        else:
            keywords=""
        print(start_url)
        # spider
        dict_kv = {
            "$NAME$": name,
            "$START_URL$":start_url,
            "$DOMAIN$":domain,
            "'$NAX_NUM_URLS$'":str(max_num_urls),
            "$DATA_ROOT$": str(saved_folder).replace("\\","/"),
            "$IS_SAVE_FULLTEXT$": str(is_save_fulltext),
            "$USE_PLAIN_TEXT$": str(use_plain_text),
            "$KEYWORDS$": str(keywords),
            "$USE_KEYWORDS$": str(use_keywords)
        }
        revise_config_path(current_path + "/scrapy_projects/news_site/news_site/spiders/news_spider_template.py",dict_kv=dict_kv)
        # settings
        dict_kv = {
            "'$DOWNLOAD_TIMEOUT$'": download_time_out,
            "'$DNS_TIMEOUT$'": dns_time_out
        }
        revise_config_path(current_path + "/scrapy_projects/news_site/news_site/settings_template.py",
                           dict_kv=dict_kv)

        current_path = os.path.dirname(os.path.realpath(__file__))
        # datasets_path=Path(current_path).parent.absolute()

        os.chdir(current_path+"/scrapy_projects/news_site")

        if saved_folder=="":
            os.system(f"scrapy crawl {name}")
        else:
            saved_path = f"{saved_folder}/{name}.csv"
            saved_path = saved_path.replace("\\", "/")
            print(saved_path)
            os.system(f"scrapy crawl {name} -o \"file:///{saved_path}\" -t csv")
        os.chdir(current_path)

import csv

def get_model_from_csv_file(file_path,fields):
    list_model=[]
    with open(file_path, newline='',encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        list_result = []
        for row in reader:
            list_model.append(row)
    return list_model

def summarize_downloaded_data(data_folder,save_path=""):
    list_model_all=[]
    for name in os.listdir(data_folder):
        csv_file = os.path.join(data_folder, name)
        if csv_file.endswith(".csv"):
            list_model=get_model_from_csv_file(csv_file,"title,lang,keywords,description,url,id".split(","))
            for idx,model in enumerate(list_model):
                list_model[idx]["name"]=name.replace(".csv","")
                list_model[idx]["domain"]=get_domain(model["url"])
                list_model_all.append(list_model[idx])
    if save_path!="":
        quick_save_csv(save_path=save_path,field_names="name,domain,title,lang,keywords,description,url,id".split(","),list_rows=list_model_all)
    return list_model_all

def get_language_code_of_page(url):
    try:
        html_str=get_html_str_with_browser(url,driver_path="browsers/chromedriver.exe",slient=True)
        if html_str.strip()=="":
            return ""
        meta_model=get_page_meta(html_str)
        lang=meta_model["lang"]
        return lang
    except:
        return ""

def get_language_code_of_page_quick(url,timeout=5):
    try:
        html_str=quick_html_page(url,timeout=5)
        if html_str.strip()=="":
            return ""
        meta_model=get_page_meta(html_str)
        lang=meta_model["lang"]
        return lang
    except:
        return ""
