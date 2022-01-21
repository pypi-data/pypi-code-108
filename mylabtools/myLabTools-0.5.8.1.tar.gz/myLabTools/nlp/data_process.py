import json
import os

def read_tsv_data(data_file_path,encoding = "utf-8"):
    with open(data_file_path,"r",encoding = encoding) as f:
        data = []
        for line in f:
            data.append(line.strip().split("\t"))

def dict_list2jsonline_file(data,output_dir,saved_file_name):
    with open(os.path.join(output_dir,saved_file_name),"w+",encoding="utf-8") as f:
        for example in data:
            f.write(json.dumps(example,ensure_ascii=False)+"\n")

def train_dev_test_data2jsonline(data_dir,output_dir):
    file_name_list = ["dev","train","test"]
    for file_name in file_name_list:
        if os.path.exists(os.path.join(data_dir,file_name+".txt")):
            data = read_tsv_data(os.path.join(data_dir,file_name+".txt"))
            dict_list2jsonline_file(data,output_dir,file_name+".json")
        else:
            print("can not read ", os.path.join(data_dir,file_name+".txt"))
            