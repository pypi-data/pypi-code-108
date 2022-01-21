import pickle
import json
import string
from time import time
import logging
import re
from line_profiler import LineProfiler
from functools import wraps
import re
from os.path import join as pjoin

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')
en_char = string.ascii_lowercase+string.ascii_uppercase + " -_."

class PickleTool:
    def load_pkl(self,data_path):
        data = pickle.load(open(data_path ,"rb"))
        return data
    
    def dump_pkl(self,data,save_path):
        pickle.dump(data,open(save_path,"wb"))
        return True

class JsonTool:
    def load_json(self,data_path,encoding = "utf-8"):
        data = json.load(open(data_path,"r",encoding = encoding))
        return data
    
    
    def dump_json(self,data,save_path,encoding = "utf-8"):
        json.dump(data,open(save_path,"w+",encoding = encoding),ensure_ascii=False,indent=2)
        return True
    
    
    def dump_str(self,data):
        return json.dumps(data,ensure_ascii=False,indent=2)
    
    
    def load_str(self,data_str):
        return json.loads(data_str)
def is_all_eng(strs):
    '''
    print(is_all_eng('i love yiu '))
    print(is_all_eng('i love you'))
    print(is_all_eng('xx中国'))
    '''
    for i in strs:
        if i not in en_char:
            return False
    return True

def time_costing(func):
    def core():
        start = time()
        func()
        print('time costing:', time() - start)
    return core

def find_refs(text):
    citation_re_pattern = "REF#(.*?)#"
    citaions_id_list = re.findall(citation_re_pattern,text)
    return citaions_id_list

def code_ana(func,args = None):
    lp = LineProfiler()#实例化
    #测试jc函数性能
    lp_wrapper = lp(func) #输入函数
    if not args is None:
        lp_wrapper(*args) #输入函数参数
    lp.print_stats()

def func_line_time(f):
     @wraps(f)
     def decorator(*args, **kwargs):
         func_return = f(*args, **kwargs)
         lp = LineProfiler()
         lp_wrap = lp(f)
         lp_wrap(*args, **kwargs) 
         lp.print_stats() 
         return func_return 
     return decorator 

def cited_sents_extract(text):
    temp = re.findall("(“.*?”)", text)
    cited_sents  = []
    for sent in temp:
        if len(sent) >= 8 \
                or "，" in sent \
                or "。" in sent \
                or "？" in sent \
                or "！" in sent:
            cited_sents.append(sent)
    return cited_sents

def data_split(
    all_data, 
    test_size=0.2, 
    dev_size=0.2,
    saved_dir = "/data/code/python/ner/data/bieo/wiki"):
    """
    @description  : 将数据进行切分 训练集 60% ， 验证集 2）% ， 测试集 20%
                    保存在 saved_dir 中
    @param        :
    @Returns      :
    """
       
    from sklearn.model_selection import train_test_split
    data = {}
    data["train"], _temp, = train_test_split(
        all_data, test_size=test_size+dev_size, random_state=42)
    data["test"], data["dev"] = train_test_split(
        _temp, test_size=dev_size/(dev_size+test_size), random_state=42)
    for dataset_name,dataset in data.items():
        print(dataset_name)
        with open(pjoin(saved_dir , dataset_name + ".txt"),"w+",encoding = "utf-8") as f:
            for sample in dataset:
                for row in sample:
                    f.write("%s %s\n" % (row[0],row[1]))
                f.write("\n")


def gen_label_list(
    include_label_names_list, 
    saved_dir = "./",
    saved_name = "labels.txt",
    mode = "BIEO"):
    """
    @description  : 生成一个 ner 标签文件 label.txt
    @param        :
    @Returns      :
    """
    print(include_label_names_list)
    print("saved in :",pjoin(saved_dir,saved_name))
    print("*"*20)
    with open(pjoin(saved_dir,saved_name),"w+",encoding = "utf-8") as f:
        temp_labels = ["O"] + [prefix + "-" + label for prefix in list(mode[:-1]) for  label in include_label_names_list]
        for label in temp_labels:
            f.write("%s\n" % (label))
            print(label)
    print("*"*20)


def book_extract(text):
    '''
    书籍名称提取
    :param text:文本
    :return: list 书名
    '''
    books = re.findall("《.*?》", text)
    return books

punctuation = "~!@#$%^&*()_+`{}|\[\]\:\";\-\\\='<>?,，。“”‘’·？！a-zA-Z\d《》./"
def char_filter(text):
    '''
    文本过滤
    :param text:
    :return:
    '''
    text = re.sub(r'[{}]+'.format(punctuation), '', text)
    return text.strip()
