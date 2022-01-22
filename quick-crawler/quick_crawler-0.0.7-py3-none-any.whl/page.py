import requests
import csv
import json
from bs4 import BeautifulSoup


def quick_html_page(url,headers=None,page_encoding='utf-8',save_file_path=None,save_encoding="utf-8",timeout=5,ignore_error=False):
    html_str=None
    try:
        if headers==None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            }
        response = requests.get(url, headers=headers,timeout=timeout)
        html_str = response.content.decode(encoding=page_encoding)
        if save_file_path!=None:
            f_out = open(save_file_path, "w", encoding=save_encoding)
            f_out.write(str(html_str))
            f_out.close()
    except Exception as err:
        if ignore_error:
            print(err)
        else:
            raise err
    return html_str

def quick_html_object(html_str):
    soup = BeautifulSoup(html_str, features="lxml")
    return soup

def quick_html_page_range(url,headers=None,page_encoding='utf-8',save_encoding="utf-8",save_file_path=None,min_page=1,max_page=100):
    list_html_str=[]
    for pi in range(min_page,max_page+1):
        current_url=url.replace("{pi}",str(pi))
        print(current_url)
        if save_file_path!=None:
            html_str=quick_html_page(current_url,headers,page_encoding, save_file_path=save_file_path.replace("{pi}",str(pi)), save_encoding=save_encoding)
        else:
            html_str = quick_html_page(current_url, headers, page_encoding)
        list_html_str.append(html_str)
    return list_html_str

def quick_remove_unicode(str,encoding='gbk',decoding='gbk'):
    string_encode = str.encode(encoding, "ignore")
    string_decode = string_encode.decode(decoding)
    return string_decode

def quick_save_csv(save_path,field_names=None,list_rows=None,encoding='utf-8'):
    if field_names==None:
        field_names=[]
        if len(list_rows)==0:
            raise Exception("To infer the field names of data, please ensure the list is NOT empty.")
        model=list_rows[0]
        for k in model.keys():
            field_names.append(k)
    print(field_names)
    with open(save_path, 'w', newline='',encoding=encoding) as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        if list_rows!=None:
            for row in list_rows:
                dict_model = {}
                for f in field_names:
                    dict_model[f]=row[f]
                writer.writerow(dict_model)

def quick_json_obj(url,headers=None,data=None):
    if headers==None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        }
    if data!=None:
        x = requests.get(url, headers=headers, data=data)
    else:
        x = requests.get(url, headers=headers)
    # print(x.text)
    raw_str = quick_remove_unicode(x.text)
    pageObj = json.loads(raw_str)
    return pageObj

def quick_read_csv(csv_path,fields):
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        list_result=[]
        for row in reader:
            l=[]
            for f in fields:
                l.append(row[f])
            list_result.append(l)
        return list_result

def quick_read_csv_model(csv_path,encoding='utf-8'):
    with open(csv_path, newline='',encoding=encoding) as csvfile:
        reader = csv.DictReader(csvfile)
        list_result=[]
        for row in reader:
            list_result.append(row)
        return list_result

def quick_download_file(url,save_file_path,headers=None,):
    if headers!=None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        }
    r = requests.get(url, headers=headers, stream=True)
    if r.status_code == 200:
        open(save_file_path, 'wb').write(r.content)  # 将内容写入图片

def quick_post_html_page(url,headers=None,data=None):
    if headers!=None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        }
    if data!=None:
        r = requests.post(url, json=data,
                      headers=headers)
    else:
        r = requests.post(url)
    return r.text

def quick_post_json_obj(url,headers=None,data=None):
    if headers==None:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        }
    if data!=None:
        x = requests.post(url, headers=headers, data=data)
    else:
        x = requests.post(url, headers=headers)
    # print(x.text)
    raw_str = quick_remove_unicode(x.text)
    pageObj = json.loads(raw_str)
    return pageObj

def quick_save_text(file_path,str,encoding='utf-8'):
    f_out=open(file_path,'w',encoding=encoding)
    f_out.write(str)
    f_out.close()

def quick_read_text(file_path,encoding='utf-8'):
    f_in=open(file_path,'r',encoding=encoding)
    result=f_in.read()
    return result
'''
def quick_content(html_str):
    content = bare_extraction(html_str)
    return content
'''

def quick_remove_tags(html_str,remove_tags="style,script,svg,path,noscript"):
    html_obj = BeautifulSoup(html_str, features='lxml')
    remove_tag_list = remove_tags.split(",")
    for tag in remove_tag_list:
        for item in html_obj.findAll(tag):
            item.decompose()
    return str(html_obj)