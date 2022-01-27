import hashlib
import os

from quick_crawler.browser import *
import uuid
from carbon2.api.submit import Carbon2Api
from tqdm import tqdm

def get_page_meta(html_str):
    try:
        soup = BeautifulSoup(html_str, features="lxml")
        title=""
        keywords=""
        description=""

        if soup!=None and soup.title!=None:
            title = soup.title.string


        # print(soup.attrs)
        html=soup.find("html")
        if "lang" in html.attrs.keys():
            lang = html["lang"]
        else:
            lang = ""
        # print("lang = ",lang)

        meta = soup.find_all('meta')
        # print(html_str)
        for tag in meta:
            if 'name' in tag.attrs.keys():
                name=tag.attrs['name'].strip().lower()
                if name=="description":
                    if 'content' in tag.attrs.keys():
                        description=tag.attrs['content']
                    else:
                        description=""
                if name=="keywords":
                    keywords=tag.attrs['content']
        model = {
            "title":title.replace("\n",""),
            "lang":lang,
            "keywords":keywords.replace("\n",""),
            "description":description.replace("\n","")
        }
    except:
        model = {
            "title": "",
            "lang": "",
            "keywords": "",
            "description":""
        }
    print("【Meta】")
    print('title = ', model["title"])
    print('keywords = ', model["keywords"])
    print('description = ', model["description"])
    print('language = ', model["lang"])
    return model

def upload_to_server(server_url,user_id,target_url,driver_path="",save_folder="html_data",use_md5url_as_id=False,tag="",language="",publishtime=""):
    print("==========Begin Upload===============")
    print("UserId: "+user_id, ", Target Url:"+target_url)

    if driver_path=="" or not os.path.exists(driver_path):
        print("Chromedriver.exe is not set due to the invalid driver path; use conventional crawler instead. ")

    # carbon2system's url
    root_url = f"{server_url}/api"
    c2api = Carbon2Api(root_url)

    # the page url that you want to upload
    # target_url="http://xinhuanet.com/"

    # 1. Generate an unique ID
    page_id=""
    if use_md5url_as_id:
        unique_id=hashlib.md5(target_url.encode())
        page_id=str(unique_id.hexdigest())
    else:
        unique_id = uuid.uuid4()
        page_id=str(unique_id)

    print(f"Using ID: {page_id}...")

    # check if exists
    if c2api.exists_url(target_url)==1:
        print(f"Url exists: {target_url}, skip the url.")
        return

    # 2. quick obtain an HTML page
    if driver_path=="" or not os.path.exists(driver_path):
        html_str=quick_html_page(target_url)
    else:
        html_str=get_html_str_with_browser(url=target_url,driver_path=driver_path,slient=True)
    if html_str=="":
        print("getting html page occurs error, empty html string, skip uploading")
        return

    if not os.path.exists(save_folder):
        print("Creating the folder: ", save_folder)
        os.mkdir(save_folder)
    saved_file_path=f"{save_folder}/{page_id}.txt"
    print("Saved file path: ", saved_file_path)
    f_out=open(saved_file_path,"w",encoding="utf-8")
    f_out.write(html_str)
    f_out.close()

    # 2.1 get meta info
    meta_model = get_page_meta(html_str)

    # 3. submit the meta data

    r=c2api.submit_metadata(target_url,meta_model["title"],user_id,keywords=meta_model["keywords"],description=meta_model["description"], file_id=page_id,tag=tag,language=language,publishtime=publishtime)

    if r==1:
        # 4. submit the file with same unique id
        r=c2api.submit_file(f"{save_folder}/{page_id}.txt")

        # 5. Verify if upload success
        download_url=f"{server_url}/WebData/{page_id}.txt"
        if check_url_ok(download_url):
            print("Upload successfully")
    else:
        print("Upload error: the url may be repeated!")
    print("==========End Upload===============")

# the csv file must contain fields real_url, title.
def submit_page_list(server_url, user_id,csv_file,save_html_folder, use_md5url_as_id=False, driver_path="browsers/chromedriver.exe",tag="",language="",url_field_name="real_url",publishtime="",try_raise_error=False):
    list_model = quick_read_csv_model(csv_file, encoding='utf-8')
    for idx,model in enumerate(list_model):
        print(f"{idx + 1}/{len(list_model)}")
        url = model[url_field_name]
        if try_raise_error:
            upload_to_server(server_url, user_id, url, use_md5url_as_id=use_md5url_as_id, driver_path=driver_path,
                             tag=tag, language=language, save_folder=save_html_folder, publishtime=publishtime)
        else:
            try:
                upload_to_server(server_url,user_id, url,use_md5url_as_id=use_md5url_as_id, driver_path=driver_path,tag=tag,language=language,save_folder=save_html_folder,publishtime=publishtime)
                print()
            except Exception as err:
                print("【ERROR】")
                print("Error Info: ",err)
                print()

def submit_url_list(server_url, user_id,list_url,use_md5url_as_id=False, driver_path="",tag="",language="",save_html_folder="html_data",publishtime=""):
    for idx,url in enumerate(list_url):
        try:
            print(f"{idx+1}/{len(list_url)}")
            upload_to_server(server_url,user_id, url,use_md5url_as_id=use_md5url_as_id, driver_path=driver_path,tag=tag,language=language,save_folder=save_html_folder,publishtime=publishtime)
            print()
        except:
            print("Error in calling API!")
            print()

