import os
from quick_crawler.browser import get_page_meta
from quick_crawler.page import *
from quick_crawler.browser import get_html_str_with_browser
from tqdm import tqdm

import hashlib


def get_md5(s):
    hl = hashlib.md5()
    hl.update(s.encode(encoding='utf-8'))
    return hl.hexdigest()

def create_dataset(list_csv_path,save_csv_path, processed_data_folder,text_field='text',file_id_field='FileId',func_process_file=None,func_add_fields=None):
    list_model = quick_read_csv_model(list_csv_path)
    list_model_new = []
    for model in list_model:
        file_path = f"{processed_data_folder}/{model[file_id_field]}.txt"
        text = open(file_path, 'r', encoding='utf-8').read()

        if func_add_fields!=None:
            dict_new_field=func_add_fields(text)
            for k in dict_new_field.keys():
                model[k]=dict_new_field[k]

        if func_process_file!=None:
            text=func_process_file(text)
        model[text_field] = text

        list_model_new.append(model)

    quick_save_csv(save_csv_path, list_model_new[0].keys(), list_model_new)

def get_page_list(url_pattern,min_page,max_page,func_find_list,func_item,save_csv_path,timeout=60,use_web_driver="",download_folder=""):
    list_item = []

    for p in tqdm(range(min_page, max_page + 1)):
        print(f"Page {p}")
        if use_web_driver != "":
            html_str=get_html_str_with_browser( url_pattern.replace("{p}",str(p)),driver_path=use_web_driver)
        else:
            html_str = quick_html_page(
                url_pattern.replace("{p}",str(p)), timeout=timeout)

        # print(html_str)


        html_obj = quick_html_object(html_str)

        items = func_find_list(html_obj)

        for item in items:
            # datetime = item.find("span").text
            #title = item.find("a").text
            # url = item.find("a")["href"]
            title,url,datetime=func_item(item)
            print(title, url)
            md5_id=get_md5(url)
            model = {
                "title": title,
                "url": url,
                "datetime": datetime,
                "file_id":md5_id
            }
            if download_folder!="":
                if not os.path.exists(download_folder):
                    os.mkdir(download_folder)
                if use_web_driver != "":
                    html_str = get_html_str_with_browser(url, driver_path=use_web_driver)
                else:
                    html_str = quick_html_page(
                        url, timeout=timeout)
                quick_save_text(f'{download_folder}/{md5_id}.txt',html_str)
            list_item.append(model)
        print()
    if save_csv_path!="":
        quick_save_csv(save_csv_path, field_names=['title', 'url', 'datetime','file_id'], list_rows=list_item)

def run_web_list_analysis_shell(url_pattern,min_page,max_page,fn_find_list,fn_get_item,working_folder,tag):

    if not os.path.exists(working_folder):
        os.mkdir(working_folder)

    if not os.path.exists(f"{working_folder}/list_{tag}_data"):
        os.mkdir(f"{working_folder}/list_{tag}_data")

    get_page_list(url_pattern=url_pattern,
                  min_page=min_page,
                  max_page=max_page,
                  func_find_list=fn_find_list,
                  func_item=fn_get_item,
                  save_csv_path=f"{working_folder}/list_{tag}.csv",
                  download_folder=f"{working_folder}/list_{tag}_data"
                  )

    def get_html_fields(html_str):
        meta_model = get_page_meta(html_str)
        keywowrds = meta_model["keywords"]
        description = meta_model["description"]
        return {
            'keywords': keywowrds,
            'description': description
        }

    def get_main_text(html_str):
        text = bare_extraction(html_str)['text']
        text = text.replace("\n", "")
        return text

    create_dataset(
        list_csv_path=f"{working_folder}/list_{tag}.csv",
        save_csv_path=f"{working_folder}/list_{tag}_detail.csv",
        processed_data_folder=f"{working_folder}/list_{tag}_data",
        file_id_field='file_id',
        func_add_fields=get_html_fields,
        func_process_file=get_main_text
    )