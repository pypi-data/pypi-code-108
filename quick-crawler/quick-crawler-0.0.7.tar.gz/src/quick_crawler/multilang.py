from quick_crawler import page, browser
import pickle
from quick_crawler.language import *

def get_sites_with_multi_lang_keywords(init_urls, src_term="digital economy",src_language="en",target_langs=None,use_dict_path="",
                              save_multilang_file=False,save_file_path="",save_data_folder="data",summarize_after_finished=False,summary_file_path="",max_num_urls=1000):
    if use_dict_path!="":
        dict_lang=pickle.load(open(use_dict_path,"rb"))
    else:
        dict_lang = get_lang_dict_by_translation(src_language, src_term,target_langs)
        if save_file_path=="":
            save_file_path=f"multi-lang-{src_term}.pickle"

    if save_multilang_file:
        pickle.dump(dict_lang, open(save_file_path, 'wb'))

    # https://www.w3newspapers.com/russia/
    # current folder path
    current_path = os.path.dirname(os.path.realpath(__file__))
    # get multi language search string

    #

    list_item=[]
    for item in init_urls:
        name=item[0]
        url=item[1]
        lang=item[2]
        print(lang)
        if lang in dict_lang:
            keyword = dict_lang[lang]
        else:
            print("Not Found Language: ",lang)
            keyword=src_term
        print("using keyword: ",keyword)
        if keyword==None:
            keyword=src_term
        print("Detecting...",url)
        '''
        lang=browser.get_language_code_of_page_quick(url)
        print("lang = ",lang)
        if lang==None:
            lang="en"
        if lang in dict_lang:
            keyword=dict_lang[lang]
        else:
            keyword=src_term
        '''
        list_item.append([name,url,keyword])

    browser.fetch_meta_info_from_sites(list_item, save_data_folder,
                                       is_save_fulltext=True,
                                       use_plain_text=False,
                                       max_num_urls=max_num_urls,
                                       use_keywords=True
                                       )

    if summarize_after_finished:
        list_model=browser.summarize_downloaded_data(data_folder=save_data_folder,
                                         save_path=summary_file_path
                                         )
        return list_model
    return None
