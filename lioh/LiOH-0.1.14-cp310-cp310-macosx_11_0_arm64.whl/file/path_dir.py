import os
from typing import List,Tuple
import platform
if platform != 'Windows':
    def tmpfun():
        return 'ok'


def find_dir_name_path_list(path:str,name:str)->List[str]:
    '''输出路径下全部某名字文件路径'''
    name_path_list = []
    for fi in os.listdir(path):
        fi_path = path+'/'+fi
        if os.path.isdir(fi_path):
            #   如果是文件夹
            name_path_list.extend(find_dir_name_path_list(fi_path,name))
            tmp = fi_path.split('/')[-1]
            if tmp==name:
                name_path_list.append(fi_path)
    return name_path_list

def find_file_name_path_list(path:str,name:str)->List[str]:
    '''输出路径下全部某名字文件路径'''
    name_path_list = []
    for fi in os.listdir(path):
        fi_path = path+'/'+fi
        if os.path.isdir(fi_path):
            #   如果是文件夹
            name_path_list.extend(find_file_name_path_list(fi_path,name))
        else:
            #   如果是文件
            tmp = fi_path.split('/')[-1]
            if tmp==name:
                name_path_list.append(fi_path)
    return name_path_list

def find_suffix_path_list(path:str,suffix:str)->List[str]:
    '''输出路径下全部某后缀的文件路径'''
    suffix_path_list = []
    for fi in os.listdir(path):
        fi_path = path+'/'+fi
        if os.path.isdir(fi_path):
            #   如果是文件夹
            suffix_path_list.extend(find_suffix_path_list(fi_path,suffix))
        else:
            #   如果是文件
            tmp_suffix = fi_path.split('.')[-1]
            if tmp_suffix==suffix:
                suffix_path_list.append(fi_path)
    return suffix_path_list

def all_dir_file_paths(path:str)->Tuple[List[str],List[str]]:
    '''输出路径下全部文件夹,文件路径'''
    dirs_path = []
    files_path = []
    for fi in os.listdir(path):
        fi_path = path+'/'+fi
        if os.path.isdir(fi_path):
            #   如果是文件夹
            dirs_path.append(fi_path)
            tmp1,tmp2 = all_dir_file_paths(fi_path)
            dirs_path.extend(tmp1)
            files_path.extend(tmp2)
        else:
            #   如果是文件
            files_path.append(fi_path)
    return dirs_path,files_path

class dirPath():
    '''是一个文件夹的路径类, .path是该文件路径, .sub_dirs是子文件夹路径, .sub_files是子文件路径'''
    def __init__(self,path:str):
        self.path = path
        self.sub_dirs = []
        self.sub_files = []

    def tree(self,tmp_=''):
        tmp = tmp_
        tmp = tmp + self.path.split('/')[-1]
        print_str = tmp
        if tmp_ =='└── ':
            tmp_ = tmp_[:-4] + '    '
        elif tmp_!='':
            tmp_ = tmp_[:-4] + '│   '
        
        for i in range(len(self.sub_dirs)):
            if i==len(self.sub_dirs)-1 and len(self.sub_files)==0:
                tmp = tmp_  + '└── '
            else:
                tmp = tmp_ + '├── '
            print_str = print_str +'\n'+ self.sub_dirs[i].tree(tmp)

        for i in range(len(self.sub_files)):
            if i==len(self.sub_files)-1:
                tmp = tmp_ + '└── '
            else:
                tmp = tmp_ + '├── '
            print_str = print_str +'\n'+ tmp + self.sub_files[i].split('/')[-1]
        tmp_ = ''
        return print_str
                
def all_paths_dir_and_its_files(path:str,in_model_dir_list:List[str]=[],in_model_file_list:List[str]=[])->dirPath:
    ''' 输出路径下文件夹dirPath.认为dirPath是文件夹,str是文件。
        in_model_dir_list 是不显示的文件夹。
        in_model_file_list 是不显示的文件。
    '''
    def in_model(fi,in_model_list):
        in_model = True
        if fi in in_model_list:
            in_model = False
        # if fi=='__pycache__':
        #     in_model = False
        return in_model

    dirs_path = dirPath(path)
    for fi in os.listdir(path):
        fi_path = path+'/'+fi
        if os.path.isdir(fi_path):
            #   如果是文件夹
            if in_model(fi,in_model_dir_list):
                dirs_path.sub_dirs.append(all_paths_dir_and_its_files(fi_path,in_model_dir_list,in_model_file_list))
        else:
            #   如果是文件
            in_model_file_list.append('.DS_Store')
            if in_model(fi,in_model_file_list):
                dirs_path.sub_files.append(fi_path)
    dirs_path.sub_files.sort()
    return dirs_path

def print_dir_tree(path:str,in_model_dir_list:List[str]=[],in_model_file_list:List[str]=[]):
    ''' 打印文件夹树形结构。
        in_model_dir_list 是不显示的文件夹。
        in_model_file_list 是不显示的文件。
    '''
    print(all_paths_dir_and_its_files(path,in_model_dir_list,in_model_file_list).tree())