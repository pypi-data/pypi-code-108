import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from bs4 import BeautifulSoup
from scrapy.exceptions import CloseSpider
from quick_crawler import page
import hashlib
import os
MAX_NUM_URLS=1000
DATA_ROOT='../quick_crawler/news_data3'
IS_SAVE_FULLTEXT='True'
USE_PLAIN_TEXT='False'
KEYWORDS='digital economy'
USE_KEYWORDS='True'
url_count=0
list_keywords=KEYWORDS.split(";")
list_keywords=[k.strip().lower() for k in list_keywords]

def get_md5_url(url):
    url=str(url)
    m = hashlib.md5()
    m.update(url.encode('utf-8'))
    return m.hexdigest()

def get_page_meta(html_str):
    soup = BeautifulSoup(html_str, features="lxml")

    keywords=""
    description=""

    title = soup.title.string
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
    model = {
        "title":title.replace("\n",""),
        "lang":lang,
        "keywords":keywords.replace("\n",""),
        "description":description.replace("\n","")
    }
    return model

def get_body(html):
    if html != None:
        body = html.find("body")
    else:
        body = None
    return body

class NewsSpider(CrawlSpider):
    name = 'en-cnn'
    allowed_domains = ['edition.cnn.com']
    start_urls = ['https://edition.cnn.com/']

    rules = (
        Rule(LinkExtractor(), callback='parse_item', follow=True),
    )

    def parse_item(self, response):
        global url_count
        global list_model
        url_count+=1
        if url_count>=int(MAX_NUM_URLS):
            raise CloseSpider('termination condition met')
        print(self.name + "'s URL: ", response.url)
        html_str=response.text
        html=BeautifulSoup(html_str,features='lxml')
        remove_tags=['style','script','svg','path','noscript']
        for tag in remove_tags:
            for item in html.findAll(tag):
                item.decompose()
        # detect if exists keywords
        if USE_KEYWORDS=="True":
            if len(list_keywords)!=0:
                body=get_body(html)
                flag_find=False
                for k in list_keywords:
                    if body!=None and k in body.text:
                        flag_find=True
                        break
                if flag_find==False:
                    # stop the call back
                    return None

        html_str=str(html.find("html"))
        if IS_SAVE_FULLTEXT=="True":
            name_folder=DATA_ROOT+"/"+self.name
            if not os.path.exists(name_folder):
                os.mkdir(name_folder)
            url_id=get_md5_url(response.url)
            url_file_path=name_folder+"/"+url_id+".txt"
            # if url has been downloaded, ignore
            if not os.path.exists(url_file_path):
                f_out=open(url_file_path,'w',encoding='utf-8')
                if USE_PLAIN_TEXT=="True":
                    body=get_body(html)
                    if body!=None:
                        f_out.write(body.text)
                else:
                    f_out.write(html_str)
                f_out.close()
                f_out = open(name_folder + "/" + url_id + "_url.txt",'w',encoding='utf-8')
                f_out.write(response.url)
                f_out.close()

        meta_model=get_page_meta(html_str)
        meta_model["url"]=page.quick_remove_unicode(response.url)
        meta_model["id"]=page.quick_remove_unicode(self.name)
        print(meta_model)
        #list_model.append(meta_model)

        return meta_model


