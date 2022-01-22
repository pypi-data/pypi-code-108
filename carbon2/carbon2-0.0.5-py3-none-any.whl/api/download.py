import time

import requests
import json
from tqdm import tqdm
from quick_crawler.page import quick_html_page,quick_html_object,quick_download_file,quick_save_csv
from quick_crawler.browser import get_html_str_with_browser
import os

def get_page_count_from_server(server_url,page_size,uploader,tag,use_fields):
    api_url = f"{server_url}/api/Data"
    parameters = {
        "PageIndex": 1,
        "PageSize": page_size
    }

    if uploader != "":
        parameters["Uploader"] = uploader
    if tag != "":
        parameters["Tag"] = tag
        parameters["Fields"] = use_fields

    r = requests.get(api_url, params=parameters)
    page = json.loads(r.text)
    # print(page)
    print("PageCount:", page["PageCount"])
    return page["PageCount"]

def download_data_from_server(server_url,page_size,save_csv_path="",save_rawdata_folder="",func_process=None,uploader="",tag="",use_fields="*",sleep_time=-1,server_timeout=20,func_download_before=None):

    api_url = f"{server_url}/api/Data"
    list_model = []
    fields = []
    page_count=get_page_count_from_server(server_url,page_size,uploader,tag,use_fields)
    print(f"Downloading raw data to: {save_rawdata_folder}")
    for page_index in tqdm(range(1,page_count+1)):# page count
        parameters = {
            "PageIndex": page_index,
            "PageSize": page_size
        }
        if uploader!="":
            parameters["Uploader"]=uploader
        if tag!="":
            parameters["Tag"]=tag
            parameters["Fields"]=use_fields

        r = requests.get(api_url, params=parameters)
        page = json.loads(r.text)
        print(page)
        # print(page)
        # print("Page index = ",page_index)
        # print("PageCount:", page["PageCount"])
        if page==None or page["DataTable"]==None:
            continue
        for row in page["DataTable"]:
            # print(row)
            if len(fields) == 0:
                fields = row.keys()
                # print(fields)
            file_id = row["FileId"]
            download_fulltext_url = f"{server_url}/WebData/{file_id}.txt"
            if save_rawdata_folder!="":
                if not os.path.exists(save_rawdata_folder):
                    os.mkdir(save_rawdata_folder)
                save_path = f"{save_rawdata_folder}/{file_id}.txt"
                if not os.path.exists(save_path):
                    try:
                        if func_download_before!=None:
                            if func_download_before(server_url,file_id)==True:
                                print("downloading...")
                                quick_download_file(download_fulltext_url, save_file_path=save_path)
                            else:
                                continue
                        else:
                            quick_download_file(download_fulltext_url, save_file_path=save_path)
                        if func_process!=None:
                            func_process(row,open(save_path,"r",encoding='utf-8').read())
                    except:
                        print("error in downloading file", download_fulltext_url)
            else:
                html_str=quick_html_page(download_fulltext_url,timeout=server_timeout)
                func_process(row,html_str)
            if save_csv_path!="":
                list_model.append(row)
        if sleep_time!=-1:
            time.sleep(sleep_time)
    if save_csv_path!="":
        print("Saving meta data file to: ",save_csv_path)
        quick_save_csv(save_csv_path, field_names=fields, list_rows=list_model)
    print("Finished!")
