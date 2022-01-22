import uuid
import requests
import time
import json
# pip install quick_crawler
from quick_crawler.page import quick_html_page
from quick_crawler.browser import check_url_ok

class Carbon2Api:
    def __init__(self,root_url):
        self.root_url=root_url

    def exists_url(self,url):
        api_url = f'{self.root_url}/Data'

        parameters = {"Url": url
                      }

        r = requests.get(api_url, params=parameters)
        # print(r.text)
        result_obj=json.loads(r.text)
        return int(result_obj["Result"])

    def submit_metadata(self,url,title,uploader,publisher="",publishtime="",keywords="",description="",html="",language="",baidu_url="",search_keywords="",remark="",tag="",file_id=""):
        api_url = f'{self.root_url}/Data'

        parameters = {"Url": url,
                      "Title": title,
                      "Publisher": publisher,
                      "PublishTime": publishtime,
                      "Keywords": keywords,
                      "Description": description,
                      "Html": html, # 这个可以设置为空，因为是后面会有上传，不需要录入数据库
                      "Language": language,
                      "Uploader": uploader,# 用户的姓名全拼，用于区分不同用户的数据
                      "AddTime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
                      "BaiduUrl": baidu_url,
                      "SearchKeywords": search_keywords,
                      "Remark": remark,
                      "Tag": tag,
                      "FileId": file_id,
                      }
        r = requests.post(api_url, params=parameters)
        # print(r.text)
        result_obj=json.loads(r.text)
        return int(result_obj["Result"])

    def submit_file(self,file_path):
        files = [
            ('file_1', open(file_path, 'rb')),
           # ('file_2', open('data/baidu_peark_carbon_emission_opinion.txt', 'rb')),
        ]
        resp = requests.post(f'{self.root_url}/Data',  files=files)
        # print(resp.request.body.decode('utf-8'))
        return resp.text






